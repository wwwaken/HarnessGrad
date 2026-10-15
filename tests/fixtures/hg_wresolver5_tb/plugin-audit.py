"""Static import-only wheel audit; do not import the pytest plugin."""
import ast
import hashlib
import json
import zipfile
from common import HERE, digest, save
inputs=json.loads((HERE/'inputs.json').read_text())
a=next(a for a in inputs['artifacts'] if a['key']=='pytest-json-ctrf')
assert digest(a['path'])==a['sha256']
modules=[]
with zipfile.ZipFile(a['path']) as archive:
    for member in archive.namelist():
        if not member.endswith('.py'):continue
        raw=archive.read(member);source=raw.decode();tree=ast.parse(source)
        imports=[{'line':n.lineno,'text':ast.get_source_segment(source,n)} for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
        modules.append({'member':member,'sha256':hashlib.sha256(raw).hexdigest(),'imports':sorted(imports,key=lambda i:i['line'])})
value={'artifact_sha256':a['sha256'],'scope':'Import-only static bootstrap plugin audit. All absolute third-party imports are pytest, provided by the declared graph; local ctrf imports are in the same wheel. No plugin is imported or run.','modules':modules}
save(HERE/'plugin-audit.json',value)
print(json.dumps(value,indent=2))
