"""Count unmeasured cached candidates separately from prerequisite-verified tasks."""
import json,pathlib
packet=pathlib.Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
previous=json.loads(read(packet/'prior-tb89c-result.json')['stdout'])
old={r['task_id'] for r in previous['rows'] if r['raw_measured']}
b=json.loads(json.loads(read(packet/'prior-tb89b-result.json')['stdout'])['stdout'])
old.update(r['task_id'] for r in b['rows'] if r['raw_measured'])
n=json.loads(json.loads(json.loads(read(packet/'prior-openssl-result.json')['stdout'])['stdout'])['stdout'])
assert n['ctrf_files'] and not n['invalid'];old.update(n['raw_per_task'])
inv=read(packet/'inventory.json');batch=read(packet/'batch.json');cached={r['task_id'] for r in inv['rows'] if r['image_present']};meta=set(batch['metadata_candidates']);sel=set(batch['selected'])
assert old<=cached and not old&sel
out=dict(prior_unique_measured=sorted(old),prior_measured_count=len(old),cached_not_previously_measured=len(cached-old),metadata_not_previously_measured=len(meta-old),new_selected=len(sel),cached_new_outside_batch=len(cached-old-sel),metadata_new_outside_batch=len(meta-old-sel),prerequisite_verified_not_selected=len(batch['prerequisite_verified_not_selected']),remaining_certified_queue_after_fixed_batch=0,note='Cache/metadata availability is not runtime readiness. Only the fixed selected tasks have fresh tool/input probes; runtime readiness includes real verifier bootstrap, observed during execution.')
with (packet/'availability.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps(out,indent=2))
