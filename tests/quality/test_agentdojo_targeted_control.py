"""Targeted controls must work with the mixed/heldout prompt catalog absent."""
from __future__ import annotations
import json
from types import SimpleNamespace
import pytest
from data.datasets import agentdojo
from data.scaffolds import command_control

def test_explicit_control_uses_only_its_prepared_case(tmp_path, monkeypatch):
    case = tmp_path / 'prepared/7/case.json'; case.parent.mkdir(parents=True)
    case.write_text(json.dumps({'suite':'banking','user':'user_task_0','injection':'injection_task_0','prompt':'synthetic'}))
    monkeypatch.setattr(agentdojo,'DATASET_ROOT',tmp_path)
    monkeypatch.setattr(agentdojo,'records',lambda: pytest.fail('mixed catalog read'))
    task=command_control.pick(agentdojo,'agentdojo/7'); assert task['task_id']=='agentdojo/7'; assert task['goal'].startswith('synthetic\n')
    for name in ('ENV','SETUP','VERIFY'): assert len(getattr(agentdojo,name))==agentdojo.TASK_COUNT

def test_control_requires_explicit_id_before_any_catalog_read(monkeypatch):
    monkeypatch.setattr(agentdojo,'records',lambda: pytest.fail('mixed catalog read'))
    with pytest.raises(SystemExit,match='require --task-id'): command_control.pick(agentdojo,None)

@pytest.mark.parametrize('task_id',['agentdojo/949','agentdojo/-1','agentdojo/007','other/7','agentdojo/../7'])
def test_invalid_control_id_is_rejected_before_any_read(task_id,monkeypatch):
    monkeypatch.setattr(agentdojo.Path,'read_text',lambda *a,**k: pytest.fail('case read'))
    with pytest.raises(SystemExit,match='unknown task id'): command_control.pick(agentdojo,task_id)

def test_user_group_rule_keeps_variants_together(monkeypatch):
    rows=[{'suite':suite,'user':user,'injection':str(v)} for suite in ('banking','slack') for user in ('user_task_0','user_task_1','user_task_2') for v in range(4)]
    monkeypatch.setattr(agentdojo,'records',lambda: rows); split=agentdojo.SPLIT
    assert set(split['train']).isdisjoint(split['eval']); assert set(split['train']+split['eval'])=={f'agentdojo/{i}' for i in range(len(rows))}
    groups={}
    for side,ids in split.items():
        for tid in ids: groups.setdefault((rows[int(tid.split('/')[-1])]['suite'],rows[int(tid.split('/')[-1])]['user']),set()).add(side)
    assert all(len(sides)==1 for sides in groups.values())

def test_other_adapters_keep_existing_explicit_selection():
    module=SimpleNamespace(load=lambda:([{'task_id':'fixture/0'}],{})); assert command_control.pick(module,'fixture/0')=={'task_id':'fixture/0'}
