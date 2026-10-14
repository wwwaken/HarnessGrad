"""Execute both unmodified upstream programs using wholly invented inputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path('/opt/hg-wujson/evaluator')
out = Path('/receipts/synthetic')
out.mkdir()
provenance = json.loads((root / 'provenance.json').read_text())
row = {'_id': 'SYNTHETIC-W-UJSON-A', 'answer': 'fictional azure',
       'answer_id': 'SYNTHETIC-Q-W-UJSON',
       'supporting_facts': [['Synthetic Document A', 0], ['Synthetic Document B', 1]],
       'evidences': [['invented subject', 'imaginary relation', 'fabricated object']],
       'evidences_id': []}
pred = {'answer': {row['_id']: row['answer']},
        'sp': {row['_id']: row['supporting_facts']},
        'evidence': {row['_id']: row['evidences']}}
(out / 'gold.json').write_text(json.dumps([row]))
(out / 'prediction.json').write_text(json.dumps(pred))
(out / 'aliases.jsonl').write_text('')
results = []
for name in ('2wikimultihop_evaluate.py', '2wikimultihop_evaluate_v1.1.py'):
    source = root / name
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest == provenance['files'][name]['sha256']
    args = [sys.executable, '-I', '-B', str(source), str(out / 'prediction.json'), str(out / 'gold.json')]
    if 'v1.1' in name:
        args.append(str(out / 'aliases.jsonl'))
    p = subprocess.run(args, capture_output=True, text=True, timeout=30)
    (out / (name + '.stdout.txt')).write_text(p.stdout)
    (out / (name + '.stderr.txt')).write_text(p.stderr)
    assert p.returncode == 0, p.stderr
    metrics = json.loads(p.stdout)
    assert len(metrics) == 16 and set(metrics.values()) == {100.0}, metrics
    results.append({'argv': args, 'returncode': p.returncode,
                    'source_sha256': digest, 'metrics': metrics})
print(json.dumps({'scope': 'fabricated one-row control; no benchmark or model',
                  'metric_identity': 'upstream Answer/Sup/Evi/Joint EM,F1,precision,recall percent',
                  'results': results, 'passed': True}, indent=2))
