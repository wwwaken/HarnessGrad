import tempfile,venv,shutil,json
from pathlib import Path
from common import HERE,run,clean_env,save
work=Path(tempfile.mkdtemp(prefix='hg-wresolver4-bootstrap-diagnostic-'))
try:
 venv.EnvBuilder(with_pip=False,system_site_packages=False).create(work/'venv')
 result=run('appworld-ensurepip-diagnostic',[work/'venv/bin/python3.11','-m','ensurepip','--upgrade','--default-pip'],env=clean_env(work))
finally:
 shutil.rmtree(work)
 save(HERE/'raw/bootstrap-diagnostic-cleanup.json',{'directory':str(work),'removed':not work.exists()})
print(json.dumps(result,sort_keys=True))
