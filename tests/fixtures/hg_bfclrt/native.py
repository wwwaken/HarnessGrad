#!/usr/bin/env python3
"""Offline ELF inspection, not dlopen/ldd/scorer execution."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect import BASE, OUT, identity, write, write_chunks

inputs, observed = {}, {}
for file in ('smoke-base.jsonl', 'smoke-tree.jsonl'):
    for line in (OUT / file).read_text().splitlines():
        r = json.loads(line)
        if r['kind'] == 'observed-mapped-file':
            p = Path(r['path'])
            inputs.setdefault(p, set()).add(file)
            observed.setdefault(file, set()).add(p)
for line in (OUT / 'native-members.jsonl').read_text().splitlines():
    r = json.loads(line)
    inputs.setdefault(Path(r['path']), set()).add('selected-distribution RECORD: ' + r['name'])
rows = []
for p, reasons in sorted(inputs.items()):
    with p.open('rb') as f:
        if f.read(4) != b'\x7fELF':
            continue
    cmd = ['readelf', '-h', '-d', '-p', '.comment', str(p)]
    env = dict(os.environ, LC_ALL='C')
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    version_cmd = ['readelf', '-V', str(p)]
    vr = subprocess.run(version_cmd, capture_output=True, text=True, env=env)
    full = Path('/mnt/20t/xubuqiang/hg-work/bfclrt/elf-version') / (identity(p)['sha256'] + '.txt')
    full.parent.mkdir(exist_ok=True)
    full.write_text(vr.stdout)
    needs = []
    taking = False
    for line in vr.stdout.splitlines():
        if line.startswith('Version needs section'):
            taking = True
        elif line.startswith('Version ') or line.startswith('No version information'):
            taking = False
        if taking:
            needs.append(line)
    needed = re.findall(r'\(NEEDED\).*Shared library: \[([^]]+)\]', result.stdout)
    soname = re.findall(r'\(SONAME\).*Library soname: \[([^]]+)\]', result.stdout)
    rows.append({**identity(p), 'reasons': sorted(reasons), 'command': cmd,
                 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
                 'command_env': {'LC_ALL': 'C'},
                 'version_command': version_cmd, 'version_exit_code': vr.returncode,
                 'version_needs_exact_excerpt': '\n'.join(needs),
                 'full_version_stdout_scratch': identity(full), 'version_stderr': vr.stderr,
                 'needed': needed, 'soname': soname,
                 'build_interpreter_version_exact': 'UNKNOWN',
                 'build_toolchain_complete': 'UNKNOWN; .comment is partial evidence only'})
write_chunks('elf', rows)
links = []
for row in rows:
    for needed in row['needed']:
        resolutions = {}
        for smoke, mapped in observed.items():
            if Path(row['path']) not in mapped:
                continue
            matches = [r['path'] for r in rows if Path(r['path']) in mapped and
                       (Path(r['path']).name == needed or needed in r['soname'])]
            resolutions[smoke] = {'matches_in_same_process': matches,
                                  'state': 'FOUND unique mapped SONAME/name candidate' if len(matches) == 1 else 'UNKNOWN'}
        links.append({'from': row['path'], 'needed': needed, 'resolutions': resolutions,
                      'state': 'FOUND DT_NEEDED edge; loader binding UNKNOWN unless separately observed',
                      'source_command': row['command']})
write('native-links.jsonl', links)
print('ELF files inspected:', len(rows))
