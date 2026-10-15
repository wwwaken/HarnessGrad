"""Accept the support-library retry only after independent digest verification."""
import hashlib
import json
from acquire import HERE,save
records=json.loads((HERE/'support-artifacts.json').read_text())
r=next(r for r in records if r['name']=='libstdcxx-ng')
a=json.loads((HERE/'index/support-libstdcxx-api-retry.receipt.json').read_text())
p=HERE/'libstdcxx-api-retry.conda'
assert a['exit_code']==0 and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']==a['sha256']
original=HERE/'artifacts'/r['fn']
original.rename(HERE/'quarantine'/(r['fn']+'.incomplete'))
p.rename(original)
r['prior_acquisition']=r['acquisition'];r['acquisition']=a;r['verified']=True
save(HERE/'support-artifacts.json',records)
assert all(d['verified'] for d in records)
print(json.dumps(r,indent=2))
