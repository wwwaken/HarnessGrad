"""Bounded local production-verifier lifecycle controls; never a benchmark run.

Only the Docker transport is wrapped to retain commands/results, unmodified.
Independent daemon/proc observations include cleanup BEFORE any collector rescue.
No admission, limits, scorer classification or verifier code is replaced.
"""
import argparse
import ast
from contextlib import contextmanager
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

PACKET = ROOT / 'reports/w-e6-evidence'
RUN = 'w-e6-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
OUT = PACKET / RUN
OUT.mkdir(exist_ok=False)
WORK = Path(tempfile.mkdtemp(prefix=RUN + '-'))
seq = 0
lock = threading.Lock()
known = {}
proc_ids = {}
temporary_binds = set()
image_ids = []
network_names = []
summary = {'run_id': RUN, 'work_root': str(WORK), 'source_scope': 'authored lifecycle controls, not dataset scoring',
           'benchmark_scoring': False, 'model': None, 'endpoint': None, 'jobs': 1,
           'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'routes': {}}
parser = argparse.ArgumentParser()
parser.add_argument('--routes', nargs='+', choices=['appworld', 'gaia', 'tau_bench'], default=['appworld', 'gaia', 'tau_bench'])
args = parser.parse_args()
summary['invocation'] = [sys.executable, *sys.argv]
summary['executed_sources'] = {}
for source in (Path(__file__), Path(__file__).with_name('probe.py')):
    shutil.copyfile(source, OUT / ('executed-' + source.name))
    summary['executed_sources'][str(source.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()

def audit(event, argv):
    if event == 'subprocess.Popen':
        with lock:
            with (OUT / 'subprocess-argv.jsonl').open('a') as f:
                f.write(json.dumps({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                    'executable': argv[0], 'argv': argv[1], 'cwd': argv[2]}) + '\n')
sys.addaudithook(audit)

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')

def command(label, argv, timeout=30):
    global seq
    with lock:
        seq += 1
        stem = OUT / 'commands' / f'{seq:04d}-{label}'
        stem.parent.mkdir(exist_ok=True)
    info = {'argv': list(map(str, argv)), 'cwd': str(ROOT), 'timeout_s': timeout,
            'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        p = subprocess.run(info['argv'], capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        info['exception'] = repr(exc)
        stem.with_suffix('.stdout.txt').write_bytes(exc.stdout or b'')
        stem.with_suffix('.stderr.txt').write_bytes(exc.stderr or b'')
        save(stem.with_suffix('.json'), info)
        raise
    info['returncode'] = p.returncode
    stem.with_suffix('.stdout.txt').write_bytes(p.stdout)
    stem.with_suffix('.stderr.txt').write_bytes(p.stderr)
    save(stem.with_suffix('.json'), info)
    return subprocess.CompletedProcess(info['argv'], p.returncode, p.stdout.decode(errors='replace'), p.stderr.decode(errors='replace'))

def transport(*args, timeout=120):
    # Same subprocess.run semantics as the production docker helper in non-stream mode.
    return command('platform-' + args[0], ['docker', *args], timeout)

from eval.observe import progress
assert progress.task_of() is None, 'do not replace streaming transport'
container.docker = transport

def proc(pid):
    path = Path('/proc') / str(pid)
    try:
        stat = (path / 'stat').read_text()
        identity = stat[stat.rindex(')') + 2:].split()[19]
        key = str(pid) + '-' + identity
        if key in proc_ids:
            return
        d = {'pid': pid, 'starttime': identity, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        for name in ('stat', 'status', 'limits', 'cgroup', 'mountinfo', 'cmdline'):
            try:
                d[name] = (path / name).read_bytes().decode(errors='replace')
            except OSError as exc:
                d[name] = {'error': str(exc)}
        d['affinity'] = sorted(os.sched_getaffinity(pid))
        d['cgroup_files'] = {}
        for row in str(d['cgroup']).splitlines():
            if row.startswith('0::'):
                cpath = Path('/sys/fs/cgroup') / row[3:].lstrip('/')
                for name in ('cpu.max', 'memory.max', 'memory.swap.max', 'pids.max', 'memory.current', 'pids.current', 'cgroup.events'):
                    try:
                        d['cgroup_files'][str(cpath / name)] = (cpath / name).read_text()
                    except OSError as exc:
                        d['cgroup_files'][str(cpath / name)] = {'error': str(exc)}
        proc_ids[key] = d
        save(OUT / 'proc' / (key + '.json'), d)
    except (OSError, ValueError, ProcessLookupError):
        pass  # races are not absence observations

def inspect_object(cid, phase):
    p = command(phase + '-inspect', ['docker', 'inspect', cid])
    if p.returncode:
        return None
    obj = json.loads(p.stdout)[0]
    ident = obj['Id']
    if ident not in known:
        known[ident] = {'name': obj['Name'], 'first_phase': phase, 'pid': obj['State']['Pid']}
    for mount in obj.get('Mounts', []):
        source = mount.get('Source', '')
        if Path(source).name.startswith(('hg-verdict-', 'hg-snapshot-idle-')):
            temporary_binds.add(source)
    pid = obj['State']['Pid']
    if pid:
        proc(pid)
        top = command(phase + '-top', ['docker', 'top', ident, '-eo', 'pid,ppid,args'])
        if not top.returncode:
            for row in top.stdout.splitlines()[1:]:
                try:
                    proc(int(row.split()[0]))
                except (ValueError, IndexError):
                    pass
    return obj

halt = threading.Event()
def observe():
    seen_signatures = set()
    while not halt.is_set():
        # Unlabelled mount-route verifier: identify by its exclusive task bind root.
        p = subprocess.run(['docker', 'ps', '-aq', '--no-trunc'], capture_output=True, text=True, timeout=10)
        for cid in p.stdout.splitlines():
            q = subprocess.run(['docker', 'inspect', cid], capture_output=True, text=True, timeout=10)
            if q.returncode:
                continue
            obj = json.loads(q.stdout)[0]
            belongs = obj.get('Config', {}).get('Labels', {}).get('harnessgrad.run') == RUN
            belongs |= any(str(m.get('Source', '')).startswith(str(WORK) + '/') for m in obj.get('Mounts', []))
            if not belongs:
                continue
            signature = (cid, obj['State']['Status'])
            # Periodic top/proc samples catch checker children even after initial start.
            with (OUT / 'samples.jsonl').open('a') as f:
                f.write(json.dumps({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'inspect': obj}) + '\n')
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                inspect_object(cid, 'observer')
            if obj['State']['Running']:
                for mount in obj.get('Mounts', []):
                    source = Path(mount.get('Source', '/missing'))
                    if source.name.startswith('hg-verdict-'):
                        temporary_binds.add(str(source))
                        for file in source.glob('*.json'):
                            try:
                                data = file.read_bytes()
                                # Retain each byte variant; never replace a prior observation.
                                dest = OUT / 'captured-verdict' / cid / (file.name + '-' + hashlib.sha256(data).hexdigest())
                                dest.parent.mkdir(parents=True, exist_ok=True)
                                if not dest.exists():
                                    dest.write_bytes(data)
                            except OSError:
                                pass
                top = subprocess.run(['docker', 'top', cid, '-eo', 'pid,ppid,args'], capture_output=True, text=True, timeout=10)
                with (OUT / 'top.jsonl').open('a') as f:
                    f.write(json.dumps({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'container': cid, 'argv': top.args, 'returncode': top.returncode, 'stdout': top.stdout, 'stderr': top.stderr}) + '\n')
                for row in top.stdout.splitlines()[1:]:
                    try:
                        proc(int(row.split()[0]))
                    except (ValueError, IndexError):
                        pass
        halt.wait(0.15)

def snapshot_control(dataset, base):
    result = {'image': base, 'modes': {}}
    summary['routes'][dataset] = result
    network = services.create_network(RUN, dataset)
    network_names.append(network)
    actor = services.label('hg-' + RUN + '-' + dataset + '-seed')
    try:
        # Production snapshot helpers, on authored state only, not a dataset task.
        with container.snapshot_startup() as (entry, mounts):
            container.create(actor, image=base, limits=container.limits_from({'cpus': 2, 'memory_mb': 4096}),
                             network=network, extra_mounts=mounts, startup_entrypoint=entry,
                             run_id=RUN, task_id=dataset)
            container.start(actor)
            inspect_object(actor, dataset + '-seed-started')
            state = WORK / (dataset + '-state.txt')
            state.write_text('authored lifecycle state\n')
            container.cp_in(actor, state, '/we6-state.txt')
            container.stop(actor)
            inspect_object(actor, dataset + '-seed-stopped')
            image = container.commit(actor, 'harnessgrad-we6:' + RUN + '-' + dataset)
            image_ids.append(image)
            result['snapshot'] = image
        container.remove_container(actor)
        for mode in ('normal', 'timeout'):
            stage = WORK / (dataset + '-' + mode)
            stage.mkdir()
            spec = {'kind': 'command', 'scorer_bundle': {'isolation_class': 'snapshot-service'},
                    'argv': ['python3', '/we6-probe.py', '--mode', mode, '--state', '/we6-state.txt'],
                    'inputs': [{'dst': '/we6-probe.py', 'from': str(Path(__file__).with_name('probe.py'))}],
                    'reward_file': '/verifier/reward.txt', 'evidence_file': '/verifier/evidence.json'}
            save(OUT / dataset / mode / 'input.json', {'spec': spec, 'staging': str(stage), 'network': network,
                  'declared_network': 'none', 'timeout_s': 15 if mode == 'normal' else 4,
                  'dataset_network_not_reproduced': dataset == 'gaia'})
            verdict = verifier._verify_container_state(image, spec, task_mount='/', staging=stage,
                        timeout_s=15 if mode == 'normal' else 4, run_id=RUN,
                        task_id=dataset + '-' + mode, network=network, declared_network='none',
                        limits=container.limits_from({'cpus': 2, 'memory_mb': 4096}), expected_snapshot=image)
            result['modes'][mode] = verdict
            save(OUT / dataset / mode / 'verdict.json', verdict)
            if stage.exists():
                shutil.copytree(stage, OUT / dataset / mode / 'staging-copy')
            inspect_object(services.label('hg-verify-' + RUN + '-' + dataset + '-' + mode), dataset + '-' + mode + '-after-native')
    except Exception as exc:
        result['failed_prerequisite_or_exception'] = repr(exc)
    finally:
        container.remove_container(actor)
        result['network_cleanup'] = services.remove_network(network)

def appworld_control():
    # Read the literal declaration without loading the dataset pool/factory.
    tree = ast.parse((ROOT / 'data/datasets/appworld.py').read_text())
    expr = next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'DEFAULT_ENV' for t in n.targets))
    bindings = json.loads((PACKET / 'preflight/bindings.json').read_text())
    symbols = {'IMAGE': bindings['appworld-image']['image'], 'SERVICE_IMAGE': bindings['appworld-service_image']['image'], 'WORKDIR': '/app'}
    def literal(node):
        if isinstance(node, ast.Name):
            return symbols[node.id]
        if isinstance(node, ast.Dict):
            return {literal(k): literal(v) for k, v in zip(node.keys, node.values)}
        if isinstance(node, ast.List):
            return [literal(x) for x in node.elts]
        return ast.literal_eval(node)
    env = literal(expr)
    result = {'environment': env, 'selected_service_task': 'cf6abd2_2', 'modes': {},
              'recording_scope': 'service startup only; no initialize/execute/evaluate request'}
    summary['routes']['appworld'] = result
    running = None
    try:
        running = services.start(env['services'], recordings_root=WORK / 'recordings', run_id=RUN, task_id='cf6abd2_2', run_seed=RUN)
        network_names.append(running.network)
        result['recordings'] = {k: str(v) for k, v in running.recordings.items()}
        inspect_object(running.containers['appworld'], 'appworld-live-capped-service')
        for mode in ('normal', 'timeout'):
            work = WORK / ('appworld-' + mode)
            work.mkdir()
            spec = {'kind': 'command', 'scorer_bundle': {'isolation_class': 'snapshot-service'},
                    'argv': ['python3', 'probe.py', '--mode', mode, '--record', '/recordings/appworld'],
                    'inputs': [{'path': 'probe.py', 'from': str(Path(__file__).with_name('probe.py'))}],
                    'image': bindings['appworld-verifier_image']['image'],
                    'reward_file': '/verifier/reward.txt', 'evidence_file': '/verifier/evidence.json'}
            save(OUT / 'appworld' / mode / 'input.json', {'spec': spec, 'work': str(work), 'env': env, 'timeout_s': 15 if mode == 'normal' else 4})
            verdict = verifier._verify(work, spec, '', sandbox=True, timeout_s=15 if mode == 'normal' else 4,
                        env=env, service_specs=env['services'], running=running, task_id='cf6abd2_2', run_id=RUN)
            result['modes'][mode] = verdict
            save(OUT / 'appworld' / mode / 'verdict.json', verdict)
            # Observe before service teardown or any collector rescue.
            time.sleep(0.4)
            for cid in list(known):
                inspect_object(cid, 'appworld-' + mode + '-after-native')
            shutil.copytree(work, OUT / 'appworld' / mode / 'work-copy')
    except Exception as exc:
        result['failed_prerequisite_or_exception'] = repr(exc)
    finally:
        if running:
            result['native_stop_problems'] = running.stop()
            for cid in list(known):
                inspect_object(cid, 'after-service-stop-before-rescue')
        record = WORK / 'recordings'
        if record.exists():
            shutil.copytree(record, OUT / 'appworld/recordings-retained')

observer = threading.Thread(target=observe, daemon=True)
observer.start()
try:
    command('git-head', ['git', 'rev-parse', 'HEAD'])
    if 'appworld' in args.routes:
        appworld_control()
    bindings = json.loads((PACKET / 'preflight/bindings.json').read_text())
    for dataset in ('gaia', 'tau_bench'):
        if dataset not in args.routes:
            continue
        # Fail closed on absent local images. Never allow Docker to pull.
        image = bindings[dataset + '-image']['image']
        if command(dataset + '-cached-image', ['docker', 'image', 'inspect', image]).returncode:
            summary['routes'][dataset] = {'failed_prerequisite': 'exact pinned image absent locally'}
        else:
            snapshot_control(dataset, image)
finally:
    halt.set()
    observer.join(timeout=15)
    # Archive observation files from live timeout containers before force removal.
    before = {}
    for cid in known:
        obj = inspect_object(cid, 'final-before-collector-rescue')
        before[cid] = None if obj is None else obj['State']
        if obj and obj['State']['Running']:
            command('rescue-copy-observation', ['docker', 'cp', cid + ':/verifier/.', str(OUT / ('rescued-' + cid[:12]))])
            command('collector-remove-leaked-container', ['docker', 'rm', '--force', cid])
        inspect_object(cid, 'final-after-rescue')
    summary['before_collector_rescue'] = before
    for image in image_ids:
        container.remove_image(image)
        command('snapshot-absent-after', ['docker', 'image', 'inspect', image])
    for network in network_names:
        command('network-before-rescue', ['docker', 'network', 'inspect', network])
        services.remove_network(network)
        command('network-absent-after', ['docker', 'network', 'inspect', network])
    end = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for cid in known:
        command('events-' + cid[:12], ['docker', 'events', '--since', summary['started_utc'], '--until', end, '--filter', 'container=' + cid, '--format', '{{json .}}'])
    summary['known_containers'] = known
    summary['temporary_binds_after_native'] = {p: {'exists': Path(p).exists(), 'is_mountpoint': os.path.ismount(p)} for p in sorted(temporary_binds)}
    summary['processes_after_cleanup'] = {}
    for key, d in list(proc_ids.items()):
        pid = d['pid']
        try:
            stat = (Path('/proc') / str(pid) / 'stat').read_text()
            current = stat[stat.rindex(')') + 2:].split()[19]
        except OSError:
            current = None
        summary['processes_after_cleanup'][key] = {'pid_path_exists': Path('/proc', str(pid)).exists(), 'same_starttime_present': current == d['starttime']}
    summary['work_retained_as_evidence'] = str(WORK)
    summary['ended_utc'] = end
    save(OUT / 'summary.json', summary)
    print(json.dumps({'packet': str(OUT), 'routes': summary['routes'], 'before_collector_rescue': before}, indent=2))
