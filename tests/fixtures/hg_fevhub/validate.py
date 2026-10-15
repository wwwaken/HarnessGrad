import hashlib,json,re,subprocess
from pathlib import Path
p=Path('tests/fixtures/hg_fevhub')
report=Path('registry/w-fevhub-receipts.md').read_text()
proposal=json.loads(Path('registry/proposals/w-fevhub.json').read_text())
assert proposal['outcome']=='absent'
assert set(proposal)=={'worker','dataset','blocker','outcome','producing_execution_receipt','nei_input_receipt','enumerated_scope','observed_append','next_action_replacement','standing_limit_argument'}
assert '\n' not in proposal['standing_limit_argument']
plans=[pair for f in sorted(p.glob('plan-*.json')) for pair in json.loads(f.read_text())]
receipts=[json.loads(f.read_text()) for f in p.glob('*.request.json')]
assert len(plans)==len(receipts)==226
by_name={r['name']:r for r in receipts}
for name,url in plans:assert by_name[name]['url']==url
for path,line in re.findall(r'((?:tests/fixtures/hg_fevhub/|registry/)[A-Za-z0-9_./-]+):([0-9]+)',report):
 f=Path(path);assert f.is_file(),path
 assert int(line)<=len(f.read_text().splitlines()),(path,line)
pattern = r'verbatim excerpt `([^`]+):([0-9]+)`:' + chr(10)*2 + '```text' + chr(10) + r'(.*?)' + chr(10) + '```'
quotes = re.findall(pattern, report, re.S)
assert len(quotes) == 32, len(quotes)
for filename, number, quote in quotes:
 body=Path(filename).read_text(); assert quote in body, filename
 assert body[:body.index(quote)].count(chr(10))+1 == int(number), (filename,number)
scope=json.loads((p/'scope.json').read_text())
assert len(scope['main_history'])==33
assert all(x['tree_state']=='FOUND' for x in scope['main_history'])
unknown=[x['commit']['id'] for x in scope['generated_history'] if x['tree_state']=='UNKNOWN']
assert unknown==['ad8321607bcad0e534c243ec8c108a5787cea6c8']
text_unknown=[x['oid'] for x in scope['hub_text_objects'] if x['state']=='UNKNOWN']
assert text_unknown==['ab71339be067bc98bcad7df12a12c0e05fc6b521']
assert sum(x['path']=='README.md' and x['state']=='FOUND' for x in scope['hub_text_objects'])==7
assert all(r['url'].startswith('https://') for r in receipts)
assert not any('/8002' in r['url'] or '/8001' in r['url'] or r['url'].endswith(('valid.jsonl','train.jsonl','.parquet')) for r in receipts)
files=sorted([f for f in p.rglob('*') if f.is_file()]+[Path('registry/w-fevhub-receipts.md'),Path('registry/proposals/w-fevhub.json'),Path('registry/w-fevhub-validation.txt')])
for f in files:assert f.stat().st_size<1_000_000,(str(f),f.stat().st_size)
changed=subprocess.run(['git','diff','--exit-code','--','registry/dataset-blockers.json','docs/adapter-integration-journal.md'],text=True,capture_output=True)
assert changed.returncode==0 and changed.stdout=='',changed.stdout
print(json.dumps({'valid':True,'planned_requests':len(plans),'fixture_files':len(files)-3,'commit_files':len(files),'all_files_under_1_MB':True,'main_history_trees':'33/33','card_blobs':'7/7','generated_inventory_unknown':unknown,'loader_blob_unknown':text_unknown,'registry_and_journal_unchanged':True},sort_keys=True))
print('FILE SIZES (bytes)')
for f in files:print(str(f.stat().st_size)+' '+str(f))
