import sys,sysconfig,platform,ssl,sqlite3,json,hashlib,pathlib,importlib.metadata as md,subprocess,os

def identity(p):
 p=pathlib.Path(p).resolve(); return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size}
r={'version':sys.version,'executable':sys.executable,'real_executable':identity(sys.executable),'implementation':platform.python_implementation(),'cache_tag':sys.implementation.cache_tag,'SOABI':sysconfig.get_config_var('SOABI'),'EXT_SUFFIX':sysconfig.get_config_var('EXT_SUFFIX'),'platform':sysconfig.get_platform(),'libc':platform.libc_ver(),'openssl':ssl.OPENSSL_VERSION,'sqlite':sqlite3.sqlite_version,'distributions':[],'native':[]}
for d in sorted(md.distributions(),key=lambda d:d.metadata['Name'].lower()):
 r['distributions'].append({'name':d.metadata['Name'],'version':d.version,'requires':d.requires,'files':[identity(d.locate_file(f)) for f in d.files if str(f).endswith(('METADATA','WHEEL','RECORD'))]})
import _ssl,_hashlib,_sqlite3,_ctypes,zlib,_bz2,_lzma
seen=set();todo=[sys.executable]+[m.__file__ for m in [_ssl,_hashlib,_sqlite3,_ctypes,zlib,_bz2,_lzma]]
while todo:
 p=str(pathlib.Path(todo.pop()).resolve())
 if p in seen:continue
 seen.add(p);a=identity(p);v=subprocess.run(['ldd',p],text=True,capture_output=True);a.update(ldd_stdout=v.stdout,ldd_stderr=v.stderr,ldd_returncode=v.returncode);r['native'].append(a)
 for line in v.stdout.splitlines():
  for word in line.split():
   if word.startswith('/') and pathlib.Path(word).is_file():todo.append(word)
print(json.dumps(r,indent=2))
