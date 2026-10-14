#!/usr/bin/env python3
"""Rehash unchanged adapter and checker bytes against this worktree's base."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = '9dab533'
names = ('reasoning_gym', 'bird_minidev', 'ds1000', 'spreadsheetbench', 'jericho', 'scienceworld')
paths = set()
for name in names:
    paths.add(ROOT / 'data/datasets' / (name + '.py'))
    paths.update((ROOT / 'data/datasets' / name).rglob('*.py'))
records = []
for path in sorted(paths):
    relative = str(path.relative_to(ROOT))
    body = path.read_bytes()
    assert body == subprocess.check_output(['git','show',f'{BASE}:{relative}'],cwd=ROOT), relative
    records.append({'path':relative,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
(HERE / 'local-source-pins.json').write_text(json.dumps({'baseline':BASE,'files':records},indent=2)+'\n')
print(json.dumps({'baseline':BASE,'unchanged_source_files':len(records)}))
