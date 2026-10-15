"""Inventory the actual encrypted release; stage only selected study evaluators/data."""
import ast
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import zipfile
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

OUT = Path('/output')
DATA = Path('/appworld/data')
SELECTED = ['82e2fac_1', '50e1ac9_1', 'cf6abd2_2']
sha = lambda b: hashlib.sha256(b).hexdigest()
def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
raw = Path('/release/data.bundle').read_bytes()
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                 salt=b'Nvx#rYcYQ2%btf', iterations=100000).derive(b'WEquKLy##9M@qu')
dec = Cipher(algorithms.AES(key), modes.CFB(raw[:16])).decryptor()
archive = zipfile.ZipFile(io.BytesIO(dec.update(raw[16:]) + dec.finalize()))
names = archive.namelist()
assert len(names) == len(set(names))
splits = {s: archive.read('data/datasets/' + s + '.txt').decode().split()
          for s in ['train', 'dev', 'test_normal', 'test_challenge']}
by_id = {tid: s for s, ids in splits.items() for tid in ids}
entries = sorted(n for n in names if n.startswith('data/tasks/')
                 and n.endswith('/ground_truth/evaluation.py'))
rows = []
for name in entries:
    tid = name.split('/')[2]
    source = archive.read(name)
    functions = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)
                 and n.name == 'evaluate']
    installed = DATA.parent / name
    row = {'task_id': tid, 'split': by_id[tid], 'member': name,
           'symbol': 'evaluate', 'lines': [n.lineno for n in functions],
           'sha256': sha(source), 'bytes': len(source),
           'image_path': str(installed), 'image_present': installed.is_file(),
           'image_sha256': sha(installed.read_bytes()) if installed.is_file() else None,
           'selected': tid in SELECTED,
           'dynamic_reachability': 'pending execution' if tid in SELECTED else
             ('not attempted; bounded study selection' if by_id[tid] in ['train', 'dev']
              else 'not attempted; held-out execution excluded')}
    assert len(functions) == 1
    rows.append(row)
# Only study-side selected gold and databases are materialized. No solutions/API oracles.
assert all(by_id[tid] in ['train', 'dev'] for tid in SELECTED)
leaves = {'metadata.json', 'public_data.json', 'private_data.json',
          'answer.json', 'test_data.json', 'evaluation.py'}
staged = []
for name in names:
    if name.endswith('/'):
        continue
    parts = name.split('/')
    use = (name == 'data/version.txt' or name.startswith('data/base_dbs/')
           or name.startswith('data/api_docs/'))
    if len(parts) > 3 and parts[:2] == ['data', 'tasks'] and parts[2] in SELECTED:
        use = (parts[3] == 'dbs' or parts[3:] == ['specs.json']
               or (parts[3] == 'ground_truth' and parts[-1] in leaves))
    if not use:
        continue
    content = archive.read(name)
    target = OUT / 'selected-root' / name
    if not name.startswith('data/base_dbs/'):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    installed = DATA.parent / name
    host = Path('/host-data') / name.removeprefix('data/')
    staged.append({'member': name, 'sha256': sha(content), 'bytes': len(content),
                   'host_path': '/mnt/20t/xubuqiang/datasets/appworld/_src/unpacked/' + name,
                   'host_sha256': sha(host.read_bytes()) if host.is_file() else None,
                   'image_present': installed.is_file(),
                   'image_sha256': sha(installed.read_bytes()) if installed.is_file() else None})
# Explicit authored state controls. Gold injection is only a scorer positive control;
# it never supplies an actor/task receipt or executes a released solution.
cases = []
for tid in SELECTED:
    answer = json.loads(archive.read(f'data/tasks/{tid}/ground_truth/answer.json'))
    for label, calls in [
        ('no-calls', []),
        ('wrong-answer', [{'method': 'post', 'url': '/supervisor/message',
                           'data': {'answer': 'HG_WAWP_WRONG_SENTINEL'}}]),
        ('gold-answer-only', [{'method': 'post', 'url': '/supervisor/message',
                              'data': {'answer': answer}}]),
    ]:
        case = {'id': tid + '--' + label, 'task_id': tid, 'source_split': by_id[tid],
                'control': label, 'calls': calls}
        cases.append(case)
        log = OUT / 'inputs' / (case['id'] + '.jsonl')
        log.parent.mkdir(exist_ok=True)
        log.write_text(''.join(json.dumps(c, sort_keys=True) + '\n' for c in calls))
save('inputs.json', {'selection': 'first released train, first released dev, prior mounted-service train task',
                     'selected_tasks': SELECTED, 'cases': cases,
                     'not_benchmark_or_actor_evidence': True})
save('inventory.json', {'bundle_path': '/mnt/20t/xubuqiang/datasets/appworld/_src/data-0.1.0.bundle',
      'bundle_sha256': sha(raw), 'bundle_bytes': len(raw), 'archive_members': len(names),
      'split_counts': {s: len(ids) for s, ids in splits.items()},
      'evaluator_count': len(rows), 'evaluate_function_count': sum(len(r['lines']) for r in rows),
      'image_evaluator_count': len(list((DATA/'tasks').glob('*/ground_truth/evaluation.py'))),
      'image_identical_evaluators': sum(r['sha256'] == r['image_sha256'] for r in rows),
      'evaluators': rows})
save('selected-byte-pins.json', {'members': staged, 'count': len(staged),
      'bytes': sum(r['bytes'] for r in staged),
      'image_identical': sum(r['sha256'] == r['image_sha256'] for r in staged)})
source_pins = []
for p in [Path('/usr/local/lib/python3.11/site-packages/appworld') / rel for rel in
          ['evaluator.py', 'ground_truth.py', 'environment.py', 'task.py']]:
    source_pins.append({'path': str(p), 'sha256': sha(p.read_bytes())})
save('runtime-source-pins.json', {'appworld_version': importlib.metadata.version('appworld'),
                                'files': source_pins})
print(json.dumps({'evaluators': len(rows), 'splits': {s: len(ids) for s, ids in splits.items()},
                  'image_identical_evaluators': sum(r['sha256'] == r['image_sha256'] for r in rows),
                  'selected_tasks': SELECTED, 'cases': len(cases),
                  'staged_members': len(staged), 'staged_bytes': sum(r['bytes'] for r in staged)}, indent=2))
