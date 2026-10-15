"""Supplement bounded capture: launch helpers, archive pins, context import sites.

No scorer, world, submitted program, workbook or benchmark task is executed.
"""
import ast
import hashlib
import importlib.metadata as md
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SITE = Path(sys.prefix) / 'lib/python3.12/site-packages'


def sha(p):
    with Path(p).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


sources = json.loads((OUT / 'source-index.json').read_text())
extra_sources = ['textworld/envs/__init__.py', 'textworld/envs/wrappers/generic.py',
 'textworld/generator/__init__.py', 'textworld/gym/core.py', 'textworld/gym/envs/textworld_batch.py',
 'alfworld/agents/expert/__init__.py', 'alfworld/agents/expert/handcoded_expert_tw.py',
 'alfworld/agents/expert/handcoded_expert_thor.py', 'mkl/_init_helper.py']
for rel in extra_sources:
    p = SITE / rel
    if not p.is_file():
        sources.append({'path': str(p), 'exists': False})
        continue
    dest = OUT / 'source/installed' / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(p.read_bytes())
    sources.append({'path': str(p), 'fixture': str(dest.relative_to(ROOT)), 'sha256': sha(p), 'exists': True})

dsroot = Path('/mnt/20t/xubuqiang/datasets/ds1000/_src')
for p in sorted(dsroot.glob('DS-1000-*/execution.py')):
    dest = OUT / 'source/ds1000' / p.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(p.read_bytes())
    sources.append({'path': str(p), 'fixture': str(dest.relative_to(ROOT)), 'sha256': sha(p), 'exists': True})
for p in sorted(dsroot.glob('DS-1000-*/environment.yml')):
    dest = OUT / 'source/ds1000' / p.name
    dest.write_bytes(p.read_bytes())
    sources.append({'path': str(p), 'fixture': str(dest.relative_to(ROOT)), 'sha256': sha(p), 'exists': True})

# Preserve only dependency statements, not question/answer/test bodies. The
# full JSONL hash is recomputed to bind each path:row/context-line locator.
contexts = []
for path in dsroot.glob('test.jsonl'):
    for file_line, raw in enumerate(path.read_text().splitlines(), 1):
        row = json.loads(raw)
        context = row.get('code_context', '')
        sites = []
        for line, text in enumerate(context.splitlines(), 1):
            if re.match(r'\s*(import |from )', text) or any(x in text for x in
                    ['subprocess.', 'os.system(', 'ctypes.', 'load_library(', 'load_library(', 'cpp_extension']):
                sites.append({'context_line': line, 'text': text})
        contexts.append({'path': str(path), 'file_line': file_line, 'sites': sites})
    save('ds1000-context-source.json', {'path': str(path), 'sha256': sha(path), 'context_dependency_sites': contexts})

# Launch helpers can be selected through script branches or native oosplash.
extra = {}
for name in ['basename', 'ls', 'dirname', 'sed', 'grep', 'uname', 'dash']:
    p = shutil.which(name)
    if p:
        extra[str(Path(p).resolve())] = 'spreadsheetbench:launcher-helper-observed'
for name in ['javaldx', 'uno.bin', 'gpgme-w32spawn', 'xpdfimport']:
    p = Path('/usr/lib/libreoffice/program') / name
    if p.is_file():
        extra[str(p.resolve())] = 'spreadsheetbench:installed-auxiliary-superset'

# Version-trace successful opens expose dlopen providers omitted by ldd.
trace_opens = []
for name, dataset in [('java-load-trace', 'scienceworld'), ('libreoffice-version-trace', 'spreadsheetbench')]:
    path = OUT / (name + '.stderr.txt')
    if not path.is_file():
        continue
    for line, text in enumerate(path.read_text().splitlines(), 1):
        match = re.search(r'(?:openat\([^,]+, |execve\()"([^"]+)".*= (\d+)', text)
        if not match:
            continue
        p = Path(match.group(1))
        if not p.is_absolute() or not p.is_file():
            continue
        with p.open('rb') as stream:
            elf = stream.read(4) == b'\x7fELF'
        trace_opens.append({'trace': str(path.relative_to(ROOT)), 'line': line, 'text': text,
                            'path': str(p), 'sha256': sha(p), 'elf': elf})
        if elf:
            extra[str(p.resolve())] = dataset + ':version-launch-observed'
