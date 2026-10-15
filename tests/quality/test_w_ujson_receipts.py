"""Audit immutable runtime receipts without containers, network or dataset reads."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/fixtures/hg_wujson'
if not (FIXTURE / 'SHA256SUMS').is_file():
    pytest.skip("tests/fixtures/hg_wujson is internal (see .gitignore) and absent from this clone",
                allow_module_level=True)

RUNTIME = FIXTURE / 'runtime-v9'
WHEEL_SHA256 = 'f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1'


def read(path):
    return json.loads((FIXTURE / path).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_manifest_covers_every_receipt_and_distribution_input():
    manifest = {}
    for line in (FIXTURE / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        assert name not in manifest
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        manifest[name] = digest
        assert sha(FIXTURE / name) == digest, name
    actual = {str(p.relative_to(FIXTURE)) for p in FIXTURE.rglob('*') if p.is_file()}
    assert set(manifest) == actual - {'SHA256SUMS'}


def test_image_manifest_and_denied_container_bind_the_successful_receipts():
    summary = read('provenance.json')
    index = read('base-manifest-proxy.stdout.txt')
    assert summary['base_image'].endswith('sha256:' + sha(FIXTURE / 'base-manifest-proxy.stdout.txt'))
    platform = next(m for m in index['manifests']
                    if m.get('platform') == {'architecture': 'amd64', 'os': 'linux'})
    assert platform['digest'] == summary['base_amd64_manifest']
    assert platform['digest'] == 'sha256:' + sha(FIXTURE / 'base-amd64-manifest.stdout.txt')
    image = read('deployment-v6-inspect.stdout.txt')[0]
    assert summary['deployment_image'] in image['RepoDigests']
    assert image['Architecture'] == 'amd64' and image['Os'] == 'linux'
    for when in ('before', 'after'):
        container = read(f'runtime-v9-inspect-{when}.stdout.txt')[0]
        assert container['Image'] == image['Id']
        assert container['HostConfig']['NetworkMode'] == 'none'
        assert container['HostConfig']['ReadonlyRootfs'] is True
        assert container['HostConfig']['CapDrop'] == ['ALL']
    assert container['State']['ExitCode'] == 0 and not container['State']['OOMKilled']
    assert read('runtime-v9-start.command.json')['returncode'] == 0
    assert (FIXTURE / 'runtime-v9-cleanup-check.stdout.txt').read_text() == ''
    assert (FIXTURE / 'final-owned-container-check.stdout.txt').read_text() == ''
    denial = read('runtime-v9/network-denial.json')
    assert denial['passed'] and denial['interfaces'] == ['lo']
    assert denial['errno_name'] == 'ENETUNREACH'


def test_exact_wheel_installed_members_and_notices_are_in_the_image(site_archive):
    wheel = next((FIXTURE / 'deployment-v6').glob('*.whl'))
    assert sha(wheel) == WHEEL_SHA256
    pip = read('runtime-v9/pip-install-report.json')
    assert len(pip['install']) == 1
    assert pip['install'][0]['download_info']['archive_info']['hashes']['sha256'] == WHEEL_SHA256
    native = read('runtime-v9/native-import.json')
    deployed = read('runtime-v9/deployed-native-import.json')
    assert native['passed'] and deployed['passed']
    assert native['ujson'] == deployed['ujson'] == '5.10.0'
    assert native['glibc'][0] == 'glibc'
    assert native['python'].startswith('3.12.') and native['machine'] == 'x86_64'
    with zipfile.ZipFile(wheel) as archive:
        names = {n for n in archive.namelist() if not n.endswith(('/', '/RECORD'))}
        assert set(native['installed_members']) == names
        for name in names:
            expected = hashlib.sha256(archive.read(name)).hexdigest()
            assert native['installed_members'][name]['sha256'] == expected
            assert deployed['installed_members'][name]['sha256'] == expected
    for name in ('ujson-LICENSE.txt', 'double-conversion-LICENSE'):
        original = site_archive('/site/b6-blocker-evidence/ujson-supplemental-notices/' + name)
        distributed = FIXTURE / 'deployment-v6/notices' / name
        assert original.read_bytes() == distributed.read_bytes()
        path = '/usr/local/share/licenses/hg-wujson/' + name
        assert native['notices'][path] == deployed['notices'][path] == sha(original)


def test_recursive_symbols_include_python_tls_and_kernel_providers():
    files = read('runtime-v9/providers/files.json')
    symbols = read('runtime-v9/providers/symbols.json')
    summary = read('runtime-v9/providers-summary.json')
    expected_undefined = set()
    sonames, needed = set(), set()
    for filename, identity in files.items():
        if filename == '[vdso]':
            assert identity['sha256'] == sha(RUNTIME / 'providers/vdso.so')
            continue
        label = Path(filename).name
        elf = (RUNTIME / 'providers' / (label + '.readelf.stdout.txt')).read_text()
        ldd = (RUNTIME / 'providers' / (label + '.ldd.stdout.txt')).read_text()
        assert 'not found' not in ldd
        sonames.update(re.findall(r'\(SONAME\).*\[(.*?)\]', elf))
        needed.update(identity['needed'])
        for binding, name in re.findall(r'\s\d+:\s+\S+\s+\d+\s+\S+\s+(GLOBAL|WEAK)\s+\S+\s+UND\s+(\S+)', elf):
            expected_undefined.add((filename, name, binding))
    assert needed <= sonames
    assert {(s['consumer'], s['symbol'], s['binding']) for s in symbols} == expected_undefined
    assert summary['undefined_symbols_checked'] == len(symbols)
    assert summary['strong_resolution_failures'] == 0 and summary['passed']
    for symbol in symbols:
        if 'error' in symbol:
            assert symbol['binding'] == 'WEAK'
        else:
            assert symbol['provider_sha256'] == files[symbol['provider']]['sha256']
    assert any('tls_block_address' in s for s in symbols)
    assert any(s.get('provider') == '[vdso]' for s in symbols)
    trace = (RUNTIME / 'loader-debug.stderr.txt').read_text()
    module = read('runtime-v9/native-import.json')['module']
    bindings = [line for line in trace.splitlines() if f'binding file {module} [0] to ' in line]
    for symbol in symbols:
        if symbol['consumer'] == module and symbol['binding'] == 'GLOBAL':
            name = symbol['symbol'].partition('@')[0]
            assert any(f"normal symbol `{name}'" in line for line in bindings), name


def test_unchanged_synthetic_evaluators_and_remaining_custody_gap():
    result = read('runtime-v9/synthetic-evaluator.json')
    assert result['passed'] and len(result['results']) == 2
    for execution in result['results']:
        filename = Path(execution['argv'][3]).name
        upstream = ROOT / 'tests/fixtures/twowikimultihopqa_upstream_codex197' / filename
        assert execution['source_sha256'] == sha(upstream)
        assert execution['returncode'] == 0
        raw = json.loads((RUNTIME / 'synthetic' / (filename + '.stdout.txt')).read_text())
        assert raw == execution['metrics']
        assert len(raw) == 16 and set(raw.values()) == {100.0}
    summary = read('provenance.json')
    assert summary['runtime_checks_passed'] and summary['notices_in_distribution']
    assert summary['original_wheel_source_build_attested'] is False
    assert summary['blocker_closed'] is summary['production_authorized'] is False
    assert (FIXTURE / 'pypi-build-attestation.stdout.txt').read_text() == '404\n'
    assert 'No provenance available' in (FIXTURE / 'pypi-build-attestation.body').read_text()
    document = json.loads((ROOT / 'registry/dataset-blockers.json').read_text())
    dataset = next(d for d in document['datasets'] if d['dataset'] == 'twowikimultihopqa')
    blocker = next(b for b in dataset['blockers'] if b['id'] == 'ujson-native-offline-closure')
    assert blocker['status'] == 'external'
    assert {'kind': 'external-reference', 'path': '/site/w-ujson-receipts.md',
            'locator': '## Remaining source/build custody requirement'} in blocker['evidence']
