#!/usr/bin/env python3
"""Independent consistency/custody check; no comparator or scorer calls."""
from collections import Counter
import hashlib
import json
from pathlib import Path


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    here = Path(__file__).resolve().parent
    inventory = (here / 'eligibility.jsonl').read_bytes()
    records = [json.loads(line) for line in inventory.splitlines()]
    summary = json.loads((here / 'summary.json').read_bytes())
    metadata_bytes = Path(summary['metadata']['path']).read_bytes()
    rows = json.loads(metadata_bytes)
    root = Path(summary['metadata']['path']).parents[1]
    assert len(records) == len(rows) == 400
    assert len({r['task_id'] for r in records}) == 400
    assert sha(metadata_bytes) == summary['metadata']['sha256']
    assert sha(inventory) == summary['inventory_sha256']
    assert len(inventory) == summary['inventory_bytes'] < 1_000_000
    count = Counter(r['classification'] for r in records)
    assert dict(count) == {k: v for k, v in summary['classes'].items() if v}
    rehashed = 0
    for i, (record, row) in enumerate(zip(records, rows)):
        assert record['task_id'] == str(row['id']) and record['metadata_index'] == i
        canonical = json.dumps(row, ensure_ascii=False, sort_keys=True,
                               separators=(',', ':'), allow_nan=False).encode()
        assert record['row_sha256'] == sha(canonical)
        assert record['metadata_sha256'] == sha(metadata_bytes)
        assert record['answer_position'] == row['answer_position']
        assert record['declared_exclude'] == row.get('exclude')
        assert record['execution_eligibility'] == 'UNKNOWN' and record['measured'] is None
        for book in record['inputs'].values():
            assert sha((root / book['path']).read_bytes()) == book['sha256']
            assert book['archive_member_equal'] is True
            rehashed += 1
        if record['classification'] == 'structurally_gradable':
            assert record['single_variant']
            assert all(b['ooxml_open'] for b in record['inputs'].values())
            assert all(t['sheet_present'] and t['addressable']
                       for t in record['inputs']['golden']['targets'])
            assert all(c['cell_count'] > 0 for c in record['references'])
    zero = [r['task_id'] for r in records if r['classification'] == 'range_zero_policy_only']
    assert zero == ['283-32']
    for key in ('measured_task_coverage', 'trial_coverage', 'selected', 'invalid',
                'unmeasured', 'run_id'):
        assert summary[key] is None
    assert summary['production_authorized'] is False
    print(json.dumps({'valid': True, 'rows': len(records), 'workbooks_rehashed': rehashed,
                      'classes': dict(sorted(count.items())),
                      'not_gradable': {r['task_id']: r['reason'] for r in records
                                       if r['classification'] == 'not_gradable_as_installed'},
                      'range_zero_tasks': zero,
                      'formula_routes': summary['formula_routes'],
                      'inventory_bytes': len(inventory), 'inventory_sha256': sha(inventory)},
                     sort_keys=True))


if __name__ == '__main__':
    main()
