#!/usr/bin/env python3
"""Bounded local image integrity probes; no benchmark, scorer or model invocation."""
import datetime
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import eval.containers.container as container

OUT = Path(__file__).resolve().parent
RAW = OUT / 'raw'
RAW.mkdir(exist_ok=True)
BASE = 'sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12'
HIST = 'sha256:59c94f3462a248e5af5909b2249cba07e2e46574eee4fd362896d7c048eac779'
RUN = 'w-snap-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
seq = 0
containers = []
images = []
volumes = []
limits = {'cpus': '1', 'memory': '256m', 'pids': 64}

def record(argv, timeout=120, check=True):
    global seq
    seq += 1
    stem = RAW / f'{seq:03d}'
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    stem.with_suffix('.stdout.txt').write_text(p.stdout)
    stem.with_suffix('.stderr.txt').write_text(p.stderr)
    stem.with_suffix('.command.json').write_text(json.dumps({'argv': argv, 'cwd': str(ROOT), 'started_utc': started, 'timeout_s': timeout, 'returncode': p.returncode}, indent=2)+'\n')
    if check and p.returncode:
        raise RuntimeError(f'{stem.name}: {argv}: {p.stderr}')
    return p

def docker(*args, timeout=120):
    return record(['docker', *args], timeout, check=False)

# Execute the real helpers unchanged; retain every subprocess and its unmodified output.
container.docker = docker

def inspect(name):
    return json.loads(record(['docker', 'inspect', name]).stdout)[0]

def image_inspect(name):
    return json.loads(record(['docker', 'image', 'inspect', name]).stdout)[0]

def create(name, image, **kwargs):
    containers.append(name)
    container.create(name, image=image, limits=limits, network='none', run_id=RUN, task_id=name.rsplit('-', 1)[-1], **kwargs)

def exec_ok(name, script):
    return record(['docker', 'exec', name, '/bin/sh', '-c', script]).stdout

def commit(name, tag):
    result = container.commit(name, tag)
    images.append(result)
    return result

def sha(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()

def export_hash(image, label, temp):
    archive = Path(temp) / (label+'.tar')
    record(['docker', 'image', 'save', '-o', str(archive), image], timeout=120)
    dest = OUT / 'image-metadata' / label
    dest.mkdir(parents=True, exist_ok=True)
    blobs = {}
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        for member in members:
            if not member.isfile():
                continue
            if member.size > 1024*1024 and not member.name.startswith('blobs/'):
                continue
            f = tar.extractfile(member)
            h = hashlib.sha256()
            while chunk := f.read(1024*1024):
                h.update(chunk)
            digest = 'sha256:'+h.hexdigest()
            blobs[member.name] = {'sha256': digest, 'size': member.size}
            if member.size < 1024*1024:
                data = tar.extractfile(member).read()
                try:
                    json.loads(data)
                except (ValueError, UnicodeDecodeError):
                    continue
                dst = dest / member.name
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)
        def get(digest):
            return tar.extractfile('blobs/sha256/'+digest.split(':')[1]).read()
        # Docker 29/containerd exposes the manifest digest as Id; never assume config hash.
        manifest = json.loads(get(image))
        assert sha(get(image)) == image
        config_digest = manifest['config']['digest']
        config = json.loads(get(config_digest))
        assert sha(get(config_digest)) == config_digest
        layers = []
        for layer, diffid in zip(manifest['layers'], config['rootfs']['diff_ids'], strict=True):
            member_name = 'blobs/sha256/'+layer['digest'].split(':')[1]
            assert blobs[member_name]['sha256'] == layer['digest']
            f = tar.extractfile(member_name)
            stream = gzip.GzipFile(fileobj=f) if 'gzip' in layer['mediaType'] else f
            h = hashlib.sha256(); size=0
            while chunk := stream.read(1024*1024):
                h.update(chunk); size += len(chunk)
            actual = 'sha256:'+h.hexdigest()
            assert actual == diffid
            layers.append({'descriptor': layer, 'blob_sha256': blobs[member_name]['sha256'], 'uncompressed_sha256': actual, 'uncompressed_bytes': size})
        result = {'image_id': image, 'manifest_sha256': sha(get(image)), 'config_sha256': sha(get(config_digest)), 'config_descriptor': manifest['config'], 'layers': layers, 'all_archive_members': blobs, 'layer_bytes_retained': False}
    archive.unlink()
    (dest/'recomputed.json').write_text(json.dumps(result, indent=2)+'\n')
    print(label, image, 'verified manifest/config/layers/diffids', flush=True)
    return result

