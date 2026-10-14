"""Capture local scorer bytes, not scores. No adapter, task, or world is invoked.

Run from the repository root. Output is deliberately separate from historical evidence.
External dataset/package files are read in place; only manifests enter the repository.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import sysconfig

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DATA = Path('/mnt/20t/xubuqiang/datasets')
QA = ['bfcl_v3', 'chessbench_puzzles', 'fever', 'gsm8k', 'hotpotqa', 'musique',
      'physicsquestions', 'reasoning_gym', 'sportsunderstanding', 'strategyqa',
      'triviaqa', 'twowikimultihopqa']
NATIVE = ['alfworld', 'bird_minidev', 'ds1000', 'jericho', 'livecodebench',
          'scienceworld', 'spreadsheetbench']
NAMES = sorted(QA + NATIVE)
CACHE: dict[str, dict] = {}


def dump(name, value):
    dest = OUT / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    return file_record(dest)


def file_record(path):
    path = Path(path).absolute()
    key = str(path)
    if key in CACHE:
        return CACHE[key]
    result = {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else key,
              'location': 'checkout' if path.is_relative_to(ROOT) else 'external-local',
              'exists': path.is_file()}
    if path.is_file():
        before = path.stat()
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(4 << 20), b''):
                digest.update(block)
        after = path.stat()
        assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), key
        result.update(bytes=after.st_size, sha256=digest.hexdigest())
        if path.is_symlink():
            result.update(symlink=os.readlink(path), resolved_path=str(path.resolve()))
    CACHE[key] = result
    return result


def tree_files(path):
    return sorted(p for p in Path(path).rglob('*') if p.is_file()
                  and '__pycache__' not in p.parts and p.suffix != '.pyc')


def source_record(path):
    path = Path(path)
    rec = dict(file_record(path))
    if not path.is_file() or path.suffix != '.py':
        return rec
    text = path.read_text()
    tree = ast.parse(text)
    lines = text.splitlines()
    rec['definitions'] = [{'symbol': n.name, 'line': n.lineno,
                           'locator': lines[n.lineno - 1]}
                          for n in ast.walk(tree)
                          if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    rec['imports'] = [{'line': n.lineno, 'locator': lines[n.lineno - 1],
                      'statement': ast.get_source_segment(text, n)}
                     for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    return rec


def declarations(name):
    path = ROOT / 'data/datasets' / (name + '.py')
    text = path.read_text()
    result = []
    for node in ast.parse(text).body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name) and any(k in target.id for k in
                    ('REVISION', 'COMMIT', 'VERSION', 'SHA256', 'REFERENCE', 'RELEASE', 'REPO_TAG')):
                result.append({'symbol': target.id, 'line': node.lineno,
                               'source': ast.get_source_segment(text, node)})
    return result


# Only package imports in fresh interpreters; never import an adapter (build() may load tasks).
# Network is denied even during import. Constructors, score functions and candidate code
# are never called. Package stdout/stderr is preserved separately from the JSON receipt.
PROBE = r'''
import importlib, importlib.metadata as md, json, pathlib, sys, sysconfig
def deny(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo', 'socket.bind'):
        raise RuntimeError('network denied during import-only inspection: ' + event)
sys.addaudithook(deny)
requested = json.loads(sys.argv[1])
before = set(sys.modules)
errors = {}
for name in requested:
    try:
        importlib.import_module(name)
    except Exception as exc:
        errors[name] = type(exc).__name__ + ': ' + str(exc)
site = pathlib.Path(sysconfig.get_path('purelib')).resolve()
mapping = md.packages_distributions()
modules = []
packages = {}
startup_packages = {}
unmapped = []
for name, module in sorted(sys.modules.copy().items()):
    origin = getattr(module, '__file__', None)
    if not origin:
        continue
    p = pathlib.Path(origin)
    if not p.is_file():
        continue
    phase = 'preexisting interpreter/inspection' if name in before else 'requested package import'
    modules.append({'module': name, 'path': str(p.resolve()), 'phase': phase})
    if not p.resolve().is_relative_to(site):
        continue
    owners = mapping.get(name.split('.')[0], [])
    if not owners:
        unmapped.append({'module': name, 'path': str(p.resolve())})
    for owner in owners:
        d = md.distribution(owner)
        target = startup_packages if name in before else packages
        target[d.metadata['Name']] = d.version
pathlib.Path(sys.argv[2]).write_text(json.dumps({
    'requested_imports': requested, 'errors': errors,
    'inspection': 'import-only; network denied; no scorer, task, world or model called',
    'modules': modules, 'packages': packages, 'startup_or_inspection_packages': startup_packages,
    'unmapped_site_modules': unmapped}, indent=2, sort_keys=True) + '\n')
'''

IMPORTS = {
    'qa_parquet_startup': ['pyarrow.parquet'],
    'chessbench_puzzles': ['chess', 'chess.engine'],
    'reasoning_gym': ['reasoning_gym'],
    'alfworld': ['textworld.gym', 'alfworld.agents.environment.alfred_tw_env'],
    'bird_minidev': ['sqlite3'],
    'ds1000': ['numpy', 'pandas', 'scipy', 'sklearn', 'matplotlib', 'seaborn', 'torch', 'PIL', 'yaml'],
    'jericho': ['jericho'],
    'livecodebench': ['numpy'],
    'scienceworld': ['scienceworld'],
    'spreadsheetbench': ['openpyxl'],
}

SPECS = {
    'gsm8k': ('gsm8k', ['main/test-00000-of-00001.parquet', 'main/train-00000-of-00001.parquet'],
              'openai/gsm8k@740312add88f781978c0658806c59bc2815b9866; main test + train'),
    'fever': ('fever', ['valid.jsonl'],
              'copenlu/fever_gold_evidence@a6b8d891d393e97a4efac791afffb2d7de5e57c6; validation'),
    'hotpotqa': ('hotpotqa', ['fullwiki/validation-00000-of-00001.parquet'],
                 'hotpot_qa@1908d6afbbead072334abe2965f91bd2709910ab; fullwiki validation'),
    'musique': ('musique', ['musique_ans_v1.0_dev.jsonl'],
                'dgslibisey/MuSiQue@c8f4f8c9465fb69d31a8eae894c3fd509c4ca321; Ans v1.0 dev; mirror provenance retained'),
    'reasoning_gym': ('reasoning_gym', ['pool.jsonl'],
                      'reasoning-gym==0.1.25; seed=20261008, size=20 per family, 89 families; adapter POOL_SHA256'),
    'triviaqa': ('triviaqa', ['rc.nocontext/validation-00000-of-00001.parquet',
                              'rc.nocontext/train-00000-of-00001.parquet'],
                 'mandarjoshi/trivia_qa@0f7faf33a3908546c6fd5b73a660e0f8ff173c2f; validation + even-stride study train; withheld test excluded'),
    'twowikimultihopqa': ('twowikimultihopqa', ['dev.json', 'id_aliases.json'],
                          'kamelliao/2wikimultihopqa@f4f0d7e4ae275d9281e90c46c93e66d6cdda3674; dev + alias table; third-party mirror'),
    'chessbench_puzzles': ('chessbench_puzzles', ['_src/puzzles.csv'],
                           'google-deepmind/searchless_chess@90ae0e6b121673fc3079aaeffa047580bb600c0a; GCS CSV, adapter CSV_SHA256'),
    'bfcl_v3': ('bfcl-v3', [
        'gorilla-1.3/berkeley-function-call-leaderboard/bfcl_eval/data/BFCL_v3_simple.json',
        'gorilla-1.3/berkeley-function-call-leaderboard/bfcl_eval/data/BFCL_v3_irrelevance.json',
        'gorilla-1.3/berkeley-function-call-leaderboard/bfcl_eval/data/possible_answer/BFCL_v3_simple.json'],
        'ShishirPatil/gorilla@v1.3; archive digest pin in adapter; simple answer names + irrelevance expected empty list'),
    'ds1000': ('ds1000', ['_src/test.jsonl', 'seaborn-data/*.csv'],
               'xlangai/DS-1000@4416080ac5cb80bdf7576aefb8f9a0b4d5426a44; context tests; seaborn-data@71e2436a092d714350de0fc409ca8a8714e7e78f'),
    'livecodebench': ('livecodebench', ['pool.jsonl', 'tests/*.json'],
                      'livecodebench/code_generation_lite@0fe84c3912ea0c4d4a78037083943e8f0c4dd505 release_v6; prepare.py decodes test files'),
    'alfworld': ('alfworld', ['json_2.1.1/valid_unseen/**/game.tw-pddl'],
                 'ALFWorld release 0.4.2 json_2.1.3_tw-pddl.zip; adapter strips walkthrough before staging'),
    'bird_minidev': ('bird_minidev', ['_src/unpacked/minidev/MINIDEV/mini_dev_sqlite.json',
                                       '_src/unpacked/minidev/MINIDEV/mini_dev_sqlite_gold.sql',
                                       '_src/unpacked/minidev/MINIDEV/dev_databases/**/*.sqlite'],
                      'BIRD Mini-Dev release 2024-06-20/7BEB6DAB11E65F0FDE563E644A1EA319; adapter DATA_SHA256'),
    'jericho': ('jericho', ['z-machine-games-master/jericho-game-suite/*'],
                'BYU-PCCL/z-machine-games master archive, bytes digest-pinned in adapter; game seeds/maxima also in installed Jericho package'),
    'scienceworld': ('scienceworld', [],
                     'scienceworld==1.2.3 package JAR and data; repository test_fold.json; Temurin JRE 17.0.20.1+1'),
    'spreadsheetbench': ('spreadsheetbench', [
        'spreadsheetbench_verified_400/dataset.json',
        'spreadsheetbench_verified_400/spreadsheet/**/*golden*.xlsx'],
        'KAKA22/SpreadsheetBench@ab0b742b0fc95b946f212d80ac7771b5531272e4; verified_400 archive'),
}
for name, csv in [('physicsquestions', 'physics_question'), ('strategyqa', 'strategy_qa'),
                  ('sportsunderstanding', 'sports_understanding')]:
    SPECS[name] = (name, [f'ReWOO-9cd0283043ff4be0c9d614fda2789d143ca6ffd1/data/bigbench/{csv}.csv'],
                   'billxbf/ReWOO@9cd0283043ff4be0c9d614fda2789d143ca6ffd1; vendored BIG-bench CSV; adapter archive digest pin')

EXTRA = {
    'ds1000': ['_src/DS-1000-b39aab71/execution.py', '_src/DS-1000-b39aab71/environment.yml'],
    'livecodebench': ['_src/upstream/LiveCodeBench-28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24/lcb_runner/evaluation/testing_util.py',
                      '_src/upstream/LiveCodeBench-28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24/lcb_runner/evaluation/pass_k_utils.py'],
}

FINDINGS = {
    'bfcl_v3': ['Implemented function-name diagnostic is expressly NOT official BFCL AST scoring; no official BFCL execution claim.',
                'Selected-index byte binding and per-task private gold are not materialized in this inspection.'],
    'chessbench_puzzles': ['chess==1.11.2 has no configured wheel hash; alternate trusted stepwise route is in-process and is outside this default QA record.',
                          'Survey predates the recorded-class fix; current chess_stepwise.py source is hashed separately.'],
    'fever': ['Gold labels/evidence are mirror validation data; official strict metric execution is not performed here.'],
    'gsm8k': ['Adapter import attempts PyArrow before checking data visibility; failed loader exceptions are caught.'],
    'hotpotqa': ['Adapter import conditionally imports PyArrow when the source parquet is visible; sandbox visibility is not measured.'],
    'musique': ['Mirror identity against canonical HF remains unverified; joint answer/support reward is platform-defined; trusted mode must match.'],
    'physicsquestions': ['ReWOO vendor provenance is pinned; direct upstream BIG-bench metric provenance/execution is not independently established here.'],
    'sportsunderstanding': ['Ambiguous-label refusal diverges from historical substring scoring; this hashes the implemented rule.'],
    'strategyqa': ['ReWOO vendor table is the source; upstream BIG-bench task removal does not authorize a replacement metric.'],
    'triviaqa': ['Adapter startup can attempt PyArrow; comparison itself is stdlib. Withheld test gold is neither read nor required.'],
    'twowikimultihopqa': ['Official release is obtained via third-party mirror; witness is provenance-only, not scoring input.',
                         'Structured joint and legacy answer-only modes must be reported separately.'],
    'reasoning_gym': ['Distribution version 0.1.25 differs from source __version__ 0.1.19; both are preserved.',
                      'Family constructors/score_answer are not called; family-specific lazy imports/resources and offline behavior are not live-validated.'],
    'alfworld': ['Raw released game hashes do not identify the stripped game.tw-pddl actually staged per task.',
                 'TextWorld/Fast Downward dlopen and complete runtime custody remain unestablished.'],
    'bird_minidev': ['SQLite is a stdlib extension/native library dependency; no sqlite CLI or upstream pandas/func_timeout is reached.',
                     'Per-task gold.sql serialization and SQLite read-only enforcement are not measured.'],
    'ds1000': ['Task/candidate execution can add imports beyond inspected eligible-context packages; no candidate is executed.',
               'Actor context.json is not restored by VERIFY.inputs; gold test custody remains unresolved.',
               'Installed Python/scientific builds differ from upstream environment.yml; seaborn cache misses may fetch.'],
    'jericho': ['ROM selection/seed comes from installed game_info.py; source archive uses moving master URL with content digest.',
                'Frotz dlopen, copied runtime and game-dependent resources need live custody; dormant spaCy download is not replay evidence.'],
    'livecodebench': ['Decoded tests are hashed individually; linkage to pinned raw shards/prepare.py is not re-executed.',
                      'Candidate code can import additional modules; no arbitrary submitted-code closure is claimed.'],
    'scienceworld': ['JRE tree/JAR/package bytes are hashed; Java override/fallback selection and Py4J IPC lifecycle are not observed.',
                     'No static answer key: expected outcome is JVM state for task_name/variation, not a fabricated gold answer.'],
    'spreadsheetbench': ['LibreOffice version/plugins/OS dependency closure are not configured pins; formula branch can overwrite a read-only actor workbook.',
                         'Formula recalculation, external references and per-task task.json custody need live validation.'],
}


def main():
    survey = ROOT / 'reports/w-shared-topology-survey.md'
    survey_rows = [line for line in survey.read_text().splitlines()
                   if line.startswith('| `') and 'actor-workdir' in line]
    surveyed = sorted(re.match(r'\| `([^`]+)`', line).group(1) for line in survey_rows)
    assert surveyed == NAMES, (surveyed, NAMES)
    commands = []
    imported = {}
    for label, imports in IMPORTS.items():
        dest = OUT / 'imports' / (label + '.json')
        dest.parent.mkdir(exist_ok=True)
        cmd = [sys.executable, '-B', '-c', PROBE, json.dumps(imports), str(dest)]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', MPLCONFIGDIR='/tmp/hg-wclo-actor-mpl',
                   CUDA_VISIBLE_DEVICES='', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
        proc = subprocess.run(cmd, cwd='/tmp', env=env, capture_output=True, text=True, timeout=120)
        (dest.with_suffix('.stdout.txt')).write_text(proc.stdout)
        (dest.with_suffix('.stderr.txt')).write_text(proc.stderr)
        commands.append({'argv': cmd, 'cwd': '/tmp', 'returncode': proc.returncode,
                         'environment_overrides': {k: env[k] for k in
                            ['PYTHONDONTWRITEBYTECODE', 'MPLCONFIGDIR', 'CUDA_VISIBLE_DEVICES',
                             'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS']}})
        assert proc.returncode == 0, (label, proc.stderr)
        imported[label] = json.loads(dest.read_text())
        for module in imported[label]['modules']:
            module.update(file_record(module.pop('path')))
        dump('imports/' + label + '.json', imported[label])
        print('import-only:', label, 'errors:', imported[label]['errors'], flush=True)
    dump('import-commands.json', commands)
    if '--imports-only' in sys.argv:
        return

    # Installed distribution bytes: never trust RECORD's claimed digests. Hash each
    # existing member ourselves. Omit regenerable pyc; missing members remain findings.
    from packaging.requirements import Requirement
    queue = sorted({n for record in imported.values() for group in
                    ['packages', 'startup_or_inspection_packages'] for n in record[group]})
    distributions = {}
    while queue:
        name = queue.pop(0)
        canonical = re.sub(r'[-_.]+', '-', name).lower()
        if canonical in distributions:
            continue
        try:
            dist = metadata.distribution(name)
        except metadata.PackageNotFoundError:
            distributions[canonical] = {'name': name, 'installed': False}
            continue
        requirements = []
        for raw in dist.requires or []:
            req = Requirement(raw)
            active = req.marker is None or req.marker.evaluate({'extra': ''})
            if canonical == 'textworld' and req.marker:
                active = active or req.marker.evaluate({'extra': 'pddl'})
            requirements.append({'requirement': raw, 'active_default_or_textworld_pddl': active})
            if active:
                queue.append(req.name)
        files, missing = [], []
        for rel in sorted(dist.files or [], key=str):
            if '__pycache__' in Path(str(rel)).parts or str(rel).endswith('.pyc'):
                continue
            rec = file_record(dist.locate_file(rel))
            (files if rec['exists'] else missing).append(rec)
        manifest = dump('packages/' + canonical + '.json', {
            'name': dist.metadata['Name'], 'version': dist.version,
            'scope': 'All metadata-enumerated installed members except regenerable bytecode; no wheel payload archived',
            'files': files, 'missing_members': missing, 'requirements': requirements})
        distributions[canonical] = {'name': dist.metadata['Name'], 'version': dist.version,
            'installed': True, 'content_manifest': manifest,
            'metadata_files': [f for f in files if Path(f['path']).name in ('METADATA', 'RECORD', 'WHEEL')],
            'missing_members': len(missing), 'file_count': len(files), 'requirements': requirements}
    dump('packages.json', distributions)
    print('installed package manifests:', len(distributions), flush=True)

    # Interpreter/stdlib identity is observed here, not the interpreter of a prior run.
    stdlib = Path(sysconfig.get_path('stdlib'))
    runtime_files = [p for p in tree_files(stdlib) if 'site-packages' not in p.parts]
    runtime = dump('interpreter-files.json', [file_record(p) for p in runtime_files])
    host = {'argv_name': 'python3', 'which': shutil.which('python3'),
        'executable': file_record(sys.executable), 'resolved_executable': str(Path(sys.executable).resolve()),
        'version': sys.version, 'soabi': sysconfig.get_config_var('SOABI'),
        'stdlib_content_manifest': runtime, 'no_docker_image': True,
        'finding': 'Native host bytes observed; python3 argv/PATH does not enforce this identity in future verifier sandboxes.'}
    dump('interpreter.json', host)

    common_paths = [ROOT / p for p in ['eval/verification/verifier.py', 'eval/containers/sandbox.py',
                    'eval/run/runner.py', 'eval/run/chess_stepwise.py']]
    common_paths += [p for p in (ROOT / 'data/scaffolds/qa').glob('*.py')]
    common_paths += [ROOT / 'data/scaffolds/qa/verify/check.py']
    common_paths += [ROOT / p for p in ['data/__init__.py', 'data/datasets/__init__.py',
                                       'data/scaffolds/__init__.py', 'data/scaffolds/registry.py',
                                       'data/scaffolds/command_control.py']]
    dump('common-sources.json', [source_record(p) for p in sorted(set(common_paths))])
    gold_counts = {}
    for name in NAMES:
        folder, patterns, provenance = SPECS[name]
        root = DATA / folder
        gold_files, absent = [], []
        for pattern in patterns:
            matches = sorted(p for p in root.glob(pattern) if p.is_file())
            if not matches:
                absent.append(pattern)
            gold_files += [file_record(p) for p in matches]
        if name == 'scienceworld':
            gold_files.append(file_record(ROOT / 'data/datasets/scienceworld/test_fold.json'))
            dist = metadata.distribution('scienceworld')
            gold_files += [file_record(dist.locate_file(f)) for f in dist.files or []
                           if str(f).endswith(('.jar', '.json', '.tsv'))]
        archives = sorted(p for p in (root / '_src').glob('*') if p.is_file()
                          and (p.name.endswith(('.tar.gz', '.zip', '.jsonl'))))
        if name in ['physicsquestions', 'sportsunderstanding', 'strategyqa']:
            archives.append(root / 'rewoo.tar.gz')
        gold = {'dataset': name, 'provenance_pin': provenance, 'dataset_root': str(root),
                'artifacts': gold_files, 'missing_patterns': absent,
                'provenance_archives_or_shards': [file_record(p) for p in archives],
                'binding': 'These are source/expected-data bytes. Inline per-task gold/task/context files are created by the hashed adapter and are not generated or attested here.',
                'artifact_count': len(gold_files)}
        gold_manifest = dump('gold/' + name + '.json', gold)
        gold_counts[name] = len(gold_files)
        paths = [ROOT / 'data/datasets' / (name + '.py')]
        if name in NATIVE:
            paths += [ROOT / 'data/datasets' / name / 'verify/check.py']
            paths += list((ROOT / 'data/datasets' / name / 'lib').glob('*.py'))
        paths += list((ROOT / 'data/datasets' / name).glob('prepare.py'))
        sources = [source_record(p) for p in paths]
        sources += [source_record(root / rel) for rel in EXTRA.get(name, [])]
        labels = [name] if name in IMPORTS else []
        if name in ['gsm8k', 'hotpotqa', 'triviaqa']:
            labels.append('qa_parquet_startup')
        packages = sorted({p for label in labels for p in imported[label]['packages']})
        findings = list(FINDINGS[name]) + [
            'No adapter-enforced interpreter/stdlib/complete ABI lock or offline-installable runtime bundle is provisioned by this manifest.',
            'No per-task staged gold/answer/prediction binding is produced; no score or benchmark task is executed.',
            'Actor-workdir import precedence, trusted resource/lifecycle/cleanup observations and live offline controls are not established by byte inspection.']
        if absent:
            findings.append('Missing expected-data patterns: ' + ', '.join(absent))
        record = {'dataset': name, 'closure_status': 'partial-local-byte-closure; not production offline closure',
            'executed_isolation_class_from_survey': 'actor-workdir',
            'class_evidence_kind': 'source route; no new executed observation',
            'survey_row': next(line for line in survey_rows if line.startswith('| `' + name + '`')),
            'route': 'Q: shared QA command' if name in QA else 'F: native command',
            'adapter_and_check_sources': sources,
            'qa_check_path': 'data/scaffolds/qa/verify/check.py:133' if name in QA else None,
            'shared_sources': file_record(OUT / 'common-sources.json'),
            'provenance_declarations': declarations(name), 'gold_expected_data': gold_manifest,
            'interpreter': file_record(OUT / 'interpreter.json'),
            'import_receipts': [file_record(OUT / 'imports' / (label + '.json')) for label in labels],
            'directly_observed_imported_packages': {p: distributions[re.sub(r'[-_.]+', '-', p).lower()]
                                                    for p in packages},
            'transitive_installed_requirements': file_record(OUT / 'packages.json'),
            'not_pinned_or_not_established': findings}
        dump('datasets/' + name + '.json', record)
        print('dataset:', name, 'gold artifacts:', len(gold_files), 'missing:', absent, flush=True)

    jre = DATA / 'scienceworld/jre/jdk-17.0.20.1+1-jre'
    dump('jre-files.json', [file_record(p) for p in tree_files(jre)])
    # Existing readelf/ldd receipts are leads only: hash actual current files they name.
    # Do not execute Java/LibreOffice or a loader to infer runtime behavior.
    candidates = {Path(sys.executable).resolve(), Path('/usr/lib/libreoffice/program/soffice.bin')}
    for label in imported:
        candidates.update(Path(m['path']) for m in imported[label]['modules']
                          if '.so' in Path(m['path']).name)
    for name in ['native/binary-inspection.json', 'native/import-and-jvm-elf.json',
                 'scope/native-needed-readelf.txt']:
        text = (ROOT / 'tests/fixtures/hg_wtbdep' / name).read_text()
        candidates.update(Path(s) for s in re.findall(r'/[^\s"\'()\\]+', text)
                          if Path(s).is_file() and ('.so' in Path(s).name or Path(s).name in ('java', 'python3')))
    candidates.update(p for p in tree_files(jre) if '.so' in p.name or p.name == 'java')
    for canonical in ['jericho', 'fast-downward-textworld']:
        manifest = distributions.get(canonical, {}).get('content_manifest')
        if manifest:
            candidates.update(Path(f['path']) for f in json.loads((ROOT / manifest['path']).read_text())['files']
                              if '.so' in Path(f['path']).name)
    dump('native-files.json', {'scope': 'Current bytes for imported extensions and existing inventory ELF paths/JRE. Not a complete dlopen/plugin/OS ABI closure.',
                              'files': [file_record(p) for p in sorted(candidates) if p.is_file()]})
    evidence = [survey, ROOT / 'reports/w-tbdep-transitive-inventory.md', ROOT / 'reports/w-net-receipts.md']
    evidence += [ROOT / 'reports/w-alf-receipts.md', ROOT / 'reports/w-alf-evidence/runtime-attempt/run-one-result.json',
                 ROOT / 'reports/w-alf-evidence/resource-observations.json', ROOT / 'reports/w-alf-evidence/cleanup-observations.json']
    dump('prior-evidence.json', {'files': [file_record(p) for p in evidence],
        'findings': ['w-net is snapshot-service and cannot establish actor-workdir closure.',
                     'w-alf supplies an existing actor-workdir noop scorer observation, with unknown formal lifecycle and no proven CPU/RAM caps; it is not a complete class control.',
                     'hg_wtbdep/python and hg_wtbdep/runtime directories cited by the prior report are absent in this checkout; their prose/hashes are not reused as byte evidence.']})
    dump('scope.json', {'datasets': NAMES, 'qa_command': QA, 'native_command': NATIVE,
        'excluded_snapshot_service': ['appworld', 'gaia', 'tau_bench', 'terminal_bench'],
        'gold_artifact_counts': gold_counts,
        'source_git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'boundary': 'Source/bytes and guarded package imports only; no benchmark, scorer, model, GPU, endpoint, Docker or frozen-run execution.'})


if __name__ == '__main__':
    main()
