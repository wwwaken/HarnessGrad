"""Record validation commands and streams without modifying run receipts."""
import json,pathlib,subprocess,sys
repo=pathlib.Path(__file__).resolve().parents[2];packet=repo/'reports/w-tb89e-evidence'
checks=[['python3','tools/check_dataset_blockers.py'],['python3','reports/w-tb89e-evidence/verify.py'],['python3','-m','pytest','tests/quality/test_dataset_blockers.py','--basetemp=/tmp/w-tb89e-registry-pytest','-q'],['git','diff','--check']]
with (repo/'reports/w-tb89e-validation.txt').open('w') as out:
 out.write('Focused policy/registry/authorization/scorer-isolation tests run before execution:\n$ python3 -m pytest tests/quality/test_dataset_blockers.py tests/quality/test_diagnostic_policy.py tests/quality/test_unobserved_diagnostic_c2.py tests/quality/test_scorer_isolation_option_b.py --basetemp=/tmp/w-tb89e-pytest -q\n')
 out.write(pathlib.Path('/tmp/w-tb89e-focused-tests.txt').read_text())
 for args in checks:
  r=subprocess.run(args,cwd=repo,text=True,capture_output=True)
  out.write('\n$ '+' '.join(args)+'\n'+r.stdout+r.stderr+'\n[exit '+str(r.returncode)+']\n');out.flush()
  if r.returncode:print('Failed',args);sys.exit(r.returncode)
 sizes=[(p.stat().st_size,str(p.relative_to(repo))) for p in packet.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 for name in ('reports/w-tb89e-receipts.md','reports/w-tb89e-validation.txt','docs/dataset-blockers.json','docs/adapter-integration-journal.md'):
  p=repo/name;sizes.append((p.stat().st_size,name))
 out.write('\nChanged-file byte sizes (including modified existing documents):\n'+json.dumps(sorted(sizes,reverse=True),indent=2)+'\n')
 assert all(size<1000000 for size,name in sizes if name.startswith('reports/w-tb89e'))
 out.write('\nEvery new evidence/report file is under 1,000,000 bytes. Full raw/bulk artifacts remain external.\n')
print('Validation passed; reports/w-tb89e-validation.txt')
