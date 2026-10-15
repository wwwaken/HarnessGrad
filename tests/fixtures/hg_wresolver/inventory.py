"""Re-read source and derive scope/metadata gaps without executing benchmark code."""
import ast
import email
import json
from pathlib import Path
import re
import subprocess
import sys

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.tags import parse_tag, sys_tags
from common import HERE, ROOT, digest, save

inputs = json.loads((HERE / 'inputs.json').read_text())
prior = ROOT / 'tests/fixtures/hg_wwheelhouse'
scope = json.loads((prior / 'source-scope.json').read_text())['datasets']
prior_payloads = json.loads((prior / 'dataset-payloads.json').read_text())
registry = json.loads((HERE / 'registry-before.json').read_text())
datasets = [r['dataset'] for r in registry['datasets'] if 'scorer-offline-closure' in r['shared_blockers']]
paths = {p for row in scope.values() for p in row.get('source_paths', []) if not Path(p).is_absolute()}
paths.update(f'data/datasets/{name}.py' for name in scope if name in datasets)
paths.update(['data/scaffolds/qa/base.py', 'data/scaffolds/qa/verify/check.py',
              'data/scaffolds/qa/read.py', 'eval/verification/verifier.py'])
for name in ['gaia', 'tau_bench', 'appworld', 'terminal_bench']:
    paths.add(f'data/datasets/{name}.py')
    for suffix in ['verify/check.py', 'Dockerfile']:
        if (ROOT / f'data/datasets/{name}/{suffix}').is_file():
            paths.add(f'data/datasets/{name}/{suffix}')
paths.update(['tests/fixtures/hg_wuvx/source/tasks/' + name + '/test.sh'
              for name in ['openssl-selfsigned-cert', 'mailman', 'build-cython-ext']])
paths.update([str(Path(sys.base_prefix) / 'lib/python3.12/importlib/_bootstrap_external.py'),
              str(Path(sys.base_prefix) / 'lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/candidates.py'),
              str(Path(sys.base_prefix) / 'lib/python3.12/site-packages/pip/_internal/index/collector.py')])
sources = []
for index, rel in enumerate(sorted(paths)):
    source = Path(rel) if Path(rel).is_absolute() else ROOT / rel
    content = source.read_text()
    preimage = HERE / 'source' / f'{index:03d}-{source.name}.txt'
    preimage.parent.mkdir(exist_ok=True)
    preimage.write_bytes(source.read_bytes())
    imports = []
    if source.suffix == '.py':
        for node in ast.walk(ast.parse(content)):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append({'line': node.lineno, 'text': content.splitlines()[node.lineno - 1]})
    sources.append({'path': str(source), 'repository_path': rel,
                    'sha256': digest(source), 'preimage': str(preimage.relative_to(ROOT)),
                    'imports': sorted(imports, key=lambda r: r['line'])})
save(HERE / 'source-inventory.json', sources)
normalize = lambda s: re.sub(r'[-_.]+', '-', s).lower()
artifacts = {r['key']: r for r in inputs['artifacts']}
env = default_environment()
env['extra'] = ''
graph = []
for row in inputs['artifacts']:
    for literal in row['requires_dist']:
        requirement = Requirement(literal)
        active = requirement.marker is None or requirement.marker.evaluate(env)
        found = artifacts.get(normalize(requirement.name))
        graph.append({'parent': row['key'], 'requirement': literal, 'default_extra_active': active,
                      'candidate_version': found['version'] if found else None,
                      'satisfied_by_candidate': bool(found and requirement.specifier.contains(found['version'])),
                      'metadata_path': row['metadata']['METADATA']['path'],
                      'line': next(i for i, line in enumerate((ROOT / row['metadata']['METADATA']['path']).read_text().splitlines(), 1)
                                   if line == 'Requires-Dist: ' + literal)})
save(HERE / 'metadata-graph.json', graph)
# Recheck the inherited unavailable version against the saved release JSON. This
# is a saved-index-scoped finding, never a new index request or global claim.
release_path = prior / 'index/mkl-service.json'
release = json.loads(release_path.read_text())
tags = set(sys_tags())
files = []
for item in release['urls']:
    compatible = False
    if item['filename'].endswith('.whl'):
        compatible = bool(parse_tag('-'.join(item['filename'][:-4].split('-')[-3:])) & tags)
    files.append({'filename': item['filename'], 'packagetype': item['packagetype'],
                  'compatible_wheel': compatible})
