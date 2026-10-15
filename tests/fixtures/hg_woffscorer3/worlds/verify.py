"""Read-only fixture integrity/coverage validator; never replay a world."""
import hashlib,json,pathlib,tarfile
F=pathlib.Path(__file__).resolve().parent;R=F.parents[3]
checked=0
for line in (F/'SHA256SUMS').read_text().splitlines():
 digest,rel=line.split('  ',1);p=F/rel
 assert p.is_file(),rel
 assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,rel
 checked+=1
for dataset in ['alfworld','appworld']:
 identity=json.loads((F/f'{dataset}-identities.json').read_text())
 for row in identity['files']:
  if 'copy' in row:assert hashlib.sha256((F/row['copy']).read_bytes()).hexdigest()==row['sha256'],row
  elif row['path'].startswith('data/'):
   assert hashlib.sha256((R/row['path']).read_bytes()).hexdigest()==row['sha256'],row
  elif pathlib.Path(row['path']).is_file():
   assert hashlib.sha256(pathlib.Path(row['path']).read_bytes()).hexdigest()==row['sha256'],row
assert (R/'data/datasets/appworld/verify/check.py').read_bytes()==(F/'appworld-local-check.py').read_bytes()
identity=json.loads((F/'appworld-identities.json').read_text())
archive=F/'appworld-controlled-inputs.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==identity['controlled_archive_sha256']
with tarfile.open(archive) as tf:
 for row in identity['controlled_members']:
  b=tf.extractfile('data/'+row['path']).read();assert len(b)==row['bytes'];assert hashlib.sha256(b).hexdigest()==row['sha256']
 tasks={p.name.split('/')[2] for p in tf if p.name.startswith('data/tasks/')}
 assert tasks=={'hgcontrol_1'},tasks
comparisons=json.loads((F/'comparison.json').read_text())
for dataset,c in comparisons.items():
 assert c['counts']['controlled_inputs']==len(c['results'])
 assert c['counts']['numeric_agreements']==sum(x['agreement'] is True for x in c['results'])
 assert c['counts']['numeric_divergences']==sum(x['agreement'] is False for x in c['results'])
print(json.dumps({'manifest_files_checked':checked,'source_copy_and_local_identity_checks':'pass','controlled_archive_members_checked':len(identity['controlled_members']),'only_authored_appworld_task':True,'comparison_counts':{n:c['counts'] for n,c in comparisons.items()}},indent=2))
