#!/usr/bin/env python3
"""Build review indexes from observed packet records; never fill unknown identities."""
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect import OUT, BASE, TARGETS, norm, write, write_chunks


def read(pattern):
    return [(json.loads(l), f'{f.relative_to(Path.cwd())}:{n}')
            for f in sorted(OUT.glob(pattern)) for n, l in enumerate(f.read_text().splitlines(), 1)]


def cite(ref):
    return '`' + ref + '`'


sources = read('source-modules.jsonl')
source_edges = read('source-edges.jsonl')
selected = read('selected-distributions.jsonl')
candidates = read('candidates-*.jsonl')
smoke = read('smoke-base.jsonl')
tree_smoke = read('smoke-tree.jsonl')
elfs = read('elf-*.jsonl')
owners = read('native-owners.jsonl')
smoke_paths = {r['module']: (r, ref) for r, ref in smoke if r['kind'] == 'requested-import'}

# Resolve explicit modules to already-read source modules only. Never call a loader.
known = {r['module']: r['path'] for r, ref in sources}
for r, ref in read('installed-edges-*.jsonl'):
    known[r['module']] = r['path']
observed = {r['module']: r for r, ref in smoke if r['kind'] == 'observed-module'}
frontier, resolved = [], []
for group, ref in read('installed-edges-*.jsonl'):
    module = group['module']
    package = module if Path(group['path']).name == '__init__.py' else module.rpartition('.')[0]
    for edge in group['edges']:
        if 'to' not in edge:
            frontier.append({'from': module, 'state': 'UNKNOWN dynamic call targets',
                             'edge': edge, 'source': f"{group['path']}:{edge['line']}"})
            continue
        target = edge['to']
        if target.startswith('.'):
            try:
                target = importlib.util.resolve_name(target, package)
            except (ValueError, ImportError):
                pass
        state = 'FOUND read source' if target in known else (
            'FOUND observed origin; source graph UNKNOWN' if target in observed else 'UNKNOWN uninspected target')
        row = {'from': module, 'to': target, 'names': edge.get('names', []),
               'state': state, 'source': f"{group['path']}:{edge['line']}",
               'scope': edge.get('scope'), 'guards': edge.get('guards'),
               'resolution_rule': 'explicit module only; from-import symbols not assumed to be submodules'}
        if target not in known:
            frontier.append(row)
groups = {}
for row in frontier:
    target = row.get('to', row.get('edge', {}).get('dynamic_call', '<unknown>'))
    key = (target, row['state'])
    group = groups.setdefault(key, {'target': target, 'state': row['state'], 'source_edge_locations': []})
    source_path, line = row['source'].rsplit(':', 1)
    group['source_edge_locations'].append({'module': row['from'], 'line': int(line)})
write_chunks('module-frontier', list(groups.values()))
for old in OUT.glob('module-resolved-*.jsonl'):
    old.unlink()
write('module-resolution-index.jsonl', [{'module': k, 'read_path': v} for k, v in sorted(known.items())])

summary = {
    'retained_python_files': len(sources),
    'all_source_hashes_match_prior_inventory': all(r['matches_prior_inventory'] for r, ref in sources),
    'source_import_edges': sum('to' in r for r, ref in source_edges),
    'source_dynamic_call_sites': sum('dynamic_call' in r for r, ref in source_edges),
    'selected_distribution_records': len(selected),
    'selected_found_metadata': sum('version' in r for r, ref in selected),
    'metadata_dependency_edges': len(read('metadata-edges.jsonl')),
    'read_installed_python_files_with_edges': len(read('installed-edges-*.jsonl')),
    'read_installed_import_or_dynamic_sites': sum(len(r['edges']) for r, ref in read('installed-edges-*.jsonl')),
    'candidate_records': len(candidates),
    'elf_files_inspected': len(elfs),
    'native_needed_edges': len(read('native-links.jsonl')),
    'native_exact_conda_archive_matches': sum(isinstance(o['archive_to_installed_member_binding'], dict) and
        o['archive_to_installed_member_binding']['matches'] for r, ref in owners for o in r['owners']),
    'native_conda_archive_mismatches': sum(isinstance(o['archive_to_installed_member_binding'], dict) and
        not o['archive_to_installed_member_binding']['matches'] for r, ref in owners for o in r['owners']),
    'official_scorer_executed': False, 'production_authorized': False,
    'closure_complete': False, 'exact_compiled_build_interpreters': 'UNKNOWN',
}
write('summary.jsonl', [summary])

