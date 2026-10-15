"""Completion-aware fabricated control: state, completion, recording and replay are separable.

The AppWorld protocol review (`registry/w-appworld-protocol-review.md`) found that the public prompt
pointed the actor at a harness-side final answer while the official checker replays recorded API calls
into a fresh world and evaluates *that*, and it recorded one absent control:

    ABSENT in enumerated synthetic protocol scope: a completion-aware recording/replay/scoring control.

This module is that control. It is **entirely fabricated**: an authored world with one state
requirement and one *separate* completion requirement, an authored HTTP service, and a replay of the
recorded calls into a fresh world. It reads no dataset row, no prompt, no gold answer and no released
task, it calls no official scorer, and it touches no GPU, model or endpoint. It cannot satisfy
`appworld / successful-task-evidence` - only a genuine successful measured actor task can - and it
authorizes nothing. What it can do is make four outcomes distinguishable instead of one number:

1. correct live state, no completion request      -> the actor/guidance boundary
2. completion in the live world but not in the recording -> the recording/verifier wiring
3. correct completion replayed, wrong state       -> a task-state failure
4. both requirements satisfied                    -> a complete fabricated control (NOT a benchmark win)

The observable set is the one the review asked for: printed state readback, the completion
request/response, the local harness submission, and the replayed completion state.
"""
from __future__ import annotations

import contextlib
import io
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import pytest

TASK_ID = "fabricated/control/0"
GOAL = "Set the documented value and then complete the task through the documented API."


def _fresh_world() -> dict:
    """A new world: one authored state slot and one authored completion flag."""
    return {"value": None, "completed": False, "completion_calls": 0}


def _apis(world: dict, log: list):
    """The fabricated service API surface, bound to one world and one call log."""

    def show_app_descriptions():
        return [{"name": "synthetic", "description": "Authored control"},
                {"name": "supervisor", "description": "Authored completion surface"}]

    def show_api_descriptions(app_name):
        assert app_name in ("synthetic", "supervisor"), app_name
        if app_name == "synthetic":
            return [{"name": "set_value"}]
        return [{"name": "complete_task"}]

    def show_api_doc(app_name, api_name):
        if app_name == "synthetic" and api_name == "set_value":
            return {"parameters": [{"name": "value", "type": "string"}]}
        assert app_name == "supervisor" and api_name == "complete_task", (app_name, api_name)
        return {"parameters": []}

    def set_value(value):
        log.append(("synthetic.set_value", {"value": value}))
        world["value"] = value
        return {"value": value}

    def complete_task():
        log.append(("supervisor.complete_task", {}))
        world["completed"] = True
        world["completion_calls"] += 1
        return {"completed": True}

    return SimpleNamespace(
        api_docs=SimpleNamespace(show_app_descriptions=show_app_descriptions,
                                 show_api_descriptions=show_api_descriptions,
                                 show_api_doc=show_api_doc),
        synthetic=SimpleNamespace(set_value=set_value),
        supervisor=SimpleNamespace(complete_task=complete_task))


