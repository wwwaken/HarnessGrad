#!/usr/bin/env python3
"""Compare measured common metrics; retain errors and separate policy differences."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEYS = {
    'hotpotqa': ['em', 'f1', 'sp_em', 'sp_f1', 'joint_em', 'joint_f1'],
    'triviaqa': ['exact_match'],
    'musique': ['answer_f1', 'answer_em', 'support_f1'],
    'twowikimultihopqa': [prefix + name for prefix in ['', 'sp_', 'evi_', 'joint_']
                        for name in ['em', 'f1', 'prec', 'recall']],
}


def project_local(ds, value):
    if ds == 'triviaqa': return {'exact_match': value['reward'] * 100}
    raw = value['official']
    if ds == 'musique': return {key: round(raw[key], 3) for key in KEYS[ds]}
    if ds == 'twowikimultihopqa': return {key: round(raw[key] * 100, 2) for key in KEYS[ds]}
    return {key: raw[key] for key in KEYS[ds]}


def main():
    results = {}
    for ds, keys in KEYS.items():
        official = json.loads((HERE / 'outputs' / ds / 'official.stdout.json').read_text())
        local = json.loads((HERE / 'outputs' / ds / 'local.stdout.json').read_text())
        cases = json.loads((HERE / 'inputs' / ds / 'cases.json').read_text())['cases']
        assert [row['id'] for row in official['cases']] == [row['id'] for row in local['cases']] == [row['id'] for row in cases]
        rows = []
        for gold, lhs, rhs in zip(cases, official['cases'], local['cases']):
            common_local = project_local(ds, rhs['raw_return']) if rhs['error'] is None else None
            common_official = {key: lhs['metrics'][key] for key in keys} if lhs['error'] is None else None
            differences = ([key for key in keys if common_official[key] != common_local[key]]
                           if common_official is not None and common_local is not None else None)
            row = {'id': lhs['id'], 'scope': gold['scope'], 'official_metrics': common_official,
                   'local_metrics_at_official_scale_and_rounding': common_local, 'divergent_metric_keys': differences,
                   'official_error': lhs['error'], 'local_error': rhs['error']}
            if ds == 'musique':
                raw = rhs['raw_return']
                row['platform_reward'] = raw['reward']
                row['official_answer_f1_raw_local_component'] = raw['official']['answer_f1']
                row['reward_differs_from_official_answer_f1'] = raw['reward'] != raw['official']['answer_f1']
            if ds == 'triviaqa' and lhs['error'] is None:
                row['upstream_f1_auxiliary_local_unimplemented'] = lhs['metrics']['f1']
            rows.append(row)
        measured = [row for row in rows if row['divergent_metric_keys'] is not None]
        results[ds] = {'compared_metric_keys': keys, 'total_controlled_inputs': len(rows),
                       'numeric_comparisons': len(measured),
                       'agreeing_inputs': sum(not row['divergent_metric_keys'] for row in measured),
                       'divergent_inputs': sum(bool(row['divergent_metric_keys']) for row in measured),
                       'non_numeric_inputs': len(rows) - len(measured),
                       'compared_metric_cells': len(measured) * len(keys),
                       'divergent_metric_cells': sum(len(row['divergent_metric_keys']) for row in measured), 'cases': rows}
        if ds == 'musique':
            results[ds]['platform_reward_vs_official_answer_f1_policy_difference_count'] = sum(row['reward_differs_from_official_answer_f1'] for row in rows)
        if ds in ['musique', 'twowikimultihopqa']:
            results[ds]['aggregate_common_metrics_equal'] = all(
                official['aggregate_raw']['metrics'][key] == local['aggregate_raw'][key] for key in keys)
    (HERE / 'comparison.json').write_text(json.dumps(results, indent=2, sort_keys=True) + '\n')
    print(json.dumps({ds: {key: value for key, value in info.items() if key != 'cases'} for ds, info in results.items()}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
