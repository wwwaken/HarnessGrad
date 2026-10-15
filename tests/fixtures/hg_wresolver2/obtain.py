"""Acquire exact observed missing versions from PyPI; retain all HTTP bodies.

Existing w-resolver constraints are immutable. Installed metadata only guides
candidate selection; satisfaction and hashes are verified from wheel bytes.
No sdists, builds, extras, language models or dataset imports are executed.
"""
import email
import importlib.metadata as installed
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.tags import sys_tags
from packaging.utils import parse_wheel_filename

from common import HERE, ROOT, digest, save, run


def normalize(name):
    return re.sub(r'[-_.]+', '-', name).lower()


def fetch(url, dest, limit):
    assert not dest.exists(), dest
    started = time.monotonic()
    request = urllib.request.Request(url, headers={'User-Agent': 'HarnessGrad-w-resolver2/1'})
    try:
        response = urllib.request.urlopen(request, timeout=45)
    except urllib.error.HTTPError as exc:
        response = exc
    with response:
        body = response.read(limit + 1)
        assert len(body) <= limit, 'HTTP body budget exceeded'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(body)
        record = {'request_url': url, 'response_url': response.url,
                  'status': response.status, 'headers': dict(response.headers),
                  'bytes': len(body), 'sha256': digest(dest),
                  'elapsed_seconds': time.monotonic() - started}
        save(dest.with_name(dest.name + '.http.json'), record)
    assert record['status'] == 200, record
    return body


