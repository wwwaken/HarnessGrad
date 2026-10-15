"""Preserve failed transfer evidence, accept only the digest-matching retry."""
import hashlib
import json
from acquire import HERE, save
records=json.loads((HERE/'artifacts.json').read_text())
r=next(r for r in records if r['name']=='mkl')
retry=json.loads((HERE/'index/mkl-api-retry.receipt.json').read_text())
p=HERE/'mkl-api-retry.conda'
assert retry['exit_code']==0 and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']==retry['sha256']
original=HERE/'artifacts'/r['fn']
quarantine=HERE/'quarantine';quarantine.mkdir(exist_ok=True)
original.rename(quarantine/(r['fn']+'.incomplete'))
r['prior_acquisition']=r['acquisition']
p.rename(original)
r['acquisition']=retry;r['verified']=True
save(HERE/'artifacts.json',records)
print(json.dumps(r,indent=2))
