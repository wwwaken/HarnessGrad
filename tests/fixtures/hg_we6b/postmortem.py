"""Read-only exact-object checks for all preserved attempts; never resumes a control."""
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[3]
packet_root = root / 'reports/w-e6b-evidence'
for packet in sorted(packet_root.glob('w-e6b-*')):
    names, networks, pids = set(), set(), {}
    for file in packet.glob('*.jsonl'):
        for line in file.read_text().splitlines():
            r = json.loads(line)
            argv = r.get('argv', [])
            if argv[:2] in (['docker', 'run'], ['docker', 'create']) and '--name' in argv:
                names.add(argv[argv.index('--name') + 1])
            if argv[:3] == ['docker', 'network', 'create']:
                networks.add(argv[argv.index('--internal') + 1])
            if r['kind'] == 'proc-observation':
                pids[r['identity']] = r['raw']
    print(json.dumps({'packet': packet.name, 'object_names': sorted(names), 'network_names': sorted(networks)}))
    for name in sorted(names):
        argv = ['docker', 'inspect', '--format', '{{json .Id}}', name]
        p = subprocess.run(argv, capture_output=True, text=True, timeout=15)
        print(json.dumps({'argv': argv, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}))
        assert p.returncode and 'no such object:' in p.stderr.lower()
    for name in sorted(networks):
        argv = ['docker', 'network', 'inspect', name]
        p = subprocess.run(argv, capture_output=True, text=True, timeout=15)
        print(json.dumps({'argv': argv, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}))
        assert p.returncode and 'not found' in p.stderr
    for key, d in sorted(pids.items()):
        try:
            raw = (Path('/proc') / str(d['pid']) / 'stat').read_text()
            same = raw[raw.rindex(')') + 2:].split()[19] == d['starttime']
        except OSError as exc:
            raw, same = str(exc), False
        print(json.dumps({'identity': key, 'raw_stat_or_error': raw, 'same_starttime_present': same}))
        assert not same

# Recheck the historical *actual AppWorld startup* failed precondition read-only.
# No files, recordings or old run IDs are executed, changed, copied or resumed.
old = json.loads((root / 'reports/w-e6-evidence/prerequisite-observations.json').read_text())
for entry in old:
    if entry['argv'][0] != 'stat':
        continue
    p = subprocess.run(entry['argv'], capture_output=True, text=True, timeout=15)
    print(json.dumps({'scope': 'historical actual-startup log prerequisite, read-only recheck',
                      'argv': entry['argv'], 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}))
