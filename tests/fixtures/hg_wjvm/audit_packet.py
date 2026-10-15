#!/usr/bin/env python3
"""Audit retained observations without executing any scorer; emit exact raw locators."""
import hashlib
import json
import os
from pathlib import Path
import re

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / 'reports/w-jvm-evidence'
# Selected from the corresponding external /proc capture and exec/fork traces.
CASES = {
    'scienceworld': ('live', {'check': 601047, 'jvm': 601049}),
    'jericho': ('live', {'native_game_and_check': 601115}),
    'spreadsheetbench': ('followup', {'check': 602985, 'launcher': 603101,
                                    'first_soffice': 603144, 'conversion_soffice': 603251}),
    'ds1000': ('followup', {'check': 603773, 'runner': 603801, 'manager': 603803, 'worker': 603808}),
    'livecodebench': ('followup', {'check': 603956, 'worker': 603958}),
    'bird_minidev': ('followup', {'sqlite_and_check': 603987}),
}


def load(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cases = {}
    all_sources = []
    for name, (group, roles) in CASES.items():
        base = EVIDENCE / group / name
        summary = load(base / 'process-summary.json')
        cleanup = load(base / 'cleanup.json')
        verdict = load(base / 'output/evidence.json')
        config = load(base / 'config.json')
        assert verdict['measured'] is True
        assert not summary['timed_out']
        assert not summary['remaining_before_collector_path_cleanup']
        assert cleanup['case_absent'] and cleanup['scratch_absent']
        assert all(cleanup['observed_pid_absence'].values())
        assert not (base / 'collector-forced-cleanup.json').exists()
        assert float((base / 'output/reward.txt').read_text()) == verdict['reward']
        observed_roles = {}
        for role, pid in roles.items():
            rows = []
            for line_number, line in enumerate((base / 'proc-snapshots.jsonl').read_text().splitlines(), 1):
                record = json.loads(line)
                if record['pid'] != pid or not isinstance(record['limits'], str):
                    continue
                limits = {}
                for limit_line in record['limits'].splitlines()[1:]:
                    fields = re.split(r'\s{2,}', limit_line.strip())
                    limits[fields[0]] = {'soft': fields[1], 'hard': fields[2],
                                        'units': fields[3] if len(fields) > 3 else None}
                # Ignore early pre-entry snapshots of the same PID.
                if limits['Max cpu time']['soft'] != str(config['rlimits']['RLIMIT_CPU']):
                    continue
                assert limits['Max address space']['soft'] == str(config['rlimits']['RLIMIT_AS'])
                assert limits['Max open files']['soft'] == str(config['rlimits']['RLIMIT_NOFILE'])
                assert record['affinity'] == config['affinity']
                rows.append({'pid': pid, 'raw_snapshot': str((base / 'proc-snapshots.jsonl').relative_to(REPO)),
                             'line': line_number, 'time_ns': record['time_ns'],
                             'exe': record['exe'], 'cwd': record['cwd'], 'cmdline': record['cmdline'],
                             'limits': limits, 'affinity': record['affinity'], 'cgroup': record['cgroup']})
            assert rows, (name, role, pid)
            observed_roles[role] = rows[-1]
        sources = load(base / 'sources.json')
        for source in sources:
            path = Path(source['path'])
            assert path.is_file() and digest(path) == source['sha256'], source
        all_sources.extend(sources)
        # These are byte-for-byte production checks, not patched scoring functions.
        check = base / 'inputs' / ('check.py' if name in ('scienceworld', 'jericho') else 'verify/check.py')
        assert digest(check) == digest(REPO / f'data/datasets/{name}/verify/check.py')
        network = load(base / 'output/network.json')
        assert network['netns'] != network['parent_netns']
        assert not network['routes'].splitlines()[1:]
        workbook_values = None
        if name == 'spreadsheetbench':
            import openpyxl
            before = openpyxl.load_workbook(base / 'inputs/result.xlsx', data_only=False)
            after = openpyxl.load_workbook(base / 'after-work/result.xlsx', data_only=True)
            workbook_values = {'input_A1_formula': before.active['A1'].value,
                               'output_A1_cached_value': after.active['A1'].value}
            before.close()
            after.close()
            assert workbook_values == {'input_A1_formula': '=1+2', 'output_A1_cached_value': 3}
        cases[name] = {'artifact_directory': str(base.relative_to(REPO)), 'roles': observed_roles,
                       'native_check_evidence': verdict,
                       'process_summary': summary, 'cleanup': cleanup,
                       'scratch': load(base / 'scratch-observations.json'),
                       'resource_scope': 'collector-controlled local execution, not production admission',
                       'cgroup_raw': str((base / 'cgroups.json').relative_to(REPO)),
                       'workbook_values': workbook_values}
    # A later independent bounded absence check also includes superseded attempts.
    absence = {}
    for summary_path in sorted(EVIDENCE.rglob('process-summary.json')):
        summary = load(summary_path)
        for pid, record in summary['observed_pids'].items():
            path = Path('/proc') / pid / 'stat'
            if path.exists():
                raw = path.read_text()
                current_start = raw[raw.rindex(')') + 2:].split()[19]
                absent = current_start != record['start_ticks']
            else:
                absent = True
            absence[f'{summary_path.relative_to(REPO)}:pid={pid}'] = absent
    assert all(absence.values())
    roots = [load(p) for p in sorted(EVIDENCE.rglob('root-cleanup.json'))]
    assert all(row['absent'] and not Path(row['work_root']).exists() for row in roots)
    fold = REPO / 'data/datasets/scienceworld/test_fold.json'
    fold_rows = load(fold)['tasks']
    split = {'scienceworld_test_fold_path': str(fold.relative_to(REPO)), 'sha256': digest(fold),
             'scienceworld_variation_zero_in_test_fold': any(row['task_name'] == 'task-3-find-non-living-thing' and row['variation'] == 0 for row in fold_rows),
             'jericho_acorncourt_hash_split_bucket': hashlib.sha256(b'acorncourt').digest()[0] % 3,
             'reference_walkthrough_requested_or_replayed': False}
    assert split['scienceworld_variation_zero_in_test_fold'] is False
    report = {'cases': cases, 'all_captured_pid_identities_absent_at_audit': absence,
              'root_cleanup_receipts': roots, 'input_scope': split,
              'source_identities_recomputed_and_matching': all_sources,
              'missing_prerequisites_for_final_controls': [],
              'benchmark': False, 'production_authorized': False,
              'unexercised': ['production verifier envelope and trusted admission',
                              'timeout/kill and error branches beyond retained LibreOffice abort',
                              'exhaustive descendants/namespaces and peak resource use',
                              'other dataset tasks, scientific-library dependencies and runtime branches']}
    (EVIDENCE / 'observations.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    # Includes the observer sources as well as every raw and derived artifact.
    paths = sorted(p for root in (EVIDENCE, REPO / 'tests/fixtures/hg_wjvm')
                   for p in root.rglob('*') if p.is_file() and p.name != 'SHA256SUMS'
                   and '__pycache__' not in p.parts)
    lines = [f'{digest(p)}  {p.relative_to(REPO)}\n' for p in paths]
    (EVIDENCE / 'SHA256SUMS').write_text(''.join(lines))
    print(json.dumps({'audited_runtime_controls': list(cases), 'source_hashes_match': True,
                      'all_captured_pid_identities_absent': True, 'all_owned_roots_absent': True,
                      'manifest_entries': len(paths), 'production_authorized': False}, sort_keys=True))


if __name__ == '__main__':
    main()