save('version-trace-opens.json', trace_opens)

# These are observed artifact digests; only an existing source SHA declaration
# is called a configured artifact pin. They do not bind host ELF dependencies.
artifacts = []
for pattern in [str(Path(sys.prefix) / 'share/py4j/*.jar'),
                '/mnt/20t/xubuqiang/datasets/scienceworld/*.tar.gz']:
    import glob
    for s in sorted(glob.glob(pattern)):
        p = Path(s)
        artifacts.append({'path': s, 'sha256': sha(p), 'bytes': p.stat().st_size})
save('jvm-artifacts.json', artifacts)

# Resolve and hash every extra ELF provider recursively. Existing evidence is
# immutable; this separate supplement has its own raw commands.
objects = {}
queue = list(extra)
while queue:
    path = queue.pop(0)
    if path in objects:
        continue
    p = Path(path)
    rec = {'path': path, 'sha256': sha(p), 'scope': extra[path]}
    with p.open('rb') as stream:
        elf = stream.read(4) == b'\x7fELF'
    rec['elf'] = elf
    if elf:
        for name, argv in [('ldd', ['ldd', path]), ('readelf', ['readelf', '-lW', '-dW', path])]:
            proc = subprocess.run(argv, capture_output=True, text=True, timeout=25)
            rec[name] = {'argv': argv, 'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}
        providers = sorted({str(Path(s).resolve()) for s in re.findall(r'(/[^\s()]+)', rec['ldd']['stdout']) if Path(s).is_file()})
        rec['resolved_providers'] = providers
        rec['unresolved_sonames'] = re.findall(r'^\s*(\S+)\s+=>\s+not found', rec['ldd']['stdout'], re.M)
        for provider in providers:
            extra.setdefault(provider, rec['scope'])
            queue.append(provider)
    objects[path] = rec
save('supplement-objects.json', objects)
paths = sorted(set(objects) | {r['path'] for r in artifacts})
argv = ['sha256sum', '--', *paths]
proc = subprocess.run(argv, capture_output=True, text=True, timeout=180)
(OUT / 'supplement-sha256sum.stdout.txt').write_text(proc.stdout)
(OUT / 'supplement-sha256sum.stderr.txt').write_text(proc.stderr)
save('supplement-sha256sum.command.json', {'argv': argv, 'returncode': proc.returncode})
save('source-index.json', sources)

# All citations carry the exact preimage text and fresh path+line, including
# native resolver edges which enter via ELF DT_NEEDED rather than Python code.
sites = []
for source in sources:
    if not source.get('fixture'):
        continue
    p = ROOT / source['fixture']
    for line, text in enumerate(p.read_text().splitlines(), 1):
        if re.search(r'\b(import|from|CDLL|LoadLibrary|subprocess|Popen|python3|soffice|libreoffice|load_lib|launch_gateway|java_home|JRE_SHA256|JAR_PATH|ro-bind|RUNTIME)\b', text):
            sites.append({'source_path': source['path'], 'fixture_path': source['fixture'], 'line': line, 'text': text})
save('source-sites.json', sites)
summary = json.loads((OUT / 'summary.json').read_text())
main_objects = json.loads((OUT / 'objects.json').read_text())
save('supplement-summary.json', {'supplement_objects': len(objects),
    'new_unique_objects': len(set(objects) - set(main_objects)),
    'unique_objects_with_digest': len(set(objects) | set(main_objects)),
    'jvm_artifacts': artifacts, 'pinned_native_surfaces': summary['pinned_native_surfaces']})
print(json.dumps(json.loads((OUT / 'supplement-summary.json').read_text()), indent=2))
