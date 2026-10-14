"""Snapshot actor/verifier network parity without Docker, models or benchmark data."""
from __future__ import annotations

import json
import subprocess

import pytest

from eval.containers import container, container_state


@pytest.mark.parametrize("declared_network", ["bridge", "none", None])
def test_snapshot_verifier_honours_declared_network(tmp_path, monkeypatch, declared_network):
    repo = tmp_path / "harness"
    repo.mkdir()
    (repo / "harness.json").write_text(json.dumps({"entrypoint": "agent.py"}))
    events = []
    networks = {}
    internal = "synthetic-model-network"

    def denied(*args, **kwargs):
        pytest.fail("unit control must never reach Docker")

    monkeypatch.setattr(container, "docker", denied)
    monkeypatch.setattr(container_state.services_mod, "create_network", lambda *a: internal)
    monkeypatch.setattr(container_state.services_mod, "remove_network",
                        lambda name: events.append(("remove_network", name)))
    monkeypatch.setattr(container, "image_python", lambda *a: "/synthetic/python")
    monkeypatch.setattr(container, "container_env", lambda *a, **kw: {})
    monkeypatch.setattr(container_state.harness_runtime, "lookup", lambda *a, **kw: None)
    monkeypatch.setattr(container_state.harness_runtime, "record", lambda *a, **kw: {})

    def create(name, **kwargs):
        networks[name] = {kwargs["network"]}
        events.append(("create", name))

    def connect(name, network):
        networks[name].add(network)
        events.append(("connect", name))

    monkeypatch.setattr(container, "create", create)
    monkeypatch.setattr(container, "network_connect", connect)
    for operation in ("start", "stop", "mkdir_in", "cp_in", "remove_container", "remove_image"):
        monkeypatch.setattr(container, operation,
                            lambda name, *a, _op=operation, **kw: events.append((_op, name)))
    monkeypatch.setattr(container, "exec_in",
                        lambda *a, **kw: subprocess.CompletedProcess([], 0, "", ""))
    monkeypatch.setattr(container, "commit", lambda *a: "synthetic-snapshot")
    monkeypatch.setattr(container, "cp_out", lambda *a, **kw: False)

    env = {"image": "synthetic-image", "state": "container"}
    if declared_network is not None:
        env["network"] = declared_network
    result = container_state._run_one_container_state(
        repo, {"task_id": "t", "goal": "Synthetic network control"}, env_spec=env,
        setup=None, verifier={"kind": "command", "argv": ["synthetic-check"],
                              "scorer_bundle": {"isolation_class": "snapshot-service"}},
        timeout_s=1, verify_timeout_s=1, run_id="synthetic-w-net", run_seed="s",
        recordings_root=None)

    actor, verifier = "hg-synthetic-w-net-t", "hg-verify-synthetic-w-net-t"
    expected = {internal, "bridge"} if declared_network == "bridge" else {internal}
    assert networks == {actor: expected, verifier: expected}
    for name in (actor, verifier):
        assert ("create", name) in events and ("remove_container", name) in events
        if declared_network == "bridge":
            assert events.index(("create", name)) < events.index(("connect", name))
            assert events.index(("connect", name)) < events.index(("start", name))
        else:
            assert ("connect", name) not in events
    assert result["verdict"]["passed"]
    assert result["verdict"]["scorer_isolation_class"] == "snapshot-service"
    assert events[-1] == ("remove_network", internal)
