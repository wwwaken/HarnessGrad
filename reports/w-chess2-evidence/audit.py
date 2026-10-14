"""Read-only verification of original receipts, extraction identity and scoped edits."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
EX = OUT / 'execution'
identity = json.loads((EX / 'identity.json').read_text())
run = Path(identity['run_dir'])
sha = lambda data: hashlib.sha256(data).hexdigest()
read = lambda name: json.loads((EX / name).read_text())
result = read('task-result.json')
policy = read('diagnostic_receipt.json')
inventory = json.loads((OUT / 'artifact-inventory.json').read_text())
with tarfile.open(OUT / 'run-artifacts.tar.gz') as tar:
    for row in inventory:
        original = Path(row['source']).read_bytes()
        copy = (ROOT / row['copy']).read_bytes()
        archived = tar.extractfile(run.name + '/' + row['relative_path']).read()
        assert original == copy == archived
        assert len(original) == row['bytes'] and sha(original) == row['sha256']
archive = json.loads((OUT / 'archive-sha256.json').read_text())
assert sha((ROOT / archive['path']).read_bytes()) == archive['sha256']
assert (OUT / 'actor-trace.jsonl').read_text() == result['trace']
prior = json.loads((ROOT / 'reports/w-chess-evidence/execution/task-result.json').read_text())
assert (OUT / 'previous-trace.jsonl').read_text() == prior['trace']
for step in (6, 7):
    item = json.loads((OUT / f'previous-step-{step}.json').read_text())
    event = json.loads(prior['trace'].splitlines()[item['trace_line'] - 1])
    assert item['command'] == event['command']
    assert (OUT / f'previous-step-{step}.sh').read_text() == event['command']
for line in (17, 19, 22, 83, 84):
    event = json.loads(result['trace'].splitlines()[line - 1])
    assert json.loads((OUT / f'actor-trace-line-{line}.json').read_text()) == event
    if line in (17, 19, 22):
        assert (OUT / f'actor-command-line-{line}.sh').read_text() == event['codex_event']['item']['command'] + '\n'
assert policy['context']['hashes']['manifest'] == sha((EX / 'launch/manifest.json').read_bytes())
assert read('launch/platform-diff.json') == dict(added=[], removed=[], modified=[])
verdict = result['verdict']
assert verdict['evidence']['measured'] is False and 'score' not in verdict
assert policy['score'] is None
before = json.loads(subprocess.check_output(['git', 'show', 'HEAD:docs/dataset-blockers.json'], cwd=ROOT, text=True))
after = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
old_chess = next(row for row in before['datasets'] if row['dataset'] == 'chessbench_puzzles')
new_chess = next(row for row in after['datasets'] if row['dataset'] == 'chessbench_puzzles')
old_target = next(b for b in old_chess['blockers'] if b['id'] == 'trusted-stepwise-transport')
new_target = next(b for b in new_chess['blockers'] if b['id'] == 'trusted-stepwise-transport')
assert old_target['status'] == new_target['status'] == 'runtime'
assert old_target['next_action'] == new_target['next_action']
new_chess['blockers'][new_chess['blockers'].index(new_target)] = old_target
assert after == before  # Includes interruption-closure, shared gates and all history.
old_journal = subprocess.check_output(['git', 'show', 'HEAD:docs/adapter-integration-journal.md'], cwd=ROOT)
assert (ROOT / 'docs/adapter-integration-journal.md').read_bytes().startswith(old_journal)
production = subprocess.check_output(['git', 'diff', '--name-only', '--', 'eval', 'data', 'driver.py', 'base_harness'], cwd=ROOT, text=True).splitlines()
assert production == []
record = dict(run_id=identity['run_id'], original_copy_archive_files_checked=len(inventory),
              original_copy_archive_match=True, trace_extractions_match=True,
              manifest_binding_matches=True, unrelated_registry_entries_unchanged=True,
              journal_append_only=True, production_diff_paths=production,
              protocol=verdict['protocol'], scorer_isolation_class=verdict['scorer_isolation_class'],
              measured=verdict['evidence']['measured'], raw_unmeasured_reason=verdict['unmeasured'],
              transport_reason=verdict['evidence']['transport']['reason'],
              coverage=policy['coverage'])
with (OUT / 'report-audit.json').open('x') as f:
    json.dump(record, f, indent=2)
    f.write('\n')
print(json.dumps(record, indent=2))
