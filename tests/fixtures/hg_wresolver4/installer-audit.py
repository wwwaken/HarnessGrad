"""Inspect shipped installer and applications as source, never execute benchmark code.

Only .source/apps.bundle is decrypted with the algorithm shipped in the wheel.
No package-tests bundle, task data, evaluator answer or experiment payload is read.
"""
import ast
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
from common import HERE,ROOT,save,digest

assert not (HERE/'installer-audit.json').exists()
wheel=next(Path('/tmp/hg-wresolver4-appworld-candidates').glob('appworld-*.whl'))
with zipfile.ZipFile(wheel) as archive:
 constants=archive.read('appworld/common/constants.py').decode()
 values={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(constants).body
         if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in {'PASSWORD','SALT'}}
 encrypted=archive.read('appworld/.source/apps.bundle')
 key=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=values['SALT'],iterations=100000).derive(values['PASSWORD'].encode())
 cipher=Cipher(algorithms.AES(key),modes.CFB(encrypted[:16])).decryptor()
 plain=cipher.update(encrypted[16:])+cipher.finalize()
 modules=[]
 with zipfile.ZipFile(io.BytesIO(plain)) as bundle:
  for name in sorted(bundle.namelist()):
   if not name.endswith('.py'):continue
   # Source-only applications, no task/test payload.
   assert name.startswith('apps/') and '..' not in Path(name).parts,name
   raw=bundle.read(name);lines=raw.decode().splitlines();imports=[]
   for node in ast.walk(ast.parse(raw,filename=name)):
    if isinstance(node,(ast.Import,ast.ImportFrom)):
     names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or '']
     for n in names:imports.append({'line':node.lineno,'module':n,'level':getattr(node,'level',0),'text':lines[node.lineno-1]})
   modules.append({'member':name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'imports':imports})
 for name in ['appworld/cli.py','appworld/install.py','appworld/common/utils.py','appworld/common/constants.py']:
  p=HERE/'appworld-wheel-source'/name
  assert p.read_bytes()==archive.read(name)
 app_roots=sorted({i['module'].split('.')[0] for m in modules for i in m['imports'] if i['level']==0 and i['module'].split('.')[0] not in sys.stdlib_module_names|{'appworld'}})
 record={'wheel':str(wheel),'wheel_sha256':digest(wheel),'apps_bundle_member':'appworld/.source/apps.bundle','apps_bundle_sha256':hashlib.sha256(encrypted).hexdigest(),'decrypted_zip_sha256':hashlib.sha256(plain).hexdigest(),'modules':modules,'application_third_party_import_roots':app_roots,'installer_source':{n:digest(HERE/'appworld-wheel-source'/n) for n in ['appworld/cli.py','appworld/install.py','appworld/common/utils.py','appworld/common/constants.py']},'scope':'Static installer/application-source inspection; no AppWorld import or CLI execution. install_package unpacks bundled applications and tests; no wheel install or network call occurs in that function. Only applications decrypted for source audit; tests bundle untouched. This is not installer execution or image/source/runtime equivalence.'}
 save(HERE/'installer-audit.json',record)
 print(json.dumps({'wheel_sha256':digest(wheel),'application_source_modules':len(modules),'application_source_bytes':sum(m['bytes'] for m in modules),'third_party_import_roots':app_roots,'scope':record['scope']},indent=2,sort_keys=True))
 for module in modules:
  print(module['sha256'],module['member'])
  for i in module['imports']:print(f"{module['member']}:{i['line']}: {i['text']}")
