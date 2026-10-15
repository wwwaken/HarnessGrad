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
    request = urllib.request.Request(url, headers={'User-Agent': 'HarnessGrad-w-resolver4/1'})
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


tags = list(sys_tags())
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
