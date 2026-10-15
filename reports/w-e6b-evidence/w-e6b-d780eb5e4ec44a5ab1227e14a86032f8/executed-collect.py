"""Serial real-platform E6 controls; compact raw text only, no transport fault mocks.

Subprocess recording preserves production argv, deadlines, return values and errors.
Create/start callbacks only observe the actual daemon state before returning it.
No subreaper, collector rlimit, gate replacement, model or acquisition is used.
"""
import datetime
import hashlib
import json
import os
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

RUN = 'w-e6b-' + uuid.uuid4().hex
OUT = ROOT / 'reports/w-e6b-evidence' / RUN
OUT.mkdir(parents=True, exist_ok=False)
for source in (Path(__file__), Path(__file__).with_name('probe.py')):
    shutil.copyfile(source, OUT / ('executed-' + source.name))
WORK = Path(tempfile.mkdtemp(prefix=RUN + '-'))
PROBE = Path(__file__).with_name('probe.py')
original_run = subprocess.run
lock = threading.RLock()
case = 'preflight'
known = {}
binds = set()
identities = {}
summary = {'run_id': RUN, 'work_root': str(WORK), 'jobs': 1,
           'model': None, 'endpoint': None, 'benchmark_scoring': False,
           'metric': 'authored process/object lifecycle; not a benchmark metric',
           'dataset_selection_trial_counts': None, 'cases': {},
           'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def emit(kind, value):
    with lock:
        with (OUT / (case + '.jsonl')).open('a') as f:
            f.write(json.dumps({'kind': kind, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), **value}, default=str) + '\n')


def proc(pid):
    base = Path('/proc') / str(pid)
    try:
        stat = (base / 'stat').read_text()
        start = stat[stat.rindex(')') + 2:].split()[19]
    except OSError as exc:
        return {'pid': pid, 'error': str(exc)}
    key = str(pid) + '-' + start
    if key not in identities:
        d = {'pid': pid, 'starttime': start, 'stat': stat}
        for name in ('limits', 'cgroup', 'cmdline'):
            try:
                d[name] = (base / name).read_bytes().decode(errors='replace')
            except OSError as exc:
                d[name] = {'error': str(exc)}
        d['cgroup_files'] = {}
        for row in str(d['cgroup']).splitlines():
            if row.startswith('0::'):
                cg = Path('/sys/fs/cgroup') / row[3:].lstrip('/')
                for ancestor in (cg, *cg.parents):
                    if ancestor.is_relative_to('/sys/fs/cgroup'):
                        for name in ('cpu.max', 'memory.max', 'pids.max'):
                            try:
                                val = (ancestor / name).read_text()
                            except OSError as exc:
                                val = {'error': str(exc)}
                            d['cgroup_files'][str(ancestor / name)] = val
        identities[key] = d
        emit('proc-observation', {'identity': key, 'raw': d})
    return key


# A projection requested from Docker itself, not a saved bulk inspect dump.
FMT = ('{"Id":{{json .Id}},"Name":{{json .Name}},"Image":{{json .Image}},'
       '"State":{{json .State}},"Mounts":{{json .Mounts}},'
       '"NanoCpus":{{json .HostConfig.NanoCpus}},"Memory":{{json .HostConfig.Memory}},'
       '"MemorySwap":{{json .HostConfig.MemorySwap}},"PidsLimit":{{json .HostConfig.PidsLimit}},'
       '"ReadonlyRootfs":{{json .HostConfig.ReadonlyRootfs}},"Tmpfs":{{json (index .HostConfig "Tmpfs")}},'
       '"Ulimits":{{json (index .HostConfig "Ulimits")}},"StorageOpt":{{json (index .HostConfig "StorageOpt")}},'
       '"NetworkMode":{{json .HostConfig.NetworkMode}}}')


def cmd(*argv, timeout=15):
    return subprocess.run(list(argv), capture_output=True, text=True, timeout=timeout)


