"""Independent checks on the saved mapping and bounded worker deliverables."""
import csv
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

root = Path('tests/fixtures/hg_stratsplit')
summary = json.loads((root / 'binding-summary.json').read_text())
ids = json.loads((root / 'membership-ids.json').read_text())
rows = list(csv.DictReader((root / 'installed-row-binding.tsv').open(), delimiter='\t'))
assert len(rows) == 2290
assert [int(r['row_index']) for r in rows] == list(range(2290))
assert [r['task_id'] for r in rows] == ['strategyqa/test/' + str(i) for i in range(2290)]
assert Counter(r['original_partition'] for r in rows) == {'Train': 2290}
assert Counter(r['author_unofficial_partition'] for r in rows) == {'train': 2061, 'dev': 229}
assert Counter(r['imposed_side'] for r in rows) == {'train': 1520, 'eval': 770}
sets = {k: set(v) for k, v in ids.items()}
for row in rows:
    assert set(row['zip_qid_candidates'].split(',')) <= sets['distribution_train']
    assert set(row['author_qid_candidates'].split(',')) <= sets[
        'author_unofficial_' + row['author_unofficial_partition']]
ambiguous = [int(r['row_index']) for r in rows if ',' in r['zip_qid_candidates']]
assert ambiguous == [42, 1987]
for name in ['zip_qid_candidates', 'author_qid_candidates']:
    assert Counter(len(r[name].split(',')) for r in rows) == {1: 2288, 2: 2}
    singletons = {r[name] for r in rows if ',' not in r[name]}
    assert len(singletons) == 2288
    assert len(set(rows[42][name].split(','))) == 2
    assert rows[42][name] == rows[1987][name]
    assert not (singletons & set(rows[42][name].split(',')))
assert hashlib.sha256((root / 'installed-row-binding.tsv').read_bytes()).hexdigest() == summary['binding']['sha256']
assert all(len(r['csv_parsed_row_sha256']) == len(r['question_utf8_sha256']) == 64 for r in rows)
assert 'answer' not in rows[0] and 'question' not in rows[0]
for p in ['AGENTS.md', 'registry/dataset-blockers.json', 'registry/withdrawn-requirements.md',
          'docs/adapter-integration-journal.md', 'tests/fixtures/hg_wsel/strategyqa.json']:
    assert not subprocess.check_output(['git', 'diff', 'HEAD', '--', p])
receipts = list(root.glob('*.receipt.json'))
assert len(receipts) == 20
for p in receipts:
    r = json.loads(p.read_text())
    if 'raw_fixture' in r:
        target = Path(r['raw_fixture'])
        assert target.is_symlink()
        assert target.resolve().parent == Path('/mnt/20t/xubuqiang/hg-work/stratsplit')
        raw = target.read_bytes()
        assert len(raw) == r['bytes'] and hashlib.sha256(raw).hexdigest() == r['sha256']
    else:
        assert r['status'] is None and 'error' in r
proposal = json.loads(Path('registry/proposals/w-stratsplit.json').read_text())
assert proposal['status_change_requested'] is None
assert 'For any separately authorized diagnostic' in proposal['next_action_replacement']
assert 'Do not report local EM as original Accuracy.' in proposal['next_action_replacement']
print('PASS: saved mapping covers all 2290 ordered tasks; 2288 singleton IDs and two explicit duplicate rows; partition totals and membership sets agree; no answer/question columns.')
print('PASS: 20 request receipts; every observed raw response preserved outside git with exact size/digest; protected files unchanged; proposal retains diagnostic and metric restrictions.')
