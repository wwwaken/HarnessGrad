"""Validate retained evidence and summarize the bounded non-reproduction result."""
import hashlib
import json
from pathlib import Path

packet = Path(__file__).resolve().parents[1]
read = lambda p: json.loads((packet / p).read_text())
c = read('comparison/comparison.json')
source = read('source-verification.json')
expected = 'f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1'
assert c['wheels']['published']['sha256'] == expected
assert source['passed'] and source['blob_count'] == 102
for label in ('published', 'rebuilt'):
    w = c['wheels'][label]
    actual = next((packet / ('comparison/' + label)).glob('*.so'))
    item = next(m for m in c['members'] if m['member'].endswith('.so'))
    assert hashlib.sha256(actual.read_bytes()).hexdigest() == item[label + '_sha256']
    assert len(c['symbols'][label]['double_conversion_defined']) == 53
    assert not c['symbols'][label]['double_conversion_undefined']
assert set(c['symbols']['published']['double_conversion_defined']) == set(c['symbols']['rebuilt']['double_conversion_defined'])
assert c['file_member_sets_equal'] and not c['whole_wheel_equal']
assert sum(m['equal'] for m in c['members']) == 3

runtimes = {}
for mode in ('build', 'comparison', 'published-runtime', 'rebuilt-runtime'):
    assert read(mode + '/network-denial.json')['passed']
    for when in ('before', 'after'):
        obj = read('commands/' + mode + '-inspect-' + when + '.stdout.txt')[0]
        assert obj['HostConfig']['NetworkMode'] == 'none'
        assert obj['HostConfig']['ReadonlyRootfs']
        assert obj['Config']['Image'] == 'python@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b'
        assert obj['ImageManifestDescriptor']['digest'] == 'sha256:edd0b3ec946cc68bd20e39480bd03929016d0fb6254cbf870cd3bc55ea25116d'
        if when == 'after':
            assert obj['State']['ExitCode'] == 0 and not obj['State']['OOMKilled']
    assert not (packet / 'commands' / (mode + '-cleanup.stdout.txt')).read_text().strip()
    if mode.endswith('-runtime'):
        native = read(mode + '/native-import.json')
        synthetic = read(mode + '/synthetic-evaluator.json')
        provider = read(mode + '/providers-summary.json')
        assert native['passed'] and synthetic['passed'] and provider['passed']
        assert provider['strong_resolution_failures'] == 0
        assert len(native['notices']) == 2
        assert len(synthetic['results']) == 2
        for result in synthetic['results']:
            assert result['returncode'] == 0 and len(result['metrics']) == 16 and set(result['metrics'].values()) == {100.0}
        runtimes[mode] = {'wheel_sha256': native['wheel_sha256'],
                          'undefined_symbols_checked': provider['undefined_symbols_checked'],
                          'strong_resolution_failures': provider['strong_resolution_failures'],
                          'optional_weak_unresolved': len(provider['optional_weak_unresolved']),
                          'synthetic_evaluators_passed': len(synthetic['results'])}
for file in (packet / 'commands').glob('*.command.json'):
    assert json.loads(file.read_text())['returncode'] == 0, file
summary = {'source_blobs_verified': source['blob_count'], 'source_root_tree': source['reconstructed_root_tree'],
    'published_wheel_sha256': c['wheels']['published']['sha256'], 'rebuilt_wheel_sha256': c['wheels']['rebuilt']['sha256'],
    'file_member_set_equal': True, 'identical_file_members': 3, 'file_members_each': len(c['members']),
    'wheel_reproduced': False, 'double_conversion_defined_symbols_each': 53,
    'double_conversion_link_form': 'implementation embedded in extension; no undefined double-conversion imports or double-conversion DT_NEEDED',
    'producer_vendored_vs_external_static_selection_authenticated': False,
    'original_wheel_source_build_custody_authenticated': False,
    'blocker_closed': False, 'status': 'external', 'runtimes': runtimes,
    'scope': 'source rebuild and fabricated controls only; no benchmark/model/GPU/endpoint; no H0 authorization'}
(packet / 'assessment.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
