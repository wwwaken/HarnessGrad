#!/usr/bin/env python3
"""Disentangle rounding from policy using official unrounded AnswerMetric calls."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
from verify import caught, load_official, write_api_inputs

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0,str(REPO))
official, source = load_official('musique')
from data.scaffolds.qa import base
before = base.QASpec.records
def refuse(spec): raise PermissionError('no released rows during independent scoring')
base.QASpec.records = refuse
try:
    local = importlib.import_module('data.datasets.musique')
finally:
    base.QASpec.records = before
assert not local._SPEC._records
panels = {}
for panel in ['authored', 'crosscheck']:
    cases = json.loads((HERE / ('inputs-' + panel + '.json')).read_text())['musique']
    per_input = []
    local_values = []
    gold_lines, prediction_lines = [], []
    for row in cases:
        gf,pf = write_api_inputs('musique',row,HERE/'api-inputs'/panel/'musique'/row['id'])
        gold_lines.append(gf.read_text())
        prediction_lines.append(pf.read_text())
        unrounded = official.AnswerMetric()
        unrounded(row['prediction']['answer'], [row['gold']['answer'], *row['gold']['aliases']])
        raw_em, raw_f1 = unrounded.get_metric()
        local_value = local.score_prediction(row['prediction'],row['gold'])
        local_values.append(local_value)
        rounded = official.evaluate(str(pf),str(gf))
        per_input.append({'id':row['id'],'official_unrounded_answer_f1':raw_f1,
            'official_rounded_evaluator_answer_f1':rounded['answer_f1'],
            'local_unrounded_answer_f1':local_value['official']['answer_f1'],
            'local_reward':local_value['reward'],
            'true_policy_difference':raw_f1 != local_value['reward'],
            'rounded_column_vs_unrounded_reward_difference':rounded['answer_f1'] != local_value['reward']})
    aggregate_dir = HERE/'api-inputs'/panel/'musique'/'aggregate'
    aggregate_dir.mkdir(parents=True,exist_ok=True)
    gagg,pagg = aggregate_dir/'gold.jsonl',aggregate_dir/'predictions.jsonl'
    gagg.write_text(''.join(gold_lines)); pagg.write_text(''.join(prediction_lines))
    upstream = caught(lambda:official.evaluate(str(pagg),str(gagg)))
    adapter = caught(lambda:local.aggregate(local_values))
    keys = ['answer_f1','answer_em','support_f1']
    panels[panel] = {'per_input':per_input,
        'true_policy_difference_count':sum(r['true_policy_difference'] for r in per_input),
        'rounded_column_vs_unrounded_reward_difference_count':sum(r['rounded_column_vs_unrounded_reward_difference'] for r in per_input),
        'aggregate_official':upstream,'aggregate_local':adapter,
        'aggregate_common_metrics_equal':all(upstream['return'][key] == adapter['return'][key] for key in keys)}
assert not local._SPEC._records
print(json.dumps({'panels':panels,'raw_metric_source_sha256':hashlib.sha256((HERE/'source/musique/metrics/answer.py').read_bytes()).hexdigest(),
                  'explanation':'Initial verify.py reward_policy_differences field compares rounded official evaluator column to unrounded reward. This independently calls official AnswerMetric to distinguish policy from precision.',
                  'released_records_loaded':len(local._SPEC._records)},indent=2))
