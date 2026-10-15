"""Derive finite test.sh bootstrap roots; never execute or retain test bodies."""
import ast
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys
from common import HERE, digest, run, save

upstream=Path('/mnt/20t/xubuqiang/datasets/terminal-bench')
seen=set(); selected=[]; audit=[]
for task in sorted(p for p in upstream.iterdir() if p.is_dir() and (p/'task.toml').is_file()):
    script=task/'tests/test.sh'
    if not script.is_file(): continue
    lines=script.read_text().splitlines()
    declarations=[]
    for lineno,line in enumerate(lines,1):
        if re.match(r'^pip install ',line):
            tokens=shlex.split(line)[2:]
            pins=[t for t in tokens if not t.startswith('--')]
            if pins and all(re.fullmatch(r'[A-Za-z0-9_.-]+==[^\s]+',p) for p in pins):
                declarations.append({'line':lineno,'text':line,'pins':pins})
    if not declarations: continue
    pins=sorted({p for d in declarations for p in d['pins']})
    key=tuple(pins)
    record={'task_id':task.name,'script_origin':str(script),'script_sha256':digest(script),
            'declarations':declarations,'root_requirements':pins,
            'disposition':'duplicate-bootstrap-graph' if key in seen else 'selected-distinct-bootstrap'}
    audit.append(record)
    if key in seen: continue
    seen.add(key)
    record['script_preimage']='source/'+task.name+'-test.sh'
    dest=HERE/record['script_preimage'];dest.parent.mkdir(exist_ok=True);dest.write_bytes(script.read_bytes())
    test=task/'tests/test_outputs.py'
    source=test.read_text(); tree=ast.parse(source)
    imports=[]
    for node in ast.walk(tree):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            names=[a.name.split('.')[0] for a in node.names] if isinstance(node,ast.Import) else [node.module.split('.')[0]] if node.module else []
            imports.append({'line':node.lineno,'text':ast.get_source_segment(source,node),'roots':names,
                            'stdlib':[n for n in names if n in sys.stdlib_module_names]})
    record['test_import_audit']={'origin':str(test),'sha256':digest(test),'imports':sorted(imports,key=lambda x:x['line']),
        'policy':'AST import statements only retained. Task/application/image imports outside declared verifier bootstrap are not claimed resolved.'}
    docker=task/'environment/Dockerfile'
    record['image_declaration_audit']={'origin':str(docker),'sha256':digest(docker),'excerpts':[
        {'line':i,'text':s} for i,s in enumerate(docker.read_text().splitlines(),1) if s.startswith(('FROM ','RUN pip install '))]}
    selected.append(record)
    profile=HERE/'profiles'/task.name;profile.mkdir(parents=True,exist_ok=True)
    (profile/'roots.in').write_text(''.join(p+'\n' for p in pins))
    if len(selected)==3: break
assert [r['task_id'] for r in selected]==['build-cython-ext','headless-terminal','hf-model-inference']
value={'selection_rule':'Sorted task id among direct pip install verifiers with only finite exact distribution pins; skip identical bootstrap pin sets; select first three distinct graphs. Stop after three, do not extrapolate duplicate-task coverage.',
       'scope':'Host CPython 3.12 reconstruction of test.sh pip-bootstrap metadata tooling only, not task/image/native/application dependencies or complete Terminal-Bench task graphs.',
       'selected':selected,'considered_prefix':audit,'selected_task_count':len(selected),'distinct_profile_count':len(selected),
       'total_task_count':len([p for p in upstream.iterdir() if p.is_dir() and (p/'task.toml').is_file()])}
save(HERE/'source-audit.json',value)
run('source-sha256sum',['sha256sum',*[r['script_origin'] for r in selected],*[r['test_import_audit']['origin'] for r in selected],*[r['image_declaration_audit']['origin'] for r in selected]])
print(json.dumps(value,indent=2))
