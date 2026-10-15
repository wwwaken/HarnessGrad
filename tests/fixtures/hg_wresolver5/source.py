"""Read only code_context import metadata, never reference_code/prompts or execute it."""
import ast
import importlib.metadata
import json
from pathlib import Path
import re
import sys
import warnings
from common import HERE, ROOT, digest, run, save

dataset = Path('/mnt/20t/xubuqiang/datasets/ds1000/_src')
release = dataset/'DS-1000-b39aab71'
mapping = {'PIL':'pillow', 'sklearn':'scikit-learn', 'tensorflow':'tensorflow-cpu',
           'yaml':'PyYAML', 'torch':'torch'}
sites = {}
rows = 0
errors = []
# Discard non-context fields immediately; no prompt, reference or test body is exported.
def context_only(pairs):
    return {k:v for k,v in pairs if k == 'code_context'}
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    for row, line in enumerate((dataset/'test.jsonl').open(), 1):
        context = json.loads(line, object_pairs_hook=context_only)['code_context']
        rows += 1
        try:
            tree = ast.parse(context)
        except SyntaxError as exc:
            errors.append(dict(jsonl_line=row, exception=type(exc).__name__, message=str(exc)))
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level:
                modules = [node.module] if node.module else []
            else:
                continue
            for module in modules:
                root = module.split('.')[0]
                if root not in sys.stdlib_module_names:
                    sites.setdefault(root, []).append(dict(jsonl_line=row, context_line=node.lineno,
                                                          import_module=module))
    warning_records = [{'category':w.category.__name__, 'message':str(w.message)} for w in caught]
assert not errors, errors
environment = (release/'environment.yml').read_text()
pins = dict(re.findall(r'^  - ([\w-]+)==([\w.]+)$', environment, re.M))
torch_pin = re.search(r'pytorch::pytorch==([\w.]+)', environment).group(1)
tensorflow_pin = re.search(r'tensorflow-cpu==([\w.]+)', environment).group(1)
roots = [f'{name}=={version}' for name, version in sorted(pins.items())]
roots += [f'torch=={torch_pin}', f'tensorflow-cpu=={tensorflow_pin}']
observed = {}
for module in sorted(sites):
    dist = mapping.get(module, module)
    if dist.lower() not in {r.split('==')[0].lower() for r in roots}:
        version = importlib.metadata.version(dist)
        observed[dist] = dict(version=version, policy='Fresh host observation for source-unpinned import; not an upstream pin or installed-image claim')
        roots.append(f'{dist}=={version}')
profile = HERE/'profile'
profile.mkdir(exist_ok=True)
assert not (profile/'roots.in').exists()
(profile/'roots.in').write_text('\n'.join(sorted(roots))+'\n')
sources = []
for path in [ROOT/'data/datasets/ds1000.py', ROOT/'data/datasets/ds1000/verify/check.py',
             release/'environment.yml', release/'execution.py']:
    text = path.read_text()
    excerpts = [dict(line=i, text=l) for i,l in enumerate(text.splitlines(),1)
                if re.search(r'code_context|exec\(|import |^  - |^      - |^channels:|^  - defaults|^name:', l)]
    sources.append(dict(path=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                        sha256=digest(path), bytes=path.stat().st_size, excerpts=excerpts))
record = dict(selection_rule='Remaining nonempty datasets only. DS1000: first derive static import roots from every released code_context with a metadata-only AST pass, retain exact upstream Python 3.10/minor and all declared version pins; resolve the finite Python metadata union if a faithful named mapping is available. Terminal-Bench gets a separate bounded deterministic bootstrap selection. Nine stdlib-only routes are audited, never empty-solved.',
              scope='All released context static imports plus upstream declared Python roots. No candidate-dependent imports, task execution, gold/reference/prompt export, or Conda/native/image equivalence.',
              dataset_source=dict(path=str(dataset/'test.jsonl'), sha256=digest(dataset/'test.jsonl'), bytes=(dataset/'test.jsonl').stat().st_size),
              rows=rows, syntax_errors=errors, syntax_warnings=warning_records,
              import_roots={k:dict(distribution=mapping.get(k,k), import_site_count=len(v), first_sites=v[:4]) for k,v in sorted(sites.items())},
              roots=sorted(roots), observed_unpinned=observed, sources=sources,
              pytorch_mapping='Conda pytorch::pytorch==2.2.0 + cpuonly is represented ONLY for Python metadata by official torch==2.2.0+cpu wheel, satisfying original ==2.2.0 under PEP440. cpuonly is a Conda selector, not an importable Python distribution. No CUDA wheel/substitute version/native Conda equivalence is asserted.',
              yaml_mapping='environment.yml yaml is a native Conda libyaml requirement, retained as a native gap; actual code_context import yaml maps to PyYAML. All other Python module/distribution aliases are explicit.')
save(HERE/'source.json', record)
run('source-sha256sum', ['sha256sum', dataset/'test.jsonl', *[ROOT/s['path'] if not Path(s['path']).is_absolute() else s['path'] for s in sources]])
print(json.dumps(record, indent=2, sort_keys=True))
