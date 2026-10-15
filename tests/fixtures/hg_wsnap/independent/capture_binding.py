#!/usr/bin/env python3
"""Independent, bounded binding validation. No benchmark, reward file or model."""
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from eval.containers import container
from eval.verification.verifier import _verify_container_state

BASE = json.loads((HERE.parent / 'summary.json').read_text())['base_id']
RUN = 'w-snap2-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
RAW = HERE / RUN
RAW.mkdir()
LIMITS = {'cpus': '1', 'memory': '256m', 'pids': 64}
seq = 0
owned_containers = []
owned_images = []
owned_tags = []
commands = []
summary = {'run_id': RUN, 'limits': LIMITS, 'network': 'none',
           'benchmark_scoring_runs': 0, 'model_gpu_endpoint_calls': 0}


def record(label, argv, timeout=120, check=True):
    global seq
    seq += 1
    stem = RAW / f'{seq:03d}-{label}'
    info = {'argv': list(map(str, argv)), 'cwd': str(ROOT),
            'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'timeout_s': timeout}
    try:
        proc = subprocess.run(info['argv'], capture_output=True, timeout=timeout)
    except BaseException as exc:
        info['exception'] = repr(exc)
        stem.with_suffix('.command.json').write_text(json.dumps(info, indent=2) + '\n')
        raise
    info['returncode'] = proc.returncode
    stem.with_suffix('.stdout.txt').write_bytes(proc.stdout)
    stem.with_suffix('.stderr.txt').write_bytes(proc.stderr)
    stem.with_suffix('.command.json').write_text(json.dumps(info, indent=2) + '\n')
    commands.append({'label': label, 'stem': stem.name, 'returncode': proc.returncode})
    if check and proc.returncode:
        raise RuntimeError(f'{stem.name}: {proc.stderr.decode(errors="replace")}')
    return proc


def inspect(name, label='inspect'):
    return json.loads(record(label, ['docker', 'inspect', name]).stdout)[0]


def transport(*args, timeout=120):
    # Only transport is wrapped; no gate, admission, argument or return value is changed.
    if args[0] == 'create':
        owned_containers.append(args[args.index('--name') + 1])
    proc = record('helper-' + args[0], ['docker', *args], timeout=timeout, check=False)
    result = subprocess.CompletedProcess(proc.args, proc.returncode,
                                         proc.stdout.decode(), proc.stderr.decode())
    if proc.returncode == 0 and args[0] in ('create', 'start'):
        name = args[args.index('--name') + 1] if args[0] == 'create' else args[-1]
        if name.startswith('hg-verify-' + RUN):
            phase = 'before-start' if args[0] == 'create' else 'after-start'
            meta = inspect(name, name.rsplit('-', 1)[-1] + '-' + phase)
            summary.setdefault('route_observations', {}).setdefault(name, {})[phase] = {
                'Image': meta['Image'], 'Config.Image': meta['Config']['Image'],
                'Running': meta['State']['Running'], 'Mounts': meta['Mounts']}
            if name.endswith('-changed'):
                record('changed-' + phase + '-cp', ['docker', 'cp', name + ':/app/binding-value', str(RAW / ('changed-' + phase + '.txt'))])
    return result


container.docker = transport


def create(name, image, **kwargs):
    return container.create(name, image=image, limits=LIMITS, network='none',
                            run_id=RUN, task_id=name.rsplit('-', 1)[-1], **kwargs)


def execute(name, script, label):
    return record(label, ['docker', 'exec', name, '/bin/sh', '-c', script]).stdout.decode()


def commit(name, suffix):
    tag = 'hg-wsnap2:' + RUN + '-' + suffix
    owned_tags.append(tag)
    result = container.commit(name, tag)
    owned_images.append(result)
    return result, tag


def route(image, task):
    stage = RAW / ('staging-' + task)
    stage.mkdir()
    # A read-only observation command; no benchmark check or reward is supplied.
    return _verify_container_state(image, {'kind': 'command', 'argv': [
        '/bin/sh', '-c', 'if test -f /app/binding-value; then cat /app/binding-value; else echo binding-value-absent; fi; readlink /proc/1/exe']},
        task_mount='/app', staging=stage, timeout_s=30, run_id=RUN,
        task_id=task, network='none', declared_network='none', limits=LIMITS)


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
    record('git-head', ['git', 'rev-parse', 'HEAD'])
    record('docker-version', ['docker', 'version', '--format', '{{json .}}'])
    record('docker-store', ['docker', 'info', '--format', '{{json .DriverStatus}}'])
    base = json.loads(record('base-inspect', ['docker', 'image', 'inspect', BASE]).stdout)[0]
    assert base['Id'] == BASE and not base['Config'].get('Volumes')
    summary['base_id'] = base['Id']
    summary['base_volumes'] = base['Config'].get('Volumes')
    actor = RUN + '-actor'
    bind = RAW / 'bind-source'
    bind.mkdir()
    (bind / 'value').write_text('bind-before\n')
    create(actor, BASE, extra_mounts=('--mount', f'type=bind,src={bind},dst=/binding-ro,readonly'), tmpfs=('/binding-tmp',))
    container.start(actor)
    execute(actor, "printf 'committed-value\n' > /app/binding-value; printf 'tmpfs-value\n' > /binding-tmp/value; test ! -S /var/run/docker.sock", 'actor-write')
    record('detached-writer', ['docker', 'exec', '-d', actor, '/bin/sh', '-c', 'while :; do date +%s%N > /app/binding-tick; /usr/bin/sleep 0.02; done'])
    container.stop(actor)
    summary['stopped_actor_state'] = inspect(actor, 'stopped-actor')['State']
    record('stopped-tick-cp', ['docker', 'cp', actor + ':/app/binding-tick', str(RAW / 'stopped-tick.txt')])
    snapshot, tag = commit(actor, 'ordinary')
    summary['expected_snapshot'] = snapshot
    snapmeta = json.loads(record('snapshot-inspect', ['docker', 'image', 'inspect', snapshot]).stdout)[0]
    summary['fresh_bytes'] = export_and_hash(snapshot)
    assert snapmeta['Id'] == snapmeta['Descriptor']['digest'] == summary['fresh_bytes']['manifest_sha256']
    assert snapmeta['Id'] != summary['fresh_bytes']['config_sha256']
    # Host observer changes only its own stopped scratch container/tag/bind source.
    replacement = RAW / 'after-commit.txt'
    replacement.write_text('changed-stopped-actor\n')
    record('change-stopped-actor', ['docker', 'cp', str(replacement), actor + ':/app/binding-value'])
    (bind / 'value').write_text('bind-after\n')
    record('retarget-own-tag', ['docker', 'image', 'tag', BASE, tag])
    summary['retargeted_tag'] = json.loads(record('retargeted-inspect', ['docker', 'image', 'inspect', tag]).stdout)[0]['Id']
    summary['looks_pinned'] = {'committed_digest': container.looks_pinned(snapshot),
                               'other_real_digest': container.looks_pinned(BASE),
                               'retargeted_tag': container.looks_pinned(tag)}
    verifier = RUN + '-verify'
    create(verifier, snapshot)
    summary['ordinary_before_start'] = inspect(verifier, 'ordinary-before-start')
    container.start(verifier)
    summary['ordinary_probe'] = execute(verifier, 'cat /app/binding-value; test ! -e /binding-ro/value && echo bind-excluded; test ! -e /binding-tmp/value && echo tmpfs-excluded; test ! -S /var/run/docker.sock && echo no-docker-socket', 'ordinary-binding-observation')
    record('snapshot-tick-cp', ['docker', 'cp', verifier + ':/app/binding-tick', str(RAW / 'snapshot-tick.txt')])
    summary['tick_bytes_equal'] = (RAW / 'stopped-tick.txt').read_bytes() == (RAW / 'snapshot-tick.txt').read_bytes()
    # Valid but foreign identity at the direct verifier boundary (host-controlled input).
    assert BASE != snapshot
    summary['foreign_identity_route'] = {'expected': snapshot, 'supplied': BASE,
                                         'returned': route(BASE, 'foreign')}
    # Syntactically valid identity recomputed from real retained config bytes, which
    # is not a locally available image manifest; --pull=never prevents network access.
    unavailable = summary['fresh_bytes']['config_sha256']
    assert unavailable != snapshot
    summary['unavailable_image_probe'] = record('config-id-unavailable', ['docker', 'image', 'inspect', unavailable], check=False).returncode
    if summary['unavailable_image_probe'] != 0:
        missing_name = RUN + '-unavailable'
        owned_containers.append(missing_name)
        summary['unavailable_identity_create'] = record('unavailable-identity-refusal', [
            'docker', 'create', '--pull=never', '--name', missing_name, '--network', 'none',
            '--cpus', '1', '--memory', '256m', '--pids-limit', '64', unavailable, 'sleep', 'infinity'], check=False).returncode
    # A benign startup executable changes one scratch file; no verdict or platform file.
    changed_actor = RUN + '-changed-actor'
    create(changed_actor, BASE)
    container.start(changed_actor)
    execute(changed_actor, "printf 'committed-before-start\n' > /app/binding-value; printf '%s\n' '#!/bin/sh' \"printf 'changed-during-start\\n' > /app/binding-value\" 'exec /usr/bin/sleep \"$@\"' > /usr/local/bin/sleep; chmod 755 /usr/local/bin/sleep; sha256sum /usr/local/bin/sleep; cat /app/binding-value; test ! -S /var/run/docker.sock", 'changed-actor-setup')
    container.stop(changed_actor)
    changed_snapshot, _ = commit(changed_actor, 'changed')
    summary['changed_snapshot'] = changed_snapshot
    summary['changed_filesystem_route'] = route(changed_snapshot, 'changed')
    summary['changed_before_bytes'] = (RAW / 'changed-before-start.txt').read_text()
    summary['changed_after_bytes'] = (RAW / 'changed-after-start.txt').read_text()
    summary['changed_image_after'] = json.loads(record('changed-image-still-same', ['docker', 'image', 'inspect', changed_snapshot]).stdout)[0]['Id']
finally:
    cleanup = []
    for name in reversed(owned_containers):
        removal = record('cleanup-container', ['docker', 'rm', '--force', name], check=False)
        absent = record('container-absence', ['docker', 'inspect', name], check=False)
        cleanup.append({'container': name, 'remove_rc': removal.returncode, 'absence_rc': absent.returncode})
    for tag in reversed(owned_tags):
        result = record('cleanup-tag', ['docker', 'image', 'rm', tag], check=False)
        absent = record('tag-absence', ['docker', 'image', 'inspect', tag], check=False)
        cleanup.append({'tag': tag, 'remove_rc': result.returncode, 'absence_rc': absent.returncode})
    for image in reversed(owned_images):
        result = record('cleanup-image', ['docker', 'image', 'rm', image], check=False)
        absent = record('image-absence', ['docker', 'image', 'inspect', image], check=False)
        cleanup.append({'image': image, 'remove_rc': result.returncode, 'absence_rc': absent.returncode})
    summary['cleanup'] = cleanup
    summary['base_after'] = json.loads(record('base-still-present', ['docker', 'image', 'inspect', BASE]).stdout)[0]['Id']
    summary['commands'] = commands
    (RAW / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print('BINDING_VALIDATION', json.dumps(summary, sort_keys=True), flush=True)
