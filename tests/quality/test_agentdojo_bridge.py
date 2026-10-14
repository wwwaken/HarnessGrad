"""Trusted AgentDojo replay preflight; not evidence of a published adapter yet.

Pinned runtime lives outside git. Agent-visible tools still need a stripped package;
these tests only establish official gold/noop utility and trusted replay semantics.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DATA = Path('/mnt/20t/xubuqiang/datasets/agentdojo')
PYTHON = DATA / 'runtime/bin/python'
BRIDGE = ROOT / 'data/datasets/agentdojo/bridge.py'


def run_bridge(mode, case_file=None, action_file=None):
    if not PYTHON.is_file():
        pytest.skip('isolated AgentDojo runtime not provisioned')
    argv = [str(PYTHON), str(BRIDGE), mode]
    if case_file is not None:
        argv += ['--case', str(case_file)]
    if action_file is not None:
        argv += ['--action', str(action_file)]
    proc = subprocess.run(argv, capture_output=True, text=True, timeout=90)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.loads(proc.stdout)


def test_version_and_pair_count():
    cases = run_bridge('metadata')
    assert len(cases) == 949
    assert {c['suite'] for c in cases} == {'workspace', 'travel', 'banking', 'slack'}
    assert len({(c['suite'], c['user']) for c in cases}) == 97
    assert all(set(c) == {'suite', 'user', 'injection', 'prompt'} for c in cases)


def test_tool_only_cli_replays_gold_with_real_observations(tmp_path):
    import shutil
    case = json.loads((DATA / '_src/cases.json').read_text())[0]
    initial = DATA / 'prepared/0/initial.json'
    shutil.copy2(initial, tmp_path / 'dojo.initial.json')
    case_path = tmp_path / 'case.json'
    case_path.write_text(json.dumps(case))
    oracle = run_bridge('oracle', case_path)
    cli = ROOT / 'data/datasets/agentdojo/cli/dojo'
    python = DATA / 'agent_runtime/bin/python'
    tools = subprocess.run([str(python), str(cli), 'tools'], cwd=tmp_path,
                           capture_output=True, text=True, timeout=30)
    assert tools.returncode == 0, tools.stderr
    assert json.loads(tools.stdout)
    for call in oracle['calls']:
        proc = subprocess.run([str(python), str(cli), 'call', json.dumps(call)], cwd=tmp_path,
                              capture_output=True, text=True, timeout=30)
        assert proc.returncode == 0, proc.stderr
        assert json.loads(proc.stdout)['error'] is None
    proc = subprocess.run([str(python), str(cli), 'submit', oracle['output']], cwd=tmp_path,
                          capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stderr
    result = run_bridge('evaluate', case_path, tmp_path / 'action.json')
    assert result['utility'] is True
    assert result['attack_success'] is False


def test_gold_noop_and_forged_state(tmp_path):
    cases = run_bridge('metadata')
    case = tmp_path / 'case.json'
    case.write_text(json.dumps(cases[0]))
    gold = run_bridge('oracle', case)
    action = tmp_path / 'action.json'
    action.write_text(json.dumps(gold))
    result = run_bridge('evaluate', case, action)
    assert result['suite_version'] == 'v1.2.2'
    assert result['utility'] is True
    assert result['attack_success'] is False
    assert result['reward'] == 1.0
    noop = run_bridge('evaluate', case)
    assert noop['utility'] is False
    assert noop['attack_success'] is False
    assert noop['reward'] == 0.0
    action.write_text(json.dumps({'calls': [], 'output': '', 'utility': True,
                                'environment': gold, 'tool_results': gold}))
    forged = run_bridge('evaluate', case, action)
    assert forged['utility'] is False
    assert forged['reward'] == 0.0
