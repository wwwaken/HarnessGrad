"""Add source-resolved entry points and pin checks to the byte inventory; no scoring."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import tarfile
import zipfile

from inspect_closures import OUT, ROOT, NAMES, QA, dump, file_record


def read(name):
    return json.loads((OUT / name).read_text())


def entry(path, symbol, role):
    path = Path(path)
    lines = path.read_text().splitlines()
    nodes = [n for n in ast.walk(ast.parse(path.read_text()))
             if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == symbol]
    assert nodes, (path, symbol)
    return [dict(file_record(path), symbol=symbol, line=n.lineno,
                 locator=lines[n.lineno - 1], role=role) for n in nodes]


ADAPTER_BUILDER = {'alfworld': '_verifier', 'bird_minidev': '_verify', 'ds1000': 'verify_for',
                   'jericho': '_verifier', 'livecodebench': '_verify',
                   'scienceworld': '_verifier', 'spreadsheetbench': '_verifier'}
CHECK_FUNCTIONS = {
    'alfworld': ['main', 'official_reduction'],
    'bird_minidev': ['main', 'run_query', 'calculate_ex'],
    'ds1000': ['main'], 'jericho': ['main'],
    'livecodebench': ['main', '_run_official', '_aggregate_official'],
    'scienceworld': ['main'],
    'spreadsheetbench': ['main', 'compare_workbooks', 'recalculate', 'workbook_has_formulas'],
}
GOLD_READ = {
    'alfworld': ('data/datasets/alfworld/verify/check.py', 'args.game'),
    'bird_minidev': ('data/datasets/bird_minidev/verify/check.py', 'gold_sql ='),
    'ds1000': ('data/datasets/ds1000/verify/check.py', 'context.json'),
    'jericho': ('data/datasets/jericho/verify/check.py', 'args.game'),
    'livecodebench': ('data/datasets/livecodebench/verify/check.py', 'args.tests'),
    'scienceworld': ('data/datasets/scienceworld/verify/check.py', 'args.task'),
    'spreadsheetbench': ('data/datasets/spreadsheetbench/verify/check.py', 'args.golden'),
}


def line_match(path, needle, role):
    path = ROOT / path
    lines = path.read_text().splitlines()
    matches = [(i, s) for i, s in enumerate(lines, 1) if needle in s and not s.lstrip().startswith('#')]
    assert matches, (path, needle)
    return [dict(file_record(path), line=i, locator=s, role=role) for i, s in matches]


def member_bindings(name, gold):
    """Compare existing source members to actual local archive bytes; never extract."""
    wanted_archive = {
        'physicsquestions': 'rewoo.tar.gz', 'sportsunderstanding': 'rewoo.tar.gz',
        'strategyqa': 'rewoo.tar.gz', 'bfcl_v3': 'gorilla-v1.3.tar.gz',
        'alfworld': 'json_2.1.3_tw-pddl.zip', 'bird_minidev': 'minidev.zip',
        'jericho': 'z-machine-games.zip', 'spreadsheetbench': 'spreadsheetbench_verified_400.tar.gz',
    }.get(name)
    if not wanted_archive:
        return []
    archives = [a for a in gold['provenance_archives_or_shards'] if Path(a['path']).name == wanted_archive]
    if not archives:
        return [{'archive_name': wanted_archive, 'finding': 'archive absent; no member provenance established'}]
    archive = archives[0]
    path = Path(archive['path'])
    bindings = []
    with (zipfile.ZipFile(path) if path.suffix == '.zip' else tarfile.open(path, 'r:gz')) as handle:
        members = handle.namelist() if isinstance(handle, zipfile.ZipFile) else handle.getnames()
        for artifact in gold['artifacts']:
            if artifact['location'] != 'external-local':
                continue
            relative = str(Path(artifact['path']).relative_to(gold['dataset_root']))
            # BIRD's local extraction adds _src/unpacked/; other archives can add
            # one release directory. A unique suffix match must then pass a byte hash.
            suffixes = [relative]
            if relative.startswith('_src/unpacked/'):
                suffixes.append(relative[len('_src/unpacked/'):])
            candidates = sorted({m for m in members for suffix in suffixes
                                 if m.lstrip('./') == suffix or m.endswith('/' + suffix)})
            if not candidates:
                # Preserve unresolved custody instead of assuming a matching basename.
                bindings.append({'artifact': artifact['path'], 'archive': archive['path'],
                                 'finding': 'no unique full-relative suffix member found'})
                continue
            hashes = []
            for member in candidates:
                stream = handle.open(member) if isinstance(handle, zipfile.ZipFile) else handle.extractfile(member)
                h = hashlib.sha256()
                with stream:
                    for block in iter(lambda: stream.read(4 << 20), b''):
                        h.update(block)
                hashes.append({'member': member, 'sha256': h.hexdigest(),
                               'equals_local_artifact': h.hexdigest() == artifact['sha256']})
            bindings.append({'artifact': artifact['path'], 'archive': archive['path'], 'candidates': hashes})
    return bindings


def main():
    packages = read('packages.json')
    for name in NAMES:
        path = ROOT / 'data/datasets' / (name + '.py')
        text = path.read_text()
        record = read('datasets/' + name + '.json')
        labels = [name] if (OUT / 'imports' / (name + '.json')).is_file() else []
        if name in ['gsm8k', 'hotpotqa', 'triviaqa']:
            labels.append('qa_parquet_startup')
        imports = [read('imports/' + label + '.json') for label in labels]
        record['import_receipts'] = [file_record(OUT / 'imports' / (label + '.json')) for label in labels]
        record['directly_observed_imported_packages'] = {
            p: packages[re.sub(r'[-_.]+', '-', p).lower()]
            for receipt in imports for p in receipt['packages']}
        record['startup_or_inspection_packages'] = {
            p: packages[re.sub(r'[-_.]+', '-', p).lower()]
            for receipt in imports for p in receipt.get('startup_or_inspection_packages', {})}
        points = []
        if name in QA:
            symbols = {n.name for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
            for symbol in ['score', 'score_prediction']:
                if symbol in symbols:
                    points += entry(path, symbol, 'adapter scorer reached by shared QA check')
            points += entry(ROOT / 'data/scaffolds/qa/base.py', 'verifier', 'QA command/input construction')
            points += entry(ROOT / 'data/scaffolds/qa/verify/check.py', 'main', 'shared QA check entry')
            edges = []
            for needle, role in [('gold = json.loads(', 'read trusted gold.json'),
                                 ('adapter = __import__(', 'import staged adapter'),
                                 ('evidence_scorer(structured, gold', 'structured evidence branch'),
                                 ('else scorer(prediction, gold', 'answer branch')]:
                edges += line_match('data/scaffolds/qa/verify/check.py', needle, role)
            record['qa_check_path'] = next(p['path'] + ':' + str(p['line']) for p in points
                                          if p['role'] == 'shared QA check entry')
        else:
            points += entry(path, ADAPTER_BUILDER[name], 'native command/input construction')
            check = ROOT / 'data/datasets' / name / 'verify/check.py'
            actual = {n.name for n in ast.walk(ast.parse(check.read_text())) if isinstance(n, ast.FunctionDef)}
            for symbol in CHECK_FUNCTIONS[name]:
                if symbol in actual:
                    points += entry(check, symbol, 'native check/reduction entry')
            gold_path, needle = GOLD_READ[name]
            edges = line_match(gold_path, needle, 'expected-data use in native check')
        for source in record['adapter_and_check_sources']:
            if source['location'] == 'external-local' and source['path'].endswith('.py'):
                wanted = {'check_correctness', 'run_test', 'compute_metrics_from_results'}
                for definition in source.get('definitions', []):
                    if definition['symbol'] in wanted:
                        points += entry(Path(source['path']), definition['symbol'], 'upstream scorer child/aggregation')
        record['entry_points'] = points
        record['execution_edges'] = edges
        direct = record['directly_observed_imported_packages']
        queue = [re.sub(r'[-_.]+', '-', p).lower() for p in direct]
        transitive = set()
        # Edges are inventory metadata, not a claim of dynamic use.
        from packaging.requirements import Requirement
        while queue:
            key = queue.pop()
            if key in transitive:
                continue
            transitive.add(key)
            for dependency in packages[key].get('requirements', []):
                if dependency['active_default_or_textworld_pddl']:
                    queue.append(re.sub(r'[-_.]+', '-', Requirement(dependency['requirement']).name).lower())
        record['declared_dependency_package_keys'] = sorted(transitive)
        record['native_abi_inventory'] = file_record(OUT / 'native-files.json')
        if name == 'scienceworld':
            record['jre_content_manifest'] = file_record(OUT / 'jre-files.json')
        # Match actual computed bytes against literal configured SHA-256s. An absent
        # match is explicit; an archive pin is not silently promoted to a member pin.
        configured = set(re.findall(r'\b[a-f0-9]{64}\b', text))
        gold = read('gold/' + name + '.json')
        for group in ['artifacts', 'provenance_archives_or_shards']:
            for artifact in gold[group]:
                artifact['matches_literal_adapter_digest'] = artifact.get('sha256') in configured
        gold['archive_member_bindings'] = member_bindings(name, gold)
        gold['pin_finding'] = ('Computed member hashes pin current bytes; matching adapter literals are marked separately. '
            'Archive members are independently read and compared only where archive_member_bindings records an equal hash; '
            'other archive/derived-file linkage is not attested. '
            'No per-task inline serialization or submitted prediction is generated.')
        gold_manifest = dump('gold/' + name + '.json', gold)
        record['gold_expected_data'] = gold_manifest
        if name == 'gsm8k':
            finding = 'Current decimal-aware extraction plus absolute tolerance <1e-6 is an adapter metric, explicitly distinct from upstream normalized exact match; official equivalence is not claimed.'
            if finding not in record['not_pinned_or_not_established']:
                record['not_pinned_or_not_established'].insert(0, finding)
        if name == 'fever':
            finding = 'Provisioning leaves JSONL SHA-256 null; this inspection pins current valid.jsonl bytes but does not establish immutable Hub export reconstruction.'
            if finding not in record['not_pinned_or_not_established']:
                record['not_pinned_or_not_established'].insert(0, finding)
        dump('datasets/' + name + '.json', record)

    # Scorer-package function locations: inspect AST only. Capture every Reasoning
    # Gym score_answer/family constructor, including families not touched by import.
    import importlib.metadata as metadata
    installed = []
    for package, symbols in [('reasoning-gym', {'create_dataset', 'score_answer', '__init__'}),
                             ('chess', {'Board'}), ('jericho', {'FrotzEnv'}),
                             ('scienceworld', {'ScienceWorldEnv'})]:
        dist = metadata.distribution(package)
        entries = []
        for rel in dist.files or []:
            path = Path(dist.locate_file(rel))
            if path.suffix != '.py' or not path.is_file() or '__pycache__' in path.parts:
                continue
            source = path.read_text()
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in symbols:
                    entries.append(dict(file_record(path), symbol=node.name, line=node.lineno,
                                         locator=source.splitlines()[node.lineno - 1]))
        installed.append({'package': package, 'version': dist.version, 'entry_points': entries,
                          'scope': 'AST candidates; no constructor or scorer called'})
    dump('installed-scorer-entry-points.json', installed)
    for name in ['reasoning_gym', 'chessbench_puzzles', 'jericho', 'scienceworld']:
        record = read('datasets/' + name + '.json')
        record['installed_scorer_entry_points'] = file_record(OUT / 'installed-scorer-entry-points.json')
        dump('datasets/' + name + '.json', record)
    print('Resolved entry points, gold pin checks, and per-dataset dependency graphs:', len(NAMES))


if __name__ == '__main__':
    main()
