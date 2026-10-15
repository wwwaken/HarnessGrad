#!/usr/bin/env python3
"""Focused evidence checks; no scorer/runtime invocation."""
import hashlib
import json
from pathlib import Path

packet = Path(__file__).resolve().parent
files = sorted(p for p in packet.rglob('*') if p.is_file())
for p in files:
    assert p.stat().st_size < 1000000, p
    p.read_bytes().decode('utf-8')
json_records = 0
for p in sorted(packet.glob('*.jsonl')):
    for line in p.read_text().splitlines():
        json.loads(line)
        json_records += 1
source_rows = [json.loads(l) for l in (packet / 'source-modules.jsonl').read_text().splitlines()]
for r in source_rows:
    p = Path(r['path'])
    assert hashlib.sha256(p.read_bytes()).hexdigest() == r['sha256'] == r['prior_inventory_sha256']
for name in ('licenses.jsonl', 'archive-licenses.jsonl', 'native-licenses.jsonl'):
    for l in (packet / name).read_text().splitlines():
        r = json.loads(l)
        if r.get('retained_path'):
            actual = hashlib.sha256(Path(r['retained_path']).read_bytes()).hexdigest()
            assert actual == r.get('retained_sha256', r['sha256']), r
citations = []
for part in Path('registry/w-bfclrt-custody.md').read_text().split(chr(96)):
    if part.startswith(('tests/', 'registry/')) and ':' in part:
        name, number = part.rsplit(':', 1)
        if number.isdigit():
            citations.append((name, number))
counts = {}
for name, number in citations:
    p = Path(name)
    assert p.is_file(), (name, number)
    if name not in counts:
        counts[name] = len(p.read_text().splitlines())
    assert 1 <= int(number) <= counts[name], (name, number, counts[name])
summary = json.loads((packet / 'summary.jsonl').read_text())
assert not summary['closure_complete'] and not summary['official_scorer_executed']
assert not summary['production_authorized']
proposal = json.loads(Path('registry/proposals/w-bfclrt.json').read_text())
assert set(proposal) == {'worker', 'dataset', 'blocker', 'observed_append', 'next_action_replacement'}
assert proposal['worker'] == 'w-bfclrt' and proposal['dataset'] == 'bfcl_v3'
assert proposal['blocker'] == 'simple-ast-contract'
assert 'leave this blocker external/open' in proposal['next_action_replacement']
assert 'scorer-offline-closure' not in proposal['next_action_replacement']
assert 'artifact-only-state-export' not in proposal['next_action_replacement']
print(json.dumps({'valid': True, 'packet_text_files': len(files),
                  'jsonl_records': json_records, 'source_hashes_rechecked': len(source_rows),
                  'report_file_line_citations_checked': len(citations),
                  'max_packet_file_bytes': max(p.stat().st_size for p in files),
                  'scope': 'packet integrity and bounded citations; not complete runtime/scorer validation'},
                 sort_keys=True))
