"""One fresh existing ALFWorld noop control; unknown gates are never passed."""
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import secrets
import shlex
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from data.datasets import alfworld
from eval.policy import diagnostic_policy


def write(name, value):
    with (OUT / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture(name, argv):
    p = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=30)
    write(name, dict(argv=argv, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr))
    return p


run_id = ('w-alf-noop-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
          + '-' + secrets.token_hex(4))
run_dir = ROOT / 'runs' / run_id
work = Path('/tmp') / (run_id + '-work')
assert not run_dir.exists() and not work.exists()
write('identity.json', dict(run_id=run_id, run_dir=str(run_dir), work_root=str(work),
                           evidence_dir=str(OUT), control='alfworld-oracle 1, noop arm'))
capture('git-head.json', ['git', 'rev-parse', 'HEAD'])
capture('git-status-before.json', ['git', 'status', '--short'])
capture('active-drivers-before.json', ['ps', '-eo', 'pid,ppid,args'])
with urllib.request.urlopen('http://127.0.0.1:8002/v1/models', timeout=15) as r:
    payload = r.read()
    (OUT / 'endpoint-models.json').write_bytes(payload)
    write('endpoint-probe.json', dict(url=r.url, status=r.status))
    assert any(m['id'] == 'qwen3.5-9b-local' for m in json.loads(payload)['data'])

eligible = alfworld.SPLIT['train']
selected = diagnostic_policy.staged_task_set(eligible, 'diagnostic')
tid = selected[0]
record = next(r for r in alfworld._RECORDS if r['task_id'] == tid)
write('selection.json', dict(provision=alfworld.provision_status(), eligible_task_ids=eligible,
                            selected_task_ids=selected, environment=alfworld.ENV[tid],
                            verifier=alfworld.VERIFY[tid], official_pool='valid_unseen',
                            control_arm='noop: no .oracle/actions.json staged',
                            setup_paths=[f['path'] for f in alfworld.SETUP[tid]['files']]))
write('split.json', alfworld.SPLIT)
source_paths = [ROOT / p for p in (
    'data/datasets/alfworld.py', 'data/datasets/alfworld/verify/check.py',
    'data/datasets/alfworld/lib/gym_env.py', 'data/datasets/alfworld/cli/alf',
    'eval/run/runner.py', 'eval/verification/verifier.py', 'eval/policy/runtime_policy.py',
    'eval/containers/sandbox.py', 'driver.py')]
source_paths += [record['game_path'], record['game_path'].parent / 'traj_data.json']
write('source-hashes.json', {str(p): sha(p) for p in source_paths})
harness = alfworld.ASSETS / 'oracle_harness'
write('harness-hashes.json', {str(p): sha(p) for p in sorted(harness.iterdir()) if p.is_file()})
write('package-versions.json', {p: importlib.metadata.version(p) for p in ('alfworld', 'textworld')})
write('python-runtime.json', dict(executable=sys.executable, version=sys.version,
                                 executable_sha256=sha(Path(sys.executable).resolve())))
cg = {}
for p in ('/proc/self/limits', '/proc/self/cgroup', '/proc/self/status',
          '/sys/fs/cgroup/cpu.max', '/sys/fs/cgroup/memory.max', '/sys/fs/cgroup/pids.max'):
    try:
        cg[p] = Path(p).read_text()
    except OSError as exc:
        cg[p] = {'unavailable': str(exc)}
write('inherited-resource-observations.json', cg)
write('launch-manifest.json', dict(run_id=run_id, selected_task_ids=selected, rounds=0,
                                 trials=1, jobs=1, work_root=str(work),
                                 source_hashes_sha256=sha(OUT/'source-hashes.json'),
                                 harness_hashes_sha256=sha(OUT/'harness-hashes.json'),
                                 control_arm='noop', observer_only=True))
policy = {'context': dict(dataset='alfworld', side='train',
    metric=dict(name='ALFWorld replayed won within action budget',
                scorer_sha256=sha(alfworld.VERIFY_DIR/'check.py')),
    hashes=dict(source=sha(OUT/'source-hashes.json'), split=sha(OUT/'split.json'),
                manifest=sha(OUT/'launch-manifest.json'), model=None,
                harness=sha(OUT/'harness-hashes.json')),
    endpoint='http://127.0.0.1:8002/v1', limits=dict(resource=None, budget=None),
    gates=dict(status='unknown', receipt_sha256=None,
               detail='Shared scorer-offline-closure and artifact-only-state-export remain open; no gate attestation.'),
    comparability_notes=[
        'Existing dataset control noop arm only; no model completion or method result. Endpoint is configured for staged admission; model weights hash unknown.',
        'Platform hash train side of official valid_unseen. Completed alfworld-h0-10pct-v4 is preserved; historical comparison needs original trial/provenance receipts.',
        'Resource and budget enforcement remain unknown before execution. Passive observations are separate from admission attestations. No publication, expansion or production authorization.'])}
diagnostic_policy.validate_context(policy['context'])
write('policy-input.json', policy)
reason = ('Operator requests one fresh selected ALFWorld noop control to establish current runtime/scorer '
          'identity, effective limits and cleanup independently of the completed historical generation. '
          'Existing dataset oracle harness is used with no walkthrough staged, no method and no model '
          'completion. Enforcement and shared gates remain unknown; no comparable publication, pilot '
          'expansion or production authorization.')
driver_args = ['--harness', '../data/datasets/alfworld/oracle_harness', '--dataset', 'alfworld',
    '--sampling', 'diagnostic', '--policy-evidence', str(OUT/'policy-input.json'),
    '--authorize-unobserved-diagnostic', reason, '--rounds', '0', '--trials', '1', '--jobs', '1',
    '--side', 'train', '--improver', 'none', '--run-id', run_id, '--runs-root', str(ROOT/'runs'),
    '--work-root', str(work)]
env = dict(HG_AGENT_BACKEND='openai', HG_AGENT_MODEL='qwen3.5-9b-local',
           HG_AGENT_BASE_URL='http://127.0.0.1:8002/v1', HG_AGENT_API_KEY='local')
argv = ['python3', str(OUT/'observe_driver.py'), str(OUT), *driver_args]
write('launch-input.json', dict(cwd=str(ROOT), argv=argv, environment=env,
                              equivalent_driver_argv=['python3', 'driver.py', *driver_args]))
(OUT/'command.txt').write_text(shlex.join(['env', *[f'{k}={v}' for k,v in env.items()], *argv])+'\n')
print(json.dumps(dict(run_id=run_id, selected=selected, command_file=str(OUT/'command.txt'))), flush=True)
with (OUT/'driver.stdout.txt').open('x') as stdout, (OUT/'driver.stderr.txt').open('x') as stderr:
    result = subprocess.run(argv, cwd=ROOT, env={**os.environ, **env}, stdout=stdout, stderr=stderr)
write('launch-result.json', dict(returncode=result.returncode, run_exists=run_dir.exists(),
                                work_exists=work.exists()))
print(json.dumps(dict(returncode=result.returncode, run_dir=str(run_dir))), flush=True)
