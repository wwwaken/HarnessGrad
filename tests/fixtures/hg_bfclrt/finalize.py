#!/usr/bin/env python3
"""Execute final focused checks and retain exact commands/stdout/stderr/exit codes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect import OUT, identity, write

records = []


def run(argv):
    env = dict(os.environ, TMPDIR='/mnt/20t/xubuqiang/hg-work/bfclrt/tmp', PYTHONDONTWRITEBYTECODE='1')
    r = subprocess.run(argv, capture_output=True, text=True, env=env)
    record = {'command_argv': argv, 'cwd': str(Path.cwd()),
              'environment_overrides': {k: env[k] for k in ('TMPDIR', 'PYTHONDONTWRITEBYTECODE')},
              'exit_code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}
    records.append(record)
    print(json.dumps(record, sort_keys=True), flush=True)
    return r


# Packet manifest excludes its own digest and this mutable final-check record.
manifest = []
for p in sorted(OUT.rglob('*')):
    if p.is_file() and p.name not in ('SHA256SUMS', 'final-checks.jsonl'):
        manifest.append(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + str(p.relative_to(OUT)))
(OUT / 'SHA256SUMS').write_text('\n'.join(manifest) + '\n')
run(['python3', '-B', 'tests/fixtures/hg_bfclrt/validate.py'])
run(['python3', 'tools/check_dataset_blockers.py'])
run(['git', 'diff', '--check'])
run(['git', 'diff', 'HEAD', '--', 'registry/dataset-blockers.json', 'docs/adapter-integration-journal.md', 'AGENTS.md'])
run(['git', 'branch', '--show-current'])
run(['git', 'diff', '--cached', '--name-only', '--', 'registry/dataset-blockers.json',
     'docs/adapter-integration-journal.md', 'AGENTS.md', 'tests/fixtures/hg_bfcl',
     'tests/fixtures/hg_trivia', 'tests/fixtures/hg_wprov'])
write('final-checks.jsonl', records)

text = [
    'w-bfclrt validation record', '',
    'All commands below ran in /mnt/20t/xubuqiang/hg-wt/w-bfclrt unless explicitly stated.',
    'Scratch/TMPDIR: /mnt/20t/xubuqiang/hg-work/bfclrt/tmp. No download/install/model/scorer command was run.',
    '',
    'INITIAL REQUIRED CHECK (before exact local baseline restoration):',
    '$ python3 tools/check_dataset_blockers.py',
    'exit_code=2',
    'stdout: {"valid": false, "error": "bfcl_v3: missing evidence tests/fixtures/hg_bfcl/README.md"}',
    'stderr: (empty)',
    '',
    'Baseline inspection commands and exact observed output:',
    '$ git ls-tree -r --name-only HEAD tests/fixtures/hg_bfcl',
    '(empty output; exit_code=0)',
    '$ git log --all --oneline -- tests/fixtures/hg_bfcl/README.md',
    'f8f9eb82 registry: force-add the four observation files the checker requires',
    'a3f2fe42 untrack the per-worker evidence packets: keep the digest manifests, keep the captures on disk',
    '6735a2e6 Record BFCL v1.3 archive custody and Simple code review',
    'db42c897 Record BFCL v1.3 archive custody and Simple code review',
    '',
    'The four exact local Git objects listed in baseline-restoration.jsonl were restored',
    'as ignored local files. For each, the exact read command was git show',
    'f8f9eb82220ee2fda0b689bdfc62513b08586423:<path>; stdout bytes have the recorded size/SHA-256.',
    'Those files are not part of this worker commit. Parent integration must retain that independent',
    'baseline repair; a fresh checkout of this worker branch alone still lacks those four evidence files.',
    '',
    'REPRODUCTION COMMANDS AND EXACT OBSERVED OUTPUT CARRIERS:',
    'Common environment: export TMPDIR=/mnt/20t/xubuqiang/hg-work/bfclrt/tmp; export PYTHONDONTWRITEBYTECODE=1',
    '$ python3 -u tests/fixtures/hg_bfclrt/collect.py graph',
    'source-modules.jsonl: 81 records',
    'source-edges.jsonl: 429 records',
    '$ python3 -B -u tests/fixtures/hg_bfclrt/collect.py closure',
    'observed-distribution-owners.jsonl: 52 records',
    'selected-distributions.jsonl: 84 records',
    'metadata-edges.jsonl: 1047 records',
    'The closure command was repeated after the smoke to include actually observed optional owners.',
    'Earlier exploratory traversal (not the final evidence): selected-distributions.jsonl: 61 records;',
    'metadata-edges.jsonl: 916 records. Final counts above supersede that partial traversal.',
    '',
    '$ python3 -B -u tests/fixtures/hg_bfclrt/smoke.py base > tests/fixtures/hg_bfclrt/smoke-base.jsonl',
    '$ /mnt/8t/xubuqiang/anaconda3/envs/Efficient-MAS/bin/python -B -u tests/fixtures/hg_bfclrt/smoke.py tree > tests/fixtures/hg_bfclrt/smoke-tree.jsonl',
    'Both exited 0; stderr empty. Exact stdout is retained verbatim in the named files.',
    'These are offline import smoke tests, NOT scorer execution; network/process audit events are refused.',
    'Projection preparation: each source-modules.jsonl original_path was symlinked under',
    '/mnt/20t/xubuqiang/hg-work/bfclrt/projection; observed stdout: scratch source symlinks: 81',
    '',
]
for command, output_file in (
    ('python3 -B -u tests/fixtures/hg_bfclrt/collect.py search', 'search-output.txt'),
    ('python3 -B -u -W ignore::SyntaxWarning tests/fixtures/hg_bfclrt/collect.py files', 'files-output.txt'),
    ('python3 -B -u tests/fixtures/hg_bfclrt/native.py', 'native-output.txt'),
    ('python3 -B -u tests/fixtures/hg_bfclrt/artifacts.py', 'artifacts-output.txt'),
    ('python3 -B -u tests/fixtures/hg_bfclrt/summarize.py', 'summarize-output.txt'),
):
    p = Path('/mnt/20t/xubuqiang/hg-work/bfclrt') / output_file
    text.extend(['$ ' + command, 'exit_code=0', 'exact combined stdout/stderr:', p.read_text(), ''])
text += [
    'ELF commands: every exact argv, LC_ALL=C override, return code, stdout, stderr and version-needs',
    'excerpt is in elf-*.jsonl; full readelf -V output is hashed and retained under the named scratch path.',
    'Import/metadata/native/artifact searches are scripts committed with this packet; their output identities',
    'and original file:line locations are the evidence. No bare module-name-to-distribution guess is used.',
    '',
    'FINAL FOCUSED CHECKS (exact results):',
]
for record in records:
    text += [json.dumps(record, sort_keys=True)]
text += [
    '', 'WHAT WAS NOT VERIFIED:',
    '- Official scorer execution, full-call scoring/differential, metric equivalence, production readiness.',
    '- A concrete local-model handler/model-config/response grammar, inference, GPU/server/endpoint behavior.',
    '- Complete transitive import/dynamic/optional branch graph; module-frontier and runtime-gaps enumerate UNKNOWNs.',
    '- Package contents of opaque non-ZIP pip bodies, unenumerated wheelhouses/environments/users/source archives.',
    '- Exact build Python patch/interpreter/toolchain of every compiled member; tags/ELF are partial evidence only.',
    '- Complete dlopen/relocation/loader binding closure; unique mapped SONAME candidates do not prove relocations.',
    '- Installed-member equivalence where native archive comparisons differ, including prefix rewriting and stale conda records.',
    '- Clean environment reconstruction or package installation; no installation was attempted.',
    '- Complete bundled-component license scope/redistribution compliance; missing-pin licenses remain UNKNOWN.',
    '- Independent re-verification of established BFCL public archive/tag/commit custody; retained source hashes were recomputed.',
    '- Clean-base blocker checker success without the separate f8f9eb82 four-file baseline repair.',
    '', 'FILE SIZES OF EVERY FILE TO COMMIT (bytes):',
]
paths = sorted([p for p in OUT.rglob('*') if p.is_file()] +
               [Path('registry/w-bfclrt-custody.md'), Path('registry/proposals/w-bfclrt.json')])
for p in paths:
    text.append(str(p.stat().st_size) + '  ' + str(p.relative_to(Path.cwd()) if p.is_absolute() else p))
validation = Path('registry/w-bfclrt-validation.txt')
prefix = '\n'.join(text) + '\n'
size = 0
for _ in range(10):
    body = prefix + str(size) + '  registry/w-bfclrt-validation.txt\n'
    new_size = len(body.encode())
    if new_size == size:
        break
    size = new_size
validation.write_text(body)
assert validation.stat().st_size == size
print('validation file bytes:', size)
if any(r['exit_code'] for r in records):
    raise SystemExit('a final focused check failed; inspect final-checks.jsonl')
