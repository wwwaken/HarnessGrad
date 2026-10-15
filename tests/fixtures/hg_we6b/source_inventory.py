"""Print current file:line branch anchors and source digests, without adapter imports."""
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[3]
old = json.loads((root / 'reports/w-e6-evidence/source-audit.json').read_text())
paths = sorted(set(old['sources']) | {'eval/verification/pristine.py', 'eval/verification/native_runtime.py'})
pattern = re.compile(
    r'^\s*(?:def |class |(?:try|finally|except|elif |else:|if )|(?:_SPEC|VERIFY|DEFAULT_ENV|ENV_BASE)\b)'
    r'|\b(?:subprocess\.(?:run|Popen)|multiprocessing\.Process|timeout_s|timeout=|\.kill\(|\.terminate\(|'
    r'\.wait\(|\.join\(|\.close\(|signal\.|conn(?:ection)?\.|scorer_bundle|QASpec\(|scorer_input|'
    r'remove_container\(|remove_image\(|remove_network\(|mounts_for\(|\.stop\(|\.start\(|'
    r'container_mod\.(?:run|create|commit|exec_in)|api_calls\.jsonl|sqlite3\.connect|replay\(|load_task\(|load_game\()')
registry = json.loads((root / 'registry/dataset-blockers.json').read_text())
participants = [d['dataset'] for d in registry['datasets'] if 'artifact-only-state-export' in d['shared_blockers']]
print(json.dumps({'shared_dataset_count': len(participants), 'shared_datasets': participants,
                  'source_file_count': len(paths)}))
for rel in paths:
    raw = (root / rel).read_bytes()
    print(f'SOURCE {rel} sha256={hashlib.sha256(raw).hexdigest()} bytes={len(raw)}')
    for n, line in enumerate(raw.decode().splitlines(), 1):
        if pattern.search(line):
            print(f'{rel}:{n}: {line}')