# Verbatim license text evidence with conservative text identifiers, not inferred package SPDX.
def license_kind(text):
    if not text.strip():
        return 'EMPTY; no license established'
    if 'Intel Simplified Software License' in text:
        return 'Intel Simplified Software License (see full terms)'
    if 'A. HISTORY OF THE SOFTWARE' in text and 'PYTHON SOFTWARE FOUNDATION LICENSE' in text:
        return 'Python license stack (full history/terms retained)'
    if 'GNU LESSER GENERAL PUBLIC LICENSE' in text:
        return 'LGPL text (version in retained file; scope must be established)'
    if 'Academic Free License' in text:
        return 'MIT OR AFL-2.1 (dual-license statement in text)'
    if 'Zope Public License' in text:
        return 'ZPL (version in text)'
    if 'Mozilla Public License' in text or 'MPL-2.0' in text:
        return 'MPL terms or notice (full text/scope must be checked)'
    if 'GNU GENERAL PUBLIC LICENSE' in text:
        return 'GPL text, possibly with runtime exception (read full terms)'
    if 'Apache License' in text or 'Apache Software License 2.0' in text:
        return 'Apache-2.0 text; check bundled/dual-license clauses'
    if 'Permission is hereby granted, free of charge' in text or 'Permission is hereby granted, without written agreement' in text:
        return 'permissive permission text; retain exact copyright/conditions'
    if 'Redistribution and use in source and binary forms' in text:
        return 'BSD-style redistribution conditions (exact clause count in text)'
    if 'zlib License' in text or "This software is provided 'as-is'" in text:
        return 'zlib-style text; retain exact conditions'
    if 'either' in text and 'license' in text.lower():
        return 'dual-license selector; linked license texts required'
    return 'notice/custom/mixed terms; exact identifier UNKNOWN'

license_rows = []
for pattern in ('licenses.jsonl', 'archive-licenses.jsonl', 'native-licenses.jsonl'):
    for r, ref in read(pattern):
        p = r.get('retained_path')
        text = Path(p).read_text(errors='replace') if p else ''
        license_rows.append({'name': r['name'], 'version': r.get('version'),
                             'retained_path': p, 'sha256': r.get('retained_sha256', r.get('sha256')),
                             'source_evidence': ref, 'text_identifier': license_kind(text),
                             'license_scope': 'bound to exact source record/archive; not all builds or versions'})
write('license-index.jsonl', license_rows)

lines = ['# w-bfclrt: offline runtime custody', '',
         'Disposition: **blocker stays external/open; exact runtime closure remains incomplete.**', '',
         'The packet binds the retained Python source imports and a bounded local candidate runtime. '
         'It does not establish a runnable official scorer or select a local-model handler. '
         'Only offline imports and static inspection were performed; no differential, inference, GPU use, '
         'or official scorer execution was performed (test scope: '
         '`tests/fixtures/hg_bfclrt/smoke.py:1`; disposition/counts: `tests/fixtures/hg_bfclrt/summary.jsonl:1`).', '',
         '## Evidence states and exact search scope', '',
         '**FOUND** means the cited bytes/metadata/import were read. **ABSENT** always means absent '
         'from the enumerated search scope below, not the whole machine. **UNKNOWN** includes '
         'unread/opaque artifacts, source branches beyond the recorded frontier, exact build provenance, '
         'and compatibility not actually exercised. Installed trees, cached wheels, conda archives, '
         'and loaded ELF objects are separate artifacts; a shared package/version is not a byte binding.', '',
         'Reproduce the bounded search with `export TMPDIR=/mnt/20t/xubuqiang/hg-work/bfclrt/tmp; '
         'export PYTHONDONTWRITEBYTECODE=1; python3 -B -u tests/fixtures/hg_bfclrt/collect.py search`. '
         'The exact enumerated paths and outcomes follow; symlink aliases of site directories are deduplicated. '
         'Non-ZIP pip response bodies were enumerated but not unpacked; their package contents are UNKNOWN. '
         'Other users, other wheelhouses, unenumerated environments, unnamed source archives, and symlinked '
         'cache subtrees are UNKNOWN. No whole-machine absence is asserted.', '',
         '| Scope | What was read | Observation | Evidence |', '|---|---|---|---|']
