"""Adjacent snapshot and pristine teardown controls; fake Docker, no benchmark."""
from contextlib import contextmanager
import subprocess

import pytest

from eval.containers import container
from eval.verification import verifier
from test_snapshot_binding_w_snapfix import daemon, route
from test_scorer_isolation_option_b import actor, scorer, docker_double


@pytest.mark.parametrize('exit_shape', ['timeout', 'missing-argv', 'staging-error'])
def test_snapshot_post_create_exit_reaps_before_idle_unmount(tmp_path, monkeypatch, daemon, exit_shape):
    events = []

    @contextmanager
    def startup():
        try:
            yield '/trusted-idle', ()
        finally:
            events.append('idle-unmount')

    monkeypatch.setattr(container, 'snapshot_startup', startup)
    remove = container.remove_container

    def reap(name):
        remove(name)
        events.append('container-removed')

    monkeypatch.setattr(container, 'remove_container', reap)

    def fail(*args, **kwargs):
        if exit_shape == 'timeout':
            raise subprocess.TimeoutExpired(['authored-check'], 5)
        raise OSError('authored staging failure')

    if exit_shape == 'timeout':
        monkeypatch.setattr(container, 'exec_in', fail)
    elif exit_shape == 'staging-error':
        monkeypatch.setattr(verifier, '_copy_verifier_inputs', fail)
    kwargs = {'reward_file': '/verifier/reward.txt'}
    if exit_shape == 'missing-argv':
        kwargs['argv'] = []
    if exit_shape == 'staging-error':
        with pytest.raises(OSError, match='staging failure'):
            route(tmp_path, **kwargs)
    else:
        verdict = route(tmp_path, **kwargs)
        assert not verdict['passed']
        if exit_shape == 'timeout':
            assert verdict['outcome'] == 'timeout' and verdict['unmeasured']
    assert events == ['container-removed', 'idle-unmount']
    assert len(daemon['removed']) == 1


@pytest.mark.parametrize('stage', ['create', 'start'])
def test_pristine_timeout_still_attempts_named_removal(tmp_path, monkeypatch, scorer, docker_double, stage):
    transport = container.docker

    def timeout(*args, **kwargs):
        if args[0] == stage:
            # Model allocation succeeding at the daemon before acknowledgement fails.
            if stage == 'create':
                transport(*args, **kwargs)
            raise subprocess.TimeoutExpired(args, 5)
        return transport(*args, **kwargs)

    monkeypatch.setattr(container, 'docker', timeout)
    verdict = verifier._verify(actor(tmp_path), scorer, '', sandbox=False, timeout_s=5,
        task_id='t', run_id='binding-control', trial_id='round-0.harness-.trial-1')
    assert verdict['outcome'] == 'timeout' and verdict['score'] is None
    assert verdict['unmeasured']
    creates = [a for a in docker_double.calls if a[0] == 'create']
    assert len(creates) == 1
    name = creates[0][creates[0].index('--name') + 1]
    assert docker_double.calls[-1] == ('rm', '--force', name)
    assert verdict['scorer_isolation_evidence']['cleanup']['removed'] is True
