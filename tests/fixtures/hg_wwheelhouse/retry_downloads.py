"""Preserve truncated transfers and retry; never accept a prefix as an artifact."""
import hashlib
import json
import pathlib
import subprocess

HERE=pathlib.Path(__file__).resolve().parent
m=json.loads((HERE/'manifest.json').read_text())
prior={k:r for k,r in m['artifacts'].items() if r['status']=='obtain-failed'}
for k,r in prior.items():
    p=pathlib.Path(r['local_path']);q=p.parent/'quarantine';q.mkdir(exist_ok=True)
    p.rename(q/p.name);r['quarantine_path']=str(q/p.name)
(HERE/'truncated-downloads.json').write_text(json.dumps(prior,indent=2)+'\n')
for k,old in prior.items():
    r=dict(old);p=pathlib.Path(r['local_path'])
    cmd=['curl','--proxy','http://172.17.0.1:17890','--retry','3','--retry-all-errors',
         '--connect-timeout','20','--max-time','300','--fail','--location','--silent','--show-error',
         '--dump-header',str(HERE/f'{k}-retry.headers.txt'),'--output',str(p),
         '--write-out','http_code=%{http_code}\nsize_download=%{size_download}\nurl_effective=%{url_effective}\n',r['url']]
    out=subprocess.run(cmd,capture_output=True,text=True,timeout=1250)
    (HERE/f'{k}-retry.stdout.txt').write_text(out.stdout)
    (HERE/f'{k}-retry.stderr.txt').write_text(out.stderr)
    r['retry_command']=cmd;r['retry_exit_code']=out.returncode
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(4*1024*1024):h.update(b)
    r.update(bytes=p.stat().st_size,sha256=h.hexdigest())
    r['status']='obtained-wheel' if out.returncode==0 and r['bytes']==r['advertised_bytes'] and r['sha256']==r['advertised_sha256'] else 'retry-obtain-failed'
    r['prior_failed_receipt']='truncated-downloads.json'
    if r['status']=='obtained-wheel':r.pop('reason',None)
    m['artifacts'][k]=r
    (HERE/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    print(k,r['status'],r['bytes'],r['sha256'],flush=True)
