"""Static current-source branch inventory; no adapter imports or benchmark access."""
import ast
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'reports/w-e6-evidence/source-audit.json'
registry = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
shared = [d['dataset'] for d in registry['datasets'] if 'artifact-only-state-export' in d['shared_blockers']]
excluded = [d['dataset'] for d in registry['datasets'] if d['dataset'] not in shared]
paths = [ROOT / 'data/datasets' / (name + '.py') for name in shared]
paths += [p for name in shared for p in (ROOT / 'data/datasets' / name).glob('verify/check.py')]
paths += [ROOT / p for p in ('data/scaffolds/qa/base.py', 'data/scaffolds/qa/verify/check.py',
          'eval/verification/verifier.py', 'eval/service/services.py', 'eval/containers/container.py',
          'eval/containers/sandbox.py', 'eval/containers/container_state.py', 'eval/run/runner.py',
          'data/datasets/appworld/server.sh', 'data/datasets/appworld/service.py')]
audit = {'shared_dataset_count': len(shared), 'shared_datasets': shared,
         'registry_entries_without_shared_reference': excluded, 'sources': {}}
pattern = re.compile(r'\b(VERIFY|ENV|DEFAULT_ENV|ENV_BASE|QASpec|_SPEC|_verifier|verify_for|def _verify|subprocess|Popen|Process|kill|terminate|wait|join|timeout|finally|close|rmtree|mkdtemp|TemporaryDirectory|scorer_input|_verify_container_state|mounts_for|remove_container|remove_image|record|state|network)\b')
for path in sorted(set(paths)):
    data = path.read_bytes()
    lines = data.decode().splitlines()
    rel = str(path.relative_to(ROOT))
    audit['sources'][rel] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
             'matching_lines': {str(i): line for i, line in enumerate(lines, 1) if pattern.search(line)}}
    # Numbered complete copies make file+line review independent of later merges.
    copy = ROOT / 'reports/w-e6-evidence/source' / (rel + '.txt')
    copy.parent.mkdir(parents=True, exist_ok=True)
    copy.write_text(''.join(f'{i:5} {line}\n' for i, line in enumerate(lines, 1)))
OUT.write_text(json.dumps(audit, indent=2) + '\n')
print(json.dumps({'shared_dataset_count': len(shared), 'shared_datasets': shared,
                  'excluded': excluded, 'source_files': len(audit['sources'])}, indent=2))
