"""Record one real command; refuse to overwrite any prior receipt."""
import datetime
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent


def record(name, argv, *, timeout=300, check=True):
    paths = [ROOT / (name + suffix) for suffix in
             ('.stdout.txt', '.stderr.txt', '.command.json')]
    assert not any(p.exists() for p in paths), name
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(argv, capture_output=True, timeout=timeout)
    paths[0].write_bytes(result.stdout)
    paths[1].write_bytes(result.stderr)
    paths[2].write_text(json.dumps({
        'argv': argv, 'cwd': str(Path.cwd()), 'started_at_utc': started,
        'finished_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'returncode': result.returncode,
    }, indent=2) + '\n')
    print(name, 'exit', result.returncode, flush=True)
    if check:
        result.check_returncode()
    return result
