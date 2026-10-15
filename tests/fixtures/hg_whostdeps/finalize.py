"""Final bounded facts and exact source/locator audit, no scoring."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


sources = json.loads((OUT / 'source-index.json').read_text())
paths = [ROOT / 'data/scaffolds/qa/read.py',
 Path(sys.prefix) / 'lib/python3.12/sqlite3/dbapi2.py',
 Path(sys.prefix) / 'lib/python3.12/site-packages/openpyxl/reader/excel.py',
 Path(sys.prefix) / 'lib/python3.12/site-packages/openpyxl/reader/drawings.py',
 Path(sys.prefix) / 'lib/python3.12/site-packages/matplotlib/__init__.py',
 Path(sys.prefix) / 'lib/python3.12/site-packages/PIL/Image.py']
for p in paths:
    if p.is_relative_to(ROOT):
        rel = 'repo/' + str(p.relative_to(ROOT))
    else:
        rel = 'installed/' + str(p.relative_to(Path(sys.prefix) / 'lib/python3.12'))
    dest = OUT / 'source' / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(p.read_bytes())
    sources.append({'path': str(p), 'fixture': str(dest.relative_to(ROOT)), 'sha256': sha(p), 'exists': True})
(OUT / 'source-index.json').write_text(json.dumps(sources, indent=2, sort_keys=True) + '\n')

archive = Path('/mnt/20t/xubuqiang/datasets/scienceworld/_src/OpenJDK17U-jre_x64_linux_hotspot_17.0.20.1_1.tar.gz')
decl = ROOT / 'data/datasets/scienceworld/lib/scw_env.py'
import ast
tree = ast.parse(decl.read_text())
declared_sha = next(ast.literal_eval(n.value) for n in tree.body
    if isinstance(n, ast.Assign) and any(getattr(t, 'id', None) == 'JRE_SHA256' for t in n.targets))
archive_facts = {'path': str(archive), 'exists': archive.is_file(), 'source_sha_declaration': declared_sha}
if archive.is_file():
    archive_facts.update(sha256=sha(archive), bytes=archive.stat().st_size)
    argv = ['sha256sum', '--', str(archive)]
    proc = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    (OUT / 'jre-archive-sha256sum.stdout.txt').write_text(proc.stdout)
    (OUT / 'jre-archive-sha256sum.stderr.txt').write_text(proc.stderr)
    archive_facts.update(argv=argv, returncode=proc.returncode)
    archive_facts['matches_source_declaration'] = archive_facts['sha256'] == declared_sha
(OUT / 'jre-archive.json').write_text(json.dumps(archive_facts, indent=2, sort_keys=True) + '\n')

# Symbolic-link and runtime data/configuration hashes are evidence observations;
# neither a font cache nor a version string closes dynamic runtime discovery.
files = []
for s in ['/bin/sh', '/usr/bin/soffice', '/usr/bin/libreoffice', '/etc/ld.so.cache',
          '/etc/ld.so.conf', '/etc/nsswitch.conf', '/etc/localtime', '/usr/lib/locale/locale-archive',
          '/usr/lib/libreoffice/program/ooenv', '/usr/lib/libreoffice/program/javaldx']:
    p = Path(s)
    files.append({'path': s, 'exists': p.exists(), 'is_symlink': p.is_symlink(),
                  'resolved': str(p.resolve()), 'sha256': sha(p) if p.is_file() else None})
for folder in ['/etc/ld.so.conf.d', '/etc/fonts', '/usr/share/fonts',
               '/usr/lib/libreoffice/share/registry']:
    for p in sorted(Path(folder).rglob('*')):
        if p.is_file():
            files.append({'path': str(p), 'resolved': str(p.resolve()), 'sha256': sha(p),
                          'scope': 'installed-config-resource-superset'})
(OUT / 'runtime-resources.json').write_text(json.dumps(files, indent=2, sort_keys=True) + '\n')
argv = ['sha256sum', '--', *sorted({r['path'] for r in files if r.get('sha256')})]
proc = subprocess.run(argv, capture_output=True, text=True, timeout=60)
(OUT / 'runtime-resources-sha256sum.stdout.txt').write_text(proc.stdout)
(OUT / 'runtime-resources-sha256sum.stderr.txt').write_text(proc.stderr)
(OUT / 'runtime-resources-sha256sum.command.json').write_text(json.dumps({'argv': argv, 'returncode': proc.returncode}, indent=2) + '\n')
print(json.dumps({'jre_archive': archive_facts, 'runtime_resource_files': sum(bool(r.get('sha256')) for r in files),
                  'resource_hash_command_exit': proc.returncode,
                  'absent_paths': [r['path'] for r in files if r.get('exists') is False]}, indent=2))