def inspect(name):
    p = cmd('docker', 'inspect', '--format', FMT, name)
    if p.returncode:
        if 'No such object:' in p.stderr or 'No such container:' in p.stderr:
            return None
        raise RuntimeError('inspect observation failed: ' + p.stderr)
    obj = json.loads(p.stdout)
    known[obj['Id']] = obj['Name'].lstrip('/')
    for mount in obj['Mounts']:
        src = mount.get('Source', '')
        if Path(src).name.startswith(('hg-snapshot-idle-', 'hg-verdict-')):
            binds.add(src)
    if obj['State']['Pid']:
        proc(obj['State']['Pid'])
        top = cmd('docker', 'top', obj['Id'], '-eo', 'pid,ppid,args')
        for line in top.stdout.splitlines()[1:]:
            try:
                proc(int(line.split()[0]))
            except (ValueError, IndexError):
                pass
    return obj


def recorded_run(argv, **kwargs):
    record = {'argv': argv, 'kwargs': kwargs}
    try:
        if isinstance(argv, list) and argv[:3] == ['docker', 'rm', '--force']:
            for name in argv[3:]:
                inspect(name)
        result = original_run(argv, **kwargs)
    except BaseException as exc:
        record.update(exception=repr(exc), stdout=getattr(exc, 'stdout', None), stderr=getattr(exc, 'stderr', None))
        raise
    else:
        record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
        # Observe short early exits that a periodic poll could miss entirely.
        if isinstance(argv, list) and argv[:2] in (['docker', 'create'], ['docker', 'start']) and result.returncode == 0:
            name = argv[argv.index('--name') + 1] if '--name' in argv else argv[2]
            inspect(name)
        if isinstance(argv, list) and argv[:2] == ['docker', 'run'] and '--detach' in argv and result.returncode == 0:
            inspect(result.stdout.strip())
        return result
    finally:
        emit('command', record)


subprocess.run = recorded_run


def threaded_call(call, *, task=None, observation_dir=None, host=False):
    result = {}
    before = set(known)
    before_proc = set(identities)

    def invoke():
        try:
            value = call()
            result['verdict' if isinstance(value, dict) else 'return'] = value
        except BaseException as exc:
            result['exception'] = repr(exc)

    t = threading.Thread(target=invoke)
    t.start()
    until = time.monotonic() + 35
    seen = set()
    while t.is_alive() and time.monotonic() < until:
        if task:
            p = cmd('docker', 'ps', '-aq', '--no-trunc', '--filter', 'volume=' + str(task))
            for cid in p.stdout.splitlines():
                if cid not in seen:
                    obj = inspect(cid)
                    if obj and obj['State']['Running']:
                        if not any(o['Id'] == cid for o in result.setdefault('live', [])):
                            result['live'].append(obj)
                        probe_dir = observation_dir
                        if probe_dir is None:
                            probe_dir = next((Path(m['Source']) for m in obj['Mounts'] if m['Destination'] == '/verifier'), None)
                        if probe_dir and (probe_dir / 'started.json').exists():
                            result['probe_files'] = {p.name: p.read_text() for p in probe_dir.glob('*.json')}
                            # top/proc was just sampled with the now-started child.
                            seen.add(cid)
                        # Capture once again after the authored child has started.
                        if observation_dir and (observation_dir / 'started.json').exists():
                            seen.add(cid)
        if host:
            # Sample this collector's real children, no ptrace or injected envelope.
            pending = [os.getpid()]
            visited = set()
            while pending:
                pid = pending.pop()
                if pid in visited:
                    continue
                visited.add(pid)
                try:
                    for children_file in (Path('/proc') / str(pid) / 'task').glob('*/children'):
                        pending += [int(x) for x in children_file.read_text().split()]
                    if pid != os.getpid():
                        proc(pid)
                except OSError:
                    pass
        t.join(.12)
    t.join(1)
    if t.is_alive():
        raise RuntimeError('control exceeded collector observation bound')
    if observation_dir:
        result['probe_files'] = {p.name: p.read_text() for p in observation_dir.glob('*.json')}
    result['native_after_objects'] = {cid: inspect(cid) for cid in set(known) - before}
    result['observed_proc_identities'] = sorted(set(identities) - before_proc)
    result['native_after_processes'] = after_proc(result['observed_proc_identities'])
    return result


def after_proc(keys):
    after = {}
    for key in keys:
        d = identities[key]
        path = Path('/proc') / str(d['pid']) / 'stat'
        try:
            raw = path.read_text()
            same = raw[raw.rindex(')') + 2:].split()[19] == d['starttime']
        except OSError as exc:
            raw, same = str(exc), False
        after[key] = {'raw_stat_or_error': raw, 'same_starttime_present': same}
    emit('process-absence-observation', {'after': after})
    return after