summary = {'run_id': RUN, 'resource_limits': limits, 'network': 'none', 'benchmark_scoring_runs': 0, 'model_calls': 0}
try:
    record(['git', 'rev-parse', 'HEAD'])
    record(['docker', 'version', '--format', '{{json .}}'])
    record(['docker', 'info', '--format', '{{json .DriverStatus}}'])
    summary['historical_inspect_returncode'] = record(['docker', 'image', 'inspect', HIST], check=False).returncode
    base = image_inspect(BASE)
    summary['base_id'] = base['Id']
    summary['base_parent'] = base.get('Parent')
    summary['base_volumes'] = base['Config'].get('Volumes')
    with tempfile.TemporaryDirectory(prefix='hg-wsnap-') as temp:
        export_hash(BASE, 'base', temp)
        shared = Path(temp)/'readonly'; shared.mkdir(); (shared/'value').write_text('host-before\n')
        actor = RUN+'-actor'; tag = 'hg-wsnap:'+RUN
        create(actor, BASE, extra_mounts=('--mount', f'type=bind,src={shared},dst=/probe-ro,readonly'), tmpfs=('/probe-tmp',))
        container.start(actor)
        exec_ok(actor, "mkdir -p /app; printf 'committed-root\n' > /app/value; printf 'tmpfs-before\n' > /probe-tmp/value; test ! -S /var/run/docker.sock; printf 'actor-ready\n'")
        # Detached actor writer: stop must kill this as well as the main process.
        record(['docker', 'exec', '-d', actor, '/bin/sh', '-c', 'while :; do date +%s%N > /app/tick; /usr/bin/sleep 0.02; done'])
        container.stop(actor)
        summary['actor_stopped'] = inspect(actor)['State']
        snapshot = commit(actor, tag); snapmeta = image_inspect(snapshot)
        summary['snapshot_id'] = snapshot; summary['snapshot_parent'] = snapmeta.get('Parent')
        export_hash(snapshot, 'snapshot', temp)
        # Host-only adversary after commit, deliberately stronger than actor permissions.
        (shared/'value').write_text('host-after\n')
        replacement = Path(temp)/'replacement'; replacement.write_text('actor-after-commit\n')
        record(['docker', 'cp', str(replacement), actor+':/app/value'])
        record(['docker', 'image', 'tag', BASE, tag])
        summary['retargeted_tag_id'] = image_inspect(tag)['Id']
        verifier = RUN+'-verify'; create(verifier, snapshot)
        summary['verifier_before_start'] = inspect(verifier)
        container.start(verifier)
        summary['verifier_after_start'] = inspect(verifier)
        summary['baseline_probe'] = exec_ok(verifier, "cat /app/value; test ! -e /probe-ro/value && echo bind-excluded; test ! -e /probe-tmp/value && echo tmpfs-excluded; test ! -S /var/run/docker.sock && echo no-docker-socket; cat /app/tick")
        record(['docker', 'cp', verifier+':/app/tick', str(Path(temp)/'tick-before')])
        record(['docker', 'cp', actor+':/app/tick', str(Path(temp)/'tick-after')])
        summary['stopped_writer_tick_equal'] = (Path(temp)/'tick-before').read_bytes() == (Path(temp)/'tick-after').read_bytes()
        # Actor-only attack: replace the executable the platform starts on verifier creation.
        bad_actor = RUN+'-startup-actor'; create(bad_actor, BASE); container.start(bad_actor)
        exec_ok(bad_actor, "printf 'committed-before-start\n' > /app/value; printf '%s\n' '#!/bin/sh' \"printf 'rewritten-by-actor-startup\\n' > /app/value\" 'exec /usr/bin/sleep \"$@\"' > /usr/local/bin/sleep; chmod 755 /usr/local/bin/sleep; sha256sum /usr/local/bin/sleep; test ! -S /var/run/docker.sock")
        container.stop(bad_actor)
        attack_snapshot = commit(bad_actor, 'hg-wsnap:'+RUN+'-startup'); summary['attack_snapshot_id'] = attack_snapshot
        summary['attack_snapshot_metadata'] = image_inspect(attack_snapshot)
        export_hash(attack_snapshot, 'startup-snapshot', temp)
        bad_verify = RUN+'-startup-verify'; create(bad_verify, attack_snapshot)
        summary['attack_verifier_before_start'] = inspect(bad_verify)
        before = Path(temp)/'before'; record(['docker', 'cp', bad_verify+':/app/value', str(before)])
        summary['attack_before_start'] = before.read_text()
        container.start(bad_verify)
        summary['attack_after_start'] = exec_ok(bad_verify, 'cat /app/value; sha256sum /usr/local/bin/sleep; readlink /proc/1/exe')
        summary['attack_verifier_after_start'] = inspect(bad_verify)
        # Generic inherited VOLUME counterexample, explicitly not the volume-free TB base.
        volume_base = record(['docker', 'commit', '--change', 'VOLUME /app', actor, 'hg-wsnap:'+RUN+'-volume-base']).stdout.strip()
        images.append(volume_base); summary['volume_base_metadata'] = image_inspect(volume_base)
        volume_actor = RUN+'-volume-actor'; create(volume_actor, volume_base)
        volume_actor_meta = inspect(volume_actor); volumes.extend(m['Name'] for m in volume_actor_meta['Mounts'] if m['Type']=='volume')
        summary['volume_actor_before'] = volume_actor_meta; container.start(volume_actor)
        summary['volume_actor_write'] = exec_ok(volume_actor, "printf 'actor-volume-output\n' > /app/value; cat /app/value")
        container.stop(volume_actor)
        volume_snapshot = commit(volume_actor, 'hg-wsnap:'+RUN+'-volume-snapshot')
        summary['volume_snapshot_id'] = volume_snapshot; summary['volume_snapshot_metadata'] = image_inspect(volume_snapshot)
        export_hash(volume_snapshot, 'volume-snapshot', temp)
        volume_verify = RUN+'-volume-verify'; create(volume_verify, volume_snapshot)
        volume_verify_meta = inspect(volume_verify); volumes.extend(m['Name'] for m in volume_verify_meta['Mounts'] if m['Type']=='volume')
        summary['volume_verifier_before'] = volume_verify_meta; container.start(volume_verify)
        summary['volume_verifier_read'] = exec_ok(volume_verify, 'cat /app/value')
        summary['volume_actor_mounts'] = volume_actor_meta['Mounts']; summary['volume_verifier_mounts'] = volume_verify_meta['Mounts']
        record(['docker', 'image', 'rm', tag]) # removes only our retargeted alias, never BASE
finally:
    cleanup = []
    for name in reversed(containers):
        cleanup.append({'container': name, 'remove_returncode': record(['docker', 'rm', '-f', name], check=False).returncode})
        cleanup[-1]['absence_returncode'] = record(['docker', 'inspect', name], check=False).returncode
    for volume in volumes:
        cleanup.append({'volume': volume, 'remove_returncode': record(['docker', 'volume', 'rm', volume], check=False).returncode})
        cleanup[-1]['absence_returncode'] = record(['docker', 'volume', 'inspect', volume], check=False).returncode
    for image in reversed(images):
        cleanup.append({'image': image, 'remove_returncode': record(['docker', 'image', 'rm', '-f', image], check=False).returncode})
        cleanup[-1]['absence_returncode'] = record(['docker', 'image', 'inspect', image], check=False).returncode
    summary['base_still_present'] = image_inspect(BASE)['Id']
    summary['cleanup'] = cleanup
    (OUT/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k in ('run_id','snapshot_id','snapshot_parent','baseline_probe','stopped_writer_tick_equal','attack_snapshot_id','attack_before_start','attack_after_start','volume_actor_write','volume_verifier_read')}, indent=2))
