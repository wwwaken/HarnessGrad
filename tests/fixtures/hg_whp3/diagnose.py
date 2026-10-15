"""Isolate the ALFWorld native import failure; authored commands only."""
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from data.runtimes import NATIVE_PINS
from eval.verification.native_runtime import admit

with tempfile.TemporaryDirectory(prefix='hg-hp3-import-diagnose-') as directory:
    work = Path(directory)
    reward = work / 'verifier'
    reward.mkdir()
    with admit(NATIVE_PINS['alfworld']) as runtime:
        for code in ['import readline; print("readline ok")',
                     'import numpy; import readline; print("numpy readline ok")',
                     'import _curses; import readline; print("curses readline ok")',
                     'import readline; import textworld; print("readline first ok")']:
            proc = runtime.run(['python3', '-c', code], workdir=work,
                               reward_dir=reward, timeout_s=30)
            print(json.dumps({'code': code, 'returncode': proc.returncode,
                              'stdout': proc.stdout, 'stderr': proc.stderr}), flush=True)
