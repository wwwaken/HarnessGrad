#!/usr/bin/env python3
"""Authored scorer controls, never generated tasks or benchmark pool rows."""
from __future__ import annotations

import hashlib
import importlib.metadata
import inspect
import json
from pathlib import Path
import sys
import traceback
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
PROVENANCE = ROOT / 'tests/fixtures/hg_wprov/reasoning_gym/responses'


def sha(body):
    return hashlib.sha256(body).hexdigest()


def identity():
    """Recompute actual installed package bytes against published wheel and Git tree."""
    dist = importlib.metadata.distribution('reasoning-gym')
    assert dist.version == '0.1.25'
    wheel_path = PROVENANCE / 'pypi-bdist_wheel.body'
    pypi = json.loads((PROVENANCE / 'pypi-0.1.25.body').read_bytes())
    artifact = next(v for v in pypi['urls'] if v['packagetype'] == 'bdist_wheel')
    assert sha(wheel_path.read_bytes()) == artifact['digests']['sha256']
    tag = json.loads((PROVENANCE / 'github-tag.body').read_bytes())
    commit = json.loads((PROVENANCE / 'github-commit.body').read_bytes())
    tree = json.loads((PROVENANCE / 'github-tree.body').read_bytes())
    assert tag['object']['sha'] == commit['sha'] == '21e6d2a9a581b3e11aafe711abfd37402f8482d5'
    assert commit['tree']['sha'] == tree['sha'] and not tree['truncated']
    entries = {v['path']: v for v in tree['tree']}
    members = []
    with zipfile.ZipFile(wheel_path) as wheel:
        for name in sorted(wheel.namelist()):
            if not name.startswith('reasoning_gym/'):
                continue
            path = Path(dist.locate_file(name))
            body = path.read_bytes()
            git_blob = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
            assert body == wheel.read(name) and git_blob == entries[name]['sha'], name
            members.append({'path': str(path), 'package_path': name, 'sha256': sha(body),
                            'bytes': len(body), 'git_blob': git_blob})
    sources = {}
    from reasoning_gym import create_dataset
    for family in ('chain_sum', 'letter_counting', 'word_sorting'):
        scorer = type(create_dataset(family, seed=20261008, size=20)).score_answer
        path = Path(inspect.getsourcefile(scorer))
        sources[family] = {'callable': scorer.__module__ + '.' + scorer.__qualname__,
                           'path': str(path), 'sha256': sha(path.read_bytes()),
                           'method_source_sha256': sha(inspect.getsource(scorer).encode())}
    return {'distribution': dist.metadata['Name'], 'version': dist.version,
            'revision': commit['sha'], 'wheel_sha256': sha(wheel_path.read_bytes()),
            'wheel_path': str(wheel_path.relative_to(ROOT)),
            'provenance_receipts': {p.name: sha(p.read_bytes()) for p in
                                   (PROVENANCE / n for n in ('pypi-0.1.25.body', 'github-tag.body',
                                                             'github-commit.body', 'github-tree.body'))},
            'installed_package_members': members, 'package_member_count': len(members),
            'package_manifest_sha256': sha(json.dumps(members, sort_keys=True).encode()),
            'scorers': sources,
            'scope': 'full installed package import; direct upstream methods; no generated item or pool read; dependencies not independently authenticated'}


def execute(side, inputs):
    from reasoning_gym import create_dataset
    if side == 'local':
        from data.datasets import reasoning_gym as adapter
        assert adapter._SPEC._records == []
    rows = []
    for row in inputs['cases']:
        gold = row['gold']
        try:
            if side == 'official':
                dataset = create_dataset(gold['family'], seed=20261008, size=20)
                raw = dataset.score_answer(answer=row['prediction'], entry=gold['entry'])
                score = float(raw)
            else:
                raw = adapter.score(row['prediction'], gold)
                score = raw['reward']
            rows.append({'id': row['id'], 'raw_return': raw, 'score': score, 'error': None})
        except Exception as exc:
            rows.append({'id': row['id'], 'score': None, 'error': type(exc).__name__,
                         'message': str(exc), 'traceback': traceback.format_exc()})
    if side == 'local':
        assert adapter._SPEC._records == []
    return {'side': side, 'inputs_sha256': sha((HERE / 'inputs.json').read_bytes()),
            'identity': identity(),
            'adapter_sha256': sha((ROOT / 'data/datasets/reasoning_gym.py').read_bytes()),
            'cases': rows, 'production_runtime_observation': False}


def compare(inputs):
    official = json.loads((HERE / 'official.json').read_text())
    local = json.loads((HERE / 'local.json').read_text())
    assert official['identity'] == local['identity']
    rows = []
    for inp, off, loc in zip(inputs['cases'], official['cases'], local['cases'], strict=True):
        assert inp['id'] == off['id'] == loc['id']
        numeric = off['error'] is None and loc['error'] is None
        rows.append({'id': inp['id'], 'family': inp['gold']['family'],
                     'official_score': off['score'], 'local_score': loc['score'],
                     'official_error': off['error'], 'local_error': loc['error'],
                     'numeric_comparison': numeric,
                     'agreement': off['score'] == loc['score'] if numeric else None})
    return {'controlled_inputs': len(rows),
            'numeric_comparisons': sum(r['numeric_comparison'] for r in rows),
            'agreements': sum(r['agreement'] is True for r in rows),
            'divergences': sum(r['agreement'] is False for r in rows),
            'official_errors': sum(r['official_error'] is not None for r in rows),
            'local_errors': sum(r['local_error'] is not None for r in rows),
            'nonnumeric_inputs': sum(not r['numeric_comparison'] for r in rows), 'cases': rows}


if __name__ == '__main__':
    mode = sys.argv[1]
    inputs = json.loads((HERE / 'inputs.json').read_text())
    print(json.dumps(compare(inputs) if mode == 'compare' else execute(mode, inputs), indent=2))
