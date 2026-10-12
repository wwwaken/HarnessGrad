#!/usr/bin/env python3
"""Periodic, read-only H0 monitor. It never starts, stops, or retries a run."""
from __future__ import annotations
import json, os, time
from collections import Counter
from pathlib import Path

RUNS = [
    Path('/mnt/20t/xubuqiang/Study/gaia-h0-launch-v3/runs/gaia-validation-pilot-h0-20261117-v3'),
    Path('/mnt/20t/xubuqiang/Study/gaia-h0-launch-v2/runs/gaia-validation-pilot-h0-20261117-v2'),
]
OUT = Path('/tmp/harnessgrad-monitor')
OUT.mkdir(parents=True, exist_ok=True)

def summarize(root: Path) -> dict:
    path = root / 'events.jsonl'
    if not path.is_file():
        return {'run': root.name, 'status': 'not_started'}
    try:
        events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    except Exception as exc:
        return {'run': root.name, 'status': 'read_error', 'error': type(exc).__name__}
    tasks = [e for e in events if e.get('kind') == 'task']
    done = [e for e in tasks if e.get('status') == 'done']
    failed = [e for e in tasks if e.get('status') == 'failed']
    started = [e for e in tasks if e.get('status') == 'start']
    notes = [e for e in events if e.get('kind') == 'note' and e.get('level') == 'error']
    return {
        'run': root.name,
        'status': 'observed',
        'updated_at': path.stat().st_mtime,
        'events': len(events),
        'task_started': len(started),
        'task_done': len(done),
        'task_failed': len(failed),
        'last_task': tasks[-1] if tasks else None,
        'error_notes': notes[-5:],
        'curve_present': (root / 'curve.jsonl').is_file(),
    }

stamp = {'timestamp': time.time(), 'runs': [summarize(root) for root in RUNS]}
target = OUT / 'h0-status.json'
tmp = target.with_suffix('.tmp')
tmp.write_text(json.dumps(stamp, ensure_ascii=True, sort_keys=True, indent=2) + '\n')
tmp.replace(target)
# Append a compact line for humans; no notifications and no side effects on runs.
with (OUT / 'h0-status.log').open('a') as log:
    log.write(json.dumps(stamp, ensure_ascii=True, separators=(',', ':')) + '\n')
