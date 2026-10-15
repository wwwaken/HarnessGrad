"""Bounded environment-only diagnosis, not an admission pin update."""
exec((__import__('pathlib').Path(__file__).with_name('diagnose.py')).read_text().split('with tempfile.')[0])
with tempfile.TemporaryDirectory(prefix='hg-hp3-env-diagnose-') as directory:
    work = Path(directory)
    reward = work / 'verifier'
    reward.mkdir()
    with admit(NATIVE_PINS['alfworld']) as runtime:
        original = runtime.manifest['environment'].copy()
        for extra in [{'LANG': 'C', 'LC_ALL': 'C'}]:
            runtime.manifest['environment'] = {**original, **extra}
            proc = runtime.run(['python3', '-c', 'import readline; import textworld; print("ok")'],
                               workdir=work, reward_dir=reward, timeout_s=30)
            print(json.dumps({'extra': extra, 'returncode': proc.returncode,
                              'stdout': proc.stdout, 'stderr': proc.stderr}), flush=True)
