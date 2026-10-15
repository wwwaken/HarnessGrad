"""Synthetic tau controls. No released task is executed; no Docker/model is used.

Run directly with --before-check to print original/fixed observations using the
complete checkers, fake tools and a local service-owned recording.
"""
from __future__ import annotations

from contextlib import contextmanager, redirect_stdout
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
from types import SimpleNamespace
from unittest.mock import patch
import urllib.error
import urllib.request

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
ASSETS = ROOT / "data/datasets/tau_bench"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


service = load_module("tau_recording_service", ASSETS / "service.py")
checker = load_module("tau_recording_checker", ASSETS / "verify/check.py")


class SetBalance:
    @staticmethod
    def invoke(db, balance):
        db["balance"] = balance
        return "updated"

    @staticmethod
    def get_info():
        return {"function": {"name": "set_balance"}}


class Transfer:
    @staticmethod
    def invoke(db):
        return "Transferred"

    @staticmethod
    def get_info():
        return {"function": {"name": "transfer_to_human_agents"}}


TOOLS = {"set_balance": SetBalance, "transfer_to_human_agents": Transfer}
SAY = {"kind": "say", "name": "respond", "arguments": {"content": "confirmed"}}
DONE = {"kind": "done", "name": "done", "arguments": {}}
TRANSFER = {"kind": "call", "name": "transfer_to_human_agents", "arguments": {}}
MUTATE = {"kind": "call", "name": "set_balance", "arguments": {"balance": 7}}


def episode_at(root):
    return service.Episode("retail_synthetic", "retail", {"balance": 0},
                           TOOLS, "Synthetic policy", root / "service/episode.json")


def grade(module, root, episode, *, actions=(), outputs=("confirmed",), local_events=()):
    root.mkdir(parents=True, exist_ok=True)
    gt = {"task_id": "retail_synthetic", "domain": "retail", "user_id": "synthetic",
          "actions": list(actions), "outputs": list(outputs)}
    (root / "gt.json").write_text(json.dumps(gt))
    (root / "clean.json").write_text('{"balance": 0}')
    # Both local artifacts are attacker-controlled and unrelated to service state.
    (root / "db.json").write_text('{"balance": 0}')
    (root / "tau_calls.jsonl").write_text(
        "".join(json.dumps(event) + "\n" for event in local_events))
    argv = ["--gt", str(root / "gt.json"), "--clean-db", str(root / "clean.json"),
            "--lib", str(ASSETS / "lib"), "--reward", str(root / "reward.txt"),
            "--evidence", str(root / "evidence.json")]
    if "recording" in module.DEFAULTS:
        argv += ["--recording", str(episode.recording)]
    else:
        argv += ["--db", str(root / "db.json"), "--call-log", str(root / "tau_calls.jsonl")]
    stream = io.StringIO()
    with patch.object(module, "import_tools", return_value=TOOLS), redirect_stdout(stream):
        sys.path.insert(0, str(ASSETS / "lib"))
        code = module.main(argv)
    reward = (root / "reward.txt").read_text().strip() if (root / "reward.txt").exists() else None
    return code, reward, json.loads((root / "evidence.json").read_text()), stream.getvalue().strip()


def test_fabricated_local_say_and_done_cannot_supply_grading_evidence(tmp_path):
    episode = episode_at(tmp_path)
    episode.act({"command": "done"})  # real service never said the required output
    code, reward, evidence, _ = grade(checker, tmp_path / "check", episode,
                                      local_events=(SAY, DONE))
    assert code == 0 and reward == "0"
    assert evidence["database_hash_matched"] is True
    assert evidence["r_outputs"] == 0 and evidence["agent_says"] == []
    assert evidence["evidence_source"] == "service-recording"


def test_terminating_tool_is_done(tmp_path):
    episode = episode_at(tmp_path)
    episode.act({"command": "say", "content": "confirmed"})
    episode.act({"command": "call", "name": "transfer_to_human_agents", "arguments": {}})
    _, reward, evidence, _ = grade(checker, tmp_path / "check", episode)
    assert reward == "1" and evidence["agent_declared_done"] is True
    assert episode.done is True


