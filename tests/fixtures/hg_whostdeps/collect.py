"""Read-only host native inventory; imports only, never datasets/tasks/scorers.

Run under unshare -Urn. All commands, failures, source preimages and provider
digests are retained. Static installed files are a conservative superset, not
an assertion that every file participates in a selected task.
"""
from __future__ import annotations

import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.metadata as md
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import time

from packaging.requirements import Requirement

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SITE = Path(sysconfig.get_path('purelib'))
DATASETS = ['alfworld', 'jericho', 'scienceworld', 'bird_minidev', 'ds1000',
            'spreadsheetbench', 'chessbench_puzzles']
PROFILES = {
    'alfworld': ['alfworld', 'textworld', 'jericho', 'fast-downward'],
    'jericho': ['jericho'],
    'scienceworld': ['scienceworld', 'py4j'],
    'bird_minidev': [],
    'ds1000': ['numpy', 'pandas', 'scipy', 'scikit-learn', 'matplotlib',
               'seaborn', 'torch', 'pillow', 'pyyaml', 'statsmodels', 'sympy',
               'gensim', 'tensorflow', 'xgboost'],
    'spreadsheetbench': ['openpyxl', 'et-xmlfile', 'lxml', 'pillow', 'numpy', 'defusedxml'],
    'chessbench_puzzles': ['chess', 'python-chess'],
}
IMPORTS = {
    'alfworld': ['alfworld.agents.environment.alfred_tw_env', 'textworld.gym'],
    'jericho': ['jericho'],
    'scienceworld': ['scienceworld'],
    'bird_minidev': ['sqlite3', 'multiprocessing'],
    'ds1000': ['numpy', 'pandas', 'scipy', 'sklearn', 'matplotlib', 'seaborn',
               'PIL', 'yaml', 'gensim'],
    'spreadsheetbench': ['openpyxl'],
    'chessbench_puzzles': ['chess'],
}


def save(name, value):
    dest = OUT / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def command(label, argv, timeout=60, env=None):
    start = time.time()
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=timeout, env=env)
        stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
        error = None
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code = exc.stdout or b'', exc.stderr or b'', None
        error = 'TimeoutExpired'
    except OSError as exc:
        stdout, stderr, code, error = b'', b'', None, repr(exc)
    (OUT / (label + '.stdout.txt')).parent.mkdir(parents=True, exist_ok=True)
    (OUT / (label + '.stdout.txt')).write_bytes(stdout)
    (OUT / (label + '.stderr.txt')).write_bytes(stderr)
    rec = {'argv': argv, 'returncode': code, 'error': error,
           'start_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(start)),
           'elapsed_s': time.time() - start,
           'stdout': label + '.stdout.txt', 'stderr': label + '.stderr.txt'}
    save(label + '.command.json', rec)
    return rec, stdout.decode(errors='replace')


def source(path, key):
    if not path.is_file():
        return {'path': str(path), 'exists': False}
    raw = path.read_bytes()
    dest = OUT / 'source' / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    return {'path': str(path), 'fixture': str(dest.relative_to(ROOT)),
            'sha256': hashlib.sha256(raw).hexdigest(), 'exists': True}


save('host.json', {'executable': sys.executable, 'real_executable': str(Path(sys.executable).resolve()),
     'version': sys.version, 'SOABI': sysconfig.get_config_var('SOABI'),
     'libc': platform.libc_ver(), 'uname': list(platform.uname()), 'site': str(SITE),
     'PATH': os.environ.get('PATH'), 'LANG': os.environ.get('LANG'),
     'loader_environment_presence': {k: k in os.environ for k in
          ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'PYTHONPATH', 'PYTHONHOME', 'JAVA_HOME', 'HG_SCIENCEWORLD_JAVA']},
     'net_devices': Path('/proc/net/dev').read_text(), 'net_routes': Path('/proc/net/route').read_text(),
     'scope': 'unshare -Urn namespace, no scorer/task/model/GPU invocation'})