for r, ref in read('search-scope.jsonl'):
    obs = f"{r['entries']} metadata entries" if 'entries' in r else (
        f"{r['files_enumerated']} files; {r['zip_wheels_or_bodies_inspected']} ZIP wheel/bodies; "
        f"{r['opaque_nonzip_bodies_not_unpacked']} opaque bodies; {len(r['errors'])} errors")
    lines.append(f"| `{r['path']}` | {r['method']} | {obs} | {cite(ref)} |")
lines += ['', '## Source graph: exact syntactic edges, guarded branches kept separate', '',
          'All retained source identities are recomputed in `source-modules.jsonl`; every explicit '
          'import statement is in `source-edges.jsonl`, with verbatim statement, original `file:line`, '
          'containing function/class and if/try guards. Each line is an edge record, not a guessed '
          'runtime execution. Package initializers are retained source members. The packet does not '
          'invent dynamic targets or equate a metadata dependency with a Python import. Counts and '
          'prior-inventory equality: `tests/fixtures/hg_bfclrt/summary.jsonl:1`.', '',
          'The checker imports `MODEL_CONFIG_MAPPING` eagerly, whose imports pull every retained '
          'provider/local handler into the module import graph. Selecting Simple/Python does not '
          'remove those import statements. The runner/helper import the same mapping. The parser '
          'utility eagerly imports both language parsers and tenacity. Their module-level '
          '`Language(..., name)` and `Parser.set_language` calls require the old Tree-sitter API; '
          'the installed 0.24.0 smoke records `Parser_has_set_language=false`.', '',
          '| Important edge | Original source citation |', '|---|---|']
key_modules = {'bfcl_eval.eval_checker.ast_eval.ast_checker', 'bfcl_eval.eval_checker.eval_runner',
               'bfcl_eval.eval_checker.eval_runner_helper', 'bfcl_eval.model_handler.utils',
               'bfcl_eval.model_handler.parser.java_parser', 'bfcl_eval.model_handler.parser.js_parser',
               'bfcl_eval.model_handler.base_handler', 'bfcl_eval.model_handler.local_inference.base_oss_handler'}
for r, ref in source_edges:
    if r['from'] in key_modules and 'to' in r:
        lines.append(f"| `{r['from']}` → `{r['to']}` ({' / '.join(r['scope']) or 'module scope'}) | {cite(r['source'])}; {cite(ref)} |")
lines += ['', 'Full dispatch edges (including each handler) are explicitly enumerated in the source-edge '
          'packet; the per-requirement table below cites each external root edge. '
          'Multi-turn dynamic imports and expression-evaluation call sites remain branch-specific '
          'unresolved behavior, recorded verbatim in `source-edges.jsonl`. No expression was evaluated '
          'by this worker.', '',
          'Third-party recursion is represented in two distinct ways: `metadata-edges.jsonl` gives '
          'each Requires-Dist header with original metadata file/line, marker and requested extras; '
          '`installed-edges-*.jsonl` gives imports read from actually observed Python files plus '
          'the unexecuted transformers/wandb entry files. Each grouped edge has its original source '
          'path/line. `module-resolution-index.jsonl` lists the read module-to-path map; '
          '`module-frontier-*.jsonl` explicitly lists unread targets and dynamic calls as UNKNOWN. '
          'This is a bounded graph with an exact frontier, not a complete transitive runtime claim. '
          'From-import symbol names are preserved and are not assumed to be child modules. '
          'The traversal/marker rules are executable in `collect.py` and `summarize.py`.', '',
          '## Python and native identity', '']
for rows, label in ((smoke, 'Base observation'), (tree_smoke, 'Tree-sitter alternative observation')):
    r, ref = next((r, ref) for r, ref in rows if r['kind'] == 'interpreter')
    lines += [f"**{label}** ({cite(ref)}):", '',
              f"- Executable `{r['executable']}`; SHA-256 `{r['executable_sha256']}`.",
              f"- `sys.version`: `{r['version']}`.",
              f"- `sys.implementation`: `{json.dumps(r['implementation'], sort_keys=True)}`.",
              f"- Platform `{r['platform']}`; SOABI `{r['config']['SOABI']}`; extension suffix `{r['config']['EXT_SUFFIX']}`.",
              '- Full compiler/configuration strings are retained in the cited record. These identify '
              'the executing interpreter, not the interpreter that built every installed extension.', '']
