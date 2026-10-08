from pathlib import Path
import sqlite3

def calculate_ex(predicted_res, ground_truth_res):
    res=0
    if set(predicted_res)==set(ground_truth_res): res=1
    return res

def test_official_ex_transcription():
    assert calculate_ex([(1,)],[(1,)])==1
    assert calculate_ex([(1,)],[(2,)])==0

def test_release_has_500_questions():
    import json
    p=Path('/mnt/20t/xubuqiang/datasets/bird_minidev/_src/unpacked/minidev/MINIDEV/mini_dev_sqlite.json')
    assert len(json.load(open(p)))==500
