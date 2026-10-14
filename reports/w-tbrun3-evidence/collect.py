"""Summarize persisted observations; this does not execute or score a task."""
import hashlib
import json
import pathlib
import shutil
import subprocess
import tarfile

ROOT = pathlib.Path('/tmp/hg-tbrun3')
OUT = ROOT / 'reports/w-tbrun3-evidence'
EXECUTION = 'w-tbrun3-terminal-bench-20261014T194115Z-7eab177b'
REFUSED = 'w-tbrun3-terminal-bench-20261014T194038Z-a228b8e2'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2) + '\n')


run = ROOT / 'runs' / EXECUTION
evidence = ROOT / 'runs' / (EXECUTION + '-launch-evidence')
meta = read(run / 'run_meta.json')
receipt = read(run / 'diagnostic_receipt.json')
work = pathlib.Path(meta['workspace'])
command = ['git', '-C', str(work), 'rev-parse', 'HEAD^{tree}']
tree = subprocess.run(command, capture_output=True, text=True, check=True)
write('harness-tree-observation.json', dict(argv=command, returncode=tree.returncode,
                                         stdout=tree.stdout, stderr=tree.stderr))
provenance = dict(
    run_id=EXECUTION,
    platform=meta['platform'],
    dataset_commit=read(evidence / 'dataset-commit.json')['stdout'].strip(),
    split=read(evidence / 'selection.json')['split'],
    harness_tree_sha=tree.stdout.strip(),
    harness_files={str(p): sha(p) for p in sorted(work.iterdir()) if p.is_file()},
    selected_source_files={str(p): sha(p) for p in (
        evidence / 'selected-task.toml', evidence / 'selected-Dockerfile',
        evidence / 'selected-verifier-test.sh')},
    harness_manifest_path=str(work / 'harness.json'),
    harness_manifest_sha256=sha(work / 'harness.json'),
    run_manifest_sha256=receipt['context']['hashes']['manifest'],
    model_weights_sha256=receipt['context']['hashes']['model'],
    endpoint=meta['config']['agent']['base_url'],
    model=meta['config']['agent']['model'],
    note='Post-execution hashes of real files, not a launch-bound run manifest or model weight identity.')
write('provenance.json', provenance)

roles = {}
for path in sorted(evidence.glob('container-inspect-*.json')):
    captured = read(path)
    if captured['returncode']:
        continue
    for c in json.loads(captured['stdout']):
        role = 'verifier' if c['Name'].startswith('/hg-verify-') else 'agent'
        row = dict(source=str(path), id=c['Id'], name=c['Name'], image=c['Image'],
                   state=c['State'], size_rw=c.get('SizeRw'),
                   limits={k: c['HostConfig'].get(k) for k in (
                       'NanoCpus', 'Memory', 'MemorySwap', 'PidsLimit', 'ReadonlyRootfs')},
                   networks=c['NetworkSettings']['Networks'], mounts=c['Mounts'])
        roles.setdefault(role, dict(first=row, last=row))['last'] = row
write('resource-observations.json', dict(
    roles=roles, statistics_paths=[str(p) for p in sorted(evidence.glob('container-stats-*.json'))],
    declared_limits=receipt['context']['limits'],
    runtime_admission_receipt=None,
    note='Raw Docker observations and sampled usage; no quota, peak usage, or trusted runtime admission attestation.'))

snapshots = []
for path in sorted(evidence.glob('snapshot-inspect-*.json')):
    captured = read(path)
    if captured['returncode'] == 0:
        for item in json.loads(captured['stdout']):
            snapshots.append(dict(source=str(path), id=item['Id'], repo_tags=item['RepoTags'],
                                  size=item['Size'], parent=item.get('Parent')))
write('snapshot-observations.json', dict(observations=snapshots,
    snapshot_admission_receipt=receipt['snapshot'], lifecycle=receipt['lifecycle'],
    note='Actual Docker snapshot identities; driver snapshot admission remains unknown.'))

cleanup = {name: read(evidence / name) for name in (
    'containers-after.json', 'networks-after.json', 'snapshot-images-after.json',
    'network-exact-after.json', 'snapshot-exact-after.json')}
write('cleanup-observations.json', dict(observations=cleanup,
    driver_cleanup=receipt['cleanup'], cleanup_admission_receipt=None,
    note='Owned-label listings and exact-object absence probes, not a lease release or admission attestation.'))

reward_paths = sorted(evidence.glob('verifier-reward.txt-*'))
presence = {name: (run / name).exists() for name in (
    'staged_plan.json', 'diagnostic_receipt.json', 'diagnostic_execution.json',
    'run_meta.json', 'events.jsonl', 'curve.jsonl')}
write('result.json', dict(
    run_id=EXECUTION, real_task_executed=True,
    driver_returncode=read(evidence / 'launch-observation.json')['returncode'],
    valid_verifier_score=None, raw_reward_files={str(p): p.read_text() for p in reward_paths},
    verdicts=read(run / 'diagnostic_execution.json')['verdicts'],
    invalid=read(run / 'diagnostic_execution.json')['invalid'],
    coverage=receipt['coverage'], score=receipt['score'], enforcement=receipt['enforcement'],
    driver_artifact_presence=presence, blocker_closed=False,
    note='The reward file exists but required CTRF evidence does not; no valid score is inferred.'))

originals = [ROOT / 'runs' / name for name in (
    REFUSED, REFUSED + '-launch-evidence', EXECUTION, EXECUTION + '-launch-evidence')]
inventory = []
for directory in originals:
    for p in sorted(directory.rglob('*')):
        if p.is_file():
            inventory.append(dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p)))
write('artifact-inventory.json', dict(files=inventory))

# Complete byte-for-byte review archive; original directories remain untouched.
archive = OUT / 'run-artifacts.tar.gz'
with tarfile.open(archive, 'w:gz') as tar:
    for directory in originals:
        tar.add(directory, arcname=str(directory.relative_to(ROOT)))
write('archive-sha256.json', dict(path=str(archive), sha256=sha(archive),
                                bytes=archive.stat().st_size,
                                original_directories=[str(p) for p in originals]))

# Small direct review copies keep the important raw artifacts readable without extraction.
for label, directory in (('execution', run), ('refused', ROOT / 'runs' / REFUSED)):
    dest = OUT / label
    dest.mkdir(exist_ok=True)
    for p in directory.rglob('*'):
        if p.is_file():
            target = dest / p.relative_to(directory)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
print(json.dumps(read(OUT / 'result.json'), indent=2))
