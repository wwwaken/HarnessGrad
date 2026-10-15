"""Read-only byte/process/source/graph/coverage/authorization verification."""
import argparse
import ast
import copy
import email
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile
from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.tags import parse_tag
from packaging.utils import parse_wheel_filename
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
from common import HERE,ROOT,digest

parser=argparse.ArgumentParser();parser.add_argument('--seal',action='store_true');args=parser.parse_args()
read=lambda p:json.loads(p.read_text())
normalize=lambda n:re.sub(r'[-_.]+','-',n).lower()
results=read(HERE/'results-complete.json')
assert results==read(HERE/'results.json')|read(HERE/'results-appworld-retry.json')
assert results.keys()=={'gaia','appworld'}
inputs={n:read(HERE/f'inputs-{n}.json') for n in results}
records={n:{a['key']:a for a in j['artifacts']} for n,j in inputs.items()}
retained=read(HERE/'retained-targets.json')
independent_retained=dict(line.split(maxsplit=1)[::-1] for line in (HERE/'raw/retained-target-sha256sum.stdout.txt').read_text().splitlines())
for r in retained:
 a=records[r['profile']][r['key']];p=ROOT/r['path']
 assert digest(p)==r['sha256']==a['sha256']==independent_retained[str(p)]
 assert p.stat().st_size==r['bytes']==a['bytes']
