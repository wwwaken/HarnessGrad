#!/usr/bin/env python3
"""Bounded real-Docker regressions, before/after; no scorer, model or run access.

Before loads the retained exact baseline sources, without changing the checkout.
Transport alone is wrapped to retain exact command output and metadata.
"""
import datetime
import hashlib
import gzip
import tarfile
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
MODE = sys.argv[1]
assert MODE in ('before', 'after')
if MODE == 'before':
    def load(name, relative):
        spec = importlib.util.spec_from_file_location(name, HERE / 'before' / relative)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    container = load('wsnapfix_before_container', 'eval/containers/container.py')
    verifier = load('wsnapfix_before_verifier', 'eval/verification/verifier.py')
    verifier.container_mod = container
else:
    from eval.containers import container
    from eval.verification import verifier

RUN = 'w-snapfix-' + MODE + '-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
RAW = HERE / RUN
RAW.mkdir()
LIMITS = {'cpus': '1', 'memory': '256m', 'pids': 64}
BASE = json.loads((ROOT / 'tests/fixtures/hg_wsnap/summary.json').read_bytes())['base_id']
seq = 0
containers, images, tags, networks = [], [], [], []
summary = dict(mode=MODE, run_id=RUN, limits=LIMITS, commands=[], cleanup=[], benchmark_scores=0,
               model_gpu_endpoint_calls=0, source_sha256={})
for relative in ('eval/containers/container.py', 'eval/verification/verifier.py'):
    path = HERE / 'before' / relative if MODE == 'before' else ROOT / relative
    summary['source_sha256'][relative] = hashlib.sha256(path.read_bytes()).hexdigest()


