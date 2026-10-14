#!/usr/bin/env python3
"""Independent scorer calls. Does not load or aggregate the old result fixtures."""
import ast
import contextlib
import copy
import hashlib
import importlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def import_source(path, name):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def caught(call):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            value = call()
        return {'return': value, 'stdout': buf.getvalue(), 'error': None}
    except Exception as exc:
        return {'return': None, 'stdout': buf.getvalue(), 'error': {
            'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}}

def load_official(ds):
    entries = {'fever': 'scorer.py', 'strategyqa': 'eval.py', 'hotpotqa': 'hotpot_evaluate_v1.py',
               'triviaqa': 'evaluation/triviaqa_evaluation.py', 'musique': 'evaluate_v1.0.py',
               'sportsunderstanding': 'task_metrics.py'}
    src = HERE / 'source' / ds / entries[ds]
    sys.path.insert(0, str(HERE / 'source' / ds))
    if ds == 'sportsunderstanding':
        # Match the report's narrow source-function scope, not the full module.
        import numpy as np
        wanted = {'measure_multiple_choice_grade', 'argmax'}
        tree = ast.parse(src.read_text(), filename=str(src))
        definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
        assert {node.name for node in definitions} == wanted
        namespace = {'np': np, 'hashlib': hashlib}
        exec(compile(ast.Module(body=definitions, type_ignores=[]), str(src), 'exec'), namespace)
        from types import SimpleNamespace
        mod = SimpleNamespace(**{k:namespace[k] for k in wanted})
    else:
        mod = import_source(src, 'verify_official_' + ds)
    return mod, src

def write_api_inputs(ds, row, directory):
    directory.mkdir(parents=True, exist_ok=True)
    ident = row['id']
    gold, prediction = row['gold'], row['prediction']
    if ds == 'hotpotqa':
        og = [{'_id': ident, 'answer': gold['answer'], 'supporting_facts': gold['supporting_facts']}]
        op = {'answer': {ident: prediction['answer']}, 'sp': {}}
        if 'predicted_evidence' in prediction:
            op['sp'][ident] = prediction['predicted_evidence']
    elif ds == 'musique':
        og = {'id': ident, 'answer': gold['answer'], 'answer_aliases': gold['aliases'], 'answerable': True,
              'paragraphs': [{'idx': pair[1], 'title': pair[0], 'is_supporting': True} for pair in gold['supporting_facts']]}
        op = {'id': ident, 'predicted_answer': prediction['answer'],
              'predicted_support_idxs': [pair[1] for pair in prediction.get('predicted_evidence', [])], 'predicted_answerable': True}
    else:
        og, op = {ident: gold}, {ident: prediction}
    suffix = '.jsonl' if ds == 'musique' else '.json'
    gf, pf = directory / ('gold' + suffix), directory / ('predictions' + suffix)
    gf.write_text(json.dumps(og) + '\n')
    pf.write_text(json.dumps(op) + '\n')
    return gf, pf

def main():
    ds, panel = sys.argv[1:]
    cases = json.loads((HERE / ('inputs-' + panel + '.json')).read_text())[ds]
    official, osource = load_official(ds)
    # Refuse all dataset record construction before imports, including native parquet.
    from data.scaffolds.qa import base
    before = base.QASpec.records
    suppressed = []
    def no_rows(spec):
        suppressed.append(spec.name)
        raise PermissionError('independent verification: released dataset row loading forbidden')
    base.QASpec.records = no_rows
    try:
        local = importlib.import_module('data.datasets.' + ds)
    finally:
        base.QASpec.records = before
    assert local._SPEC._records == []
    assert base.QASpec.records is before
    rows = []
    for row in cases:
        item = {'id': row['id'], 'input': row}
        if ds == 'strategyqa':
            def invoke():
                e = official.AnswerEvaluator(None)
                e({'answer': row['gold_answer']}, row['prediction'])
                return e.get_metrics()
            o = caught(invoke)
            g = {'answer': 'Yes' if row['gold_answer'] else 'No'}
            l = caught(lambda: local.score(row['prediction'], g))
            ov, lv = [o['return']['Accuracy']], [l['return']['reward']]
            if isinstance(row['prediction'], bool):
                p = caught(lambda: local.score('Yes' if row['prediction'] else 'No', g))
                item['boolean_projected_local'] = p
                item['projected_agrees'] = o['return']['Accuracy'] == p['return']['reward']
        elif ds == 'sportsunderstanding':
            o = caught(lambda: official.measure_multiple_choice_grade([copy.deepcopy(row['official_sample'])]))
            l = caught(lambda: local.score(row['local_prediction'], row['local_gold']))
            ov, lv = [o['return']], [l['return']['reward']]
        elif ds == 'fever':
            instance = {**copy.deepcopy(row['canonical_gold']), 'predicted_label': row['prediction']['answer'],
                        'predicted_evidence': copy.deepcopy(row['prediction']['predicted_evidence'])}
            o = caught(lambda: official.is_strictly_correct(instance, max_evidence=5))
            l = caught(lambda: local.score_prediction(copy.deepcopy(row['prediction']), copy.deepcopy(row['local_gold'])))
            item['official_full_singleton_api'] = caught(lambda: official.fever_score([copy.deepcopy(instance)]))
            ov, lv = [float(o['return'])], [l['return']['reward']]
        else:
            gf, pf = write_api_inputs(ds, row, HERE / 'api-inputs' / panel / ds / row['id'])
            if ds == 'hotpotqa':
                o = caught(lambda: official.eval(str(pf), str(gf)))
                l = caught(lambda: local.score_prediction(row['prediction'], row['gold']))
                keys = ['em', 'f1', 'sp_em', 'sp_f1', 'joint_em', 'joint_f1']
                om = ast.literal_eval(o['stdout'][o['stdout'].index('{'):]) if not o['error'] else None
                o['parsed_metrics'] = om
                ov = [om[k] for k in keys] if om else None
                lv = [l['return']['official'][k] for k in keys] if not l['error'] else None
            elif ds == 'musique':
                o = caught(lambda: official.evaluate(str(pf), str(gf)))
                l = caught(lambda: local.score_prediction(row['prediction'], row['gold']))
                keys = ['answer_f1', 'answer_em', 'support_f1']
                ov = [o['return'][k] for k in keys] if not o['error'] else None
                lv = [round(l['return']['official'][k],3) for k in keys] if not l['error'] else None
                item['reward_policy_differs_from_answer_f1'] = (
                    o['return']['answer_f1'] != l['return']['reward']) if not (o['error'] or l['error']) else None
            else:
                o = caught(lambda: official.evaluate_triviaqa(json.loads(gf.read_text()), json.loads(pf.read_text()), mute=True))
                l = caught(lambda: local.score(row['prediction'], {'accepted':local.get_ground_truths(row['gold'])}))
                ov = [o['return']['exact_match']] if not o['error'] else None
                lv = [l['return']['reward']*100] if not l['error'] else None
        item.update(official=o, local=l, official_compared=ov, local_compared=lv)
        measured = not (o['error'] or l['error'])
        item['numeric_comparison'] = measured
        item['agreement'] = all(abs(a-b)<1e-10 for a,b in zip(ov,lv,strict=True)) if measured else None
        rows.append(item)
    assert local._SPEC._records == []
    summary = {'inputs': len(rows), 'numeric_comparisons': sum(r['numeric_comparison'] for r in rows),
               'agree': sum(r['agreement'] is True for r in rows), 'diverge': sum(r['agreement'] is False for r in rows),
               'nonnumeric': sum(not r['numeric_comparison'] for r in rows)}
    if ds == 'strategyqa':
        projected = [r for r in rows if 'projected_agrees' in r]
        summary['boolean_projected_compared'] = len(projected)
        summary['boolean_projected_agree'] = sum(r['projected_agrees'] for r in projected)
    if ds == 'fever':
        summary['full_singleton_errors'] = sum(bool(r['official_full_singleton_api']['error']) for r in rows)
    if ds == 'musique':
        summary['reward_policy_differences'] = sum(r['reward_policy_differs_from_answer_f1'] is True for r in rows)
    sources = [{'path': str(osource.relative_to(REPO)), 'sha256': sha(osource)},
               {'path': str(Path(local.__file__).relative_to(REPO)), 'sha256':sha(local.__file__)}]
    for name in ['data/scaffolds/qa/evidence_scorers.py','data/scaffolds/qa/base.py','data/scaffolds/qa/prediction.py']:
        sources.append({'path':name,'sha256':sha(REPO/name)})
    result = {'dataset': ds, 'panel':panel, 'summary':summary, 'cases':rows, 'sources':sources,
        'input_sha256':sha(HERE/('inputs-'+panel+'.json')),
        'import_row_loading_guard': {'refused_specs': suppressed, 'restored_before_score':base.QASpec.records is before,
                                    'cached_records_after_score':len(local._SPEC._records)},
        'scope':'bounded synthetic scoring; no benchmark/model/production runtime execution'}
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == '__main__': main()