assert not (HERE / 'inputs.json').exists(), 'Never overwrite an evidence capture'
prior = json.loads((ROOT / 'tests/fixtures/hg_wresolver/inputs.json').read_text())
old_manifest = json.loads((ROOT / 'tests/fixtures/hg_wwheelhouse/manifest.json').read_text())
work = Path(tempfile.mkdtemp(prefix='hg-wresolver2-payloads-'))
wheels = work / 'wheels'
wheels.mkdir()
save(HERE / 'registry-before.json', json.loads((ROOT / 'docs/dataset-blockers.json').read_text()))
tags = list(sys_tags())
save(HERE / 'target.json', {'executable': sys.executable, 'sha256': digest(sys.executable),
     'sys_version': sys.version, 'SOABI': sysconfig.get_config_var('SOABI'),
     'platform': sysconfig.get_platform(), 'tags': list(map(str, tags)),
     'baseline_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()})
rank = {tag: i for i, tag in enumerate(tags)}
records = {}


def inspect(path, provenance):
    with zipfile.ZipFile(path) as archive:
        members = {}
        for suffix in ['METADATA', 'WHEEL']:
            member = next(n for n in archive.namelist() if n.endswith('.dist-info/' + suffix))
            data = archive.read(member)
            if suffix == 'METADATA':
                meta = email.message_from_bytes(data)
                key = normalize(meta['Name'])
            dest = HERE / 'metadata' / key / suffix
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            members[suffix] = {'member': member, 'path': str(dest.relative_to(ROOT)), 'sha256': digest(dest)}
    wheel_tags = parse_wheel_filename(path.name)[3]
    assert wheel_tags & rank.keys(), path
    record = {'key': key, 'name': meta['Name'], 'version': meta['Version'],
              'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path),
              'tags': sorted(map(str, wheel_tags)), 'matching_tags': sorted(map(str, wheel_tags & rank.keys())),
              'requires_python': meta.get('Requires-Python'),
              'requires_dist': meta.get_all('Requires-Dist', []), 'metadata': members,
              'provenance': provenance}
    records[key] = record
    return record


for old in prior['artifacts']:
    source = Path(old['path'])
    assert digest(source) == old['sha256']
    dest = wheels / source.name
    shutil.copyfile(source, dest)
    inspect(dest, {'kind': 'retained-w-resolver', 'source': str(source), 'source_sha256': digest(source)})

roots = {'jericho': 'jericho', 'reasoning_gym': 'reasoning-gym', 'spreadsheetbench': 'openpyxl'}
environment = default_environment()
environment['extra'] = ''
queue = list(roots.values())
visited = set()
observed = {}
edges = []
while queue:
    key = queue.pop(0)
    if key in visited:
        continue
    visited.add(key)
    if key not in records:
        assert len(records) < 100, 'artifact-count budget'
        distribution = installed.distribution(key)
        version = distribution.version
        observed[key] = {'version': version, 'metadata': distribution.read_text('METADATA'),
                         'wheel': distribution.read_text('WHEEL')}
        save(HERE / 'observed-candidates.json', observed)
        inherited = old_manifest['artifacts'].get(key)
        if inherited and inherited.get('status') == 'obtained-wheel' and inherited['version'] == version:
            source = Path(inherited['local_path'])
            assert digest(source) == inherited['sha256']
            dest = wheels / source.name
            shutil.copyfile(source, dest)
            inspect(dest, {'kind': 'retained-w-wheelhouse', 'source': str(source), 'source_sha256': digest(source)})
        else:
            url = f'https://pypi.org/pypi/{key}/{version}/json'
            body = fetch(url, HERE / 'index' / f'{key}-{version}.json', 8 * 1024 * 1024)
            payload = json.loads(body)
            compatible = []
            for artifact in payload['urls']:
                if artifact['packagetype'] != 'bdist_wheel' or artifact.get('yanked'):
                    continue
                artifact_tags = parse_wheel_filename(artifact['filename'])[3]
                matches = artifact_tags & rank.keys()
                if matches:
                    compatible.append((min(rank[t] for t in matches), artifact['filename'], artifact))
            save(HERE / 'index' / f'{key}-{version}-selection.json',
                 {'index': 'https://pypi.org/', 'url': url, 'version': version,
                  'compatible_wheels': [r[1] for r in sorted(compatible)], 'sdists':
                  [r['filename'] for r in payload['urls'] if r['packagetype'] == 'sdist']})
            assert compatible, f'No compatible exact wheel: {key}=={version}; investigate other sources'
            artifact = sorted(compatible)[0][2]
            dest = wheels / artifact['filename']
            fetch(artifact['url'], dest, 64 * 1024 * 1024)
            shutil.move(str(dest.with_name(dest.name + '.http.json')),
                        HERE / 'index' / (dest.name + '.http.json'))
            assert digest(dest) == artifact['digests']['sha256']
            assert dest.stat().st_size == artifact['size']
            record = inspect(dest, {'kind': 'pypi-exact-version', 'index_url': url,
                      'url': artifact['url'], 'advertised_sha256': artifact['digests']['sha256']})
            assert record['version'] == version
    for literal in records[key]['requires_dist']:
        requirement = Requirement(literal)
        active = requirement.marker is None or requirement.marker.evaluate(environment)
        edges.append({'parent': key, 'requirement': literal, 'active': active})
        if active:
            assert not requirement.extras and not requirement.url, 'Explicit handling required for extras/URLs'
            child = normalize(requirement.name)
            queue.append(child)
    save(HERE / 'progress.json', {'visited': sorted(visited), 'queued': queue, 'artifacts': records, 'edges': edges})
    assert sum(r['bytes'] for r in records.values()) <= 256 * 1024 * 1024, 'total payload budget'

for edge in edges:
    if edge['active']:
        req = Requirement(edge['requirement'])
        child = records[normalize(req.name)]
        edge['candidate_version'] = child['version']
        edge['satisfied'] = req.specifier.contains(child['version'])
save(HERE / 'graph.json', edges)
for name in roots:
    directory = HERE / 'profiles' / name
    directory.mkdir(parents=True, exist_ok=True)
    for filename in ['roots.in', 'constraints.txt']:
        shutil.copyfile(ROOT / 'tests/fixtures/hg_wresolver/profiles' / name / filename, directory / filename)
    with (directory / 'constraints.txt').open('a') as stream:
        stream.write(''.join(f"{records[k]['name']}=={records[k]['version']}\n" for k in sorted(records.keys() - {r['key'] for r in prior['artifacts']})))
save(HERE / 'inputs.json', {'wheel_directory': str(wheels), 'payload_directory': str(work),
     'artifacts': list(records.values()), 'profiles': roots,
     'budget': {'max_artifacts': 100, 'max_total_payload_bytes': 256 * 1024 * 1024,
                'max_http_artifact_bytes': 64 * 1024 * 1024, 'per_http_timeout_seconds': 45},
     'candidate_policy': 'Preserve all prior constraints; exact host-observed versions for newly required defaults; no extras, sdists or substitutes',
     'graph_satisfied': all(e.get('satisfied', True) for e in edges)})
run('wheel-sha256sum', ['sha256sum', *[r['path'] for r in records.values()]])
print(json.dumps({'artifacts': len(records), 'bytes': sum(r['bytes'] for r in records.values()),
                  'newly_downloaded': sum(r['provenance']['kind'] == 'pypi-exact-version' for r in records.values()),
                  'graph_satisfied': all(e.get('satisfied', True) for e in edges), 'payload_directory': str(work)}))
