#!/usr/bin/env python3
"""Verify recorded evidence without constructing/scoring/generating any dataset."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / 'tests/fixtures/hg_gymelig'
SCRATCH = Path('/mnt/20t/xubuqiang/hg-work/gymelig/control-01')
v = json.loads((FIXTURE / 'verdicts.json').read_text())
m = json.loads((FIXTURE / 'package-members.json').read_text())
p = json.loads((ROOT / 'registry/proposals/w-gymelig.json').read_text())
registry = json.loads((ROOT / 'registry/dataset-blockers.json').read_text())
b = next(d for d in registry['datasets'] if d['dataset'] == 'reasoning_gym')['blockers'][0]
assert b['id'] == p['blocker'] == 'dataset-journal-gap'
for record in [v['pool_before'], v['pool_after'], v['runner'], v['declaration'], v['interpreter']] + m['members']:
    data = Path(record['path']).read_bytes()
    assert len(data) == record['bytes']
    assert hashlib.sha256(data).hexdigest() == record['sha256'], record['path']
print('digest_validation=PASS (pool before/after, runner, declaration, interpreter, all 344 recorded package members)')
for name in ('verdicts.json', 'package-members.json'):
    assert (FIXTURE / name).read_bytes() == (SCRATCH / name).read_bytes()
assert (FIXTURE / 'control.stdout.txt').read_bytes() == SCRATCH.with_suffix('.stdout.txt').read_bytes()
assert SCRATCH.with_suffix('.stderr.txt').read_bytes() == b''
print('scratch_copy_validation=PASS (verdicts, members, exact stdout; shell stderr bytes=0)')
constants = {}
for node in ast.parse((ROOT / 'data/datasets/reasoning_gym/prepare.py').read_text()).body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in {'FAMILIES', 'PER_FAMILY'}:
                constants[target.id] = ast.literal_eval(node.value)
assert len(constants['FAMILIES']) == 89 and constants['PER_FAMILY'] == 20
assert [f['family'] for f in v['families']] == list(constants['FAMILIES'])
pool_lines = Path(v['pool_before']['path']).read_bytes().splitlines()
assert len(pool_lines) == 1780
source_paths = set()
failures = {k: [] for k in ('reference_not_full', 'empty_not_zero', 'exceptions', 'refusals', 'constructor_exceptions', 'unexecuted')}
types = Counter()
for family_position, family in enumerate(v['families']):
    name = family['family']
    if family['construction']['outcome'] != 'success':
        failures['constructor_exceptions'].append(name)
    assert len(family['rows']) == 20
    for point in ('entry_point', 'constructor'):
        loc = family[point]
        assert loc['path'] in {r['path'] for r in m['members']}
        assert loc['qualified_name'].startswith('reasoning_gym.')
        source_lines = Path(loc['path']).read_text().splitlines()
        assert source_lines[loc['line'] - 1].lstrip().startswith('def ')
    source_paths.add(family['entry_point']['path'])
    for index, row in enumerate(family['rows']):
        # Strict payload schema: coordinates, digest and verdicts only; no question/gold/reference string.
        assert set(row) == {'index', 'pool_line', 'row_sha256', 'reference', 'empty'}
        assert row['index'] == index
        assert row['pool_line'] == family_position * 20 + index + 1
        original = pool_lines[row['pool_line'] - 1]
        assert row['row_sha256'] == hashlib.sha256(original).hexdigest()
        # Parse only coordinates to prove no row swap, without printing payloads.
        original_row = json.loads(original)
        assert original_row['family'] == name and original_row['index'] == index
        for key, target in (('reference', 1.0), ('empty', 0.0)):
            verdict = row[key]
            outcome = verdict['outcome']
            if outcome == 'score':
                assert set(verdict) == {'outcome', 'value', 'return_type'}
                assert type(verdict['value']).__name__ == verdict['return_type']
                types[verdict['return_type']] += 1
                if verdict['value'] != target:
                    failures['reference_not_full' if key == 'reference' else 'empty_not_zero'].append([name, index, verdict['value']])
            else:
                failures[{'exception': 'exceptions', 'refusal': 'refusals', 'unexecuted': 'unexecuted'}[outcome]].append([name, index, key])
    refs = sum(r['reference'].get('value') == 1.0 for r in family['rows'])
    empties = sum(r['empty'].get('value') == 0.0 for r in family['rows'])
    assert refs == family['reference_full_credit_rows']
    assert empties == family['empty_zero_rows']
    assert family['eligible_on_all_frozen_rows'] == (refs == empties == 20)
assert not any(failures.values())
assert v['summary'] == {'families_tested': 89, 'rows_tested': 1780, 'score_calls': 3560,
 'reference_full_credit': 89, 'empty_zero': 89, 'reference_full_credit_rows': 1780,
 'empty_zero_rows': 1780, 'eligible_families': 89, 'exceptions': 0, 'refusals': 0,
 'constructor_exceptions': 0, 'non_eligible': []}
assert len(source_paths) == 57 and m['count'] == len(m['members']) == 344
assert v['endpoint_binding'] is None and v['model_outputs_scored'] == 0
assert v['guards']['blocked_events'] == []
assert not v['production_authorized']
print('record_scope=89 declared families x all frozen indices 0..19 x reference/empty; rows=1780; calls=3560')
print('entry_points=57 distinct implementation source files; every source/constructor location and digest validated')
print('payload_schema=PASS (coordinates, digests, scalar verdicts; no pool payload fields)')
print('actual_return_types=' + json.dumps(dict(types), sort_keys=True))
for key, values in failures.items():
    print(key + '=' + json.dumps(values, sort_keys=True))
assert hashlib.sha256(b['next_action'].encode()).hexdigest() == p['next_action_base_sha256']
old = 'Independently establish behavioral reference=1/empty=0 family eligibility.'
assert b['next_action'].count(old) == 1
prefix, suffix = b['next_action'].split(old)
assert p['next_action_replacement'].startswith(prefix)
assert p['next_action_replacement'].endswith(suffix)
assert p['next_action_replacement'] != b['next_action']
assert p['families_tested'] == p['reference_full_credit'] == p['empty_zero'] == 89
assert p['exceptions'] == p['refusals'] == 0 and p['non_eligible'] == []
print('proposal_validation=PASS (only behavioral sentence replaced; every other next_action byte retained)')
report = (ROOT / 'registry/w-gymelig-eligibility.md').read_text()
assert len(re.findall(r'^\| `[^`]+` \| `reasoning_gym\.', report, re.M)) == 89
for match in re.finditer(r'`((?:tests|registry|data)/[^`:\n ]+):(\d+)`', report):
    path = ROOT / match[1]
    assert path.is_file(), str(path)
    assert 1 <= int(match[2]) <= len(path.read_text().splitlines()), match[0]
for script in (FIXTURE / 'control.py', FIXTURE / 'verify.py'):
    compile(script.read_text(), str(script), 'exec')
print('report_validation=PASS (89 family rows; explicit repository file:line references exist; Python scripts compile in memory)')
print('summary=' + json.dumps(v['summary'], sort_keys=True))
