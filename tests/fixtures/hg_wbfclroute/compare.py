#!/usr/bin/env python3
"""Join raw outcomes, keeping failed complete routes unmeasured."""
from collections import Counter
import json
from pathlib import Path
P = Path(__file__).resolve().parent

def load(name):
    return json.loads((P / (name + '.stdout.txt')).read_text())

def compare():
    output = {'datasets': {}, 'primary_numeric_pairs': 0, 'primary_controls': 0,
              'complete_dataset_routes_demonstrated': 0, 'requested_dataset_routes': 2,
              'agreement_rate': None,
              'scope': 'The two requested complete dataset module routes; not global S4 coverage.'}
    for dataset, official_mode, local_mode in [('bfcl_v3', 'bfcl-official', 'bfcl-local'),
                                              ('chessbench_puzzles', 'chess-board', 'chess-local')]:
        official, local = load(official_mode), load(local_mode)
        assert official['inputs_sha256'] == local['inputs_sha256']
        a, b = official['rows'], local['rows']
        assert [x['id'] for x in a] == [x['id'] for x in b]
        rows = []
        for x, y in zip(a, b):
            assert x['prediction'] == y['prediction']
            pair = x['measured'] and y['measured']
            entry = {'id': x['id'], 'official': x['score'], 'local': y['score'],
                     'numeric_pair': pair, 'agreement': x['score'] == y['score'] if pair else None,
                     'official_error': x.get('error', {}).get('exception_verbatim'),
                     'official_stage': x['stage']}
            if dataset == 'chessbench_puzzles':
                entry['local_upstream_diagnostic'] = y.get('raw_return', {}).get('official', {}).get('upstream', {}).get('reward')
            rows.append(entry)
        counts = dict(controls=len(rows), numeric_pairs=sum(x['numeric_pair'] for x in rows),
                      numeric_agreements=sum(x['agreement'] is True for x in rows),
                      numeric_divergences=sum(x['agreement'] is False for x in rows),
                      official_numeric=sum(x['measured'] for x in a), official_unmeasured=sum(not x['measured'] for x in a),
                      local_numeric=sum(x['measured'] for x in b), local_unmeasured=sum(not x['measured'] for x in b),
                      official_import_failures=sum(x['stage'].startswith('import_') and 'error' in x for x in a),
                      local_score_counts=dict(Counter(str(x['score']) for x in b)))
        counts['unique_official_errors'] = dict(Counter(x['official_error'] for x in rows if x['official_error']))
        if dataset == 'chessbench_puzzles':
            row_attempt = load('chess-row')['rows']
            assert [x['id'] for x in row_attempt] == [x['id'] for x in a]
            for x, z in zip(rows, row_attempt):
                x['official_row_score'] = z['score']
                x['official_row_error'] = z.get('error', {}).get('exception_verbatim')
            counts['supplementary_row_attempts'] = len(row_attempt)
            counts['supplementary_row_numeric'] = sum(x['measured'] for x in row_attempt)
        output['datasets'][dataset] = {'counts': counts, 'rows': rows}
        output['primary_controls'] += counts['controls']
        output['primary_numeric_pairs'] += counts['numeric_pairs']
        output['complete_dataset_routes_demonstrated'] += int(counts['official_numeric'] > 0)
    imports = [load(x.stem.removesuffix('.stdout')) for x in sorted(P.glob('import-*.stdout.txt'))]
    imports.append(load('ordered-import'))
    output['import_probes'] = [dict(module=x['module'], imported=x['imported'], error=x.get('error', {}).get('exception_verbatim')) for x in imports]
    output['import_probe_counts'] = {'attempts': len(imports), 'imported': sum(x['imported'] for x in imports),
                                     'failed': sum(not x['imported'] for x in imports)}
    return output

if __name__ == '__main__':
    result = compare()
    (P / 'comparison.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'datasets' and k != 'import_probes'}, indent=2))
    print(json.dumps({k: v['counts'] for k, v in result['datasets'].items()}, indent=2))