def mounted(image):
    global case
    case = 'mounted-service-start'
    specs = [{'name': 'recording', 'image': image, 'record': True, 'cpus': 2, 'memory_mb': 4096,
              'entrypoint': 'python3', 'command': ['-c', 'import time; time.sleep(90)'],
              'health': {'argv': ['python3', '-c', 'pass'], 'timeout_s': 5}}]
    running = services.start(specs, recordings_root=WORK / 'recordings', run_id=RUN,
                             task_id='mounted', run_seed=RUN)
    summary['service'] = inspect(running.containers['recording'])
    summary['network'] = running.network
    try:
        for mode in ('timeout', 'missing-reward', 'malformed-reward', 'missing-evidence'):
            case = 'mounted-' + mode
            task = WORK / case
            task.mkdir()
            shutil.copyfile(PROBE, task / 'probe.py')
            spec = {'kind': 'command', 'image': image, 'argv': ['python3', 'probe.py', mode, '--recording'],
                    'scorer_bundle': {'isolation_class': 'snapshot-service'},
                    'reward_file': '/verifier/reward.txt', 'evidence_file': '/verifier/evidence.json'}
            emit('verify-input', {'spec': spec, 'task': str(task), 'timeout_s': 3 if mode == 'timeout' else 12})
            # Mounted verdict dirs are generated inside _verify. Discover only our bind.
            result = threaded_call(lambda: verifier._verify(task, spec, '', sandbox=True,
                timeout_s=3 if mode == 'timeout' else 12,
                env={'kind': 'exec', 'image': image, 'workdir': '/app'},
                service_specs=specs, running=running), task=task)
            summary['cases'][case] = result
            emit('case-result', result)
        case = 'mounted-writable-helper-timeout'
        task = WORK / case
        task.mkdir()
        shutil.copyfile(PROBE, task / 'probe.py')
        harness = WORK / 'authored-harness'
        (harness / '.state').mkdir(parents=True)
        (harness / 'agent.py').write_text('# authored, no model\n')
        result = threaded_call(lambda: container.run(
            ['python3', 'probe.py', 'timeout', '--out', '/app'], image=image,
            task_dir=task, task_mount='/app', harness_root=harness,
            state_dirs=(harness / '.state',), timeout_s=3, network=running.network),
            task=task, observation_dir=task)
        summary['cases'][case] = result
        emit('case-result', result)
    finally:
        case = 'mounted-native-cleanup'
        summary['native_service_stop_problems'] = running.stop()
        summary['service_after_native_stop'] = inspect(running.containers['recording'])
        p = cmd('docker', 'network', 'inspect', running.network)
        summary['network_after_native_stop'] = {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
        summary['recording_retained'] = [str(p) for p in running.recordings.values() if p.is_dir()]


def snapshot(image):
    global case
    # Actual content ID and require_snapshot_container remain in force; no commit is needed
    # for these authored post-create exits. This adds no actor/snapshot-creation coverage.
    p = cmd('docker', 'image', 'inspect', '--format', '{{.Id}}', image)
    actual = p.stdout.strip()
    for mode in ('missing-argv', 'staging-error'):
        case = 'snapshot-' + mode
        stage = WORK / case
        stage.mkdir()
        spec = {'kind': 'command', 'argv': [], 'reward_file': '/verifier/reward.txt',
                'scorer_bundle': {'isolation_class': 'snapshot-service'}}
        if mode == 'staging-error':
            spec['argv'] = ['python3', '/authored-does-not-exist.py']
            spec['inputs'] = [{'from': str(WORK / 'absent-input.py'), 'dst': '/authored-input.py'}]
        emit('verify-input', {'spec': spec, 'actual_image': actual, 'timeout_s': 5})
        result = threaded_call(lambda: verifier._verify_container_state(actual, spec,
            task_mount='/', staging=stage, timeout_s=5, run_id=RUN, task_id=mode,
            expected_snapshot=actual, limits=container.limits_from({'cpus': 2, 'memory_mb': 4096})))
        summary['cases'][case] = result
        emit('case-result', result)


def native():
    global case
    for mode in ('normal', 'single-timeout', 'missing-command'):
        case = 'unsandboxed-' + mode
        task = WORK / case
        task.mkdir()
        shutil.copyfile(PROBE, task / 'probe.py')
        spec = {'kind': 'command', 'argv': ['python3', 'probe.py', mode, '--out', 'verifier'],
                'reward_file': '/verifier/reward.txt'}
        if mode == 'missing-command':
            spec['argv'] = [str(WORK / 'absent-executable')]
        emit('verify-input', {'spec': spec, 'sandbox': False, 'timeout_s': 2 if mode == 'single-timeout' else 10})
        result = threaded_call(lambda: verifier._verify(task, spec, '', sandbox=False,
            timeout_s=2 if mode == 'single-timeout' else 10, env={'kind': 'files'}),
            observation_dir=task / 'verifier', host=True)
        summary['cases'][case] = result
        emit('case-result', result)


def unhealthy(image):
    global case
    case = 'service-health-failure'
    task_id = 'unhealthy'
    specs = [{'name': 'recording', 'image': image, 'record': True, 'cpus': 2, 'memory_mb': 4096,
              'entrypoint': 'python3', 'command': ['-c', 'import time; time.sleep(20)'],
              'health': {'argv': ['python3', '-c', 'import sys; sys.exit(7)'], 'timeout_s': 1}}]
    result = threaded_call(lambda: services.start(specs, recordings_root=WORK / 'unhealthy-recordings',
                          run_id=RUN, task_id=task_id, run_seed=RUN))
    # The failed helper never returns RunningServices. Names derive from its public labels.
    name = services.label(f'hg-{RUN}-{task_id}-recording')
    result['container_after_native_failure'] = inspect(name)
    p = cmd('docker', 'network', 'inspect', services.label(f'hg-{RUN}-{task_id}'))
    result['network_after_native_failure'] = {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    summary['cases'][case] = result
    emit('case-result', result)


try:
    cmd('git', 'rev-parse', 'HEAD')
    cmd('git', 'branch', '--show-current')
    cmd('git', 'worktree', 'list')
    cmd('python3', '--version')
    cmd('docker', 'version', '--format', '{{json .}}')
    sources = ['eval/containers/container.py', 'eval/containers/sandbox.py', 'eval/containers/container_state.py',
               'eval/verification/verifier.py', 'eval/verification/pristine.py', 'eval/service/services.py',
               'eval/run/runner.py', 'tests/fixtures/hg_we6b/collect.py', 'tests/fixtures/hg_we6b/probe.py']
    cmd('sha256sum', *sources)
    summary['source_hashes'] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources}
    bindings = json.loads((ROOT / 'reports/w-e6-evidence/preflight/bindings.json').read_text())
    image = bindings['appworld-verifier_image']['image']
    p = cmd('docker', 'image', 'inspect', '--format', '{{json .Id}} {{json .RepoDigests}}', image)
    if p.returncode:
        summary['failed_prerequisite'] = {'argv': p.args, 'returncode': p.returncode, 'stderr': p.stderr}
    else:
        summary['runtime_image'] = image
        mounted(image)
        snapshot(image)
        native()
        unhealthy(image)
except BaseException as exc:
    summary['collector_exception'] = repr(exc)
    raise
finally:
    case = 'final-native-observations'
    summary['before_rescue_objects'] = {cid: inspect(cid) for cid in known}
    summary['temporary_bind_sources_after'] = {p: Path(p).exists() for p in sorted(binds)}
    emit('bind-absence-observation', {'paths_exist': summary['temporary_bind_sources_after']})
    summary['final_process_observations'] = after_proc(list(identities))
    summary['rescue_containers'] = []
    for cid, obj in summary['before_rescue_objects'].items():
        if obj is not None:
            summary['rescue_containers'].append(cid)
            cmd('docker', 'rm', '--force', cid)
    # Only exact owned network names; preserve native state above before any rescue.
    if summary.get('native_service_stop_problems'):
        summary['rescue_network_problems'] = services.remove_network(summary['network'])
    summary['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save(OUT / 'summary.json', summary)
    print(json.dumps({'packet': str(OUT), 'case_results': {k: {x: v[x] for x in ('verdict', 'exception') if x in v}
                      for k, v in summary['cases'].items()},
                      'native_service_stop_problems': summary.get('native_service_stop_problems'),
                      'rescue_containers': summary['rescue_containers']}, indent=2))