assert {(r['profile'],r['key']) for r in retained}=={(n,k) for n,rs in records.items() for k in rs}
for name,r in results.items():
 target=read(HERE/f'target-{name}.json')
 tags={t for s in target['tags'] for t in parse_tag(s)}
 assert digest(target['executable'])==target['sha256']
 environment=target.get('marker_environment',default_environment())
 assert environment['python_full_version']==('3.12.4' if name=='gaia' else '3.11.15')
 assert environment['implementation_name']=='cpython'
 assert len(records[name])<=120 and sum(a['bytes'] for a in records[name].values())<=320*1024*1024
 independent=dict(line.split(maxsplit=1)[::-1] for line in (HERE/f'raw/{name}-wheel-sha256sum.stdout.txt').read_text().splitlines())
 for key,a in records[name].items():
  p=Path(a['path']);assert p.stat().st_size==a['bytes'] and digest(p)==a['sha256']==independent[str(p)]
  assert parse_wheel_filename(p.name)[3]&tags
  assert sorted(map(str,parse_wheel_filename(p.name)[3]&tags))==a['matching_tags']
  with zipfile.ZipFile(p) as z:
   for m in a['metadata'].values():
    preimage=ROOT/m['path'];assert z.read(m['member'])==preimage.read_bytes() and digest(preimage)==m['sha256']
  meta=email.message_from_bytes((ROOT/a['metadata']['METADATA']['path']).read_bytes())
  assert normalize(meta['Name'])==key and meta['Version']==a['version']
  assert meta.get_all('Requires-Dist',[])==a['requires_dist']
  if a['requires_python']:assert SpecifierSet(a['requires_python']).contains(environment['python_full_version'])
  provenance=a['provenance']
  if provenance['kind']=='pypi-exact-version':
   index=HERE/('index' if name=='gaia' else 'index-appworld')/f"{key}-{a['version']}.json"
   http=read(index.with_name(index.name+'.http.json'))
   assert http['status']==200 and digest(index)==http['sha256'] and http['request_url']==provenance['index_url']
   offered=next(x for x in read(index)['urls'] if x['filename']==p.name)
   get=read(index.parent/(p.name+'.http.json'))
   assert get['status']==200 and get['request_url']==offered['url']==provenance['url']
   assert get['sha256']==offered['digests']['sha256']==a['sha256']==provenance['advertised_sha256']
   assert get['bytes']==offered['size']==a['bytes']<=64*1024*1024
   if name=='appworld':assert digest(provenance['candidate_path'])==provenance['candidate_sha256']==a['sha256']
   else:assert read(HERE/'observed-gaia.json')[key]['version']==a['version']
  else:
   assert provenance['kind']=='retained-w-resolver3'
   assert digest(provenance['source'])==provenance['source_sha256']==a['sha256']
   prior={x['key']:x for x in read(ROOT/'tests/fixtures/hg_wresolver3/inputs.json')['artifacts']}
   assert prior[key]['version']==a['version'] and prior[key]['sha256']==a['sha256']
 prefix='' if name=='gaia' else 'appworld-retry-'
 profile=HERE/'profiles'/name
 assert profile.joinpath('roots.in').read_text().splitlines()==inputs[name]['profiles'][name]
 assert set(profile.joinpath('constraints.txt').read_text().splitlines())=={f"{a['name']}=={a['version']}" for a in records[name].values()}
 constraints={normalize(q.name):q for q in map(Requirement,profile.joinpath('constraints.txt').read_text().splitlines())}
 assert r['exit_code']==r['install']['exit_code']==r['check']['exit_code']==0
 for field,label in [(None,'resolve-'),('install','install-'),('check','check-'),('negative','negative-')]:
  actual=r if field is None else r[field]
  command=read(HERE/'raw'/(prefix+label+name+'.command.json'))
  assert all(actual[k]==v for k,v in command.items())
  assert command['timeout_seconds']==180 and command['elapsed_seconds']<180
 for actual in [r,r['install'],r['negative']]:
  assert '--no-deps' not in actual['argv']
  for flag in ['--ignore-installed','--no-index','--no-cache-dir','--only-binary=:all:']:assert flag in actual['argv']
 assert '--dry-run' in r['argv'] and '--require-hashes' in r['install']['argv']
 assert 'include-system-site-packages = false' in (HERE/'raw'/(prefix+name+'-pyvenv.cfg')).read_text()
 report=read(HERE/'raw'/(prefix+name+'.pip-report.json'))
 selected={normalize(e['metadata']['name']):e for e in report['install']}
 assert len(selected)==len(r['selected'])
 assert selected.keys()==records[name].keys()
 for key,e in selected.items():
  a=records[name][key]
  assert e['metadata']['version']==a['version'] and e['download_info']['archive_info']['hashes']['sha256']==a['sha256']
  assert f"{a['name']}=={a['version']} --hash=sha256:{a['sha256']}" in profile.joinpath('resolved.lock').read_text().splitlines()
 assert len(profile.joinpath('resolved.lock').read_text().splitlines())==len(selected)
 # Traverse actual wheel metadata independently, accumulating requested extras.
 pending=[Requirement(q) for q in inputs[name]['profiles'][name]]
 extras={};visited=set()
 while pending:
  req=pending.pop(0);key=normalize(req.name)
  assert not req.url and key in selected and req.specifier.contains(selected[key]['metadata']['version'], prereleases=constraints[key].specifier.prereleases), (name,str(req),selected.get(key),environment)
  extras.setdefault(key,set()).update(req.extras);state=(key,tuple(sorted(extras[key])))
  if state in visited:continue
  visited.add(state)
  for literal in records[name][key]['requires_dist']:
   child=Requirement(literal)
   if any(child.marker is None or child.marker.evaluate(dict(environment,extra=e)) for e in ['']+sorted(extras[key])):pending.append(child)
 assert {k for k,e in visited}==selected.keys()
 assert (HERE/'raw'/(prefix+'check-'+name+'.stdout.txt')).read_text().strip()=='No broken requirements found.'
 missing='et-xmlfile' if name=='gaia' else 'munch'
 assert r['negative']['exit_code']==1
 negative=(HERE/'raw'/(prefix+'negative-'+name+'.stdout.txt')).read_text()
 assert f"The user requested (constraint) {missing}=={records[name][missing]['version']}" in negative
 assert ('openpyxl 3.1.2 depends on et-xmlfile' if name=='gaia' else 'appworld 0.1.3.post1 depends on munch<5.0.0 and >=4.0.0') in negative
 assert 'ResolutionImpossible' in (HERE/'raw'/(prefix+'negative-'+name+'.stderr.txt')).read_text()
 runtime=read(HERE/'raw'/(prefix+'runtime.json'))
 assert runtime['executable_sha256']==target['sha256']
 assert runtime['environment']['CUDA_VISIBLE_DEVICES']=='' and runtime['environment']['PIP_CONFIG_FILE']=='/dev/null'
 network=read(HERE/'raw'/(prefix+'network.json'))
 assert network['errno']==101 and [p[1] for p in network['interfaces']]==['lo'] and not network['route'].splitlines()[1:]
 cleanup=read(HERE/'raw'/(prefix+'cleanup.json'))
 assert cleanup['removed'] and not Path(cleanup['directory']).exists()

