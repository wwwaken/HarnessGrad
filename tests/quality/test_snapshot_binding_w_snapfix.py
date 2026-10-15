"""Snapshot-service boundary regressions; pins rehashed from retained real metadata.

The small daemon double models the independently reproduced startup write. A separate
bounded real-Docker capture in reports/w-snapfix-evidence checks the actual mechanism.
"""
import hashlib
import inspect
import json
from pathlib import Path
import subprocess

import pytest

from eval.containers import container
from eval.verification import verifier

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / 'tests/fixtures/hg_wsnap'


def image_pin(label):
    folder = PACKET / 'image-metadata' / label
    recorded = json.loads((folder / 'recomputed.json').read_text())['image_id']
    pin = 'sha256:' + hashlib.sha256(
        (folder / 'blobs/sha256' / recorded.split(':')[1]).read_bytes()).hexdigest()
    assert pin == recorded
    return pin


SNAPSHOT = image_pin('snapshot') if PACKET.is_dir() else None
FOREIGN = image_pin('base') if PACKET.is_dir() else None


def route(tmp_path, snapshot=SNAPSHOT, expected=SNAPSHOT, **kwargs):
    # Lets the *same behavioral tests* reach the pre-fix boundary, whose defect is
    # precisely the absence of a separate expected-identity parameter.
    binding = ({'expected_snapshot': expected}
               if 'expected_snapshot' in inspect.signature(verifier._verify_container_state).parameters
               else {})
    return verifier._verify_container_state(
        snapshot, {'kind': 'command', 'argv': ['observe-committed-file'], **kwargs},
        task_mount='/app', staging=tmp_path, timeout_s=5, run_id='unit-w-snapfix',
        task_id='binding', network='service-network', declared_network='bridge', **binding)


@pytest.fixture
def daemon(monkeypatch):
    if not PACKET.is_dir():
        pytest.skip("tests/fixtures/hg_wsnap is internal (see .gitignore) and absent from this clone")
    state = dict(file='committed-before-start\n', calls=[], removed=[], command=None,
                 consumed=SNAPSHOT, startup_write=True, entrypoint_write=True, healthcheck_write=True)

    def docker(*args, **kwargs):
        state['calls'].append(args)
        if args[0] == 'create':
            state['command'] = args
        elif args[0] == 'inspect':
            return subprocess.CompletedProcess(args, 0, state['consumed'] + '\n', '')
        elif args[0] == 'start':
            cmd = state['command']
            if ((state['startup_write'] and '--entrypoint' not in cmd)
                    or (state['entrypoint_write'] and '--entrypoint' not in cmd)
                    or (state['healthcheck_write'] and '--no-healthcheck' not in cmd)):
                state['file'] = 'changed-during-start\n'
        elif args[0] == 'exec':
            # An actor-owned mkdir before the checker could also change the file.
            if args[2] == 'mkdir':
                state['file'] = 'changed-by-mkdir\n'
            return subprocess.CompletedProcess(args, 0, state['file'], '')
        elif args[0] == 'rm':
            state['removed'].append(args[-1])
        return subprocess.CompletedProcess(args, 0, '', '')

    monkeypatch.setattr(container, 'docker', docker)
    return state


def test_different_existing_snapshot_identity_is_refused(tmp_path, daemon):
    verdict = route(tmp_path, snapshot=FOREIGN)
    assert verdict.get('unmeasured') and verdict.get('score') is None
    assert 'identity' in verdict['unmeasured']
    assert daemon['command'] is None


def test_different_consumed_identity_is_refused_before_start(tmp_path, daemon):
    daemon['consumed'] = FOREIGN
    verdict = route(tmp_path)
    assert verdict.get('unmeasured') and verdict.get('score') is None
    assert not any(c[0] in ('start', 'exec') for c in daemon['calls'])
    assert daemon['removed']


def test_changed_file_startup_cannot_change_checker_input(tmp_path, daemon):
    verdict = route(tmp_path, pass_when='exit0_stdout', stdout='committed-before-start')
    assert verdict['passed'], verdict
    assert daemon['file'] == 'committed-before-start\n'
    cmd = daemon['command']
    assert '--entrypoint' in cmd and '--no-healthcheck' in cmd
    assert cmd[cmd.index('--network') + 1] == 'service-network'
    assert any(c[:2] == ('network', 'connect') and 'bridge' in c for c in daemon['calls'])


def test_reward_bind_does_not_execute_actor_mkdir_before_checker(tmp_path, daemon, monkeypatch):
    monkeypatch.setattr(container, 'cp_out', lambda *a: False)
    route(tmp_path, reward_file='/logs/verifier/reward.txt')
    cmd = daemon['command']
    assert any('dst=/logs/verifier' in a for a in cmd)
    assert not any(c[0] == 'exec' and c[2] == 'mkdir' for c in daemon['calls'])
    assert daemon['file'] == 'committed-before-start\n'


def test_missing_expected_identity_refuses_before_create(tmp_path, daemon):
    verdict = verifier._verify_container_state(
        SNAPSHOT, {'kind': 'command', 'argv': ['observe']}, task_mount='/app',
        staging=tmp_path, timeout_s=5, run_id='unit-w-snapfix', task_id='missing')
    assert verdict.get('unmeasured') and daemon['command'] is None


@pytest.mark.parametrize('snapshot,expected', [('moving:tag', SNAPSHOT), (SNAPSHOT, 'moving:tag')])
def test_pinned_syntax_is_still_required(tmp_path, daemon, snapshot, expected):
    verdict = route(tmp_path, snapshot=snapshot, expected=expected)
    assert verdict.get('unmeasured') and daemon['command'] is None


def test_matching_identity_keeps_network_limits_and_fresh_mounts(tmp_path, daemon):
    verdict = route(tmp_path)
    assert verdict['passed'] and verdict['scorer_isolation_class'] == 'snapshot-service'
    cmd = daemon['command']
    assert cmd[cmd.index('--memory') + 1] == '4g'
    assert cmd[cmd.index('--pids-limit') + 1] == '1024'
    assert '--read-only' not in cmd  # checker dependency installation still works
    assert daemon['removed']


def test_dynamic_startup_binary_is_refused(tmp_path):
    target = tmp_path / 'busybox'
    target.write_bytes(Path('/bin/true').read_bytes())
    with pytest.raises(container.SnapshotUnavailable, match='static'):
        container._require_static_elf(target)


def test_missing_static_busybox_fails_closed(tmp_path, monkeypatch, daemon):
    monkeypatch.setattr(container.shutil, 'which', lambda name: None)
    verdict = route(tmp_path)
    assert verdict.get('unmeasured') and daemon['command'] is None
