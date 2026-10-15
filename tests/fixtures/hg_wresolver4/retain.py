"""Retain bytes new to the committed fixture corpus; bind all candidate locations."""
import json
from pathlib import Path
import shutil
from common import HERE,ROOT,save,digest,run
assert not (HERE/'retained-targets.json').exists()
existing={}
for p in sorted((ROOT/'tests/fixtures').rglob('*.whl')):
 if p.is_relative_to(HERE):continue
 existing.setdefault(p.name,[]).append(p)
retained=[]
for profile in ['gaia','appworld']:
 for a in json.loads((HERE/f'inputs-{profile}.json').read_text())['artifacts']:
  source=Path(a['path']);assert digest(source)==a['sha256']
  matches=[p for p in existing.get(source.name,[]) if digest(p)==a['sha256']]
  if matches:
   dest=matches[0];kind='prior-committed-fixture'
  else:
   dest=HERE/'payloads'/source.name;dest.parent.mkdir(exist_ok=True)
   if not dest.exists():shutil.copyfile(source,dest)
   kind='new-packet-payload'
  assert digest(dest)==a['sha256']
  retained.append({'profile':profile,'key':a['key'],'path':str(dest.relative_to(ROOT)),'sha256':digest(dest),'bytes':dest.stat().st_size,'kind':kind})
save(HERE/'retained-targets.json',retained)
new={r['path']:r for r in retained if r['kind']=='new-packet-payload'}
run('retained-target-sha256sum',['sha256sum',*[ROOT/p for p in sorted({r['path'] for r in retained})]])
print(json.dumps({'candidate_locations':len(retained),'new_payload_files':len(new),'new_payload_bytes':sum(r['bytes'] for r in new.values()),'reused_prior_locations':sum(r['kind']=='prior-committed-fixture' for r in retained)},sort_keys=True))