command('host-libc-version', ['ldd', '--version'])

# Fresh exact source preimages, not earlier report assertions.
repo_paths = [ROOT / 'data/datasets' / (name + '.py') for name in DATASETS]
for name in DATASETS:
    folder = ROOT / 'data/datasets' / name
    repo_paths += list((folder / 'verify').rglob('*.py')) + list((folder / 'lib').rglob('*.py'))
repo_paths += [ROOT / p for p in ['eval/verification/verifier.py', 'eval/containers/sandbox.py',
    'data/scaffolds/qa/base.py', 'data/scaffolds/qa/verify/check.py',
    'data/scaffolds/qa/bin/qa', 'data/scaffolds/scorer_input.py']]
sources = [source(p, 'repo/' + str(p.relative_to(ROOT))) for p in sorted(set(repo_paths))]

# Default metadata graph (plus TextWorld's requested PDDL extra); installed
# distribution members are an inspection superset, never an execution closure.
roots = {}
distributions = {}
object_scopes = {}


def add_object(path, scope):
    path = Path(path)
    if path.is_file():
        object_scopes.setdefault(str(path.resolve()), set()).add(scope)


for dataset, names in PROFILES.items():
    queue, seen = list(names), set()
    while queue:
        name = queue.pop(0)
        key = re.sub('[-_.]+', '-', name).lower()
        if key in seen:
            continue
        seen.add(key)
        try:
            dist = md.distribution(name)
        except md.PackageNotFoundError:
            distributions.setdefault(key, {'name': name, 'installed': False, 'datasets': []})['datasets'].append(dataset)
            continue
        if key not in distributions:
            distributions[key] = {'name': dist.metadata['Name'], 'version': dist.version,
                                 'installed': True, 'datasets': [], 'requirements': dist.requires or [],
                                 'native_members': [], 'metadata_files': []}
            for f in dist.files or []:
                p = Path(dist.locate_file(f))
                if str(f).endswith(('/METADATA', '/RECORD', '/WHEEL')) and p.is_file():
                    distributions[key]['metadata_files'].append({'path': str(p), 'sha256': sha(p)})
                if '.so' in p.name and p.is_file():
                    distributions[key]['native_members'].append(str(p))
        distributions[key]['datasets'].append(dataset)
        for p in distributions[key]['native_members']:
            add_object(p, dataset + ':installed-metadata-superset')
        for raw in dist.requires or []:
            req = Requirement(raw)
            active = req.marker is None or req.marker.evaluate({'extra': ''})
            if key == 'textworld' and req.marker:
                active |= req.marker.evaluate({'extra': 'pddl'})
            if active:
                queue.append(req.name)
    roots[dataset] = sorted(seen)
save('distributions.json', {'profiles': roots, 'records': distributions})

# Interpreter and *all installed stdlib extensions* are a labelled superset.
for dataset in DATASETS:
    add_object(sys.executable, dataset + ':interpreter')
    for p in (Path(sysconfig.get_path('stdlib')) / 'lib-dynload').glob('*.so'):
        add_object(p, dataset + ':stdlib-installed-superset')

installed_sources = [
 'jericho/jericho.py', 'jericho/__init__.py', 'jericho/util.py',
 'alfworld/agents/environment/alfred_tw_env.py', 'alfworld/agents/environment/__init__.py',
 'alfworld/agents/utils/misc.py', 'alfworld/agents/expert/handcoded_expert.py',
 'textworld/__init__.py', 'textworld/envs/pddl/pddl.py', 'textworld/helpers.py',
 'textworld/envs/zmachine/jericho.py', 'textworld/utils.py', 'fast_downward/interface.py',
 'fast_downward/__init__.py', 'scienceworld/scienceworld.py', 'scienceworld/constants.py',
 'py4j/java_gateway.py', 'openpyxl/__init__.py', 'openpyxl/xml/__init__.py',
 'openpyxl/xml/functions.py', 'openpyxl/compat/numbers.py', 'openpyxl/drawing/image.py',
 'chess/__init__.py', 'numpy/_distributor_init.py', 'mkl/__init__.py',
 'numpy/distutils/fcompiler/__init__.py', 'gensim/matutils.py']