@pytest.mark.parametrize("terminator", [DONE, TRANSFER])
def test_recorded_events_after_first_termination_never_count(tmp_path, terminator):
    episode = episode_at(tmp_path)
    # Deliberately author a recording a broken/legacy service could produce.
    episode.events = [copy.deepcopy(terminator), copy.deepcopy(SAY), copy.deepcopy(MUTATE)]
    episode.done = True
    episode.persist()
    _, reward, evidence, _ = grade(checker, tmp_path / "check", episode)
    assert reward == "0" and evidence["agent_says"] == []
    assert evidence["agent_events"] == 1
    assert "set_balance" not in evidence["agent_tool_call_counts"]


@pytest.mark.parametrize("terminator", ["done", "transfer_to_human_agents"])
def test_service_freezes_database_and_recording_at_termination(tmp_path, terminator):
    episode = episode_at(tmp_path)
    if terminator == "done":
        episode.act({"command": "done"})
    else:
        episode.act({"command": "call", "name": terminator, "arguments": {}})
    before = episode.recording.read_bytes()
    for request in ({"command": "say", "content": "confirmed"},
                    {"command": "call", "name": "set_balance", "arguments": {"balance": 7}},
                    {"command": "done"}):
        with pytest.raises(ValueError, match="already done"):
            episode.act(request)
    assert episode.recording.read_bytes() == before
    assert episode.database == {"balance": 0}


def test_database_hash_rule_still_distinguishes_success_and_wrong_state(tmp_path):
    action = {"name": "set_balance", "arguments": {"balance": 7}}
    for changed, expected in ((False, "0"), (True, "1")):
        root = tmp_path / str(changed)
        episode = episode_at(root)
        if changed:
            episode.act({"command": "call", **action})
        episode.act({"command": "say", "content": "Confirmed"})
        episode.act({"command": "done"})
        _, reward, evidence, _ = grade(checker, root / "check", episode, actions=[action])
        assert reward == expected
        assert evidence["database_hash_matched"] is changed
        assert evidence["ground_truth_changes_database"] is True
        assert evidence["replayed_actions"] == 1


def test_unfinished_valid_recording_is_a_measured_zero(tmp_path):
    episode = episode_at(tmp_path)
    episode.act({"command": "say", "content": "confirmed"})
    _, reward, evidence, _ = grade(checker, tmp_path / "check", episode)
    assert reward == "0" and evidence["agent_declared_done"] is False


@pytest.mark.parametrize("fault", ["missing", "json", "task", "domain", "schema", "event", "done"])
def test_unusable_service_recording_is_unmeasured(tmp_path, fault):
    episode = episode_at(tmp_path)
    if fault == "missing":
        episode.recording.unlink()
    elif fault == "json":
        episode.recording.write_text('{')
    else:
        record = json.loads(episode.recording.read_text())
        record.update({"task": {"task_id": "another"}, "domain": {"domain": "airline"},
                       "schema": {"database": []}, "event": {"events": [None]},
                       "done": {"done": True}}[fault])
        episode.recording.write_text(json.dumps(record))
    code, reward, evidence, _ = grade(checker, tmp_path / "check", episode,
                                      local_events=(SAY, DONE))
    assert code == 3 and reward is None
    assert "recording unavailable or invalid" in evidence["error"]


@contextmanager
def local_http(episode):
    server = service.HTTPServer(("127.0.0.1", 0), service.handler_for(episode))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


def test_shipped_cli_and_http_service_record_only_accepted_actions(tmp_path, monkeypatch, capsys):
    episode = episode_at(tmp_path)
    cli = load_module("tau_recording_client", ASSETS / "image/tau_cli.py")
    with local_http(episode) as base:
        monkeypatch.setenv("HG_SVC_TAU_URL", base)
        initial = episode.recording.read_bytes()
        with urllib.request.urlopen(base + "/health") as response:
            assert json.load(response)["status"] == "ok"
        assert episode.recording.read_bytes() == initial
        for command in (["list"], ["policy"], ["show"]):
            assert cli.main(command) == 0
        assert episode.events == []
        assert cli.main(["call", "set_balance", '{"balance":7}']) == 0
        assert cli.main(["say", "confirmed"]) == 0
        assert cli.main(["done"]) == 0
        frozen = episode.recording.read_bytes()
        assert cli.main(["say", "too late"]) == 2
        assert cli.main(["call", "set_balance", '{"balance":0}']) == 2
        for endpoint in ("/initialize", "/reset", "/recording"):
            with pytest.raises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(base + endpoint, data=b'{}')
            assert error.value.code == 404
        assert episode.recording.read_bytes() == frozen
        assert episode.database == {"balance": 7}
    assert "already done" in capsys.readouterr().err


