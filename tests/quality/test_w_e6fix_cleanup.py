"""Offline daemon-state controls for mounted run timeout/early-exit cleanup.

The fake transport models Docker keeping a container after its client exits.
No scorer, endpoint, image pull or live Docker call is made by these tests.
"""
import json
from pathlib import Path
import subprocess

import pytest

from eval.containers import container
from eval.service import services
from eval.verification import verifier

ROOT = Path(__file__).resolve().parents[2]
PIN = json.loads((ROOT / 'reports/w-e6-evidence/preflight/bindings.json').read_text())['appworld-verifier_image']['image']


class Daemon:
    def __init__(self, failure=None, code=0):
        self.failure = failure
        self.code = code
        self.live = {}
        self.launches = []
        self.removed = []

    def run(self, cmd, **kwargs):
        self.launches.append((cmd, kwargs))
        # Model a daemon allocation BEFORE the client's timeout/early exit.
        name = cmd[cmd.index('--name') + 1] if '--name' in cmd else 'unnamed-test-container'
        self.live[name] = [cmd[i + 1] for i, a in enumerate(cmd) if a == '--mount']
        if self.failure:
            raise self.failure
        self.live.pop(name)  # Docker --rm on normal/nonzero container exit.
        return subprocess.CompletedProcess(cmd, self.code, 'preserved stdout', 'preserved stderr')

    def docker(self, *argv, **kwargs):
        if argv[:2] == ('rm', '--force'):
            self.removed.append(argv[2])
            self.live.pop(argv[2], None)
            return subprocess.CompletedProcess(argv, 0, '', '')
        if argv[:2] == ('network', 'rm'):
            return subprocess.CompletedProcess(argv, int(bool(self.live)), '',
                                               'has active endpoints' if self.live else '')
        if argv[0] == 'logs':
            return subprocess.CompletedProcess(argv, 0, '', '')
        raise AssertionError(argv)


@pytest.mark.parametrize('exit_shape', ['normal', 'nonzero', 'timeout', 'interrupt', 'launch-error'])
def test_mounted_run_reaps_exact_container_and_preserves_result(tmp_path, monkeypatch, exit_shape):
    failure = {'timeout': subprocess.TimeoutExpired(['docker', 'run'], 2),
               'interrupt': KeyboardInterrupt(), 'launch-error': OSError('client lost')} .get(exit_shape)
    daemon = Daemon(failure, code=7 if exit_shape == 'nonzero' else 0)
    monkeypatch.setattr(container.subprocess, 'run', daemon.run)
    monkeypatch.setattr(container, 'docker', daemon.docker)
    kwargs = dict(image=PIN, task_dir=tmp_path, task_mount='/app', timeout_s=2,
                  network='owned-test-network', task_dir_writable=False,
                  extra_mounts=('--mount', f'type=bind,src={tmp_path},dst=/recordings/recording,readonly'))
    if failure:
        with pytest.raises(type(failure)) as caught:
            container.run(['authored-command'], **kwargs)
        assert caught.value is failure
    else:
        result = container.run(['authored-command'], **kwargs)
        assert (result.returncode, result.stdout, result.stderr) == (
            daemon.code, 'preserved stdout', 'preserved stderr')
    assert daemon.removed, 'client exit must remove its daemon-side container'
    cmd, launch_kwargs = daemon.launches[0]
    assert daemon.removed == [cmd[cmd.index('--name') + 1]]
    assert not daemon.live, 'no recording binds or network endpoints may remain'
    assert launch_kwargs['timeout'] == 2
    assert '--rm' in cmd and '--read-only' in cmd
    assert cmd[cmd.index('--network') + 1] == 'owned-test-network'
    assert cmd[cmd.index('--pids-limit') + 1] == '1024'
    assert cmd[cmd.index('--memory') + 1] == '4g'
    assert cmd[cmd.index('--cpus') + 1] == '2'
    assert f'type=bind,src={tmp_path},dst=/app,readonly' in cmd
    assert kwargs['extra_mounts'][1] in cmd


def test_verifier_timeout_releases_mount_before_service_network_stop(tmp_path, monkeypatch):
    daemon = Daemon(subprocess.TimeoutExpired(['docker', 'run'], 2))
    monkeypatch.setattr(container.subprocess, 'run', daemon.run)
    monkeypatch.setattr(container, 'docker', daemon.docker)
    work = tmp_path / 'task'
    work.mkdir()
    record = tmp_path / 'recordings'
    record.mkdir()
    svc = [{'name': 'recording', 'record': True}]
    running = services.RunningServices(network='owned-test-network',
        containers={'recording': 'owned-test-service'}, recordings={'recording': record}, services=svc)
    daemon.live['owned-test-service'] = ['RW recording bind']
    verdict = verifier._verify(work, {
        'kind': 'command', 'argv': ['authored-check'], 'image': PIN,
        'reward_file': '/verifier/reward.txt',
        'scorer_bundle': {'isolation_class': 'snapshot-service'}}, '',
        sandbox=True, timeout_s=2, env={'kind': 'exec', 'image': PIN, 'workdir': '/app'},
        service_specs=svc, running=running)
    assert verdict['outcome'] == 'timeout' and verdict['unmeasured']
    assert 'score' not in verdict and not verdict['passed']
    assert not list(tmp_path.glob('hg-verdict-*'))
    problems = running.stop()
    assert problems == [], 'verifier endpoint must not block service network cleanup'
    assert not daemon.live


def test_runs_have_independent_cleanup_names(tmp_path, monkeypatch):
    daemon = Daemon()
    monkeypatch.setattr(container.subprocess, 'run', daemon.run)
    monkeypatch.setattr(container, 'docker', daemon.docker)
    for _ in range(2):
        container.run(['authored-command'], image=PIN, task_dir=tmp_path, task_mount='/app')
    assert len(daemon.removed) == 2
    assert len(set(daemon.removed)) == 2


def test_unpinned_refusal_still_precedes_launch_and_cleanup(tmp_path, monkeypatch):
    daemon = Daemon()
    monkeypatch.setattr(container.subprocess, 'run', daemon.run)
    monkeypatch.setattr(container, 'docker', daemon.docker)
    with pytest.raises(container.ContainerUnavailable, match='not pinned'):
        container.run(['true'], image='unpinned-test-tag', task_dir=tmp_path, task_mount='/app')
    assert not daemon.launches and not daemon.removed