for rel in installed_sources:
    sources.append(source(SITE / rel, 'installed/' + rel))
for p in (SITE / 'scienceworld').glob('*.jar'):
    sources.append({'path': str(p), 'sha256': sha(p), 'scope': 'jar-observed-digest-only'})

tools = {name: shutil.which(name) for name in ['python3', 'java', 'soffice', 'libreoffice',
         'sqlite3', 'gcc', 'g++', 'bwrap', 'bash', 'sh', 'dirname', 'readlink', 'uname',
         'grep', 'sed', 'find', 'ldd', 'readelf', 'strace', 'unshare']}
save('tools.json', tools)
for name in ['bwrap']:
    if tools[name]:
        for dataset in DATASETS:
            add_object(tools[name], dataset + ':sandbox-launcher')
for name in ['gcc', 'g++', 'sqlite3']:
    if tools[name]:
        add_object(tools[name], 'tool-observed-not-unconditional-score-requirement')

jre = Path('/mnt/20t/xubuqiang/datasets/scienceworld/jre/jdk-17.0.20.1+1-jre')
java = jre / 'bin/java'
if java.is_file():
    add_object(java, 'scienceworld:staged-jvm')
    sources.append(source(jre / 'release', 'jre/release'))
    for p in jre.rglob('*.so'):
        add_object(p, 'scienceworld:jre-installed-superset')
    command('java-version', [str(java), '-version'])
    command('java-load-trace', ['strace', '-f', '-e', 'trace=execve,openat', str(java), '-version'])

lo = Path('/usr/lib/libreoffice/program')
lo_sources = ['soffice', 'sofficerc', 'fundamentalrc', 'bootstraprc', 'versionrc']
for name in lo_sources:
    sources.append(source(lo / name, 'libreoffice/' + name))
for p in lo.rglob('*') if lo.is_dir() else []:
    if p.is_file() and ('.so' in p.name or p.name in ['soffice.bin', 'oosplash']):
        add_object(p, 'spreadsheetbench:libreoffice-installed-superset')
for name in ['soffice', 'libreoffice', 'sh', 'dirname', 'readlink', 'uname', 'grep', 'sed']:
    if tools[name]:
        add_object(tools[name], 'spreadsheetbench:wrapper-or-observed-tool')
command('system-packages', ['dpkg-query', '-W', 'libc6', 'libstdc++6', 'libreoffice-core',
          'libreoffice-calc', 'fontconfig', 'libsqlite3-0'])

# Import children use the production check's environment keys, fresh HOME and
# collector cwd, network namespace denial. No world constructors, runner, workbook
# loads, JAR server, candidate code or dataset adapter imports occur.
probe = OUT / 'import_probe.py'
with tempfile.TemporaryDirectory(prefix='hg-whostdeps-import-') as scratch:
    env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'HOME': scratch,
           'LANG': os.environ.get('LANG', 'C.UTF-8'), 'PYTHONDONTWRITEBYTECODE': '1'}
    for dataset, names in IMPORTS.items():
        label = 'imports/' + dataset
        rec, stdout = command(label, [sys.executable, str(probe), *names], timeout=90, env=env)
        if rec['returncode'] == 0:
            imported = json.loads(stdout)
            for p in imported['native_paths']:
                add_object(p, dataset + ':import-observed')
            for p in imported['module_files']:
                if p and p.endswith('.so'):
                    add_object(p, dataset + ':extension-import-observed')
    if tools['soffice']:
        command('libreoffice-version', [tools['soffice'], '--version'], env=env)
        command('libreoffice-version-trace', ['strace', '-f', '-e', 'trace=execve,openat',
                tools['soffice'], '--version'], env=env)
    save('cleanup.json', {'import_scratch': scratch, 'removed_after_context_exit': True,
                         'no_benchmark_run_or_container_created': True})
