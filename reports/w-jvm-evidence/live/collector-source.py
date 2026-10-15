#!/usr/bin/env python3
"""Observe bounded real verify checks; no scoring monkeypatch or model invocation.

Uses host /proc and strace independently of the scorer. One fresh external work
root per invocation. Retains pre-collector-cleanup leftovers before removing only
that invocation's owned paths. This is a local control, not production admission.
"""
from __future__ import annotations

import ctypes
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import sqlite3
import subprocess
import sys
import time
import uuid

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DATA = Path('/mnt/20t/xubuqiang/datasets')
JRE = DATA / 'scienceworld/jre/jdk-17.0.20.1+1-jre'
LCB = DATA / 'livecodebench/_src/upstream/LiveCodeBench-28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24/lcb_runner/evaluation'
RUNTIMES = ('scienceworld', 'jericho', 'spreadsheetbench', 'ds1000', 'livecodebench', 'bird_minidev')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def identity(path):
    path = Path(path).resolve()
    return {'path': str(path), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def read(path):
    try:
        return Path(path).read_text()
    except OSError as exc:
        return {'error': str(exc)}


def link(path):
    try:
        return os.readlink(path)
    except OSError as exc:
        return {'error': str(exc)}


def inventory(root):
    result = []
    for path in sorted(root.rglob('*')):
        row = {'path': str(path.relative_to(root)), 'is_symlink': path.is_symlink()}
        try:
            row['kind'] = 'directory' if path.is_dir() else 'file'
            if path.is_symlink():
                row['target'] = os.readlink(path)
            elif path.is_file():
                row.update(bytes=path.stat().st_size, sha256=identity(path)['sha256'])
        except OSError as exc:
            row['error'] = str(exc)
        result.append(row)
    return result


def process_table():
    table = {}
    for item in Path('/proc').iterdir():
        if not item.name.isdigit():
            continue
        try:
            raw = (item / 'stat').read_text()
            tail = raw[raw.rindex(')') + 2:].split()
            table[int(item.name)] = {'ppid': int(tail[1]), 'state': tail[0],
                                     'start_ticks': tail[19], 'stat': raw}
        except (OSError, ValueError):
            pass
    return table


def descendants(table, root):
    found = {root}
    while True:
        more = {pid for pid, row in table.items() if row['ppid'] in found}
        if more <= found:
            return found
        found |= more


def snapshot(pid):
    base = Path('/proc') / str(pid)
    result = {'pid': pid, 'time_ns': time.time_ns(), 'exe': link(base / 'exe'),
              'cwd': link(base / 'cwd'), 'netns': link(base / 'ns/net')}
    for field in ('status', 'limits', 'cgroup', 'stat', 'maps'):
        result[field] = read(base / field)
    try:
        result['cmdline'] = (base / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
        result['affinity'] = sorted(os.sched_getaffinity(pid))
        result['children'] = read(base / f'task/{pid}/children')
        result['fds'] = {p.name: link(p) for p in (base / 'fd').iterdir()}
    except OSError as exc:
        result['racing_exit'] = str(exc)
    return result


def cgroups(raw):
    result = {}
    if not isinstance(raw, str):
        return {'error': raw}
    for line in raw.splitlines():
        hierarchy, controllers, relative = line.split(':', 2)
        if hierarchy != '0' or controllers:
            continue
        target = Path('/sys/fs/cgroup') / relative.lstrip('/')
        for parent in (target, *target.parents):
            if not parent.is_relative_to('/sys/fs/cgroup'):
                break
            names = ('cgroup.controllers', 'cgroup.type', 'cpu.max', 'cpu.stat',
                     'cpuset.cpus.effective', 'memory.max', 'memory.high', 'memory.current',
                     'memory.events', 'memory.swap.max', 'pids.max', 'pids.current', 'pids.events')
            result[str(parent)] = {name: read(parent / name) for name in names}
    return result


def prepare(name, case):
    work = case / 'work'
    work.mkdir()
    (case / 'scratch/home').mkdir(parents=True)
    (case / 'output').mkdir()
    shutil.copyfile(HERE / 'entry.py', case / 'entry.py')
    source = REPO / f'data/datasets/{name}/verify/check.py'
    check = work / 'verify/check.py'
    check.parent.mkdir()
    shutil.copyfile(source, check)
    sources = [identity(source)]
    args = ['--reward-file', '/tmp/control/output/reward.txt', '--evidence-file', '/tmp/control/output/evidence.json']
    if name in ('scienceworld', 'jericho'):
        lib = 'scw_env.py' if name == 'scienceworld' else 'jer_env.py'
        libpath = REPO / f'data/datasets/{name}/lib/{lib}'
        shutil.copyfile(libpath, work / lib)
        # These checks import their materialized library beside check.py.
        shutil.move(check, work / 'check.py')
        check = work / 'check.py'
        sources.append(identity(libpath))
        if name == 'scienceworld':
            write(work / 'scw_task.json', {'task_name': 'find-non-living-thing', 'variation': 0, 'simplifications': ''})
            (work / 'scw_actions.jsonl').write_text(json.dumps({'kind': 'action', 'step': 0, 'action': 'look around'}) + '\n')
            args += ['--workdir', '/tmp/control/work', '--budget', '2']
            for path in ('bin/java', 'lib/server/libjvm.so', 'release'):
                sources.append(identity(JRE / path))
            package = Path(importlib.util.find_spec('scienceworld').origin).parent
            sources.extend(identity(package / p) for p in ('scienceworld.py', 'scienceworld.jar'))
        else:
            rom = DATA / 'jericho/z-machine-games-master/jericho-game-suite/acorncourt.z5'
            shutil.copyfile(rom, work / 'acorncourt.z5')
            sources.append(identity(rom))
            package = Path(importlib.util.find_spec('jericho').origin).parent
            sources.extend(identity(package / p) for p in ('jericho.py', 'libfrotz.so'))
            write(work / 'jer_game.json', {'task_id': 'acorncourt', 'rom': 'acorncourt.z5', 'seed': 4})
            (work / 'jer_actions.jsonl').write_text(json.dumps({'kind': 'action', 'step': 0, 'action': 'look'}) + '\n')
            args += ['--workdir', '/tmp/control/work']
    elif name == 'spreadsheetbench':
        import openpyxl
        for filename, value in (('result.xlsx', '=1+2'), ('golden.xlsx', 3)):
            book = openpyxl.Workbook()
            book.active['A1'] = value
            book.save(work / filename)
            book.close()
        write(work / 'task.json', {'task_id': 'w-jvm-authored-formula', 'answer_position': 'Sheet!A1', 'instruction_type': 'Cell-Level'})
        (work / 'answer.txt').write_text('result.xlsx\n')
        args += ['--workdir', '/tmp/control/work']
        sources.extend(identity(p) for p in ('/usr/bin/soffice', '/usr/lib/libreoffice/program/soffice.bin', '/usr/lib/libreoffice/program/oosplash'))
    elif name == 'ds1000':
        execution = DATA / 'ds1000/_src/DS-1000-b39aab71/execution.py'
        shutil.copyfile(execution, work / 'execution.py')
        sources.append(identity(execution))
        write(work / 'context.json', {'code_context': 'def test_execution(code):\n    scope = {}\n    exec(code, scope)\n    assert scope["result"] == 3\n'})
        (work / 'solution.py').write_text('import time\ntime.sleep(0.5)\nresult = 1 + 2\n')
    elif name == 'livecodebench':
        for filename in ('testing_util.py', 'pass_k_utils.py'):
            shutil.copyfile(LCB / filename, work / filename)
            sources.append(identity(LCB / filename))
        write(work / 'tests.json', {'inputs': ['1 2\n'], 'outputs': ['3\n'], 'fn_name': None})
        (work / 'solution.py').write_text('import time\ntime.sleep(0.5)\na, b = map(int, input().split())\nprint(a + b)\n')
        args += ['--tests', 'tests.json', '--solution', 'solution.py']
    else:
        with sqlite3.connect(work / 'control.sqlite') as conn:
            conn.execute('CREATE TABLE numbers (value INTEGER)')
            conn.execute('INSERT INTO numbers VALUES (3)')
        sql = 'WITH RECURSIVE n(x) AS (VALUES(0) UNION ALL SELECT x+1 FROM n WHERE x<300000) SELECT max(x) + (SELECT value FROM numbers) FROM n;\n'
        (work / 'gold.sql').write_text(sql)
        (work / 'answer.sql').write_text(sql)
        args += ['--db', 'control.sqlite', '--gold', 'gold.sql', '--pred', 'answer.sql']
    config = {'rlimits': {'RLIMIT_CPU': 30, 'RLIMIT_AS': 8 * 1024**3,
                         'RLIMIT_NOFILE': 256, 'RLIMIT_FSIZE': 64 * 1024**2, 'RLIMIT_CORE': 0},
              'affinity': sorted(os.sched_getaffinity(0))[:2],
              'parent_netns': os.readlink('/proc/self/ns/net'),
              'check_argv': ['/tmp/control/work/' + str(check.relative_to(work)), *args]}
    write(case / 'config.json', config)
    return sources, config


def run_case(name, root, evidence):
    case = root / name
    case.mkdir()
    out = evidence / name
    out.mkdir()
    try:
        sources, config = prepare(name, case)
    except Exception as exc:
        write(out / 'prerequisite-failure.json', {'type': type(exc).__name__, 'error': str(exc)})
        return
    shutil.copytree(case / 'work', out / 'inputs')
    shutil.copyfile(case / 'config.json', out / 'config.json')
    write(out / 'sources.json', sources)
    command = ['strace', '-f', '-ttt', '-s', '240', '-o', str(out / 'syscalls.txt'),
               '-e', 'trace=%process,mkdir,mkdirat,rmdir,unlink,unlinkat,rename,renameat,renameat2,prlimit64,sched_setaffinity,socket,bind,listen,connect,shutdown',
               'bwrap', '--die-with-parent', '--unshare-net', '--ro-bind', '/', '/',
               '--bind', str(case / 'scratch'), '/tmp', '--bind', str(case), '/tmp/control',
               '--proc', '/proc', '--dev', '/dev', '--chdir', '/tmp/control/work']
    if name == 'scienceworld':
        command += ['--ro-bind', str(JRE), '/tmp/control/work/jre/' + JRE.name]
    env_values = {'HOME': '/tmp/home', 'TMPDIR': '/tmp', 'XDG_CACHE_HOME': '/tmp/home/.cache',
                  'XDG_CONFIG_HOME': '/tmp/home/.config', 'PYTHONDONTWRITEBYTECODE': '1',
                  'CUDA_VISIBLE_DEVICES': '', 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1',
                  'MKL_NUM_THREADS': '1', 'JAVA_TOOL_OPTIONS': '-Xmx512m -XX:ActiveProcessorCount=2',
                  'PYTHONPATH': '/tmp/control/work', 'HF_HUB_OFFLINE': '1', 'HF_DATASETS_OFFLINE': '1'}
    for key, value in env_values.items():
        command += ['--setenv', key, value]
    command += ['--', sys.executable, '/tmp/control/entry.py']
    write(out / 'launch.json', {'command_argv': command, 'control_env': env_values,
                              'wall_bound_seconds': 50, 'root': str(case),
                              'before': inventory(case), 'benchmark': False,
                              'model': None, 'endpoint': None, 'production_runtime_observation': False})
    known = {}
    signatures = {}
    cgroup_records = {}
    paths = set()
    started = time.monotonic()
    timed_out = False
    with (out / 'stdout.txt').open('w') as stdout, (out / 'stderr.txt').open('w') as stderr, \
            (out / 'process-samples.jsonl').open('w') as samples, (out / 'proc-snapshots.jsonl').open('w') as snapshots:
        proc = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
        while True:
            table = process_table()
            active = descendants(table, proc.pid) | {p for p, row in table.items()
                                                       if p in known and row['start_ticks'] == known[p]['start_ticks']}
            # The collector is a subreaper: retain naturally orphaned owned children.
            active |= {p for p, row in table.items() if row['ppid'] == os.getpid() and p != proc.pid}
            for pid in sorted(active):
                if pid not in table:
                    continue
                row = table[pid]
                known.setdefault(pid, {'start_ticks': row['start_ticks'], 'first_ns': time.time_ns()})
                known[pid].update(last_ns=time.time_ns(), last_state=row['state'], last_ppid=row['ppid'])
                base = Path('/proc') / str(pid)
                current = {'pid': pid, 'time_ns': time.time_ns(), 'stat': row['stat'],
                           'cmdline': read(base / 'cmdline'), 'limits': read(base / 'limits'),
                           'cwd': link(base / 'cwd')}
                # NULs in /proc/cmdline are preserved as JSON escapes.
                samples.write(json.dumps(current, sort_keys=True) + '\n')
                signature = json.dumps([current['cmdline'], current['limits'], link(base / 'exe')])
                if signature != signatures.get(pid):
                    snap = snapshot(pid)
                    snapshots.write(json.dumps(snap, sort_keys=True) + '\n')
                    signatures[pid] = signature
                    cg = snap['cgroup']
                    if isinstance(cg, str) and cg not in cgroup_records:
                        cgroup_records[cg] = cgroups(cg)
            for path in (case / 'scratch').rglob('*'):
                paths.add(str(path.relative_to(case / 'scratch')))
            returncode = proc.poll()
            if returncode is not None:
                break
            if time.monotonic() - started > 50:
                timed_out = True
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait(timeout=3)
                break
            time.sleep(0.01)
    # No cleanup signal is sent on the normal path. Observe/reap adopted children.
    reaped = []
    for pid, row in known.items():
        if pid == proc.pid:
            continue
        try:
            child, status = os.waitpid(pid, os.WNOHANG)
            if child:
                reaped.append({'pid': child, 'raw_status': status, 'returncode': os.waitstatus_to_exitcode(status),
                               'reaped_by': 'external collector subreaper, after check/strace returned'})
        except ChildProcessError:
            pass
    table = process_table()
    remaining = {pid: table[pid] for pid, row in known.items()
                 if pid in table and table[pid]['start_ticks'] == row['start_ticks']}
    write(out / 'cgroups.json', cgroup_records)
    write(out / 'process-summary.json', {'root_pid': proc.pid, 'returncode': proc.returncode,
                                       'elapsed_seconds': time.monotonic() - started, 'timed_out': timed_out,
                                       'observed_pids': known, 'collector_waitpid': reaped,
                                       'remaining_before_collector_path_cleanup': remaining})
    write(out / 'scratch-observations.json', {'host_scratch': str(case / 'scratch'),
                                            'child_scratch': '/tmp', 'sampled_paths': sorted(paths),
                                            'after_check': inventory(case / 'scratch')})
    shutil.copytree(case / 'output', out / 'output')
    shutil.copytree(case / 'work', out / 'after-work')
    if (case / 'scratch').exists():
        shutil.copytree(case / 'scratch', out / 'after-scratch', symlinks=True)
    if remaining:
        # Do not hide a leftover: retain identity and signal only this control's PIDs.
        actions = []
        for pid, row in remaining.items():
            try:
                os.kill(pid, signal.SIGKILL)
                actions.append({'pid': pid, 'signal': 'SIGKILL'})
            except ProcessLookupError:
                actions.append({'pid': pid, 'already_absent': True})
        write(out / 'collector-forced-cleanup.json', actions)
    shutil.rmtree(case)
    time.sleep(0.1)
    after = process_table()
    write(out / 'cleanup.json', {'case_root': str(case), 'case_absent': not case.exists(),
                                'scratch_absent': not (case / 'scratch').exists(),
                                'observed_pid_absence': {str(pid): pid not in after or after[pid]['start_ticks'] != row['start_ticks']
                                                         for pid, row in known.items()},
                                'scope': 'bounded identity checks, not exhaustive host or namespace proof; path removal by collector recorded separately from check cleanup'})
    trace = out / 'syscalls.txt'
    with trace.open('rb') as source, gzip.open(out / 'syscalls.txt.gz', 'wb') as target:
        shutil.copyfileobj(source, target)
    trace.unlink()


def main():
    # Adopt orphaned control children so a missed scorer wait cannot leak zombies.
    if ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0):
        raise OSError(ctypes.get_errno(), 'PR_SET_CHILD_SUBREAPER')
    evidence = REPO / 'reports/w-jvm-evidence/live'
    evidence.mkdir(exist_ok=False)
    run_id = 'w-jvm-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:8]
    root = Path('/tmp') / run_id
    root.mkdir(exist_ok=False)
    shutil.copyfile(__file__, evidence / 'collector-source.py')
    shutil.copyfile(HERE / 'entry.py', evidence / 'entry-source.py')
    write(evidence / 'execution.json', {'run_id': run_id, 'command': [sys.executable, str(Path(__file__).resolve())],
                                      'work_root': str(root), 'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
                                      'started_utc': datetime.now(timezone.utc).isoformat(),
                                      'collector_subreaper': True, 'interpreter': identity(sys.executable),
                                      'runtime_count': len(RUNTIMES), 'jobs': 1, 'benchmark': False,
                                      'model': None, 'endpoint': None, 'trials': 'one authored control per runtime',
                                      'coverage': 'local verify execution only; no benchmark sampling or published score',
                                      'packages': {p: importlib.metadata.version(p) for p in ('scienceworld', 'jericho', 'py4j', 'openpyxl', 'numpy')}})
    for name in RUNTIMES:
        print('observing ' + name, flush=True)
        run_case(name, root, evidence)
    root.rmdir()
    write(evidence / 'root-cleanup.json', {'work_root': str(root), 'absent': not root.exists()})
    print('finished ' + run_id, flush=True)


if __name__ == '__main__':
    main()
