"""Run offline tests against the preserved pre-fix module without editing source."""
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from eval.containers import container
import pytest

source = ROOT / 'reports/w-e6fix-evidence/container-before.py'
raw = source.read_bytes()
print('Preserved baseline container.py SHA256 ' + hashlib.sha256(raw).hexdigest(), flush=True)
exec(compile(raw, str(source), 'exec'), container.__dict__)
raise SystemExit(pytest.main(sys.argv[1:]))
