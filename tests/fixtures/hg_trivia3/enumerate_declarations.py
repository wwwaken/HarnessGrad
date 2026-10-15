"""Transcribe the completed w-trivia2 pinned metadata enumeration, without HTTP."""
import json
import pathlib
import sys

HERE=pathlib.Path(__file__).resolve().parent
PRIOR=HERE.parent/'hg_trivia2'
revision=json.loads((PRIOR/'views/hub-revision-final.json').read_text())
routes={r['config_name']:r['data_files'] for r in revision['cardData']['configs']}
dirs={p['path'] for p in json.loads((PRIOR/'views/hub-tree-final.json').read_text())
      if p['type']=='directory'}
result={'revision':revision['sha'],'declarations':[
    {'name':v['config_name'],'counts':{s['name']:s.get('num_examples') for s in v['splits']},
     'export_routes':routes.get(v['config_name']),'export_directory':v['config_name'] in dirs}
    for v in revision['cardData']['dataset_info']]}
encoded=json.dumps(result,indent=2)+'\n'
if '--write' in sys.argv:
    (HERE/'declarations.json').write_text(encoded)
else:
    assert (HERE/'declarations.json').read_text()==encoded
for v in result['declarations']:
    print(v['name'],json.dumps(v['counts'],sort_keys=True),
          'routed='+str(v['export_routes'] is not None),'directory='+str(v['export_directory']))
