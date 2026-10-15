"""Enter the unchanged native verifier with an authored lifecycle predicate."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from eval.verification.verifier import _verify

p = argparse.ArgumentParser()
p.add_argument('--work', type=Path, required=True)
p.add_argument('--mode', choices=['normal', 'timeout'], required=True)
a = p.parse_args()
spec = {'kind': 'command',
        'argv': ['python3', 'probe.py', '--mode', a.mode, '--out', 'verifier'],
        'inputs': [{'path': 'probe.py', 'from': str(Path(__file__).with_name('probe.py'))}],
        'reward_file': '/verifier/reward.txt', 'evidence_file': '/verifier/evidence.json'}
verdict = _verify(a.work, spec, '', sandbox=True, timeout_s=15 if a.mode == 'normal' else 4,
                  env={'kind': 'files'}, task_id='authored-native-lifecycle')
print(json.dumps(verdict, indent=2))
