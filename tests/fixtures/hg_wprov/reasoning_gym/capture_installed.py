#!/usr/bin/env python3
"""Record actual installed wheel-member bytes read-only; never import the package."""
import argparse
import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    dist = importlib.metadata.distribution('reasoning-gym')
    files = []
    with zipfile.ZipFile(root / 'responses/pypi-bdist_wheel.body') as wheel:
        for name in wheel.namelist():
            path = dist.locate_file(name)
            body = path.read_bytes() if path.is_file() else None
            expected = wheel.read(name)
            files.append({'path': name, 'installed_path': str(path),
                          'installed_sha256': hashlib.sha256(body).hexdigest() if body is not None else None,
                          'installed_size': len(body) if body is not None else None,
                          'wheel_sha256': hashlib.sha256(expected).hexdigest(),
                          'wheel_size': len(expected), 'byte_equality': body == expected})
    package = dist.locate_file('reasoning_gym')
    wheel_package_names = {f['path'] for f in files if f['path'].startswith('reasoning_gym/')}
    extra = []
    for path in sorted(package.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            relative = 'reasoning_gym/' + path.relative_to(package).as_posix()
            if relative not in wheel_package_names:
                body = path.read_bytes()
                extra.append({'path': relative, 'sha256': hashlib.sha256(body).hexdigest(), 'size': len(body)})
    record = dist.locate_file('reasoning_gym-0.1.25.dist-info/RECORD').read_bytes()
    output = {'captured_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'command': 'python3 tests/fixtures/hg_wprov/reasoning_gym/capture_installed.py --output tests/fixtures/hg_wprov/reasoning_gym/installed-members.json',
              'interpreter': sys.executable, 'distribution': dist.metadata['Name'],
              'reported_version': dist.version, 'metadata_path': str(dist._path),
              'direct_url_json': dist.read_text('direct_url.json'), 'members': files,
              'extra_non_pycache_package_files': extra,
              'installed_record_sha256': hashlib.sha256(record).hexdigest(),
              'scope': 'Current interpreter static bytes; not pristine verifier namespace or transitive dependency custody.'}
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    args.output.with_name('installed-RECORD.body').write_bytes(record)
    print(f"wheel members={len(files)} equal={sum(f['byte_equality'] for f in files)} differing={[f['path'] for f in files if not f['byte_equality']]} extra_non_pycache_package_files={len(extra)}")


if __name__ == '__main__':
    main()