lines += ['ELF objects are SHA-256 bound in `elf-*.jsonl`, with exact `LC_ALL=C readelf -h -d '
          '-p .comment PATH` output and the version-needs excerpt from `readelf -V PATH`. '
          '`native-links.jsonl` records each DT_NEEDED edge and same-process mapped SONAME/name '
          'candidates. A unique mapped candidate is not proof of an individual relocation binding. '
          '`/proc/self/maps` observations appear at the end of each smoke record. '
          'Exact compiled-member build Python patch version, full toolchain and reproducible build '
          'provenance remain UNKNOWN; wheel tags/ELF architecture/.comment do not prove them.', '',
          'Conda metadata path membership can be stale after pip upgrades. `native-owners.jsonl` '
          'separately records local archive hashes and streaming comparisons of actual archive members '
          'against installed native bytes. A false `matches` value is an observed mismatch, not custody. '
          'A true value binds those exact bytes; prefix-patched files may differ and require their own '
          'documented transformation. These comparisons do not reconstruct an environment.', '',
          '| Needed linked-library name | ELF evidence with a recorded edge |', '|---|---|']
for name in sorted(set(n for r, ref in elfs for n in r['needed'])):
    r, ref = next((r, ref) for r, ref in elfs if name in r['needed'])
    lines.append(f'| `{name}` | {cite(ref)} |')

lines += ['', '## Direct requirements: artifact and import state', '',
          'Pins below are read from the retained pyproject and import edges, not newly chosen versions. '
          '`transformers` is an OSS batch-inference function import; `wandb` is guarded by the '
          'leaderboard logging option. They are recorded but were not imported by the smoke. '
          'Only one representative local artifact per member is shown; the complete candidate inventory '
          'contains every observed filename, version, SHA-256, WHEEL tags and metadata dependencies.', '',
          '| Requirement | FOUND/ABSENT/UNKNOWN and exact representative artifact | Import/source evidence |',
          '|---|---|---|']
root_to_dist = {'dotenv': 'python-dotenv', 'tree_sitter': 'tree-sitter',
                'tree_sitter_java': 'tree-sitter-java', 'tree_sitter_javascript': 'tree-sitter-javascript',
                'google': 'google-genai', 'qwen_agent': 'qwen-agent', 'writerai': 'writer-sdk',
                'datamodel_code_generator': 'datamodel-code-generator'}
from packaging.specifiers import SpecifierSet
pyproject = Path('tests/fixtures/bfcl_ast_source/candidate-codex195/files/berkeley-function-call-leaderboard/pyproject.toml')
pin_refs = {}
for number, text in enumerate(pyproject.read_text().splitlines(), 1):
    quoted = text.split(chr(34))
    declared = quoted[1] if len(quoted) > 1 else ''
    declared_name = norm(re.split('[<>=!~\[]', declared)[0])
    for name in TARGETS:
        if declared_name == name:
            pin_refs[name] = str(pyproject) + ':' + str(number)
direct_rows = []
for name, requirement in TARGETS.items():
    cs = [(r, ref) for r, ref in candidates if norm(r.get('name', '')) == name]
    constraint = requirement.split()[0] if requirement and requirement[0] in '<>=!~' else ''
    exact = [(r, ref) for r, ref in cs if not constraint or r['version'] in SpecifierSet(constraint)]
    wheels = [(r, ref) for r, ref in exact if r['kind'] == 'wheel-or-zip-body']
    installs = [(r, ref) for r, ref in exact if r['kind'] == 'installed-tree']
    state = 'FOUND identified artifact' if exact else 'ABSENT identified exact member in enumerated scope; UNKNOWN opaque/unsearched scope'
    chosen = (wheels or installs or cs)
    artifact = ''
    if chosen:
        r, ref = chosen[0]
        if 'path' in r:
            artifact = f"`{r['path']}` SHA-256 `{r['sha256']}` ({r.get('version')}; {cite(ref)})"
        else:
            artifact = f"installed metadata `{r['metadata']['path']}` SHA-256 `{r['metadata']['sha256']}` ({r['version']}; {cite(ref)})"
        if not exact:
            artifact = 'FOUND different-version alternative only: ' + artifact
    else:
        artifact = 'No identified candidate; artifact digest unobserved.'
    edge_refs = [r['source'] for r, ref in source_edges if 'to' in r and
                 root_to_dist.get(r['to'].split('.')[0], r['to'].split('.')[0]) == name]
    edge_ref = '; '.join(cite(x) for x in edge_refs[:3])
    if name in pin_refs:
        edge_ref += '; pin ' + cite(pin_refs[name])
    direct_rows.append({'name': name, 'requirement': requirement, 'state': state,
                        'exact_identified_candidates': len(exact), 'all_identified_candidates': len(cs),
                        'source_edges': edge_refs, 'opaque_or_unsearched_scope': 'UNKNOWN'})
    lines.append(f"| `{name}{requirement}` | **{state}**. {artifact} | {edge_ref} |")