save(HERE / 'mkl-release-audit.json', {'source': str(release_path.relative_to(ROOT)),
     'source_sha256': digest(release_path), 'name': release['info']['name'],
     'version': release['info']['version'], 'files': files,
     'compatible_wheels': sum(r['compatible_wheel'] for r in files),
     'sdists': sum(r['packagetype'] == 'sdist' for r in files)})
task_source = ROOT / 'tests/fixtures/hg_wuvx/source/tasks'
tasks = []
for script in sorted(task_source.glob('*/test.sh')):
    text = script.read_text()
    actual = Path('/mnt/20t/xubuqiang/datasets/terminal-bench') / script.parent.name / 'tests/test.sh'
    tasks.append({'task': script.parent.name, 'path': str(script.relative_to(ROOT)),
                  'sha256': digest(script), 'external_path': str(actual),
                  'external_present': actual.is_file(),
                  'external_sha256': digest(actual) if actual.is_file() else None,
                  'resolver': 'uvx' if re.search(r'^uvx\b', text, re.M) else
                              'uv' if re.search(r'^uv pip install\b', text, re.M) else
                              'pip' if re.search(r'^pip install\b', text, re.M) else 'unclassified'})
assert all(r['sha256'] == r['external_sha256'] for r in tasks)
save(HERE / 'tb-task-source-audit.json', tasks)
native = json.loads((HERE / 'native-results.json').read_text())
rows = []
for name in datasets:
    if name in native:
        status = 'resolved-full-python-metadata-profile' if native[name]['exit_code'] == 0 else 'resolution-failed'
    elif name == 'terminal_bench':
        status = 'one-task-profile-resolved; dataset-incomplete'
    elif prior_payloads.get(name, {}).get('payload_status') == 'no-third-party-payload-required':
        status = 'no-third-party-resolver-needed; not-counted-as-demonstration'
    else:
        status = 'not-demonstrated'
    rows.append({'dataset': name, 'status': status,
                 'prior_imported_distributions': list(prior_payloads[name]['packages']) if name in prior_payloads else None,
                 'runtime_resolver': 'task-specific pip/uv/uvx plus import system' if name == 'terminal_bench'
                                     else 'Python import system; no installer in inspected scoring entry'})
save(HERE / 'dataset-coverage.json', rows)
tb = json.loads((HERE / 'tb3/result.json').read_text())
summary = {'shared_datasets': len(rows), 'bounded_datasets': len(inputs['profiles']) + 1,
           'bounded_profiles_resolved': sum(native[n]['exit_code'] == 0 for n in inputs['profiles']) + int(tb['uvx']['exit_code'] == 0),
           'bounded_profiles_failed': sum(native[n]['exit_code'] != 0 for n in inputs['profiles']),
           'complete_nonempty_python_profiles': sum(r['status'] == 'resolved-full-python-metadata-profile' for r in rows),
           'no_third_party_payload': sum(r['status'].startswith('no-third-party') for r in rows),
           'not_demonstrated_at_dataset_profile_scope': sum(r['status'] != 'resolved-full-python-metadata-profile' for r in rows),
           'tb_demonstrated_tasks': int(tb['uvx']['exit_code'] == 0), 'tb_task_sources': len(tasks),
           'tb_task_resolvers': {r: sum(t['resolver'] == r for t in tasks) for r in ['uvx', 'uv', 'pip', 'unclassified']},
           'candidate_wheels': len(inputs['artifacts']), 'candidate_bytes': sum(r['bytes'] for r in inputs['artifacts']),
           'active_unsatisfied_metadata_edges': [r for r in graph if r['default_extra_active'] and not r['satisfied_by_candidate']],
           'meaning': 'Python metadata reconstruction only, not installed-host ABI custody or production closure'}
save(HERE / 'summary.json', summary)
print(json.dumps({k: v for k, v in summary.items() if k != 'active_unsatisfied_metadata_edges'}, sort_keys=True))
