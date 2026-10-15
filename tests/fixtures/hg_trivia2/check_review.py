"""Check evidence citations, pinned source identities and proposal shape; no scorer import."""
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[2]


if __name__ == '__main__':
    text = (REPO / 'registry/w-trivia2-review.md').read_text()
    refs = re.findall(r'(?:F/|(?:tests|registry|data)/)[A-Za-z0-9_./-]+:[0-9]+', text)
    for ref in refs:
        path, line = ref.rsplit(':', 1)
        if path.startswith('F/'):
            path = 'tests/fixtures/hg_trivia2/' + path[2:]
        assert 0 < int(line) <= len((REPO / path).read_text().splitlines()), ref
    assert '@CAT:' not in text
    for source in json.loads((ROOT / 'source-identities.json').read_text()):
        body = (REPO / source['path']).read_bytes()
        assert len(body) == source['bytes']
        assert hashlib.sha256(body).hexdigest() == source['sha256']
    pin = json.loads((REPO / 'tests/fixtures/triviaqa_upstream/provenance.json').read_text())
    for source in ['evaluation/triviaqa_evaluation.py', 'utils/dataset_utils.py']:
        body = (REPO / 'tests/fixtures/triviaqa_upstream' / source).read_bytes()
        assert hashlib.sha256(body).hexdigest() == pin['files'][source]['sha256']
    converter = (ROOT / 'decoded/project-converter.py').read_bytes()
    response = json.loads((ROOT / 'responses/project-converter-blob-direct.body').read_text())
    assert hashlib.sha1(b'blob ' + str(len(converter)).encode() + b'\0' + converter).hexdigest() == response['sha']
    proposal = json.loads((REPO / 'registry/proposals/w-trivia2.json').read_text())
    assert set(proposal) == {'worker', 'dataset', 'blocker', 'membership_findings',
                            'scorer_key_mapping', 'denominator', 'execution_receipt_outcome',
                            'standing_limit_argument', 'observed_append',
                            'next_action_replacement', 'withdrawal_entry'}
    assert proposal['execution_receipt_outcome'] == 'unknown'
    assert proposal['withdrawal_entry'] is None
    assert 'tests/fixtures/hg_wsel/triviaqa.json' in proposal['next_action_replacement']
    files = [p for p in ROOT.rglob('*') if p.is_file()]
    assert all(p.stat().st_size < 1_000_000 for p in files)
    print(json.dumps({'review_file_line_citations_checked': len(refs),
                      'observed_source_identities_verified': 5,
                      'original_scorer_and_helper_pin_match': True,
                      'decoded_converter_git_blob_match': True,
                      'proposal_keys_valid': True, 'withdrawal_entry': None,
                      'fixture_files_under_1MB': True}, sort_keys=True))
