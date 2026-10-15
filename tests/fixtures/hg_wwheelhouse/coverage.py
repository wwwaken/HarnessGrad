"""Produce the conservative, dataset-specific payload coverage ledger from receipts."""
import json
import pathlib

HERE=pathlib.Path(__file__).resolve().parent
scope=json.loads((HERE/'source-scope.json').read_text())['datasets']
m=json.loads((HERE/'manifest.json').read_text())['artifacts']
b=json.loads((HERE/'built-artifacts.json').read_text())
installs=json.loads((HERE/'install-summary.json').read_text())

def norm(s):return s.lower().replace('_','-')

out={}
empty=['bfcl_v3','bird_minidev','fever','musique','physicsquestions','sportsunderstanding','strategyqa','twowikimultihopqa']
for name in sorted(set(scope)-{'qa_parquet_startup'}):
    group='qa_parquet_startup' if name in ['gsm8k','hotpotqa','triviaqa'] else name
    keys=sorted(norm(x) for x in scope[group].get('imported_distributions',[]))
    if name=='ds1000':keys+=sorted(k for k,r in m.items() if r['role']=='torch-import-time-native-provider')
    packages={}
    for k in keys:
        r=m[k]
        install=b.get(k,r) if b.get(k,{}).get('status')=='built-offline' else r
        packages[k]={'version':r['version'],'download_status':r['status'],
                     'installable':install.get('status') in ['built-offline','obtained-wheel'],
                     'download_filename':r.get('filename'), 'install_filename':install.get('filename'),
                     'install_sha256':install.get('sha256'), 'reason':r.get('reason')}
    status='no-third-party-payload-required' if name in empty else ('complete-python-import-payloads' if name in ['scienceworld','chessbench_puzzles'] else 'partial-current-host-import-payloads')
    gaps=[]
    if name not in empty+['scienceworld','chessbench_puzzles']:
        gaps.append('mkl-service==2.4.0: no compatible cp312 Linux x86_64 wheel or sdist in preserved PyPI release response. Public NumPy wheel uses a different native provider and does not reproduce the host Conda import surface.')
    if name=='ds1000':
        gaps+=['tensorflow and xgboost appear in released scoring-context imports but have no installed distribution version to pin; no substitute version selected.',
               'Installed gensim==4.3.2 fails with installed scipy==1.13.1 (missing scipy.linalg.triu); matching distributions do not fix compatibility.',
               'Static context/import probes are not a complete selected-task execution closure.']
    if name=='reasoning_gym':gaps.append('Import-only coverage does not certify every selected family constructor, scoring branch or resource access.')
    if name=='spreadsheetbench':gaps.append('LibreOffice and plugins are outside Python wheel payload coverage; formula execution is not exercised here.')
    if name=='scienceworld':gaps.append('Complete Python installation payloads only: JVM/JAR/IPC and execution custody remain separate.')
    out[name]={'payload_status':status,'packages':packages,'gaps':gaps,
               'source_paths':scope[name]['source_paths'],'production_authorized':False}
(HERE/'dataset-payloads.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'complete_nonempty_python_profiles':[k for k,r in out.items() if r['payload_status']=='complete-python-import-payloads'],
    'no_third_party_payload_required':empty,'partial_current_host_profiles':[k for k,r in out.items() if r['payload_status'].startswith('partial')]},indent=2))
