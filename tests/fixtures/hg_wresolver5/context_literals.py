"""Audit parseable code_context string imports without exporting task contents."""
import ast
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
import warnings
from common import HERE, digest, save

calls=Counter()
sites={}
source=Path('/mnt/20t/xubuqiang/datasets/ds1000/_src/test.jsonl')
def context_only(pairs):
    return {k:v for k,v in pairs if k=='code_context'}
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    for row,line in enumerate(source.open(),1):
        tree=ast.parse(json.loads(line,object_pairs_hook=context_only)['code_context'])
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                name=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else ''
                if name in ['exec','eval','__import__','import_module','compile']:
                    calls[name]+=1
            if isinstance(node,ast.Constant) and isinstance(node.value,str) and ('import ' in node.value or 'from ' in node.value):
                try:
                    literal=ast.parse(node.value)
                except (SyntaxError,ValueError):
                    continue
                for child in ast.walk(literal):
                    modules=[a.name for a in child.names] if isinstance(child,ast.Import) else [child.module] if isinstance(child,ast.ImportFrom) and child.module else []
                    for module in modules:
                        sites.setdefault(module.split('.')[0],[]).append(dict(jsonl_line=row,outer_context_line=node.lineno,literal_line=child.lineno,module=module))
aliases={'mpl_toolkits':'matplotlib','sklearn':'scikit-learn','tensorflow':'tensorflow-cpu'}
roots={r.split('==')[0].lower() for r in (HERE/'profile/roots.in').read_text().splitlines()}
external={k:v for k,v in sites.items() if k not in sys.stdlib_module_names}
assert all(aliases.get(module,module).lower() in roots for module in external)
result=dict(source_sha256=digest(source),dynamic_call_counts=dict(calls),
     literal_import_roots={k:dict(import_site_count=len(v),first_sites=v[:3],distribution=aliases.get(k,k) if k not in sys.stdlib_module_names else 'stdlib') for k,v in sorted(sites.items())},
     extra_external_distributions_outside_declared_roots=[],
     scope='Metadata-only AST of all code_context and parseable import-containing string constants. No gold, prompt, candidate execution or task contents exported. All literal external imports are already covered, including mpl_toolkits -> matplotlib and statsmodels. Arbitrary candidate-dependent exec/eval imports are outside finite declared-root reconstruction.')
save(HERE/'context-literals.json',result)
print(json.dumps(result,sort_keys=True,indent=2))