assert not Path(scratch).exists()

# The conda NumPy/MKL loader uses absolute dlopen/preload paths not represented
# by the extension's DT_NEEDED. Include installed provider files explicitly.
for pattern in ['libmkl*.so*', 'libiomp*.so*']:
    for p in Path(sys.prefix, 'lib').glob(pattern):
        for dataset in ['alfworld', 'jericho', 'ds1000', 'spreadsheetbench']:
            add_object(p, dataset + ':mkl-installed-provider-superset')

save('source-index.json', sources)
objects = {}
queue = dict(object_scopes)


def inspect(path):
    p = Path(path)
    try:
        digest = sha(p)
        with p.open('rb') as stream:
            elf = stream.read(4) == b'\x7fELF'
        rec = {'path': path, 'sha256': digest, 'bytes': p.stat().st_size, 'elf': elf,
               'pin_status': 'recorded-digest-only; no execution enforcement'}
        if elf:
            for name, argv in [('ldd', ['ldd', path]), ('readelf', ['readelf', '-lW', '-dW', path])]:
                proc = subprocess.run(argv, capture_output=True, text=True, timeout=25)
                rec[name] = {'argv': argv, 'returncode': proc.returncode,
                             'stdout': proc.stdout, 'stderr': proc.stderr}
            rec['unresolved_sonames'] = re.findall(r'^\s*(\S+)\s+=>\s+not found', rec['ldd']['stdout'], re.M)
            rec['resolved_providers'] = sorted({str(Path(s).resolve()) for s in
                re.findall(r'(/[^\s()]+)', rec['ldd']['stdout']) if Path(s).is_file()})
        return rec
    except Exception as exc:
        return {'path': path, 'error': repr(exc)}


while queue:
    batch = sorted(queue)
    queue = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for rec in pool.map(inspect, batch):
            path = rec['path']
            objects[path] = rec
            for provider in rec.get('resolved_providers', []):
                object_scopes.setdefault(provider, set()).update(object_scopes[path])
                if provider not in objects and provider not in batch:
                    queue[provider] = True
    print('inspected objects:', len(objects), 'pending:', len(queue), flush=True)

# Propagate dataset relevance to a fixed point, including previously visited
# common providers; preserve DT_NEEDED edges and unresolved names verbatim.
changed = True
while changed:
    changed = False
    for path, rec in objects.items():
        for provider in rec.get('resolved_providers', []):
            before = len(object_scopes[provider])
            object_scopes[provider].update(object_scopes[path])
            changed |= len(object_scopes[provider]) != before
for path, rec in objects.items():
    rec['scopes'] = sorted(object_scopes[path])
save('objects.json', objects)

# Independent hash command: raw stdout retains every reachable selected object.
paths = sorted(p for p, rec in objects.items() if 'sha256' in rec)
for n in range(0, len(paths), 100):
    command('sha256sum/batch-%04d' % (n // 100), ['sha256sum', '--', *paths[n:n+100]], timeout=180)

coverage = {}
for dataset in DATASETS:
    relevant = [r for p, r in objects.items() if any(s.startswith(dataset + ':') for s in object_scopes[p])]
    coverage[dataset] = {'configured_native_surface_pinned': False,
        'recorded_objects': sum('sha256' in r for r in relevant),
        'recorded_elf_objects': sum(r.get('elf', False) for r in relevant),
        'standalone_unresolved_sonames': sorted({s for r in relevant for s in r.get('unresolved_sonames', [])}),
        'metadata_distributions_in_inspected_superset': len(roots[dataset])}
save('summary.json', {'datasets': coverage, 'pinned_native_surfaces': {'numerator': 0, 'denominator': len(DATASETS)},
    'objects_with_digest': len(paths), 'inspection_errors': [r for r in objects.values() if 'error' in r],
    'interpretation': 'Digests bind observations only; complete execution-selected surfaces are not admitted or immutable.'})
print(json.dumps(json.loads((OUT / 'summary.json').read_text()), indent=2))