write('direct-status.jsonl', direct_rows)
gaps = []
for r in direct_rows:
    if not r['exact_identified_candidates']:
        gaps.append({'kind': 'direct member', 'name': r['name'], 'constraint': r['requirement'],
                     'state': r['state'], 'exact_filename': 'UNKNOWN', 'sha256': 'UNOBSERVED',
                     'artifact_to_close': 'version-matched wheel with observed tags or complete source/build prerequisites, '
                     'member digests, source graph and license/NOTICE; CPython 3.12/Linux x86_64 if binary',
                     'source_edges': r['source_edges']})
for r in groups.values():
    gaps.append({'kind': 'unresolved import/dynamic target', 'target': r['target'],
                 'state': r['state'], 'distribution': 'UNKNOWN; bare import is not a distribution identity',
                 'version': 'UNKNOWN', 'exact_filename': 'UNKNOWN', 'sha256': 'UNOBSERVED',
                 'artifact_to_close': 'source/stdlib/module implementation containing this exact target, '
                 'choose branch and resolve import symbols before identifying wheel/source artifact; '
                 'measure SHA-256 and license; compiled target needs host-compatible ABI/build evidence',
                 'source_edge_locations': r['source_edge_locations']})
for r, ref in elfs:
    gaps.append({'kind': 'compiled build identity', 'member': r['path'],
                 'sha256': r['sha256'], 'state': 'UNKNOWN exact build interpreter/toolchain',
                 'artifact_to_close': 'build manifest bound to this SHA-256 with exact Python implementation/version/ABI, '
                 'target platform/toolchain, source versions and linked/dlopen library hashes and licenses',
                 'evidence': ref})
for r, ref in selected:
    if not r.get('version'):
        continue
    if not any(a['kind'] == 'wheel-or-zip-body' and norm(a.get('name', '')) == r['name'] and
               a.get('version') == r['version'] for a, ar in candidates):
        gaps.append({'kind': 'matching wheel archive unresolved', 'name': r['name'],
                     'version': r['version'], 'state': 'UNKNOWN original wheel/member binding; see native conda comparisons',
                     'sha256': 'UNOBSERVED wheel archive', 'exact_filename': 'UNKNOWN',
                     'artifact_to_close': 'exact matching original wheel or verified conda/source artifact '
                     'and installed-member transformation; do not infer wheel digest from RECORD', 'evidence': ref})
write_chunks('runtime-gaps', gaps)
lines += ['', 'Resolved import paths/hashes and exact import failures are in '
          '`smoke-base.jsonl` and `smoke-tree.jsonl`. The base smoke imports NumPy/Pandas and '
          'available SDK utilities; it does not run `eval_runner`, construct a model handler, '
          'parse fabricated calls, or execute a checker. The newer Tree-sitter alternative '
          'imports successfully but both BFCL parser imports fail for missing grammar modules. '
          'The old API mismatch is independently visible without constructing a language.', '',
          '## Every selected transitive/observed distribution', '',
          'This table includes direct roots, evaluated metadata dependencies and owners of optional '
          'modules actually observed during the smoke. It is not a minimal required package set. '
          'An original archive is UNKNOWN when no matching version is identified, even if the installed '
          'module bytes are FOUND. Exact archived filenames/hashes and ABI tags are in the cited records.', '',
          '| Member/version | Installed metadata identity | Matching wheel/archive identity |', '|---|---|---|']
