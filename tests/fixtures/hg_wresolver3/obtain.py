"""Extend the prior method to finite actor-workdir Python roots, with extras.

Only exact observed versions; prior resolver candidates remain unchanged.
Wheel bytes are rehashed, dependency markers/extras reach a fixed point, and
real pip independently decides satisfiability in probe.py. No package imports.
"""
import importlib.metadata as installed
import json
from pathlib import Path
import shutil
import subprocess
import sys
import sysconfig
import tempfile

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.utils import parse_wheel_filename

from common import HERE, ROOT, digest, save, run
from artifacts import normalize, fetch, inspect, records, tags, rank

assert not (HERE / 'inputs.json').exists(), 'Never overwrite evidence'
prior = json.loads((ROOT / 'tests/fixtures/hg_wresolver2/inputs.json').read_text())
corpus = json.loads((ROOT / 'tests/fixtures/hg_wwheelhouse/manifest.json').read_text())['artifacts']
resume = (HERE / 'progress.json').exists()
progress = json.loads((HERE / 'progress.json').read_text()) if resume else {}
work = Path(next(iter(progress['artifacts'].values()))['path']).parent.parent if resume else Path(tempfile.mkdtemp(prefix='hg-wresolver3-payloads-'))
wheels = work / 'wheels'
wheels.mkdir(exist_ok=True)
if not resume: save(HERE / 'registry-before.json', json.loads((ROOT / 'docs/dataset-blockers.json').read_text()))
if not resume: save(HERE / 'target.json', {'executable': sys.executable, 'sha256': digest(sys.executable),
     'sys_version': sys.version, 'SOABI': sysconfig.get_config_var('SOABI'),
     'platform': sysconfig.get_platform(), 'tags': list(map(str, tags)),
     'baseline_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()})
profiles = {
    'alfworld': ['alfworld==0.4.2', 'textworld==1.7.0'],
    'gsm8k': ['pyarrow==23.0.0'],
    'hotpotqa': ['pyarrow==23.0.0'],
    'triviaqa': ['pyarrow==23.0.0'],
    'livecodebench': ['numpy==1.26.4'],
}
if not resume: save(HERE / 'selection.json', {'profiles': profiles,
     'selection_rule': 'All remaining actor-workdir datasets with finite adapter-level nonempty Python roots, excluding DS-1000 task-context execution graph. Keep snapshot/service and task-specific profiles as separate gaps.',
     'version_policy': 'Adapter declarations for ALFWorld/TextWorld and GSM8K/TriviaQA pyarrow; exact host-observed pyarrow for shared HotpotQA reader and numpy for LiveCodeBench. Preserve prior graph candidates. No extras added except those required transitively.',
     'budget': {'max_artifacts': 120, 'max_total_payload_bytes': 320 * 1024 * 1024,
                'max_http_artifact_bytes': 64 * 1024 * 1024, 'per_http_timeout_seconds': 45}})

# Recheck retained bytes, never modify inherited evidence or payloads.
records.update(progress.get('artifacts', {}))
for old in ([] if resume else prior['artifacts']):
    source = Path(old['path'])
    assert digest(source) == old['sha256']
    dest = wheels / source.name
    shutil.copyfile(source, dest)
    inspect(dest, {'kind': 'retained-w-resolver2', 'source': str(source), 'source_sha256': digest(source)})

observed = json.loads((HERE / 'observed-candidates.json').read_text()) if resume else {}
environment = default_environment()
pending = [Requirement(r) for roots in profiles.values() for r in roots]
extras = {}
visited = set()
edges = []
while pending:
    requested = pending.pop(0)
    assert not requested.url, 'URL requirements require explicit handling'
    key = normalize(requested.name)
    extras.setdefault(key, set()).update(requested.extras)
    state = (key, tuple(sorted(extras[key])))
    if state in visited:
        continue
    visited.add(state)
    if key not in records:
        assert len(records) < 120
        distribution = installed.distribution(key)
        version = distribution.version
        observed[key] = {'version': version, 'metadata': distribution.read_text('METADATA'),
                         'wheel': distribution.read_text('WHEEL')}
        save(HERE / 'observed-candidates.json', observed)
        inherited = corpus.get(key)
        if inherited and inherited.get('status') == 'obtained-wheel' and inherited['version'] == version:
            source = Path(inherited['local_path'])
            assert digest(source) == inherited['sha256']
            dest = wheels / source.name
            shutil.copyfile(source, dest)
            inspect(dest, {'kind': 'retained-w-wheelhouse', 'source': str(source), 'source_sha256': digest(source)})
        elif (Path('/tmp/hg-wwheelhouse-payloads-e5uywviu') / (key.replace('-', '_') + '-' + version + '-py3-none-any.whl')).is_file():
            source = Path('/tmp/hg-wwheelhouse-payloads-e5uywviu') / (key.replace('-', '_') + '-' + version + '-py3-none-any.whl')
            receipt = ROOT / 'tests/fixtures/hg_wwheelhouse/offline' / ('retry-build-' + key + '.stdout.txt')
            import re
            expected = re.search(r'sha256=([a-f0-9]{64})', receipt.read_text()).group(1)
            assert digest(source) == expected
            dest = wheels / source.name
            shutil.copyfile(source, dest)
            inspect(dest, {'kind': 'retained-local-build', 'source': str(source), 'source_sha256': digest(source),
                           'build_stdout': str(receipt.relative_to(ROOT)), 'build_stdout_sha256': digest(receipt)})
        else:
            url = f'https://pypi.org/pypi/{key}/{version}/json'
            body = fetch(url, HERE / 'index' / f'{key}-{version}.json', 8 * 1024 * 1024)
            payload = json.loads(body)
            compatible = []
            for artifact in payload['urls']:
                if artifact['packagetype'] != 'bdist_wheel' or artifact.get('yanked'):
                    continue
                matches = parse_wheel_filename(artifact['filename'])[3] & rank.keys()
                if matches:
                    compatible.append((min(rank[t] for t in matches), artifact['filename'], artifact))
            save(HERE / 'index' / f'{key}-{version}-selection.json',
                 {'url': url, 'version': version, 'compatible_wheels': [r[1] for r in sorted(compatible)],
                  'sdists': [r['filename'] for r in payload['urls'] if r['packagetype'] == 'sdist']})
            assert compatible, f'No compatible exact wheel: {key}=={version}; investigate other sources'
            artifact = sorted(compatible)[0][2]
            dest = wheels / artifact['filename']
            fetch(artifact['url'], dest, 64 * 1024 * 1024)
            shutil.move(str(dest.with_name(dest.name + '.http.json')), HERE / 'index' / (dest.name + '.http.json'))
            assert digest(dest) == artifact['digests']['sha256']
            assert dest.stat().st_size == artifact['size']
            record = inspect(dest, {'kind': 'pypi-exact-version', 'index_url': url,
                             'url': artifact['url'], 'advertised_sha256': artifact['digests']['sha256']})
            assert record['version'] == version
    assert requested.specifier.contains(records[key]['version']), (str(requested), records[key]['version'])
    for literal in records[key]['requires_dist']:
        requirement = Requirement(literal)
        contexts = [''] + sorted(extras[key])
        active = any(requirement.marker is None or requirement.marker.evaluate(dict(environment, extra=e)) for e in contexts)
        edges.append({'parent': key, 'parent_extras': sorted(extras[key]), 'requirement': literal, 'active': active})
        if active:
            pending.append(requirement)
    save(HERE / 'progress.json', {'visited': sorted([list(s) for s in visited]),
         'queued': list(map(str, pending)), 'artifacts': records, 'edges': edges})
    assert sum(r['bytes'] for r in records.values()) <= 320 * 1024 * 1024

for edge in edges:
    if edge['active']:
        req = Requirement(edge['requirement'])
        edge['candidate_version'] = records[normalize(req.name)]['version']
        edge['satisfied'] = req.specifier.contains(edge['candidate_version'])
save(HERE / 'graph.json', edges)
for name, roots in profiles.items():
    directory = HERE / 'profiles' / name
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'roots.in').write_text(''.join(r + '\n' for r in roots))
    (directory / 'constraints.txt').write_text(''.join(f"{r['name']}=={r['version']}\n" for r in sorted(records.values(), key=lambda r: r['key'])))
save(HERE / 'inputs.json', {'wheel_directory': str(wheels), 'payload_directory': str(work),
     'artifacts': list(records.values()), 'profiles': profiles,
     'graph_satisfied': all(e.get('satisfied', True) for e in edges)})
run('wheel-sha256sum', ['sha256sum', *[r['path'] for r in records.values()]])
print(json.dumps({'artifacts': len(records), 'bytes': sum(r['bytes'] for r in records.values()),
      'newly_downloaded': [r['key'] for r in records.values() if r['provenance']['kind'] == 'pypi-exact-version'],
      'graph_satisfied': all(e.get('satisfied', True) for e in edges), 'payload_directory': str(work)}, sort_keys=True))
