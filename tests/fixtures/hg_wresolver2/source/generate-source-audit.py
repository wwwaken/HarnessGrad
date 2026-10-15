#!/usr/bin/env python3
"""Preserve scorer source and inspect wheel members without importing dependencies."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import sysconfig
import zipfile
from email.parser import Parser
from pathlib import Path

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.tags import sys_tags

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'tests/fixtures/hg_wresolver2'
SOURCE = OUT / 'source'
INHERITED = json.loads((ROOT / 'tests/fixtures/hg_wresolver/inputs.json').read_text())

def digest(data):
    return hashlib.sha256(data).hexdigest()

sources = []

def preserve(origin, relative, data):
    dst = SOURCE / relative
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    item = {'origin': origin, 'preimage': str(dst.relative_to(ROOT)), 'bytes': len(data), 'sha256': digest(data)}
    sources.append(item)
    return item

repo_paths = [
    'data/datasets/jericho.py', 'data/datasets/jericho/verify/check.py',
    'data/datasets/jericho/lib/jer_env.py', 'data/datasets/reasoning_gym.py',
    'data/datasets/spreadsheetbench.py', 'data/datasets/spreadsheetbench/verify/check.py',
    'data/scaffolds/qa/base.py', 'data/scaffolds/qa/verify/check.py',
]
for p in repo_paths:
    preserve(p, 'repository/' + p, (ROOT / p).read_bytes())

members = {
    'jericho': ['jericho/__init__.py', 'jericho/jericho.py', 'jericho/util.py'],
    'reasoning-gym': ['reasoning_gym/__init__.py', 'reasoning_gym/algorithmic/__init__.py',
                      'reasoning_gym/algorithmic/game_of_life.py', 'reasoning_gym/algorithmic/game_of_life_halting.py'],
    'cellpylib': ['cellpylib/__init__.py', 'cellpylib/ca_functions.py'],
    'matplotlib': ['matplotlib/contour.py'],
    'openpyxl': ['openpyxl/__init__.py', 'openpyxl/xml/__init__.py', 'openpyxl/xml/functions.py'],
}
wheels = []
for key, wanted in members.items():
    art = next(a for a in INHERITED['artifacts'] if a['key'] == key)
    wheel = Path(art['source'])
    data = wheel.read_bytes()
    assert digest(data) == art['sha256'], (key, 'retained wheel differs from inherited digest')
    wheel_record = {'key': key, 'path': str(wheel), 'bytes': len(data), 'sha256': digest(data), 'members': []}
    with zipfile.ZipFile(wheel) as z:
        wanted += [n for n in z.namelist() if n.endswith('.dist-info/METADATA') or n.endswith('.dist-info/WHEEL')]
        for name in wanted:
            item = preserve(str(wheel) + ':' + name, 'wheels/' + key + '/' + name, z.read(name))
            wheel_record['members'].append(item)
    wheels.append(wheel_record)

runtime = {
    'executable': sys.executable, 'executable_sha256': digest(Path(sys.executable).read_bytes()),
    'sys_version': sys.version, 'implementation': platform.python_implementation(),
    'SOABI': sysconfig.get_config_var('SOABI'), 'system': platform.system(), 'machine': platform.machine(),
    'sys_tags': [str(t) for t in sys_tags()],
    'prior_runtime_preimage': 'tests/fixtures/hg_wresolver/raw/native-runtime.json',
    'scope': 'CPython 3.12 Linux x86_64 metadata resolver target; no production interpreter custody claim',
}
(SOURCE / 'runtime.json').write_text(json.dumps(runtime, indent=2, sort_keys=True) + '\n')

excerpts = []
def cite(origin, line, expected):
    record = next(x for x in sources if x['origin'] == origin or x['origin'].endswith(':' + origin))
    lines = (ROOT / record['preimage']).read_text().splitlines()
    actual = lines[line - 1]
    assert expected in actual, (origin, line, expected, actual)
    entry = {'origin': record['origin'], 'preimage': record['preimage'], 'line': line, 'text': actual,
             'locator': record['preimage'] + ':' + str(line)}
    excerpts.append(entry)
    return entry

profiles = [
    {'dataset': 'jericho', 'root_requirement': 'jericho==3.3.1', 'missing_requirement': 'spacy>=2.1.0',
     'import_site': cite('jericho/util.py', 42, 'import spacy'),
     'scorer_route': [cite('data/datasets/jericho.py', 257, 'python3'),
                      cite('data/datasets/jericho/verify/check.py', 49, 'import jer_env'),
                      cite('data/datasets/jericho/lib/jer_env.py', 38, 'from jericho import FrotzEnv')],
     'root_pin': cite('data/datasets/jericho.py', 305, '3.3.1'),
     'metadata_edge': cite('jericho-3.3.1.dist-info/METADATA', 12, 'Requires-Dist: spacy>=2.1.0'),
     'import_scope': 'spaCy is a lazy util dependency. The wrapper replay path calls env.step; this source audit does not execute a game or attest a spaCy import. The normal metadata edge remains required for dependency-aware resolution.',
     'separate_model_obligation': [cite('jericho/util.py', 44, 'spacy.load'), cite('jericho/util.py', 46, 'spacy.cli.download')]},
    {'dataset': 'reasoning_gym', 'root_requirement': 'reasoning-gym==0.1.25', 'missing_requirement': 'contourpy>=1.0.1',
     'import_site': cite('matplotlib/contour.py', 1507, 'import contourpy'),
     'scorer_route': [cite('data/datasets/reasoning_gym.py', 108, 'from reasoning_gym import create_dataset'),
                      cite('reasoning_gym/__init__.py', 7, 'algorithmic'),
                      cite('reasoning_gym/algorithmic/__init__.py', 16, 'from .game_of_life'),
                      cite('reasoning_gym/algorithmic/game_of_life.py', 6, 'import cellpylib'),
                      cite('cellpylib/__init__.py', 12, 'from .ca_functions'),
                      cite('cellpylib/ca_functions.py', 1, 'import matplotlib.pyplot')],
     'root_pin': cite('data/datasets/reasoning_gym.py', 67, '0.1.25'),
     'metadata_edges': [cite('reasoning_gym-0.1.25.dist-info/METADATA', 16, 'cellpylib==2.4.0'),
                        cite('cellpylib-2.4.0.dist-info/METADATA', 18, 'matplotlib>=3.0.2'),
                        cite('matplotlib-3.8.4.dist-info/METADATA', 42, 'contourpy >=1.0.1')],
     'import_scope': 'Reasoning Gym eagerly imports game_of_life and cellpylib; contourpy is a deferred contour-operation import in retained Matplotlib. Matplotlib 3.8.4 is the retained candidate, not a root source pin. The normal contourpy metadata edge remains required even without calling contour operations.'},
    {'dataset': 'spreadsheetbench', 'root_requirement': 'openpyxl==3.1.2', 'missing_requirement': 'et-xmlfile',
     'import_site': cite('openpyxl/xml/functions.py', 36, 'from et_xmlfile import xmlfile'),
     'scorer_route': [cite('data/datasets/spreadsheetbench.py', 234, 'python3'),
                      cite('data/datasets/spreadsheetbench/verify/check.py', 169, 'import openpyxl'),
                      cite('data/datasets/spreadsheetbench/verify/check.py', 260, 'import openpyxl')],
     'root_pin': cite('data/datasets/spreadsheetbench.py', 285, '3.1.2'),
     'metadata_edge': cite('openpyxl-3.1.2.dist-info/METADATA', 26, 'Requires-Dist: et-xmlfile'),
     'branch': [cite('openpyxl/xml/functions.py', 13, 'if LXML is True'),
                cite('openpyxl/xml/functions.py', 27, 'else:'),
                cite('openpyxl/xml/__init__.py', 26, 'lxml_available() and lxml_env_set()')],
     'import_scope': 'et_xmlfile is imported on openpyxl\'s no-LXML branch. openpyxl declares et-xmlfile unconditionally and without a version bound; optional lxml availability does not remove the resolver metadata obligation.'},
]

excerpts.append(cite('data/datasets/jericho/lib/jer_env.py', 113, 'env.step(action)'))
acquired_candidates = []
for key, profile in zip(['spacy', 'contourpy', 'et-xmlfile'], profiles):
    md = (OUT / 'metadata' / key / 'METADATA').read_bytes()
    wh = (OUT / 'metadata' / key / 'WHEEL').read_bytes()
    md_record = preserve(str((OUT / 'metadata' / key / 'METADATA').relative_to(ROOT)),
                         'acquired-metadata/' + key + '/METADATA', md)
    wh_record = preserve(str((OUT / 'metadata' / key / 'WHEEL').relative_to(ROOT)),
                         'acquired-metadata/' + key + '/WHEEL', wh)
    headers = Parser().parsestr(md.decode())
    wheel_headers = Parser().parsestr(wh.decode())
    tags = wheel_headers.get_all('Tag', [])
    requirement = Requirement(profile['missing_requirement'])
    record = {'key': key, 'version': headers['Version'], 'requires_python': headers['Requires-Python'],
              'wheel_tags': tags, 'metadata': md_record, 'wheel': wh_record,
              'satisfies_required_version': headers['Version'] in requirement.specifier,
              'satisfies_current_python': platform.python_version() in SpecifierSet(headers['Requires-Python']),
              'matches_target_tag': bool(set(tags) & set(runtime['sys_tags']))}
    assert record['satisfies_required_version'] and record['satisfies_current_python'] and record['matches_target_tag'], record
    acquired_candidates.append(record)
result = {'method': 'Read current repository preimages and retained wheel members; no dependency imports, scorer execution, network, model, GPU, endpoint or runs access.',
          'profiles': profiles, 'wheels': wheels, 'sources': sources, 'runtime': runtime,
          'acquired_candidates': acquired_candidates}
(OUT / 'source-audit.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
with (SOURCE / 'excerpts.stdout.txt').open('w') as f:
    for x in excerpts:
        f.write(x['origin'] + ':' + str(x['line']) + '\n')
        f.write(x['locator'] + '\n')
        f.write(x['text'] + '\n\n')
    f.write('Fresh retained wheel digests:\n')
    for x in wheels:
        f.write(x['sha256'] + '  ' + x['path'] + '\n')
    f.write('Fresh runtime:\n' + json.dumps(runtime, indent=2, sort_keys=True) + '\n')
    f.write('Fresh acquired-candidate metadata/tag checks:\n' + json.dumps(acquired_candidates, indent=2, sort_keys=True) + '\n')
print(json.dumps({'profiles': profiles, 'wheels': [{k:v for k,v in x.items() if k != 'members'} for x in wheels],
                  'source_files': len(sources), 'acquired_candidates': acquired_candidates,
                  'runtime_identity': {k:v for k,v in runtime.items() if k != 'sys_tags'}}, indent=2, sort_keys=True))
