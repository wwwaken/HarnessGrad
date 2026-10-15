#!/usr/bin/env python3
"""Recompute custody, local source, inputs, outcomes and fixture integrity."""
import hashlib
import json
from pathlib import Path

from run import HERE, ROOT, compare, identity


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    count = 0
    listed = set()
    for line in (HERE / 'SHA256SUMS').read_text().splitlines():
        expected, relative = line.split('  ', 1)
        path = HERE / relative
        assert path.is_file() and sha(path) == expected, relative
        listed.add(relative)
        count += 1
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name != 'SHA256SUMS'}
    assert actual == listed
    inputs = json.loads((HERE / 'inputs.json').read_text())
    official = json.loads((HERE / 'official.json').read_text())
    local = json.loads((HERE / 'local.json').read_text())
    attempt = json.loads((HERE / 'import.json').read_text())
    assert official['identity'] == local['identity'] == attempt['identity'] == identity()
    assert official['adapter_sha256'] == local['adapter_sha256'] == sha(ROOT / 'data/datasets/bfcl_v3.py')
    comparison = json.loads((HERE / 'compare.json').read_text())
    assert comparison == compare(inputs)
    for side in ('import', 'official', 'local', 'compare'):
        receipts = [json.loads(line) for line in (HERE / f'{side}-offline.txt').read_text().splitlines()]
        guard = receipts[0]
        assert guard['production_runtime_observation'] is False
        assert all(p['errno'] == 1 and p['result'] == 'denied' for p in guard['socket_probes'].values())
        assert receipts[-1]['blocked_external_dataset_reads'] == []
    assert attempt['temporary_project_root_removed'] and attempt['handler_constructed'] is False
    assert all(not a['imported'] for a in attempt['attempts'])
    summary = {k: v for k, v in comparison.items() if k != 'cases'}
    print(json.dumps({'manifest_files_verified': count, 'verified_custody_members': len(official['identity']['verified_members']),
                      'comparison': summary, 'source_functions_only': True}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
