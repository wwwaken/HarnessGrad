#!/usr/bin/env python3
"""Rescore archived census verdicts under the tree this script is run in.

EVIDENCE-REPRODUCTION SCRIPT, not platform code. It is committed here because the
measurement it produces (`registry/rescore-measurement.md`) would otherwise depend on a
file outside the repository - the same durability failure this phase already hit when 47
restored provenance bodies turned out to be gitignored. Nothing imports it, no test
collects it (the filename does not match `test_*.py`), and it runs no model, no GPU and no
dataset: it replays a scorer over submissions and gold the platform already recorded.

No model, no GPU, no dataset run: it replays the *scorer* over the per-task
submission and gold that the platform already recorded in each verdict's
`evidence`, exactly as `data/scaffolds/qa/verify/check.py:251-260` does.

Prints one JSON object per (run, dataset) to stdout, plus per-task disagreement
records, so two trees can be diffed.

Usage:  python3 rescore.py            # run from a checkout root
"""
from __future__ import annotations

import json
import pathlib
import sys

CENSUS = pathlib.Path('/mnt/20t/xubuqiang/hg-census/runs')

# The script lives outside the checkout, so Python put *its* directory on sys.path.
# Import the tree we are standing in, not the one the script happens to sit in.
sys.path.insert(0, str(pathlib.Path.cwd()))

# (run directory, dataset name as it appears in `data.datasets.<name>`)
TARGETS = [
    ('gsm8k-qwen-t3-eval-full', 'gsm8k'),
    ('night-physicsquestions-eval', 'physicsquestions'),
    ('night-physicsquestions-train', 'physicsquestions'),
    ('probe2-twowikimultihopqa', 'twowikimultihopqa'),
    ('probe2-fever', 'fever'),
]

# Keys the scaffold records; `redacted` gold cannot be rescored from a verdict.
def load(run: str, dataset: str):
    module = __import__(f'data.datasets.{dataset}', fromlist=['score'])
    ev_score = getattr(module, 'score', None)
    ev_struct = getattr(module, 'score_prediction', None)
    evidence_aware = bool(getattr(module, 'EVIDENCE_AWARE', False))
    return module, ev_score, ev_struct, evidence_aware


def rescore_one(ev_score, ev_struct, evidence_aware, ev):
    """Return (reward, note) replicating the scaffold's dispatch."""
    gold = ev.get('gold')
    if isinstance(gold, dict) and gold.get('redacted'):
        return None, 'redacted-gold'
    structured = ev.get('prediction') if 'prediction_file' in ev else None
    for mode_kw in ({'mode': ev.get('score_mode')} if ev.get('score_mode') else {},):
        try:
            if (structured is not None and evidence_aware and callable(ev_struct)):
                result = ev_struct(structured, gold, **mode_kw)
            else:
                prediction = (str(structured.get('answer')) if isinstance(structured, dict)
                              else str(ev.get('prediction') or ''))
                result = ev_score(prediction, gold, **mode_kw)
        except Exception as exc:                       # noqa: BLE001
            return None, f'unmeasured:{type(exc).__name__}'
    if not isinstance(result, dict) or 'reward' not in result:
        return None, 'invalid-result'
    return float(result['reward']), 'measured'


def main() -> int:
    for run, dataset in TARGETS:
        vdir = CENSUS / run / 'verdicts'
        files = sorted(vdir.rglob('*.json')) if vdir.is_dir() else []
        if not files:
            print(json.dumps({'run': run, 'dataset': dataset, 'n': 0,
                              'note': 'no verdicts'}, sort_keys=True))
            continue
        ev_score, ev_struct, aware = load(run, dataset)[1:]
        n = agree = 0
        notes: dict[str, int] = {}
        dis: list[dict] = []
        for f in files:
            verdict = json.loads(f.read_text())
            # The archived reward is the verdict's `score` (the same number the scaffold
            # puts in `evidence.reward`); there is no top-level `reward` key. It is the
            # MEAN over trials, and each trial carries its own submission - so rescore
            # per trial and average, or a multi-trial task compares a mean to one sample.
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
                got, note = rescore_one(ev_score, ev_struct, aware, verdict.get('evidence') or {})
            n += 1
            notes[note] = notes.get(note, 0) + 1
            if got is None or archived is None:
                notes['skipped-no-comparison'] = notes.get('skipped-no-comparison', 0) + 1
                continue
            if abs(got - float(archived)) < 1e-12:
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
