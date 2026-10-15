import hashlib,json,pathlib,subprocess,sys
F=pathlib.Path('/fixture');mode=sys.argv[1];data=json.loads((F/'appworld-inputs.json').read_text());results=[]
for case in data['cases']:
 argv=[sys.executable,str(F/'run_appworld.py'),mode,case['id']]
 child=subprocess.run(argv,capture_output=True,text=True,timeout=90)
 item={'id':case['id'],'argv':argv,'exit_code':child.returncode,'stdout':child.stdout,'stderr':child.stderr}
 if child.returncode==0: item['output']=json.loads(child.stdout)
 results.append(item)
print(json.dumps({'mode':mode,'children':results,'interpreter':sys.executable,'interpreter_sha256':hashlib.sha256(pathlib.Path(sys.executable).read_bytes()).hexdigest()},indent=2))