# Preserve unsuccessful experiments separately; a bootstrap exception is not a resolver result.
assert not (HERE/'results-appworld.json').exists()
assert 'CalledProcessError' in (HERE/'probe-appworld.stderr.txt').read_text()
assert "ModuleNotFoundError: No module named 'encodings'" in (HERE/'raw/appworld-ensurepip-diagnostic.stderr.txt').read_text()
assert "ModuleNotFoundError: No module named 'packaging'" in (HERE/'raw/appworld-tooling-packaging-check.stderr.txt').read_text()
for file in ['appworld-cleanup.json','bootstrap-diagnostic-cleanup.json']:
 cleanup=read(HERE/'raw'/file);assert cleanup['removed'] and not Path(cleanup['directory']).exists()
assert read(HERE/'raw/appworld-ensurepip-diagnostic.command.json')['exit_code']==1
assert read(HERE/'raw/appworld-retry-ensurepip.command.json')['exit_code']==0
# The disclosed in-session capture repair is independently bound to the original
# exported stdout and the unchanged successful retry receipt bytes.
recovery=read(HERE/'capture-recovery.json')
assert not (HERE/'raw/appworld-runtime.json').exists()
for entry in recovery['retry_receipts_moved_byte_identically']:
 assert digest(HERE/entry['new_label'])==entry['sha256']
exports=[read(HERE/p) for p in recovery['exported_tool_records']]
exported_text='\n'.join(item.get('text','') for event in exports for item in event['payload']['output'])
for stem in ['network','cleanup']:
 receipt=(HERE/f'raw/appworld-{stem}.json').read_text()
 # The original nested command output JSON escapes each newline; compare its
 # exact escaped receipt bytes to the preserved exported tool response text.
 assert json.dumps(receipt)[1:-1] in exported_text
assert read(HERE/'raw/appworld-cleanup.json')['directory']=='/tmp/hg-wresolver4-offline-pnanzcrd'
assert read(HERE/'raw/appworld-retry-cleanup.json')['directory']==read(HERE/'raw/appworld-retry-runtime.json')['work_directory']
assert 'raw/appworld-retry-runtime.json' in (HERE/'probe-appworld-retry.py').read_text()
assert 'raw/appworld-runtime.json' in (HERE/'attempts/probe-appworld-retry-executed.py').read_text()

assert read(HERE/'raw/appworld-candidate-download.command.json')['exit_code']==0
assert '--only-binary=:all:' in read(HERE/'raw/appworld-candidate-download.command.json')['argv']

# Exact current source/preimage/hash/line custody.
for r in read(HERE/'source-audit.json')['sources']:
 preimage=ROOT/r['preimage'];origin=Path(r['source']) if r['source'].startswith('/') else ROOT/r['source']
 assert digest(preimage)==r['sha256']==digest(origin) and preimage.stat().st_size==r['bytes']
 for e in r['excerpts']+r['imports']:assert preimage.read_text().splitlines()[e['line']-1]==e['text']
gaps=read(HERE/'remainder-audit.json')
assert len(gaps['datasets'])==11
for r in gaps['sources']:
 raw=r['preimage_text'].encode();origin=Path(r['source_path']) if r['source_path'].startswith('/') else ROOT/r['source_path']
 assert hashlib.sha256(raw).hexdigest()==r['sha256']==digest(origin) and len(raw)==r['bytes']
 for e in r['excerpts']+r['imports_ast']:assert r['preimage_text'].splitlines()[e['line']-1]==e['text']
assert gaps['datasets']['tau_bench']['third_party_absolute_import_records']==[]

# Reproduce source-only bundle decoding; never open/decrypt the package-tests bundle.
audit=read(HERE/'installer-audit.json');wheel=Path(audit['wheel']);assert digest(wheel)==audit['wheel_sha256']==records['appworld']['appworld']['sha256']
with zipfile.ZipFile(wheel) as z:
 for member,expected in audit['installer_source'].items():
  assert hashlib.sha256(z.read(member)).hexdigest()==expected==digest(HERE/'appworld-wheel-source'/member)
 constants=ast.parse(z.read('appworld/common/constants.py'))
 values={n.targets[0].id:ast.literal_eval(n.value) for n in constants.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in {'PASSWORD','SALT'}}
 encrypted=z.read(audit['apps_bundle_member']);assert hashlib.sha256(encrypted).hexdigest()==audit['apps_bundle_sha256']
 key=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=values['SALT'],iterations=100000).derive(values['PASSWORD'].encode())
 decryptor=Cipher(algorithms.AES(key),modes.CFB(encrypted[:16])).decryptor();plain=decryptor.update(encrypted[16:])+decryptor.finalize()
 assert hashlib.sha256(plain).hexdigest()==audit['decrypted_zip_sha256']
 with zipfile.ZipFile(io.BytesIO(plain)) as bundle:
  assert {m['member'] for m in audit['modules']}=={n for n in bundle.namelist() if n.endswith('.py')}
  for m in audit['modules']:
   raw=bundle.read(m['member']);assert hashlib.sha256(raw).hexdigest()==m['sha256'] and len(raw)==m['bytes']
   for e in m['imports']:assert raw.decode().splitlines()[e['line']-1]==e['text']
 assert set(audit['application_third_party_import_roots'])<={key for key in records['appworld']}

