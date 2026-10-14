"""Compare original/rebuilt wheels and collect unmodified native inspection output."""
import base64
import csv
import difflib
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import zipfile

out = Path('/receipts')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def command(name, argv, allowed=(0,)):
    p = subprocess.run(argv, capture_output=True)
    (out / (name + '.stdout.txt')).write_bytes(p.stdout)
    (out / (name + '.stderr.txt')).write_bytes(p.stderr)
    (out / (name + '.command.json')).write_text(json.dumps({'argv': argv, 'returncode': p.returncode}, indent=2) + '\n')
    assert p.returncode in allowed, (argv, p.returncode, p.stderr)
    return p.stdout.decode(errors='replace')

paths = {'published': next(Path('/opt/hg-wujson').glob('*.whl')),
         'rebuilt': next(Path('/packet/build/wheels').glob('*.whl'))}
wheels = {}
elfs = {}
symbols = {}
for label, path in paths.items():
    target = out / label
    target.mkdir()
    with zipfile.ZipFile(path) as z:
        members = {i.filename: z.read(i) for i in z.infolist() if not i.is_dir()}
        inventory = [{'name': i.filename, 'size': i.file_size, 'compressed_size': i.compress_size,
                      'compression': i.compress_type, 'date_time': i.date_time, 'external_attr': i.external_attr,
                      'sha256': digest(z.read(i))} for i in z.infolist()]
        # Preserve every member, not just summaries, for independent inspection.
        for name, data in members.items():
            dest = target / name
            dest.parent.mkdir(exist_ok=True, parents=True)
            dest.write_bytes(data)
    record = next(data for name, data in members.items() if name.endswith('/RECORD'))
    record_checks = []
    for name, expected, size in csv.reader(io.StringIO(record.decode())):
        actual = 'sha256=' + base64.urlsafe_b64encode(hashlib.sha256(members[name]).digest()).decode().rstrip('=')
        record_checks.append({'name': name, 'expected': expected, 'actual': actual,
                              'size_matches': not size or int(size) == len(members[name]),
                              'hash_matches': not expected or expected == actual})
    assert all(c['size_matches'] and c['hash_matches'] for c in record_checks)
    wheels[label] = {'path': str(path), 'size': path.stat().st_size, 'sha256': digest(path.read_bytes()),
                     'inventory': inventory, 'record_checks': record_checks, 'members': members}
    (out / (label + '-members.json')).write_text(json.dumps(inventory, indent=2) + '\n')
    elf = target / next(n for n in members if n.endswith('.so'))
    elfs[label] = elf
    command(label + '-sha256', ['sha256sum', str(path), str(elf)])
    command(label + '-readelf', ['readelf', '-h', '-l', '-d', '-V', '-S', '-n', '--dyn-syms', '-W', str(elf)])
    command(label + '-comment', ['readelf', '-p', '.comment', str(elf)])
    command(label + '-nm-defined-demangled', ['nm', '-D', '-C', '--defined-only', str(elf)])
    command(label + '-nm-undefined-demangled', ['nm', '-D', '-C', '--undefined-only', str(elf)])
    command(label + '-disassembly', ['objdump', '-d', '-C', str(elf)])
    raw = command(label + '-dynsym', ['readelf', '--dyn-syms', '--wide', str(elf)])
    definitions = {}
    undefined = []
    for line in raw.splitlines():
        m = re.match(r'\s*\d+:\s+([0-9a-f]+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
        if not m:
            continue
        address, size, typ, bind, visibility, index, name = m.groups()
        if index == 'UND':
            undefined.append(name)
        else:
            definitions[name] = {'address': address, 'size': int(size), 'type': typ, 'binding': bind, 'index': index}
    symbols[label] = {'defined': definitions, 'undefined': undefined,
        'double_conversion_defined': [n for n in definitions if 'double_conversion' in n],
        'double_conversion_undefined': [n for n in undefined if 'double_conversion' in n]}
    for section in ('.text', '.rodata'):
        command(label + '-' + section[1:] + '-extract', ['objcopy', '--dump-section', section + '=' + str(target / (section[1:] + '.bin')), str(elf), '/tmp/' + label + '-objcopy.so'])
command('extension-cmp', ['cmp', str(elfs['published']), str(elfs['rebuilt'])], allowed=(0, 1))
pub = wheels['published']['members']
local = wheels['rebuilt']['members']
comparisons = []
for name in sorted(set(pub) | set(local)):
    a, b = pub.get(name), local.get(name)
    comparisons.append({'member': name, 'published_size': len(a) if a is not None else None,
                        'rebuilt_size': len(b) if b is not None else None,
                        'published_sha256': digest(a) if a is not None else None,
                        'rebuilt_sha256': digest(b) if b is not None else None,
                        'equal': a == b})
    if a != b and not name.endswith('.so') and a is not None and b is not None:
        (out / (Path(name).name + '.diff.txt')).write_text(''.join(difflib.unified_diff(a.decode().splitlines(True), b.decode().splitlines(True), fromfile='published/' + name, tofile='rebuilt/' + name)))
sections = []
for section in ('text', 'rodata'):
    a, b = [(out / label / (section + '.bin')).read_bytes() for label in paths]
    sections.append({'section': '.' + section, 'published_size': len(a), 'rebuilt_size': len(b),
                     'published_sha256': digest(a), 'rebuilt_sha256': digest(b), 'equal': a == b})
common_symbols = set(symbols['published']['defined']) & set(symbols['rebuilt']['defined'])
result = {'wheels': {label: {k:v for k,v in obj.items() if k != 'members'} for label,obj in wheels.items()},
          'file_member_sets_equal': set(pub) == set(local),
          'ordered_zip_member_names_equal': [i['name'] for i in wheels['published']['inventory']] == [i['name'] for i in wheels['rebuilt']['inventory']],
          'members': comparisons, 'sections': sections,
          'symbols': symbols,
          'defined_symbols_only_published': sorted(set(symbols['published']['defined']) - set(symbols['rebuilt']['defined'])),
          'defined_symbols_only_rebuilt': sorted(set(symbols['rebuilt']['defined']) - set(symbols['published']['defined'])),
          'common_defined_symbol_count': len(common_symbols),
          'whole_wheel_equal': paths['published'].read_bytes() == paths['rebuilt'].read_bytes(),
          'scope': 'one build in prescribed pinned CPython image; original producer build environment not authenticated',
}
(out / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'whole_wheel_equal': result['whole_wheel_equal'], 'file_member_sets_equal': result['file_member_sets_equal'],
                  'members': comparisons, 'sections': sections,
                  'double_conversion_defined_counts': {k: len(v['double_conversion_defined']) for k,v in symbols.items()},
                  'double_conversion_undefined_counts': {k: len(v['double_conversion_undefined']) for k,v in symbols.items()},
                  'common_defined_symbol_count': len(common_symbols),
                  'defined_symbols_only_published': result['defined_symbols_only_published'],
                  'defined_symbols_only_rebuilt': result['defined_symbols_only_rebuilt']}, indent=2))
