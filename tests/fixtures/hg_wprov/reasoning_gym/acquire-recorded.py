from pathlib import Path
import urllib.request,urllib.error,json,hashlib,datetime
root=Path(__file__).resolve().parent/'responses'
def fetch(name,url):
 req=urllib.request.Request(url,headers={'User-Agent':'HarnessGrad-provenance-audit/1.0','Accept-Encoding':'identity'})
 try:r=urllib.request.urlopen(req,timeout=90)
 except urllib.error.HTTPError as e:r=e
 body=r.read();headers=f'HTTP status: {r.status}\n'+str(r.headers)
 (root/(name+'.body')).write_bytes(body); (root/(name+'.headers')).write_text(headers)
 receipt={'requested_url':url,'final_url':r.geturl(),'status':r.status,'acquired_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'body_sha256':hashlib.sha256(body).hexdigest(),'body_size':len(body),'headers_sha256':hashlib.sha256(headers.encode()).hexdigest()}
 (root/(name+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));return body,r.status
body,status=fetch('pypi-0.1.25','https://pypi.org/pypi/reasoning-gym/0.1.25/json')
if status!=200: raise SystemExit(1)
j=json.loads(body)
for obj in j['urls']:
 stem='pypi-'+obj['packagetype']
 b,s=fetch(stem,obj['url'])
 assert s==200 and hashlib.sha256(b).hexdigest()==obj['digests']['sha256']
 fetch(stem+'-provenance','https://pypi.org/integrity/reasoning-gym/0.1.25/'+obj['filename']+'/provenance')
fetch('github-tag','https://api.github.com/repos/open-thought/reasoning-gym/git/ref/tags/v0.1.25')
