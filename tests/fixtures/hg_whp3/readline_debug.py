"""Host debugger attached to one authored, explicitly ptrace-enabled namespace child."""
exec((__import__('pathlib').Path(__file__).with_name('diagnose.py')).read_text().split('with tempfile.')[0])
import concurrent.futures
import os
import subprocess
import time

with tempfile.TemporaryDirectory(prefix='hg-hp3-readline-debug-') as directory:
    work = Path(directory)
    reward = work / 'verifier'
    reward.mkdir()
    with admit(NATIVE_PINS['alfworld']) as runtime, concurrent.futures.ThreadPoolExecutor() as pool:
        token = 'hg-hp3-readline-debug-child'
        code = ('import ctypes,os,pathlib,signal; libc=ctypes.CDLL(None); '
                'libc.prctl(0x59616d61,-1,0,0,0); '
                'pathlib.Path("/task/verifier/ready").write_text("ready"); '
                'os.kill(os.getpid(),signal.SIGSTOP); import readline # ' + token)
        future = pool.submit(runtime.run, ['python3', '-c', code], workdir=work,
                             reward_dir=reward, timeout_s=50)
        deadline = time.monotonic() + 30
        while not (reward / 'ready').exists() and time.monotonic() < deadline:
            time.sleep(.1)
        targets = []
        for proc in Path('/proc').iterdir():
            if not proc.name.isdigit():
                continue
            try:
                cmd = (proc / 'cmdline').read_bytes().decode(errors='replace')
                status = (proc / 'status').read_text()
                if token in cmd and 'State:\tT' in status:
                    targets.append(proc.name)
            except OSError:
                pass
        assert len(targets) == 1, targets
        argv = ['/usr/bin/gdb', '-q', '-batch', '-p', targets[0],
                '-ex', 'set pagination off', '-ex', 'handle SIGSTOP nostop noprint nopass',
                '-ex', 'signal 0', '-ex', 'bt', '-ex', 'info registers',
                '-ex', 'x/12i $pc-16', '-ex', 'info proc mappings',
                '-ex', 'signal SIGSEGV']
        debug = subprocess.run(argv, capture_output=True, text=True, timeout=20)
        print(json.dumps({'debug_argv': argv, 'debug_returncode': debug.returncode,
                          'stdout': debug.stdout, 'stderr': debug.stderr}), flush=True)
        proc = future.result()
        print(json.dumps({'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}))
