"""Avoid relative-import name collisions and retain embedded context import locations."""
import ast
import json
import pathlib
import textwrap
import warnings

HERE=pathlib.Path(__file__).resolve().parent
src=json.loads((HERE/'source-imports.json').read_text())
deps=json.loads((HERE/'installed-distributions.json').read_text())
for key,d in deps.items():
    roots=set(d['import_roots'])
    matches=[{'path':s['path'],'line':i['line'],'text':i['text']} for s in src for i in s['imports']
             if set(i['roots']) & roots and not i['text'].startswith('from .')]
    assert matches,key
    def priority(w):
        if w['path'].startswith('data/'):return (0,w['path'],w['line'])
        owner=w['path'].split('/site-packages/',1)[-1].split('/',1)[0].split('.',1)[0]
        return (2 if owner in roots else 1,w['path'],w['line'])
    d['source_witnesses']=sorted(matches,key=priority)
(HERE/'installed-distributions.json').write_text(json.dumps(deps,indent=2)+'\n')
f=HERE/'ds1000-context-imports.json';c=json.loads(f.read_text())
p=pathlib.Path(c['source']);extra=[]
for rowno,line in enumerate(p.open(),1):
    context=json.loads(line)['code_context']
    with warnings.catch_warnings():
        warnings.simplefilter('ignore');tree=ast.parse(context)
    for n in ast.walk(tree):
        if not isinstance(n,ast.Constant) or not isinstance(n.value,str) or 'import ' not in n.value:continue
        for embedded_line,statement in enumerate(n.value.splitlines(),1):
            statement=statement.strip()
            if not statement.startswith(('import ','from ')):continue
            try: node=ast.parse(statement).body[0]
            except (SyntaxError,IndentationError):continue
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                extra.append({'jsonl_line':rowno,'context_string_line':n.lineno,
                              'embedded_line':embedded_line,'text':ast.unparse(node)})
c['embedded_string_imports']=extra
c['embedded_note']='Static imports inside literal program strings; not asserted to execute for every selected task. No complete strings/tasks are exported.'
f.write_text(json.dumps(c,indent=2)+'\n')
print(json.dumps({'distribution_witnesses_refined':len(deps),'embedded_string_import_statements':len(extra)}))
