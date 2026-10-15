#!/usr/bin/env python3
"""Rescore archived census verdicts under the tree this script is run in.

EVIDENCE-REPRODUCTION SCRIPT, not platform code. It is committed here because the
measurement it produces (`registry/rescore-measurement.md`) would otherwise depend on a
file outside the repository - the same durability failure this phase already hit when 47
restored provenance bodies turned out to be gitignored. Nothing imports it, no test
collects it (the filename does not match `test_*.py`), and it runs no model, no GPU, no
dataset and no network: it replays a scorer over submissions and gold the platform already
recorded in each verdict's `evidence`.

Discovery is automatic: every census run carrying a `verdicts/` tree, a single recorded
`evidence.scorer_module`, and an unredacted `evidence.gold` is rescored with that module.

Usage:  python3 rescore-census-verdicts.py            # run from a checkout root
"""
from __future__ import annotations

import json
import pathlib
import sys

CENSUS = pathlib.Path('/mnt/20t/xubuqiang/hg-census/runs')

# The script lives outside the checkout, so Python put *its* directory on sys.path.
# Import the tree we are standing in, not the one the script happens to sit in.
sys.path.insert(0, str(pathlib.Path.cwd()))


def rescore_one(ev_score, ev_struct, evidence_aware, ev):
    """Return (reward, note) replicating the scaffold's dispatch (`check.py:251-260`)."""
    gold = ev.get('gold')
    if isinstance(gold, dict) and gold.get('redacted'):
        return None, 'redacted-gold'
    if gold is None:
        return None, 'no-gold'
    structured = ev.get('prediction') if 'prediction_file' in ev else None
    try:
        if structured is not None and evidence_aware and callable(ev_struct):
            result = ev_struct(structured, gold)
        else:
            prediction = (str(structured.get('answer')) if isinstance(structured, dict)
                          else str(ev.get('prediction') or ''))
            result = ev_score(prediction, gold)
    except Exception as exc:                       # noqa: BLE001
        return None, f'unmeasured:{type(exc).__name__}'
    if not isinstance(result, dict) or 'reward' not in result:
        return None, 'invalid-result'
    return float(result['reward']), 'measured'


def discover():
    """[(run_name, module_name, [verdict paths])] for every rescorable run."""
    found = []
    for run in sorted(p for p in CENSUS.iterdir() if p.is_dir()):
        vdir = run / 'verdicts'
        files = sorted(vdir.rglob('*.json')) if vdir.is_dir() else []
        if not files:
            continue
        modules = set()
        for f in files:
            ev = (json.loads(f.read_text()).get('evidence') or {})
            if ev.get('scorer_module'):
                modules.add(ev['scorer_module'])
        if len(modules) == 1:
            found.append((run.name, modules.pop(), files))
    return found


def main() -> int:
    for run, module_name, files in discover():
        dataset = module_name.rsplit('.', 1)[-1]
        try:
            module = __import__(module_name, fromlist=['score'])
        except Exception as exc:                   # noqa: BLE001
            print(json.dumps({'run': run, 'dataset': dataset, 'n': len(files),
                              'note': f'import-failed:{type(exc).__name__}'},
                             sort_keys=True))
            continue
        ev_score = getattr(module, 'score', None)
        ev_struct = getattr(module, 'score_prediction', None)
        aware = bool(getattr(module, 'EVIDENCE_AWARE', False))
        n = agree = 0
        notes: dict[str, int] = {}
        dis: list[dict] = []
        for f in files:
            verdict = json.loads(f.read_text())
            # The archived reward is `score`; it is the MEAN over trials, and each trial
            # carries its own submission - so rescore per trial and average.
            trials = verdict.get('trials') or []
            archived = verdict.get('score')
            if trials:
                per = [rescore_one(ev_score, ev_struct, aware, t.get('evidence') or {})
                       for t in trials]
                good = [r for r, note in per if r is not None]
                note = 'measured' if len(good) == len(per) else ';'.join(
                    sorted({note for r, note in per if r is None}))
                got = (sum(good) / len(good)) if good else None
            else:
                got, note = rescore_one(ev_score, ev_struct, aware,
                                        verdict.get('evidence') or {})
            n += 1
            notes[note] = notes.get(note, 0) + 1
            if got is None or archived is None:
                notes['skipped-no-comparison'] = notes.get('skipped-no-comparison', 0) + 1
                continue
            if abs(got - float(archived)) < 1e-6:
                agree += 1
            elif len(dis) < 25:
                sample = ((trials[0].get('evidence') or {}) if trials
                          else (verdict.get('evidence') or {}))
                dis.append({'task': verdict.get('task_id'), 'archived': archived,
                            'recomputed': got, 'trials': len(trials),
                            'prediction': str(sample.get('prediction'))[:90]})
        print(json.dumps({'run': run, 'dataset': dataset, 'n': n, 'agree': agree,
                          'disagree': n - agree, 'notes': notes,
                          'examples': dis[:6]}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
