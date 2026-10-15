"""Independent reconciliation of this packet's raw authored controls."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKET = ROOT / 'reports/w-wal-evidence'


def load(path):
    return json.loads(path.read_text())


for label in ['baseline', 'fixed']:
    tree = PACKET / label
    observation = load(tree / 'observations.json')
    assert observation['scratch_removed'] and not Path(observation['scratch']).exists()
    assert observation['live_rows'] == observation['full_export_rows'] == [['base'], ['wal-only']]
    assert observation['main_only_rows'] == [['base']]
    assert observation['closed_wal_header'] == [2, 2]
    assert observation['delete_header'] == [1, 1]
    for name, field in [('unbound-live','unbound_live'), ('bound-live','bound_live'),
                        ('unbound-main-only','unbound_main_only'), ('bound-materialized','bound_materialized'),
                        ('unbound-full-export','unbound_full_export'), ('bound-closed-wal','bound_closed_wal'),
                        ('bound-delete','bound_delete')]:
        result = load(tree / name / 'result.json')
        assert result == observation[field]
        assert result['evidence'] == load(tree / name / 'evidence.json')
        reward = tree / name / 'reward.txt'
        assert (reward.read_text() if reward.exists() else None) == result['reward_text']
        if label == 'fixed' and field in ['bound_live', 'bound_materialized', 'bound_closed_wal']:
            assert result['returncode'] == 3 and result['reward_text'] is None
            assert result['evidence']['measured'] is False
            assert result['evidence']['scorer_input']['verified'] is False
            assert 'SQLite WAL' in result['evidence']['error']
        else:
            expected = '1\n' if field in ['unbound_main_only', 'bound_live', 'bound_materialized'] else '0\n'
            assert result['returncode'] == 0 and result['reward_text'] == expected
            assert result['evidence']['measured'] is True
    for name, metadata in observation['source_before'].items():
        raw = (tree / 'full-raw-before-close' / name).read_bytes()
        assert len(raw) == metadata['bytes']
        assert hashlib.sha256(raw).hexdigest() == metadata['sha256']
    for row in observation['main_only_projection']['receipt']['files']:
        raw = (tree / 'main-only-before-probe' / row['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['sha256']
        assert raw == (tree / 'full-raw-before-close' / row['path']).read_bytes()
    # Readers can change SHM lock/index bytes; do not claim the whole source tree was unchanged.
    for name in ['database.sqlite', 'database.sqlite-wal', 'gold.sql']:
        assert observation['source_before'][name] == observation['source_after'][name]
    print(json.dumps({'packet': label, 'raw_reconciled': True,
                      'main_wal_gold_bytes_unchanged_during_copy': True,
                      'shm_unchanged': observation['source_before']['database.sqlite-shm'] ==
                                       observation['source_after']['database.sqlite-shm'],
                      'scratch_removed': observation['scratch_removed']}, sort_keys=True))

baseline_tests = (PACKET / 'baseline-corrected-tests.stdout.txt').read_text()
assert '6 failed, 3 passed' in baseline_tests
assert '9 passed' in (PACKET / 'fixed-tests.stdout.txt').read_text()
print('Baseline failures and fixed passes independently reconciled; no production dataset certified.')
