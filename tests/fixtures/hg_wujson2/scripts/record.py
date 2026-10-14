"""Record an executed argv and unmodified stdout/stderr in this evidence packet."""
import datetime
import json
from pathlib import Path
import subprocess
import sys

packet = Path(__file__).resolve().parents[1]
label, *argv = sys.argv[1:]
prefix = packet / 'commands' / label
assert not prefix.with_suffix('.command.json').exists(), label
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
with prefix.with_suffix('.stdout.txt').open('wb') as out, prefix.with_suffix('.stderr.txt').open('wb') as err:
    p = subprocess.run(argv, stdout=out, stderr=err)
prefix.with_suffix('.command.json').write_text(json.dumps({
    'argv': argv, 'cwd': str(Path.cwd()), 'started_utc': started,
    'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'returncode': p.returncode,
}, indent=2) + '\n')
print(f'{label}: exit={p.returncode}')
raise SystemExit(p.returncode)