def record(label, argv, timeout=120, check=True):
    global seq
    seq += 1
    stem = RAW / f'{seq:03d}-{label}'
    info = dict(argv=list(map(str, argv)), cwd=str(ROOT), timeout_s=timeout,
                started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        proc = subprocess.run(info['argv'], capture_output=True, timeout=timeout)
    except BaseException as exc:
        info['exception'] = repr(exc)
        stem.with_suffix('.command.json').write_text(json.dumps(info, indent=2) + '\n')
        raise
    info['returncode'] = proc.returncode
    stem.with_suffix('.command.json').write_text(json.dumps(info, indent=2) + '\n')
    stem.with_suffix('.stdout.txt').write_bytes(proc.stdout)
    stem.with_suffix('.stderr.txt').write_bytes(proc.stderr)
    summary['commands'].append(dict(stem=stem.name, returncode=proc.returncode))
    if check and proc.returncode:
        raise RuntimeError(f'{stem.name}: {proc.stderr.decode(errors="replace")}')
    return proc


def transport(*args, timeout=120):
    if args[0] == 'create':
        containers.append(args[args.index('--name') + 1])
    p = record('helper-' + args[0], ['docker', *args], timeout=timeout, check=False)
    if not p.returncode and args[0] in ('create', 'start'):
        name = args[args.index('--name') + 1] if args[0] == 'create' else args[-1]
        if name.startswith('hg-verify-' + RUN):
            phase = 'before-start' if args[0] == 'create' else 'after-start'
            record('verifier-' + phase + '-inspect', ['docker', 'inspect', name])
            if name.endswith('-changed'):
                record('verifier-' + phase + '-file', ['docker', 'cp', name + ':/app/binding-value', str(RAW / (phase + '.txt'))])
    return subprocess.CompletedProcess(p.args, p.returncode, p.stdout.decode(), p.stderr.decode())


container.docker = transport


def route(image, expected, task):
    stage = RAW / ('staging-' + task)
    stage.mkdir()
    binding = {'expected_snapshot': expected} if 'expected_snapshot' in inspect.signature(verifier._verify_container_state).parameters else {}
    return verifier._verify_container_state(
        image, {'kind': 'command', 'argv': ['/bin/cat', '/app/binding-value'],
                'pass_when': 'exit0_stdout', 'stdout': 'committed-before-start'},
        task_mount='/app', staging=stage, timeout_s=15, run_id=RUN, task_id=task,
        network=network, limits=LIMITS, **binding)


def sha(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def export_and_hash(image):
    archive = RAW / 'fresh-snapshot.tar'
    record('save-fresh-snapshot', ['docker', 'image', 'save', '-o', str(archive), image])
    out = RAW / 'fresh-metadata'
    out.mkdir()
    with tarfile.open(archive) as tar:
        def read_blob(digest):
            return tar.extractfile('blobs/sha256/' + digest.split(':')[1]).read()
        manifest_bytes = read_blob(image)
        assert sha(manifest_bytes) == image
        manifest = json.loads(manifest_bytes)
        config_bytes = read_blob(manifest['config']['digest'])
        assert sha(config_bytes) == manifest['config']['digest']
        config = json.loads(config_bytes)
        (out / 'manifest.json').write_bytes(manifest_bytes)
        (out / 'config.json').write_bytes(config_bytes)
        rows = []
        for layer, diffid in zip(manifest['layers'], config['rootfs']['diff_ids'], strict=True):
            member = 'blobs/sha256/' + layer['digest'].split(':')[1]
            stream = tar.extractfile(member)
            h = hashlib.sha256()
            while chunk := stream.read(1024 * 1024):
                h.update(chunk)
            assert 'sha256:' + h.hexdigest() == layer['digest']
            stream = tar.extractfile(member)
            if 'gzip' in layer['mediaType']:
                stream = gzip.GzipFile(fileobj=stream)
            h = hashlib.sha256()
            while chunk := stream.read(1024 * 1024):
                h.update(chunk)
            assert 'sha256:' + h.hexdigest() == diffid
            rows.append({'descriptor': layer, 'recomputed_diffid': 'sha256:' + h.hexdigest()})
        result = {'image_id': image, 'manifest_sha256': sha(manifest_bytes),
                  'config_sha256': sha(config_bytes), 'layers': rows,
                  'archive_sha256': sha(archive.read_bytes()),
                  'archive_and_layer_payloads_retained': False}
        (out / 'recomputed.json').write_text(json.dumps(result, indent=2) + '\n')
    archive.unlink()
    print('FRESH_BYTE_REHASH', json.dumps(result, sort_keys=True), flush=True)
    return result


try:
    record('baseline-head', ['git', 'rev-parse', 'HEAD'])
    record('docker-version', ['docker', 'version'])
    record('base-inspect', ['docker', 'image', 'inspect', BASE])
    if MODE == 'after':
        record('host-busybox-file', ['file', '/usr/bin/busybox'])
        record('host-busybox-elf', ['readelf', '-l', '-d', '/usr/bin/busybox'])
        record('host-busybox-sha256', ['sha256sum', '/usr/bin/busybox'])
    network = RUN + '-service'
    networks.append(network)
    record('create-service-network', ['docker', 'network', 'create', '--internal', '--label', 'harnessgrad.run=' + RUN, network])
    actor = RUN + '-actor'
    container.create(actor, image=BASE, limits=LIMITS, network='none', run_id=RUN, task_id='actor')
    container.start(actor)
    # Exact benign mutation from the verified packet: only a scratch input file.
    script = "printf 'committed-before-start\\n' > /app/binding-value; printf '%s\\n' '#!/bin/sh' \"printf 'changed-during-start\\\\n' > /app/binding-value\" 'exec /usr/bin/sleep \"$@\"' > /usr/local/bin/sleep; chmod 755 /usr/local/bin/sleep; cat /app/binding-value; sha256sum /usr/local/bin/sleep"
    record('install-startup-mutation', ['docker', 'exec', actor, '/bin/sh', '-c', script])
    container.stop(actor)
    tag = 'hg-wsnapfix:' + RUN
    tags.append(tag)
    snapshot = container.commit(actor, tag)
    images.append(snapshot)
    summary['snapshot'] = snapshot
    summary['base'] = BASE
    record('snapshot-inspect', ['docker', 'image', 'inspect', snapshot])
    if MODE == 'after':
        summary['recomputed'] = export_and_hash(snapshot)
    # Identity is the separately retained expected snapshot; BASE is a real different
    # existing image. The harmless observation does not supply a benchmark scorer.
    foreign = route(BASE, snapshot, 'foreign')
    summary['foreign_verdict'] = foreign
    summary['foreign_refused'] = bool(foreign.get('unmeasured'))
    # The shim must never run in the fresh snapshot verifier.
    changed = route(snapshot, snapshot, 'changed')
    summary['changed_verdict'] = changed
    summary['committed_file_preserved'] = (RAW / 'after-start.txt').read_bytes() == b'committed-before-start\n'
    summary['checker_observed_committed_bytes'] = changed['passed']
    summary['binding_check_passed'] = summary['committed_file_preserved'] and summary['checker_observed_committed_bytes']
    record('snapshot-still-same', ['docker', 'image', 'inspect', snapshot])
    for phase in ('before-start', 'after-start'):
        summary[phase + '_sha256'] = hashlib.sha256((RAW / (phase + '.txt')).read_bytes()).hexdigest()
    summary['checks_passed'] = int(summary['foreign_refused']) + int(summary['binding_check_passed'])
    summary['checks_failed'] = 2 - summary['checks_passed']
finally:
    for name in reversed(containers):
        record('cleanup-container', ['docker', 'rm', '--force', name], check=False)
        p = record('container-absence', ['docker', 'inspect', name], check=False)
        summary['cleanup'].append(dict(kind='container', name=name, absence_rc=p.returncode))
    for image in list(reversed(tags)) + list(reversed(images)):
        record('cleanup-image', ['docker', 'image', 'rm', image], timeout=300, check=False)
        p = record('image-absence', ['docker', 'image', 'inspect', image], check=False)
        summary['cleanup'].append(dict(kind='image', name=image, absence_rc=p.returncode))
    for name in networks:
        record('cleanup-network', ['docker', 'network', 'rm', name], check=False)
        p = record('network-absence', ['docker', 'network', 'inspect', name], check=False)
        summary['cleanup'].append(dict(kind='network', name=name, absence_rc=p.returncode))
    record('cached-base-still-present', ['docker', 'image', 'inspect', BASE])
    (RAW / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
assert all(c['absence_rc'] == 1 for c in summary['cleanup'])
assert summary['checks_passed'] == 2, 'snapshot boundary regressions still fail'