for r, ref in selected:
    name, version = r['name'], r.get('version')
    found = [(a, ar) for a, ar in candidates if a['kind'] == 'wheel-or-zip-body' and
             norm(a.get('name', '')) == name and a.get('version') == version]
    if version:
        installed = f"FOUND `{r['metadata']['sha256']}`; {cite(ref)}"
    else:
        installed = f"ABSENT selected-site metadata; {cite(ref)}"
    archive = '; '.join(f"FOUND `{a['path']}` SHA-256 `{a['sha256']}`; {cite(ar)}" for a, ar in found[:1]) or 'UNKNOWN matching original wheel; see conda candidates/owners for independently bound native members'
    lines.append(f"| `{name}` {version or '(version unobserved)'} | {installed} | {archive} |")

lines += ['', '## Licenses/notices bound to bytes actually read', '',
          '`license-index.jsonl` inventories each retained license/notice text, its source '
          'record/archive member, exact hash and conservative text identifier. `licenses.jsonl`, '
          '`archive-licenses.jsonl` and `native-licenses.jsonl` distinguish installed, wheel and '
          'conda/system sources. Copies preserve verbatim text; an empty license directory entry '
          'establishes no license. Licenses of wrong-version packages do not satisfy missing pins. '
          'Conda licenses for stale mismatching package members do not license replacement bytes.', '',
          '| Selected member | License text evidence |', '|---|---|']
for r, ref in selected:
    found = [(a, ar) for a, ar in read('license-index.jsonl') if a['name'] == r['name'] and
             a.get('version') in (None, r.get('version')) and a.get('retained_path')]
    entries = []
    seen_text = set()
    for a, ar in found:
        if a['sha256'] in seen_text:
            continue
        if not Path(a['retained_path']).read_text(errors='replace').strip():
            continue
        seen_text.add(a['sha256'])
        entries.append(cite(a['retained_path'] + ':1') + ' (' + a['text_identifier'] + ')')
    lines.append(f"| `{r['name']}` {r.get('version', '')} | " + ('; '.join(entries) if entries else
                 'UNKNOWN compatible license text; selected metadata/RECORD and matching archive inventory were inspected') + ' |')
lines += ['', 'Operational notice obligations, limited to the texts actually bound:', '',
          '- Apache-2.0 texts require retaining license/attribution notices, marking modified files '
          'and reproducing applicable NOTICE contents; actual Boto3/Botocore/S3transfer notices are '
          'separate retained files. Patent terms remain in the full text.',
          '- MIT/BSD-style texts require preserving copyright, permission/conditions and disclaimers; '
          'BSD no-endorsement clauses apply where present. Tqdm has its own dual-license and '
          'derived-work conditions, not a single blanket MIT assumption.',
          '- NumPy wheel license text also identifies bundled OpenBLAS/LAPACK/GCC runtime and other '
          'licenses; the installed MKL variant has separate Intel terms. Redistribution of a chosen '
          'variant must carry that variant’s licenses/notices. System and conda licenses are not interchangeable.',
          '- MPL/LGPL/GPL/PSF/custom or dual-license material requires the exact applicable text, '
          'source/relinking/exception conditions and component scope, rather than replacing it with '
          'the top-level distribution identifier. This packet inventories texts; it does not certify '
          'redistribution compliance.', '',
          'For the basis of those obligations and mixed terms, see the per-member verbatim files above '
          'and `license-index.jsonl`; native/license source bindings appear in `native-owners.jsonl`. '
          'Licenses/notices of missing pinned Tree-sitter/grammars/SDKs and unresolved transitive or '
          'dynamic members are UNKNOWN. Full license scope of some bundled native objects remains '
          'UNKNOWN even where a top-level LICENSE was found. System notice lookup scope is exactly '
          '`native-license-search.jsonl`.', '',
          '## Concrete remaining closure gap (no public-availability assertion)', '',
          'The following is a required-artifact specification, not an invented filename or digest. '
          'Every newly supplied artifact needs its observed filename, bytes, SHA-256, module-member '
          'hashes, matching license/NOTICE and transitive requirements. Digests of missing artifacts '
          'are unobserved and must be measured from the actual bytes. Exact version is intentionally '
          'UNKNOWN where upstream specifies only a range or no version.', '',
          '| Missing/unresolved member | Exact constraint/artifact that would close this member | State evidence |', '|---|---|---|']
