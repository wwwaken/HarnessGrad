"""Combine two preserved preselection manifests without overwriting either."""
import json,pathlib,math
p=pathlib.Path(__file__).resolve().parent
read=lambda n:json.loads((p/n).read_text())
a=read('batch.json');b=read('batch-supplement.json');inv=read('inventory.json');available=read('availability.json')
combined={**a,'runs_roots':[a['runs_root'],b['runs_root']],'selected':a['selected']+b['selected'],'selection_rule':a['selection_rule']+' Initial five source/tool probes did not certify the transitive uv download; four attempts were invalid for missing CTRF and the fifth was interrupted. All are retained. '+b['selection_rule'],'total_serial_tasks':len(a['selected'])+len(b['selected']),'prerequisite_verified':a['prerequisite_verified']+b['prerequisite_verified'],'prerequisite_verified_not_selected':[],'cached_unselected':inv['cached_images']-len(a['selected'])-len(b['selected']),'initial_batch':a,'supplemental_batch':b,'note':'Initial local tool/input prerequisites passed but transitive bootstrap was not established. Two additional pip tasks have complete dependency smoke checks. No original run ID is resumed; no task is replaced or rerun.'}
assert len(set(combined['selected']))==len(combined['selected'])<=min(30,math.ceil(inv['total_task_references']*.1))
with (p/'review-batch.json').open('x') as f:json.dump(combined,f,indent=2);f.write('\n')
cached={r['task_id'] for r in inv['rows'] if r['image_present']};old=set(available['prior_unique_measured']);sel=set(combined['selected']);meta=set(combined['metadata_candidates'])
new={**available,'new_selected':len(sel),'cached_new_outside_batch':len(cached-old-sel),'metadata_new_outside_batch':len(meta-old-sel),'remaining_certified_queue_after_fixed_batch':len(combined['prerequisite_verified_not_selected']),'end_to_end_bootstrap_verified_supplemental_tasks':b['selected'],'initial_local_probe_only_tasks':a['selected']}
with (p/'availability-all.json').open('x') as f:json.dump(new,f,indent=2);f.write('\n')
print(json.dumps(new,indent=2))
