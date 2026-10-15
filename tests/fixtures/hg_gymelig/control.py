#!/usr/bin/env python3
"""CPU-only two-point controls; never generate entries or export pool content."""
import argparse
import ast
import contextlib
import copy
import hashlib
import importlib.metadata
import inspect
import io
import json
import math
import os
from pathlib import Path
import resource
import sys

ROOT = Path(__file__).resolve().parents[3]
POOL = Path('/mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl')
PACKAGE_ROOT = Path('/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym')
EXPECTED = 'c0ff4eaef318cd59afcc61472ebe206362fc0211c4b589ed0d53946a569bd177'
SCRATCH = Path('/mnt/20t/xubuqiang/hg-work/gymelig').resolve()


def digest(path):
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if not out.is_relative_to(SCRATCH) or out.exists():
        parser.error('output must be a fresh directory under the worker scratch root')
    out.mkdir(parents=True)
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['NUMEXPR_NUM_THREADS'] = '1'
    sys.dont_write_bytecode = True
    affinity = os.sched_getaffinity(0)
    os.sched_setaffinity(0, {min(affinity)})
    resource.setrlimit(resource.RLIMIT_CPU, (300, 310))
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3))
    opened = set()
    blocked = []
    collect = True

    def audit(event, values):
        if event in {'socket.connect', 'socket.connect_ex', 'socket.getaddrinfo',
                     'socket.sendto', 'socket.sendmsg', 'subprocess.Popen',
                     'os.system', 'os.exec', 'os.posix_spawn'}:
            blocked.append(event)
            raise PermissionError('control forbids network and child processes: ' + event)
        if event == 'open' and isinstance(values[0], (str, bytes)):
            path = Path(os.fsdecode(values[0])).absolute()
            flags = values[2]
            if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                if not path.is_relative_to(SCRATCH):
                    blocked.append('write-outside-scratch')
                    raise PermissionError('control forbids writes outside worker scratch')
            if collect and path.is_relative_to(PACKAGE_ROOT):
                opened.add(path)

    def profile(frame, event, arg):
        if event == 'call' and frame.f_code.co_name == '__getitem__':
            if str(frame.f_code.co_filename).startswith(str(PACKAGE_ROOT) + '/'):
                blocked.append('entry-generation')
                raise RuntimeError('control forbids package __getitem__: no regeneration')

    sys.addaudithook(audit)
    sys.setprofile(profile)
    declaration = ROOT / 'data/datasets/reasoning_gym/prepare.py'
    tree = ast.parse(declaration.read_text())
    constants = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {'FAMILIES', 'SEED', 'PER_FAMILY', 'VERSION'}:
                    constants[target.id] = ast.literal_eval(node.value)
    version = importlib.metadata.version('reasoning-gym')
    assert version == constants['VERSION'] == '0.1.25'
    before = digest(POOL)
    assert before['sha256'] == EXPECTED
    body = POOL.read_bytes()
    rows = [json.loads(line) for line in body.splitlines()]
    families = constants['FAMILIES']
    assert len(families) == 89
    assert [(r['family'], r['index']) for r in rows] == [
        (name, index) for name in families for index in range(constants['PER_FAMILY'])]
    assert all(isinstance(r['entry']['answer'], str) and r['entry']['answer'] for r in rows)
    captured = io.StringIO()
    results = []
    source_paths = {PACKAGE_ROOT / '__init__.py', PACKAGE_ROOT / 'factory.py', PACKAGE_ROOT / 'dataset.py'}

    def identity(fn):
        path = Path(inspect.getsourcefile(fn)).resolve()
        source_paths.add(path)
        return {'qualified_name': fn.__module__ + '.' + fn.__qualname__,
                'path': str(path), 'line': inspect.getsourcelines(fn)[1]}

    def exception(exc, entry=None):
        message = str(exc)
        if entry:
            for value in sorted({entry['answer'], entry['question']}, key=len, reverse=True):
                if value:
                    message = message.replace(value, '<pool-content-redacted>')
        return {'outcome': 'exception', 'exception_type': type(exc).__module__ + '.' + type(exc).__qualname__,
                'message': message}

    def score(dataset, entry, answer):
        try:
            raw = dataset.score_answer(answer=answer, entry=copy.deepcopy(entry))
            if not isinstance(raw, (int, float)) or not math.isfinite(raw):
                return {'outcome': 'refusal', 'return_type': type(raw).__name__}
            return {'outcome': 'score', 'value': raw, 'return_type': type(raw).__name__}
        except Exception as exc:
            return exception(exc, entry)

    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
        import reasoning_gym
        from reasoning_gym.factory import DATASETS
        assert Path(reasoning_gym.__file__).resolve().parent == PACKAGE_ROOT
        for family in families:
            cls = DATASETS[family][0]
            item = {'family': family, 'dataset_class': cls.__module__ + '.' + cls.__qualname__,
                    'entry_point': identity(cls.score_answer), 'constructor': identity(cls.__init__),
                    'full_credit_target': 1.0, 'no_credit_target': 0.0,
                    'target_basis': 'data/datasets/reasoning_gym/prepare.py:13-19', 'rows': []}
            try:
                dataset = reasoning_gym.create_dataset(family, size=constants['PER_FAMILY'], seed=constants['SEED'])
                item['construction'] = {'outcome': 'success'}
            except Exception as exc:
                item['construction'] = exception(exc)
                dataset = None
            for position, row in enumerate(rows):
                if row['family'] != family:
                    continue
                if dataset is None:
                    ref = empty = {'outcome': 'unexecuted', 'reason': 'constructor exception'}
                else:
                    ref = score(dataset, row['entry'], row['entry']['answer'])
                    empty = score(dataset, row['entry'], '')
                item['rows'].append({'index': row['index'], 'pool_line': position + 1,
                                     'row_sha256': hashlib.sha256(body.splitlines()[position]).hexdigest(),
                                     'reference': ref, 'empty': empty})
            item['reference_full_credit_rows'] = sum(r['reference'].get('value') == 1.0 for r in item['rows'])
            item['empty_zero_rows'] = sum(r['empty'].get('value') == 0.0 for r in item['rows'])
            item['eligible_on_all_frozen_rows'] = (
                item['reference_full_credit_rows'] == constants['PER_FAMILY'] and
                item['empty_zero_rows'] == constants['PER_FAMILY'])
            results.append(item)
    sys.setprofile(None)
    after = digest(POOL)
    assert before == after, 'frozen pool changed'
    for module in list(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename and Path(filename).is_relative_to(PACKAGE_ROOT):
            source_paths.add(Path(filename).resolve())
    collect = False
    member_paths = sorted(opened | source_paths)
    members = [digest(p) for p in member_paths if p.is_file()]
    exceptions = sum(r[k]['outcome'] == 'exception' for f in results for r in f['rows'] for k in ('reference', 'empty'))
    refusals = sum(r[k]['outcome'] == 'refusal' for f in results for r in f['rows'] for k in ('reference', 'empty'))
    summary = {
        'families_tested': len(results), 'rows_tested': len(rows), 'score_calls': 2 * len(rows),
        'reference_full_credit': sum(f['reference_full_credit_rows'] == constants['PER_FAMILY'] for f in results),
        'empty_zero': sum(f['empty_zero_rows'] == constants['PER_FAMILY'] for f in results),
        'reference_full_credit_rows': sum(f['reference_full_credit_rows'] for f in results),
        'empty_zero_rows': sum(f['empty_zero_rows'] for f in results),
        'eligible_families': sum(f['eligible_on_all_frozen_rows'] for f in results),
        'exceptions': exceptions, 'refusals': refusals,
        'constructor_exceptions': sum(f['construction']['outcome'] == 'exception' for f in results),
        'non_eligible': [f['family'] for f in results if not f['eligible_on_all_frozen_rows']]}
    record = {'schema_version': 1, 'control_kind': 'synthetic-reference-and-empty-on-frozen-pool',
              'package_version': version, 'interpreter': digest(Path(sys.executable).resolve()),
              'interpreter_invocation': sys.executable, 'python_version': sys.version,
              'seed_for_constructor_only': constants['SEED'], 'pool_before': before, 'pool_after': after,
              'declaration': digest(declaration), 'runner': digest(Path(__file__)),
              'scope': 'all 20 preserved indices per declared family; no dataset indexing or generation',
              'resource_limits': {'cpu_seconds_soft': 300, 'cpu_seconds_hard': 310,
                                  'address_space_bytes': 4 * 1024**3, 'affinity': sorted(os.sched_getaffinity(0)),
                                  'thread_env': {k: os.environ[k] for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')}},
              'endpoint_binding': None, 'model_outputs_scored': 0, 'production_authorized': False,
              'guards': {'blocked_events': blocked, 'package_getitem_forbidden': True,
                         'network_and_child_processes_forbidden': True, 'writes_outside_scratch_forbidden': True,
                         'cuda_visible_devices': os.environ['CUDA_VISIBLE_DEVICES']},
              'captured_output': {'bytes': len(captured.getvalue().encode()),
                                  'sha256': hashlib.sha256(captured.getvalue().encode()).hexdigest()},
              'summary': summary, 'families': results}
    (out / 'verdicts.json').write_text(json.dumps(record, indent=2, allow_nan=False) + '\n')
    (out / 'package-members.json').write_text(json.dumps({
        'package_root': str(PACKAGE_ROOT),
        'scope': 'observed package file opens, loaded module sources, and inspected scorer/constructor sources; not transitive closure',
        'count': len(members), 'members': members}, indent=2) + '\n')
    print(json.dumps(summary, sort_keys=True))
    for family in results:
        if not family['eligible_on_all_frozen_rows']:
            print(json.dumps({'family': family['family'], 'entry_point': family['entry_point'],
                              'construction': family['construction'], 'failed_rows': [r for r in family['rows']
                              if r['reference'].get('value') != 1.0 or r['empty'].get('value') != 0.0]}, sort_keys=True))
    print(json.dumps({'pool_before': before, 'pool_after': after, 'package_version': version,
                      'package_members_hashed': len(members), 'blocked_events': blocked,
                      'captured_output_bytes': record['captured_output']['bytes']}, sort_keys=True))


if __name__ == '__main__':
    main()
