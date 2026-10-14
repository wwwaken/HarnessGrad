#!/usr/bin/env python3
"""Stage immutable sources/crosschecks and independently authored controlled inputs."""
import copy
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
OLD = Path('/tmp/hg-offscorer/tests/fixtures/hg_woffscorer')
receipts = []
def copied(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    before = hashlib.sha256(src.read_bytes()).hexdigest()
    after = hashlib.sha256(dst.read_bytes()).hexdigest()
    assert before == after
    receipts.append({'read_only_origin': str(src), 'copy': str(dst.relative_to(HERE)), 'sha256': after})

copied(OLD / 'offline_exec.py', HERE / 'offline_exec.py')
copied(OLD / 'fever/official_scorer.py', HERE / 'source/fever/scorer.py')
copied(OLD / 'bigbench/official-task-metrics.py', HERE / 'source/sportsunderstanding/task_metrics.py')
for name in ['eval.py', 'sari.py']:
    copied(OLD / 'numeric_boolean/source/strategyqa' / name, HERE / 'source/strategyqa' / name)
for ds in ['hotpotqa', 'triviaqa', 'musique']:
    for src in sorted((OLD / 'public_qa/source' / ds).rglob('*')):
        if src.is_file() and src.suffix in ['.py', '']:
            copied(src, HERE / 'source' / ds / src.relative_to(OLD / 'public_qa/source' / ds))

crosscheck = {
    'strategyqa': json.loads((OLD / 'numeric_boolean/inputs.json').read_text())['strategyqa'],
    'sportsunderstanding': json.loads((OLD / 'bigbench/inputs.json').read_text())['sportsunderstanding'],
    'fever': json.loads((OLD / 'fever/inputs.json').read_text()),
}
for ds in ['hotpotqa', 'triviaqa', 'musique']:
    crosscheck[ds] = json.loads((OLD / 'public_qa/inputs' / ds / 'cases.json').read_text())['cases']

# No old output files or comparison implementations are read.
# These inputs are newly authored against the inspected source contracts.
authored = {'strategyqa': [], 'sportsunderstanding': [], 'fever': [], 'hotpotqa': [], 'triviaqa': [], 'musique': []}
for g in [True, False]:
    for pred in [True, False]:
        authored['strategyqa'].append({'id': f'boolean-{g}-{pred}', 'gold_answer': g, 'prediction': pred})
authored['strategyqa'] += [
    {'id': 'upper-yes', 'gold_answer': True, 'prediction': 'YES'},
    {'id': 'padded-no', 'gold_answer': False, 'prediction': ' No! '},
    {'id': 'yes-explanation', 'gold_answer': True, 'prediction': 'Yes because it follows'},
]
for name, logits, text in [
    ('matched', [-0.2, -3.0], 'plausible'),
    ('empty', [-0.2, -3.0], ''),
    ('both', [-0.2, -3.0], 'plausible / implausible'),
    ('contradicting-vector', [-3.0, -0.2], 'plausible'),
]:
    authored['sportsunderstanding'].append({'id': name, 'official_sample': {
        'choice': ['plausible', 'implausible'], 'log_prob': logits,
        'target_scores': {'plausible': 1, 'implausible': 0}},
        'local_prediction': text, 'local_gold': {'answer': 'plausible'}})
canonical = {'label': 'SUPPORTS', 'evidence': [[[0,0,'Verify_A',3],[0,1,'Verify_B',8]]]}
for name, pred, flat in [
    ('group-complete', [['Verify_A',3],['Verify_B',8]], False),
    ('group-partial', [['Verify_A',3]], False),
    ('flat-partial', [['Verify_A',3]], True),
    ('group-wrong', [['Verify_Unknown',11]], False),
]:
    authored['fever'].append({'id': name, 'canonical_gold': copy.deepcopy(canonical),
        'local_gold': {'answer': 'SUPPORTS', 'evidence':
            [['Verify_A',3,'synthetic'],['Verify_B',8,'synthetic']] if flat else copy.deepcopy(canonical['evidence'])},
        'prediction': {'answer': 'SUPPORTS', 'predicted_evidence': pred}})
pairs = [['Verify_A',3],['Verify_B',8]]
for name, gold_support, pred_support, pred_answer in [
    ('complete', pairs, pairs, 'olive silver'),
    ('partial', pairs, pairs[:1], 'olive silver'),
    ('empty-both', [], [], 'olive silver'),
    ('partial-answer', pairs, pairs, 'olive'),
]:
    authored['hotpotqa'].append({'id': name, 'gold': {'answer': 'olive silver', 'supporting_facts': gold_support},
        'prediction': {'answer': pred_answer, 'predicted_evidence': pred_support}})
for name, aliases, prediction in [
    ('exact', ['olive silver'], 'olive silver'),
    ('normalize', ['olive silver'], 'The OLIVE-SILVER'),
    ('partial', ['olive silver'], 'olive'),
    ('empty-alias-exception', [], 'olive'),
]:
    authored['triviaqa'].append({'id': name, 'gold': {'NormalizedAliases': aliases, 'HumanAnswers': []}, 'prediction': prediction})
for name, evidence in [
    ('complete', pairs), ('partial', pairs[:1]),
    ('extra', pairs + [['Verify_C',14]]), ('omitted', None), ('empty', [])]:
    pred = {'schema_version': 1, 'answer': 'olive silver'}
    if evidence is not None: pred['predicted_evidence'] = evidence
    authored['musique'].append({'id': name, 'gold': {'id': name, 'answer': 'olive silver', 'aliases': [], 'supporting_facts': pairs}, 'prediction': pred})
(HERE / 'inputs-authored.json').write_text(json.dumps(authored, indent=2) + '\n')
(HERE / 'inputs-crosscheck.json').write_text(json.dumps(crosscheck, indent=2) + '\n')
(HERE / 'source-copy-identities.json').write_text(json.dumps(receipts, indent=2) + '\n')
print(json.dumps({'copied_source_files': len(receipts), 'authored_counts': {k:len(v) for k,v in authored.items()}, 'crosscheck_counts': {k:len(v) for k,v in crosscheck.items()}}, indent=2))