before=read(HERE/'registry-before.json');after=read(ROOT/'docs/dataset-blockers.json')
baseline=next(r for r in before['shared_blockers'] if r['id']=='scorer-offline-closure')
updated=next(r for r in after['shared_blockers'] if r['id']=='scorer-offline-closure')
observation=(HERE/'observation.txt').read_text().strip()
assert updated['observed']==baseline['observed']+' '+observation
assert updated['evidence'][:len(baseline['evidence'])]==baseline['evidence'] and len(updated['evidence'])==len(baseline['evidence'])+3
comparison=copy.deepcopy(after);row=next(r for r in comparison['shared_blockers'] if r['id']=='scorer-offline-closure')
row['observed'],row['evidence']=baseline['observed'],baseline['evidence'];assert comparison==before,'Only additive shared observation/evidence may change'
for row in after['shared_blockers']+after['datasets']:
 for e in row.get('evidence',[]):
  if e['kind']=='repository':assert e['locator'] in (ROOT/e['path']).read_text()
summary=read(HERE/'summary.json');coverage=read(HERE/'dataset-coverage.json');prior=read(ROOT/'tests/fixtures/hg_wresolver3/summary.json')
assert summary['new_profiles_resolved']==len(results)==summary['target_profiles']
assert summary['bounded_profiles_resolved']==prior['bounded_profiles_resolved']+len(results)
assert summary['bounded_profiles']==prior['bounded_profiles']+len(results)
assert summary['complete_nonempty_python_profiles']==prior['complete_nonempty_python_profiles']+len(results)==sum(r['status']=='resolved-full-python-metadata-profile' for r in coverage)
assert summary['shared_datasets']==len(coverage)==sum('scorer-offline-closure' in r['shared_blockers'] for r in before['datasets'])
assert summary['not_demonstrated_at_dataset_profile_scope']==summary['shared_datasets']-summary['complete_nonempty_python_profiles']
assert summary['no_third_party_payload']==sum(r['status'].startswith('no-third-party') for r in coverage)
assert summary['new_candidate_artifacts']==sum(len(rs) for rs in records.values())
assert summary['new_candidate_bytes']==sum(a['bytes'] for rs in records.values() for a in rs.values())
assert set(summary['remaining_datasets'])==gaps['datasets'].keys()
prior_rows={r['dataset']:r for r in read(ROOT/'tests/fixtures/hg_wresolver3/dataset-coverage.json')}
for r in coverage:
 if r['dataset'] not in results:assert r['status']==prior_rows[r['dataset']]['status']
report=(ROOT/'reports/w-resolver4-payloads.md').read_text();assert observation in report
assert f"**{summary['bounded_profiles_resolved']}/{summary['bounded_profiles']} bounded profiles and {summary['complete_nonempty_python_profiles']}/{summary['shared_datasets']} complete nonempty dataset Python profiles**" in report
assert set(re.findall(r'\b[a-f0-9]{64}\b',report))<={a['sha256'] for rs in records.values() for a in rs.values()}
assert not summary['production_authorized']
if args.seal:
 files=[p for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts]
 (HERE/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(HERE)}\n' for p in files))
else:
 sealed=set()
 for line in (HERE/'SHA256SUMS').read_text().splitlines():
  expected,rel=line.split(maxsplit=1);assert digest(HERE/rel)==expected,rel;sealed.add(rel)
 assert sealed=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts}
print(json.dumps({'valid':True,'candidate_wheels':summary['new_candidate_artifacts'],'fresh_profiles':len(results),'missing_wheel_refusals':len(results),'bounded_coverage':f"{summary['bounded_profiles_resolved']}/{summary['bounded_profiles']}",'complete_nonempty_python_coverage':f"{summary['complete_nonempty_python_profiles']}/{summary['shared_datasets']}",'production_authorized':False},sort_keys=True))
