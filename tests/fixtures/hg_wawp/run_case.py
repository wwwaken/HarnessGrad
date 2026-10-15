"""Execute the released official route or the unchanged local adapter, in a fresh process."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import socket
import sys
import tempfile

OriginalSystemExit = SystemExit
F = Path('/fixture')
mode, case_id = sys.argv[1:]
case = next(c for c in json.loads((F/'inputs.json').read_text())['cases'] if c['id'] == case_id)
interfaces = Path('/proc/net/dev').read_text()
routes = Path('/proc/net/route').read_text()
assert [line.split(':')[0].strip() for line in interfaces.splitlines() if ':' in line] == ['lo']
assert len(routes.splitlines()) == 1
sock = socket.socket()
sock.settimeout(.2)
try:
    sock.connect(('198.51.100.1', 9))
except OSError as exc:
    network = {'interfaces': interfaces, 'routes': routes, 'probe_error': type(exc).__name__,
               'errno': exc.errno, 'message': str(exc), 'namespace': os.readlink('/proc/self/ns/net')}
else:
    raise RuntimeError('external connection unexpectedly succeeded')
finally:
    sock.close()
root = Path(tempfile.mkdtemp(prefix='hg-wawp-'))
shutil.copytree(F/'selected-root/data', root/'data')
(root/'data/base_dbs').symlink_to('/base-dbs')
os.environ['APPWORLD_ROOT'] = str(root)
os.environ['APPWORLD_CACHE'] = str(root/'cache')
output = root/'output'
output.mkdir()
# Hashes precede authentic execution/safety guard activity.
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
predicate = root/'data/tasks'/case['task_id']/'ground_truth/evaluation.py'
identity = {'predicate_path': str(predicate), 'predicate_sha256': sha(predicate),
            'local_check_sha256': sha('/adapter/check.py'),
            'input_sha256': sha(F/'inputs'/(case_id+'.jsonl'))}
predicate_calls = []
def profile(frame, event, arg):
    if event == 'call' and frame.f_code.co_name == 'evaluate' and frame.f_code.co_filename.endswith('/ground_truth/evaluation.py'):
        predicate_calls.append({'file': frame.f_code.co_filename, 'line': frame.f_code.co_firstlineno,
                                'symbol': frame.f_code.co_name})

sys.setprofile(profile)
code = 0
try:
    if mode == 'official':
        from appworld import AppWorld
        from appworld.evaluator import evaluate_task
        with AppWorld(task_id=case['task_id'], experiment_name='wawp',
                      raise_on_failure=False, ground_truth_mode='minimal') as world:
            responses = []
            for call in case['calls']:
                responses.append(getattr(world.requester, call['method'])(
                    call['url'], data=call.get('data') or {}, client=world.requester.client))
            tracker = evaluate_task(case['task_id'], experiment_name='wawp')
            result = {'measured': True, 'reward': float(tracker.success),
                      'tracker': tracker.to_dict(), 'responses': responses,
                      'task_completed': getattr(tracker, 'task_completed', None)}
        (output/'result.json').write_text(json.dumps(result, indent=2, default=str)+'\n')
    elif mode == 'local':
        sys.argv = ['/adapter/check.py', '--task-id', case['task_id'], '--source-split', case['source_split'],
                    '--log', str(F/'inputs'/(case_id+'.jsonl')), '--reward-file', str(output/'reward.txt'),
                    '--evidence-file', str(output/'evidence.json')]
        try:
            runpy.run_path('/adapter/check.py', run_name='__main__')
        except OriginalSystemExit as exc:
            code = exc.code
    else:
        raise ValueError(mode)
finally:
    sys.setprofile(None)
    print('HG_WAWP_RECEIPT '+json.dumps({'case': case_id, 'mode': mode, 'identity': identity,
          'network': network, 'predicate_calls': predicate_calls, 'exit_code': code}), file=sys.stderr)
    # Output artifacts are exported by the Docker parent; scratch is private tmpfs.
    for p in sorted(output.iterdir()):
        print('HG_WAWP_ARTIFACT '+json.dumps({'name': p.name, 'content': p.read_text()}))
    shutil.rmtree(root)
    print('HG_WAWP_CLEANUP '+json.dumps({'root': str(root), 'absent': not root.exists()}), file=sys.stderr)
raise OriginalSystemExit(code)
