"""Retain referenced system licence texts and enumerate SBOM declarations."""
import json
from pathlib import Path
import re
from collect import command, digest, rows, write_rows

HERE = Path(__file__).parent


def main():
    common = []
    paths = set()
    copyright_copies = {n['copy'] for r in rows(HERE / 'system.jsonl') for c in r['candidates']
                        for o in c['ownership'] for n in o['notices']}
    for name in sorted(copyright_copies):
        paths.update(s.rstrip('.') for s in re.findall(
            r'/usr/share/common-licenses/[A-Za-z0-9.-]+', Path(name).read_text()))
    for name in sorted(paths):
        p = Path(name)
        if not p.is_file():
            common.append({'path': name, 'state': 'ABSENT', 'scope': name})
            continue
        data = p.read_bytes()
        dest = HERE / 'licenses' / (digest(data)['sha256'] + '.txt')
        dest.write_bytes(data)
        common.append({'state': 'FOUND', 'path': name, 'copy': str(dest), **digest(data),
            'scope': 'system common licence text referenced by observed package copyright',
            'owner': command(['dpkg-query', '-S', name, str(p.resolve())])})
    write_rows(HERE / 'common-licenses.jsonl', common)
    components = []
    for archive in rows(HERE / 'archives.jsonl'):
        for candidate in archive['embedded_record_candidates']:
            if 'copy' not in candidate:
                continue
            sbom = json.loads(Path(candidate['copy']).read_bytes())
            for c in sbom.get('components', []):
                components.append({'state': 'FOUND', 'archive': archive['filename'],
                    'sbom_path': candidate['copy'], 'sbom_sha256': candidate['sha256'],
                    'component': c.get('name'), 'version': c.get('version'),
                    'purl': c.get('purl'), 'hashes_declared': c.get('hashes', []),
                    'licenses_declared': c.get('licenses', []), 'properties': c.get('properties', []),
                    'scope': 'producer-packaged SBOM declaration; not measured compiled input identity',
                    'full_component_license_text': 'UNKNOWN not acquired except separately cited OpenSSL notice',
                    'exact_build_binding': 'UNKNOWN not a compiled build attestation'})
    write_rows(HERE / 'sbom-components.jsonl', components)
    print(json.dumps({'referenced_common_license_paths': len(common),
        'common_texts_found': sum(r['state'] == 'FOUND' for r in common),
        'sbom_component_declarations': len(components)}, sort_keys=True))


if __name__ == '__main__':
    main()
