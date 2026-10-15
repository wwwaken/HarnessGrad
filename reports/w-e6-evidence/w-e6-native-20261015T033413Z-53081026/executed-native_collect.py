"""Observe real native verifier children and waits without supplying an envelope."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[3]
run = 'w-e6-native-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
out = ROOT / 'reports/w-e6-evidence' / run
out.mkdir()
work = Path(tempfile.mkdtemp(prefix=run + '-'))
summary = {'run_id': run, 'work_root': str(work), 'envelope': 'unchanged platform sandbox; no collector rlimits/subreaper', 'modes': {}}
for name in ('native_collect.py', 'native_entry.py', 'probe.py'):
    shutil.copyfile(Path(__file__).with_name(name), out / ('executed-' + name))
if not shutil.which('strace'):
    (out / 'failed-prerequisite.json').write_text(json.dumps({'failed_prerequisite': 'shutil.which(strace) returned None'}))
    raise SystemExit('strace absent')
for mode in ('normal', 'timeout'):
    dest = out / mode
    dest.mkdir()
    task = work / mode
    task.mkdir()
    argv = ['strace', '-f', '-e', 'trace=process', '-o', str(dest / 'syscalls.txt'), sys.executable,
            str(Path(__file__).with_name('native_entry.py')), '--work', str(task), '--mode', mode]
    launch = {'argv': argv, 'cwd': str(ROOT), 'outer_timeout_s': 25, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (dest / 'launch.json').write_text(json.dumps(launch, indent=2) + '\n')
    identities = {}
    with (dest / 'stdout.txt').open('wb') as stdout, (dest / 'stderr.txt').open('wb') as stderr:
        process = subprocess.Popen(argv, stdout=stdout, stderr=stderr, cwd=ROOT)
        deadline = time.monotonic() + 25
        while process.poll() is None:
            if time.monotonic() > deadline:
                process.kill()
                raise RuntimeError('outer native collection timeout; retain evidence')
            pending = [process.pid]
            seen = set()
            while pending:
                pid = pending.pop()
                if pid in seen:
                    continue
                seen.add(pid)
                base = Path('/proc') / str(pid)
                try:
                    pending.extend(int(x) for x in (base / 'task' / str(pid) / 'children').read_text().split())
                    stat = (base / 'stat').read_text()
                    starttime = stat[stat.rindex(')') + 2:].split()[19]
                    key = str(pid) + '-' + starttime
                    if key in identities:
                        continue
                    d = {'pid': pid, 'starttime': starttime, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
                    for name in ('stat', 'status', 'limits', 'mountinfo', 'cgroup', 'cmdline'):
                        d[name] = (base / name).read_bytes().decode(errors='replace')
                    d['affinity'] = sorted(__import__('os').sched_getaffinity(pid))
                    d['cgroup_files'] = {}
                    for row in d['cgroup'].splitlines():
                        if row.startswith('0::'):
                            cpath = Path('/sys/fs/cgroup') / row[3:].lstrip('/')
                            # Include each ancestor: these are shared envelopes, not private caps.
                            for ancestor in (cpath, *cpath.parents):
                                if not ancestor.is_relative_to('/sys/fs/cgroup'):
                                    continue
                                for name in ('cpu.max', 'memory.max', 'pids.max'):
                                    try:
                                        d['cgroup_files'][str(ancestor / name)] = (ancestor / name).read_text()
                                    except OSError as exc:
                                        d['cgroup_files'][str(ancestor / name)] = {'error': str(exc)}
                    identities[key] = d
                    procdir = dest / 'proc'
                    procdir.mkdir(exist_ok=True)
                    (procdir / (key + '.json')).write_text(json.dumps(d, indent=2) + '\n')
                except (OSError, ValueError):
                    pass
            time.sleep(0.02)
        code = process.wait()
    shutil.copytree(task, dest / 'work-copy')
    after = {}
    for key, d in identities.items():
        base = Path('/proc') / str(d['pid'])
        try:
            stat = (base / 'stat').read_text()
            current = stat[stat.rindex(')') + 2:].split()[19]
        except OSError:
            current = None
        after[key] = {'proc_path_exists': base.exists(), 'same_starttime_present': current == d['starttime']}
    try:
        verdict = json.loads((dest / 'stdout.txt').read_text())
    except ValueError:
        verdict = None
    result = {'returncode': code, 'verdict': verdict, 'process_identities_after_native': after}
    (dest / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    summary['modes'][mode] = result
summary['work_retained_as_evidence'] = str(work)
(out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({'packet': str(out), 'summary': summary}, indent=2))
