from data import bfcl_v3

def test_import_does_not_load_mixed_pool(monkeypatch):
    monkeypatch.setattr(bfcl_v3,'_read_jsonl',lambda path: (_ for _ in ()).throw(AssertionError('mixed pool read')))
    assert bfcl_v3._RECORDS == []

def test_selected_loader_rejects_unknown_without_reads(monkeypatch):
    monkeypatch.setattr(bfcl_v3,'_read_jsonl',lambda path: (_ for _ in ()).throw(AssertionError('payload read')))
    try:
        bfcl_v3.load_selected(['unknown/0'])
    except ValueError:
        pass
    else:
        raise AssertionError('unknown selected ID accepted')

def test_irrelevance_gold_has_no_functions():
    assert bfcl_v3.score('', {'subset':'irrelevance','functions':[]})['official']['expected_functions'] == '<redacted>'
