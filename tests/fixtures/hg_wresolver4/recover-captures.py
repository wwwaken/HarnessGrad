"""Recover earlier raw output preimages from this session's exported tool records.

Do not reconstruct a missing runtime receipt from guessed values. Preserve the
successful retry's actual bytes under distinct labels and document the loss.
"""
import json
from pathlib import Path
import shutil
from common import HERE,save,digest

assert not (HERE/'capture-recovery.json').exists()
log=Path('/home/xubuqiang/.codex/sessions/2026/10/15/rollout-2026-10-15T13-15-08-01a13dfc-51bb-79d0-8254-ca1c142ad9fe.jsonl')
exports=[]
for raw in log.read_text().splitlines():
 j=json.loads(raw);v=j.get('payload',{})
 if j['type']=='response_item' and v.get('type')=='custom_tool_call_output' and 'pnanzcrd' in str(v.get('output','')):
  exports.append(j)
assert len(exports)==2,len(exports)
for i,j in enumerate(exports):
 save(HERE/'attempts'/f'original-tool-output-{i}.json',j)
 output=j['payload']['output']
 print(type(output).__name__,str(output)[:100])
# Actual retry receipts were written at the first-attempt names; preserve their
# bytes before restoring any independently exported earlier receipt.
moved=[]
for stem in ['network','runtime','cleanup']:
 source=HERE/f'raw/appworld-{stem}.json';dest=HERE/f'raw/appworld-retry-{stem}.json'
 assert not dest.exists()
 before=digest(source);shutil.move(source,dest);assert digest(dest)==before
 moved.append({'original_label':str(source.relative_to(HERE)),'new_label':str(dest.relative_to(HERE)),'sha256':before})
# Exported tool output contains JSON for the command result whose output string
# ends with the earlier cat output. Extract exact raw bytes, no inferred values.
for j in exports:
 output=j['payload']['output']
 if isinstance(output,list):
  text='\n'.join(item.get('text','') for item in output)
 else:text=output
 # functions.exec encodes the nested exec_command result in JSON after wrapper.
 decoder=json.JSONDecoder();found=[]
 for pos,c in enumerate(text):
  if c=='{':
   try:
    value,end=decoder.raw_decode(text[pos:])
    if isinstance(value,dict) and 'output' in value and isinstance(value['output'],str):found.append(value['output'])
   except json.JSONDecodeError:pass
 for stdout in found:
  for stem,required in [('network','"netns"'),('cleanup','"removed"')]:
   marker=stdout.find('{\n',stdout.find('Traceback') if stem=='network' else 0)
   for pos,c in enumerate(stdout):
    if c!='{':continue
    try:value,end=decoder.raw_decode(stdout[pos:])
    except json.JSONDecodeError:continue
    if isinstance(value,dict) and ((stem=='network' and value.get('errno')==101 and 'netns' in value) or (stem=='cleanup' and value.get('directory')=='/tmp/hg-wresolver4-offline-pnanzcrd' and value.get('removed') is True)):
     dest=HERE/f'raw/appworld-{stem}.json';assert not dest.exists()
     dest.write_text(stdout[pos:pos+end]+'\n')
assert (HERE/'raw/appworld-network.json').exists() and (HERE/'raw/appworld-cleanup.json').exists()
assert not (HERE/'raw/appworld-runtime.json').exists()
shutil.copyfile(HERE/'probe-appworld-retry.py',HERE/'attempts/probe-appworld-retry-executed.py')
recipe=HERE/'probe-appworld-retry.py'
t=recipe.read_text().replace("'raw/appworld-network.json'","'raw/appworld-retry-network.json'").replace("'raw/appworld-runtime.json'","'raw/appworld-retry-runtime.json'").replace("'raw/appworld-cleanup.json'","'raw/appworld-retry-cleanup.json'")
recipe.write_text(t)
save(HERE/'capture-recovery.json',{'scope':'In-session evidence tooling naming error, no runs or frozen receipts touched','source_log':str(log),'exported_tool_records':[f'attempts/original-tool-output-{i}.json' for i in range(len(exports))],'retry_receipts_moved_byte_identically':moved,'first_attempt_network_cleanup':'Recovered verbatim from original cat stdout in the two exported tool records. Never reconstructed from assumptions.','first_attempt_runtime':'Overwritten by retry before export; not recoverable. No replacement fabricated. First attempt failed before any resolver process, is never counted and is evidenced by original traceback plus recovered network/cleanup. Successful retry has complete actual runtime/namespace/process receipts.','recipe':'Executed retry recipe retained in attempts/probe-appworld-retry-executed.py; active recipe fixes unique runtime/network/cleanup labels. Existing results block re-execution.'})
print(json.dumps({'recovered':['first attempt network','first attempt cleanup'],'lost':'first attempt pre-resolution runtime (not fabricated)','retry_receipts_preserved':len(moved)},sort_keys=True))