class _Service:
    """Authored HTTP service: `/initialize` opens a fresh world, `/execute` runs one snippet."""

    def __init__(self):
        self.live_world = _fresh_world()
        self.live_log: list = []
        self.recorded: list[dict] = []
        self.readbacks: list[str] = []
        self.harness_submissions: list[str] = []

    def handler(self):
        service = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if self.path == "/initialize":
                    service.live_world = _fresh_world()
                    service.live_log = []
                    service.recorded = []
                    output = {"task_id": payload["task_id"], "goal": GOAL}
                elif self.path == "/execute":
                    code = payload["code"]
                    service.recorded.append({"url": "/execute", "code": code})
                    namespace = {"apis": _apis(service.live_world, service.live_log)}
                    buffer = io.StringIO()
                    with contextlib.redirect_stdout(buffer):
                        exec(code, namespace)
                    output = buffer.getvalue()
                    service.readbacks.append(output)
                elif self.path == "/harness_answer":
                    service.harness_submissions.append(payload["answer"])
                    output = {"accepted_locally": True}
                else:
                    self.send_response(404)
                    self.end_headers()
                    return
                body = json.dumps({"output": output}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        return Handler

    def replay(self, recorded=None) -> dict:
        """Replay recorded calls into a FRESH world and return that world plus its own log."""
        world, log = _fresh_world(), []
        for call in (self.recorded if recorded is None else recorded):
            namespace = {"apis": _apis(world, log)}
            with contextlib.redirect_stdout(io.StringIO()):
                exec(call["code"], namespace)
        return {"world": world, "log": list(log)}


@pytest.fixture
def service(monkeypatch):
    svc = _Service()
    server = ThreadingHTTPServer(("127.0.0.1", 0), svc.handler())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("HG_SVC_APPWORLD_URL", f"http://127.0.0.1:{server.server_port}")
    try:
        yield svc
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _evaluate(replay: dict, expected_value: str) -> dict:
    """The authored evaluator: two independent requirements, reported separately."""
    world = replay["world"]
    completed_calls = [name for name, _ in replay["log"] if name == "supervisor.complete_task"]
    return {
        "state_requirement": world["value"] == expected_value,
        "completion_requirement": bool(completed_calls),
        "detail": {"replayed_value": world["value"],
                   "replayed_completions": len(completed_calls)},
    }


def _run(service, snippets: list[str], harness_answer: str | None) -> None:
    """Drive the fabricated service the way the actor CLI does, then submit locally."""
    import urllib.request

    base = __import__("os").environ["HG_SVC_APPWORLD_URL"]

    def post(path, payload):
        request = urllib.request.Request(
            base + path, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read())

    post("/initialize", {"task_id": TASK_ID})
    for code in snippets:
        post("/execute", {"task_id": TASK_ID, "code": code})
    if harness_answer is not None:
        post("/harness_answer", {"answer": harness_answer})


def test_the_control_is_fabricated_and_uses_no_dataset_task_or_gold():
    """Guard the control's own claim: nothing here comes from a released task or an answer key."""
    import pathlib

    # Scan only the module body, not this test's own list of forbidden names.
    body = pathlib.Path(__file__).read_text(encoding="utf-8").split(
        "def test_the_control_is_fabricated")[0]
    for forbidden in ("data.datasets", "data/datasets", "ground_truth", "oracle",
                      "load(", "import data"):
        assert forbidden not in body, forbidden
    assert TASK_ID.startswith("fabricated/") and GOAL
    assert set(_fresh_world()) == {"value", "completed", "completion_calls"}
    assert "reward" not in body and "official scorer" not in body.replace(
        "it calls no official scorer", "")


def test_correct_state_without_completion_fails_only_the_completion_requirement(service):
    """Outcome 1: the actor/guidance boundary. This is the shape the review hypothesised."""
    _run(service, ["apis.synthetic.set_value('done')\nprint(apis.synthetic.set_value)"],
         harness_answer="I set the value to done.")
    assert service.live_world == {"value": "done", "completed": False, "completion_calls": 0}
    assert service.harness_submissions == ["I set the value to done."]
    result = _evaluate(service.replay(), "done")
    assert result["state_requirement"] is True
    assert result["completion_requirement"] is False
    assert result["detail"] == {"replayed_value": "done", "replayed_completions": 0}


def test_completion_in_the_live_world_but_not_in_the_recording_is_wiring(service):
    """Outcome 2: recording/verifier wiring. Live and replayed worlds disagree on completion only."""
    _run(service, ["apis.supervisor.complete_task()"], harness_answer="completed")
    assert service.live_world["completed"] is True
    # Drop the recorded completion call, as a recording/verifier wiring defect would.
    dropped = [call for call in service.recorded if "complete_task" not in call["code"]]
    assert len(dropped) == len(service.recorded) - 1
    result = _evaluate(service.replay(dropped), None)
    assert result["completion_requirement"] is False, "the replay must show what the recording holds"
    assert service.live_world["completed"] is True, "the live world still holds the completion"


def test_wrong_state_with_preserved_completion_is_a_task_state_failure(service):
    """Outcome 3: a genuine task-state failure, distinguishable from both boundary defects."""
    _run(service, ["apis.synthetic.set_value('wrong')\napis.supervisor.complete_task()"],
         harness_answer="done")
    result = _evaluate(service.replay(), "done")
    assert result["state_requirement"] is False
    assert result["completion_requirement"] is True


def test_both_requirements_satisfied_is_still_not_a_benchmark_win(service):
    """Outcome 4: a complete fabricated control - explicitly not a measured dataset result."""
    _run(service, ["apis.synthetic.set_value('done')\napis.supervisor.complete_task()"],
         harness_answer="done")
    result = _evaluate(service.replay(), "done")
    assert result["state_requirement"] is True
    assert result["completion_requirement"] is True
    # The control publishes no score, binds no dataset and asserts no success.
    assert "score" not in result and "reward" not in result
    assert service.live_world["completion_calls"] == 1


def test_discovery_exposes_the_completion_surface_without_the_answer(service):
    """The completion API must be discoverable and must not leak what the answer should be."""
    _run(service, ["print(apis.api_docs.show_api_descriptions('supervisor'))"], harness_answer=None)
    readback = service.readbacks[-1]
    assert "complete_task" in readback
    assert "done" not in readback and "fabricated/control/0" not in readback