def test_adapter_declares_recording_boundary_and_stages_matching_client(tmp_path):
    adapter = load_module("tau_recording_adapter", ROOT / "data/datasets/tau_bench.py")
    from data.scaffolds import registry
    from eval.service.services import mounts_for
    registry._check_env(adapter.DEFAULT_ENV, "retail_synthetic", "tau_bench")
    normalized = registry._normalize_env(adapter.DEFAULT_ENV)
    svc = normalized["services"][0]
    assert normalized["state"] == "mount"
    assert svc["record"] is True and svc["needs_model"] is False
    assert svc["command"] == ["python3", "-c", (ASSETS / "service.py").read_text()]
    assert mounts_for("harness", [svc], {"tau": Path('/synthetic-recording')}) == []
    assert mounts_for("verifier", [svc], {"tau": Path('/synthetic-recording')})[-1].endswith(
        'dst=/recordings/tau,readonly')
    assert checker.DEFAULTS["recording"] == Path('/recordings/tau/episode.json')
    setup = adapter._setup({})
    assert setup == {"files": [{"path": "tau", "from": str(ASSETS / "image/tau_cli.py")}]}
    from eval.observe.tracing import _materialize
    _materialize(tmp_path, setup["files"], ROOT)
    assert (tmp_path / "tau").read_bytes() == (ASSETS / "image/tau_cli.py").read_bytes()
    assert (tmp_path / "tau").stat().st_mode & 0o111
    assert adapter._verifier({"task_id": "retail_synthetic", "domain": "retail"})["argv"][-2:] == [
        "--recording", "/recordings/tau/episode.json"]


def test_service_bootstrap_binds_domain_and_paths_without_client_input(monkeypatch):
    monkeypatch.setenv("HG_ENV_TASK_ID", "airline_999")
    reads, created = [], []
    def read(path):
        reads.append(str(path))
        return '{"balance":0}' if str(path).endswith('.json') else 'Synthetic policy'
    def fake_episode(*args):
        created.append(args)
        return object()
    with patch.object(service.Path, "read_text", read), \
         patch.object(service, "Episode", side_effect=fake_episode), \
         patch.object(service.importlib, "import_module", return_value=SimpleNamespace(
             ALL_TOOLS=list(TOOLS.values()))) as imports, \
         patch.object(service, "HTTPServer") as server, \
         patch.object(sys, "path", list(sys.path)):
        service.main()
    imports.assert_called_once_with("tau_bench.envs.airline.tools")
    assert reads == ["/opt/tau/pristine/airline.json", "/opt/tau/policy/airline.txt"]
    assert created[0][:2] == ("airline_999", "airline")
    assert created[0][-1] == "/recordings/tau/episode.json"
    assert server.call_args[0][0] == ("0.0.0.0", 8080)
    server.return_value.serve_forever.assert_called_once()


def observations(before_path):
    before = load_module("tau_before", before_path)
    with tempfile.TemporaryDirectory(prefix="taubench-observations-", dir="/tmp") as scratch:
        root = Path(scratch)
        cases = (("forged-local-log", (DONE,), (SAY, DONE)),
                 ("terminate-tool", (SAY, TRANSFER), (SAY, TRANSFER)),
                 ("post-done", (DONE, SAY, MUTATE), (DONE, SAY, MUTATE)))
        for label, service_events, local_events in cases:
            episode = episode_at(root / label)
            episode.events = list(copy.deepcopy(service_events))
            episode.done = True
            episode.persist()
            for phase, module in (("pre-fix", before), ("post-fix", checker)):
                code, reward, ev, stdout = grade(module, root / label / phase, episode,
                                                  local_events=local_events)
                print(json.dumps({"control": label, "phase": phase, "exit": code,
                                  "reward": reward, "database_hash_matched": ev["database_hash_matched"],
                                  "done": ev["agent_declared_done"], "says": ev["agent_says"],
                                  "events": ev["agent_events"], "stdout": stdout}, sort_keys=True))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--before-check", type=Path, required=True)
    observations(parser.parse_args().before_check)
