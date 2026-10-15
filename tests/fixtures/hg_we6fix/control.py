"""Bounded, offline mounted-verifier lifecycle control; no benchmark/service API.

Uses the cached AppWorld verifier runtime, an authored idle recording service and
the production service/mount/verifier helpers. Each invocation has fresh IDs.
All subprocess calls preserve argv, deadline, output and exit/timeout unchanged.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from eval.containers import container
from eval.service import services
from eval.verification import verifier

parser = argparse.ArgumentParser()
parser.add_argument('phase', choices=['before', 'after'])
args = parser.parse_args()
run_id = 'w-e6fix-' + args.phase + '-' + uuid.uuid4().hex
out = ROOT / 'reports/w-e6fix-evidence' / run_id
out.mkdir(exist_ok=False)
work = Path(tempfile.mkdtemp(prefix=run_id + '-'))
shutil.copyfile(__file__, out / 'executed-control.py')
original_run = subprocess.run
lock = threading.Lock()
seq = 0


def save(path, value):
    path.write_text(json.dumps(value, indent=2, default=str) + '\n')


def recorded_run(argv, **kwargs):
    global seq
    with lock:
        seq += 1
        stem = out / f'{seq:04d}'
    record = {'argv': argv, 'kwargs': kwargs}
    try:
        result = original_run(argv, **kwargs)
    except subprocess.TimeoutExpired as exc:
        record.update(exception=repr(exc), stdout=exc.stdout, stderr=exc.stderr)
        raise
    else:
        record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
        return result
    finally:
        save(stem.with_suffix('.json'), record)


subprocess.run = recorded_run


def cmd(*argv):
    return subprocess.run(list(argv), capture_output=True, text=True, timeout=10)


def inspect(cid):
    p = cmd('docker', 'inspect', cid)
    return None if p.returncode else json.loads(p.stdout)[0]


summary = {'run_id': run_id, 'phase': args.phase, 'work': str(work),
           'model': None, 'endpoint': None, 'benchmark_scoring': False,
           'scope': 'authored idle recording service, not AppWorld API/scorer',
           'jobs': 1, 'verifier_timeout_s': 3, 'service_self_deadline_s': 45,
           'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
summary['sources'] = {}
for source in [Path(__file__), ROOT / 'eval/containers/container.py',
               ROOT / 'eval/verification/verifier.py', ROOT / 'eval/service/services.py']:
    summary['sources'][str(source.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()
    shutil.copyfile(source, out / ('source-' + source.name))
image = json.loads((ROOT / 'reports/w-e6-evidence/preflight/bindings.json').read_text())['appworld-verifier_image']['image']
summary['image'] = image
assert cmd('docker', 'image', 'inspect', image).returncode == 0, 'cached image required'
specs = [{'name': 'recording', 'image': image, 'record': True,
          'entrypoint': 'python3', 'command': ['-c', 'import time; time.sleep(45)'],
          'health': {'argv': ['python3', '-c', 'pass'], 'timeout_s': 5},
          'cpus': 2, 'memory_mb': 4096}]
running = None
known = set()
try:
    running = services.start(specs, recordings_root=work / 'recordings',
                             run_id=run_id, task_id='authored', run_seed=run_id)
    summary['service_before'] = inspect(running.containers['recording'])
    summary['modes'] = {}
    for mode in ('normal', 'timeout'):
        task = work / mode
        task.mkdir()
        (task / 'probe.py').write_text(
            "from pathlib import Path\nimport time\n"
            "assert Path('/recordings/recording').is_dir()\n"
            + ("time.sleep(30)\n" if mode == 'timeout' else '')
            + "Path('/verifier/reward.txt').write_text('1')\n")
        spec = {'kind': 'command', 'scorer_bundle': {'isolation_class': 'snapshot-service'},
                'argv': ['python3', 'probe.py'], 'image': image,
                'reward_file': '/verifier/reward.txt'}
        result = {}

        def verify():
            try:
                result['verdict'] = verifier._verify(
                    task, spec, '', sandbox=True, timeout_s=3 if mode == 'timeout' else 10,
                    env={'kind': 'exec', 'image': image, 'workdir': '/app'},
                    service_specs=specs, running=running)
            except BaseException as exc:
                result['exception'] = repr(exc)

        thread = threading.Thread(target=verify)
        thread.start()
        deadline = time.monotonic() + 20
        while thread.is_alive() and time.monotonic() < deadline:
            p = cmd('docker', 'ps', '-aq', '--no-trunc', '--filter', 'volume=' + str(task))
            for cid in p.stdout.splitlines():
                if cid not in known:
                    known.add(cid)
                    obj = inspect(cid)
                    if obj:
                        result.setdefault('live_inspections', []).append(obj)
            thread.join(.15)
        thread.join(1)
        assert not thread.is_alive(), 'bounded verifier did not return'
        result['after_return'] = {cid: inspect(cid) for cid in known}
        summary['modes'][mode] = result
    summary['native_stop_problems'] = running.stop()
    summary['service_after_native_stop'] = inspect(running.containers['recording'])
    summary['before_rescue'] = {cid: inspect(cid) for cid in known}
    p = cmd('docker', 'network', 'inspect', running.network)
    summary['network_after_native_stop'] = {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
finally:
    # Rescue only this invocation's observed verifier objects; preserve native state first.
    for cid in known:
        obj = inspect(cid)
        if obj is not None:
            cmd('docker', 'rm', '--force', cid)
    if running:
        summary['rescue_stop_problems'] = running.stop()
        summary['final_service'] = inspect(running.containers['recording'])
        p = cmd('docker', 'network', 'inspect', running.network)
        summary['final_network'] = {'returncode': p.returncode, 'stderr': p.stderr}
    summary['final_verifiers'] = {cid: inspect(cid) for cid in known}
    summary['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    summary['retained_recording'] = str(work / 'recordings')
    save(out / 'summary.json', summary)
    print(json.dumps({'packet': str(out), 'run_id': run_id,
                      'native_stop_problems': summary.get('native_stop_problems'),
                      'verdicts': {k: v.get('verdict') for k, v in summary.get('modes', {}).items()},
                      'final_network': summary.get('final_network')}, indent=2))
