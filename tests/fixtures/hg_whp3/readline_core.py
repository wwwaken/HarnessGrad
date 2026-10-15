"""Retain a core only for the authored readline startup failure."""
exec((__import__('pathlib').Path(__file__).with_name('diagnose.py')).read_text().split('with tempfile.')[0])
work = Path(tempfile.mkdtemp(prefix='hg-hp3-readline-core-'))
reward = work / 'verifier'
reward.mkdir()
with admit(NATIVE_PINS['alfworld']) as runtime:
    proc = runtime.run(['python3', '-c', 'import os,resource; os.chdir("/task/verifier"); resource.setrlimit(resource.RLIMIT_CORE,(1000000000,1000000000)); import readline'],
                       workdir=work, reward_dir=reward, timeout_s=30)
    print(json.dumps({'workdir': str(work), 'returncode': proc.returncode,
                      'stdout': proc.stdout, 'stderr': proc.stderr,
                      'artifacts': [str(p) for p in reward.iterdir()]}))