for r, ref in read('direct-status.jsonl'):
    if r['exact_identified_candidates']:
        continue
    name = r['name']
    native = name.startswith('tree-sitter')
    spec = (f"{name}{r['requirement']}; CPython 3.12 Linux x86_64 compatible binary "
            '(e.g. cp312-cp312 compatible manylinux tag, or a proven compatible abi3 tag), '
            'or complete source/build prerequisites and a measured build; grammar language ABI/API '
            'must work with tree_sitter 0.21.3') if native else (
            f"{name}{r['requirement']}; exact version " + ('is the stated pin' if r['requirement'].startswith('==') else
            'UNKNOWN until a concrete version is selected') +
            '; py3-none-any only if actually tagged pure Python, otherwise CPython 3.12/Linux x86_64 compatible binary; full transitive artifact/license graph')
    lines.append(f"| `{name}` | {spec}; actual filename and SHA-256 must be observed | {cite(ref)}; search scope above |")
lines += [
    '| Exact transitive import graph behind missing members | Read the actual chosen missing package/version sources and metadata recursively. Every unresolved explicit module/dynamic call is enumerated in `module-frontier-*.jsonl`; no version or distribution is guessed from a bare module name. | `module-frontier-*.jsonl`; `metadata-edges.jsonl` |',
    '| Available tree artifacts without original archive/member binding | Matching local wheel/conda archive plus member-byte comparison; the distribution/version table and native-owner rows list the current FOUND/UNKNOWN states. Preserve existing hashes rather than reacquiring established source custody. | Tables above; `native-owners.jsonl` |',
    '| Compiled build provenance and ABI closure | Build manifest bound to each chosen ELF/wheel hash, exact build CPython implementation/version/SOABI/target/toolchain and grammar ABI, all DT_NEEDED/dlopen libraries and symbol-version requirements. Current host identity and ELF requirements are already recorded; exact build interpreter remains UNKNOWN. | `elf-*.jsonl`; `native-links.jsonl`; `archive-native-*.jsonl`; smoke record line 1 |',
    '| Native/transitive license scope | Missing version-matched license/NOTICE texts and bundled-component scope/binding; satisfy the obligations of the selected variant (wheel/OpenBLAS versus installed/MKL), not a mixed environment. | `license-index.jsonl`; `native-owners.jsonl`; `native-license-search.jsonl` |',
    '| Handler-dependent branch closure | A concrete local-model handler/model-config/response-grammar binding is still unselected; batch tokenizer/model assets, transformers optional runtime and wandb logging are branch-dependent. Do not infer a deployment or start a server from an import graph. | Original function/guard citations in `source-edges.jsonl`; `direct-status.jsonl` |',
    '',
    'The parent proposal retains the actual technical source/selected-only/full-call/containment and '
    'official-execution work. It does not reinstate withdrawn shared `scorer-offline-closure` or '
    '`artifact-only-state-export` requirements (operator record: '
    '`registry/withdrawn-requirements.md:18`; `registry/withdrawn-requirements.md:44`). '
    'No registry or journal is edited by this worker.', '',
    'Validation dependency: this starting worktree lacks four registry evidence files. '
    'The initial checker failed; the exact four existing Git-object bytes from '
    '`f8f9eb82220ee2fda0b689bdfc62513b08586423` were restored locally, without '
    'committing them or changing the registry. Their identities are in '
    '`tests/fixtures/hg_bfclrt/baseline-restoration.jsonl:1` and the following three lines. '
    'The parent must preserve/integrate that independent baseline repair for a clean '
    'checkout to pass; this commit alone does not supply those four files. '
    'Exact initial/final checker results are in `registry/w-bfclrt-validation.txt`.', '',
    'The per-target machine-readable gap inventory is `runtime-gaps-*.jsonl`: it names every '
    'unresolved explicit/dynamic target, missing direct member, unbound original wheel and '
    'compiled build-identity requirement, without inventing distribution/version/digest values.', '',
    'Most important review uncertainty: the bounded imported-source/metadata graph is not the exact '
    'complete runtime closure of a chosen handler. Missing pinned packages, unread frontier branches, '
    'native build identities and variant-specific bindings must not be treated as satisfied by '
    'successful imports or by installed metadata.', '']
Path('registry/w-bfclrt-custody.md').write_text('\n'.join(lines))
print('registry/w-bfclrt-custody.md: written from observed records')
