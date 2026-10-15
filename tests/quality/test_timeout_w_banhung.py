"""A native launch that times out or is killed must clean up after itself.

**The mechanism half.** Every case below drives a real `runner.run_one` whose harness
spawns a descendant that inherits stdout/stderr, then reports what it observed. The
discriminating assertion is `token_probe.returncode == 1` - no descendant survives the
launch - because that is the one that is red before `eval/containers/process.py` and green
after. A bounded return time and an empty task tree are asserted too, but they were already
true before the fix: `subprocess.run` on POSIX calls `process.wait()` after killing the
direct child, not an unbounded drain, so the grandchild never held the call open. w-banhung's
own `reports/w-banhung-evidence/reproduction-wait-before.log` records `RETURNED 0
outer_elapsed_s 0.464` **with** a surviving `time.sleep(30)` descendant. The defect was a
leaked process, not a hang, and this file's first version overstated it.

**The scoring half belongs to `INTERFACE.md` §2.2 and to `w-outcome` (`59cbf662`), not to
this worker.** The verifier grades the artifact; the process does not decide the score. So a
budget timeout, a self-crash and an outside kill are all *measured* when the artifact is
right, and the only unmeasured ending is a signal kill with nothing passing
(`runner._stopped_by_signals`). An earlier draft of this file asserted that a timeout is
unmeasured and that a signalled wrapper must skip the verifier; that reading was superseded
by the operator's contract and is corrected here rather than in `eval/`.

**One case is deliberately pinned as ambiguous rather than asserted as correct.** A bwrap
wrapper relays an inner kill as exit `128+signal`, so the platform sees `137` (positive) where
a direct kill gives `-9`. `process_outcome` reads the sign, so the sandboxed case is scored
while the host case is unmeasured. w-banhung's own comment says a wrapper exit "is a signal
convention, not proof of its cause" - which is exactly why it cannot be used to withdraw a
measurement. See `test_a_sandboxed_inner_signal_is_ambiguous_today`.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from eval.containers.process import run
from eval.policy.runtime_policy import phase_timeout
from eval.run import runner

CONTROL = Path(__file__).with_name("banhung_timeout_control.py")
#: Behaviours whose harness leaves `answer.txt` correct before it ends.
RIGHT_ARTIFACT = ("wait", "orphan", "kill", "kill-child", "term", "crash")


def _observe(tmp_path, mode, behavior):
    """Run one real launch through the control supervisor and return its report."""
    proc = subprocess.run([sys.executable, str(CONTROL), mode, str(tmp_path / behavior), behavior],
                          capture_output=True, text=True, timeout=120,
                          env={**os.environ, "TMPDIR": str(tmp_path)})
    assert proc.returncode == 0, proc.stderr[-2000:]
    return json.loads(proc.stdout.splitlines()[-1])


@pytest.mark.parametrize("mode", ["host", "sandbox"])
@pytest.mark.parametrize("behavior", ["wait", "orphan", "kill", "kill-child", "term",
                                      "crash", "zero", "kill-zero"])
def test_real_launch_returns_and_leaves_no_descendant(tmp_path, mode, behavior):
    observed = _observe(tmp_path, mode, behavior)
    assert observed["elapsed_s"] < 2, observed["elapsed_s"]
    assert observed["task_trees"] == []
    # Every process group the launcher created is empty, and the token that only the
    # harness's descendant carries is gone. This is the assertion the fix earns.
    assert all(p["returncode"] == 1 and p["stdout"] == "" for p in observed["groups"]), observed
    assert observed["token_probe"]["returncode"] == 1, observed["token_probe"]


@pytest.mark.parametrize("behavior", RIGHT_ARTIFACT)
def test_the_artifact_decides_the_score_after_a_timeout_or_a_kill(tmp_path, behavior):
    """§2.2: a timeout, a self-crash and an outside kill all still grade the artifact."""
    observed = _observe(tmp_path, "host", behavior)
    assert observed["per_task"] == {"synthetic": 1.0}, observed["invalid"]
    assert observed["invalid"] == {}
    assert len(observed["cache"]) == 1


def test_a_completed_wrong_answer_is_a_real_measured_zero(tmp_path):
    observed = _observe(tmp_path, "host", "zero")
    assert observed["per_task"] == {"synthetic": 0.0}
    assert observed["invalid"] == {}


def test_a_signal_with_no_passing_artifact_is_unmeasured(tmp_path):
    """The one ending that is not a score: nothing was graded, so nothing is published."""
    observed = _observe(tmp_path, "host", "kill-zero")
    assert observed["per_task"] == observed["cache"] == {}
    bad = observed["invalid"]["synthetic"]
    assert bad["outcome"] == "stopped_by_signal"
    assert bad["stage"] == "harness"
    assert "signal 9" in bad["detail"] and "not a score" in bad["detail"]
    assert "score" not in observed["progress"]


def test_a_sandboxed_inner_signal_is_ambiguous_today(tmp_path):
    """Pins an observed asymmetry so a future decision is visible, not silent.

    In the sandbox the direct child is `bwrap`, which relays an inner kill as exit 137 -
    positive, so `process_outcome` classifies it as `harness_crash` and the task scores,
    where the identical self-kill on the host gives `-9` and is unmeasured. A wrapper exit
    cannot distinguish a harness that killed itself from an outside kill of the process
    inside the sandbox, and no rule in `INTERFACE.md` covers it, so this test asserts what
    happens rather than what should. If the operator decides `128+signal` means
    `stopped_by_signal`, this assertion is the one that changes.
    """
    observed = _observe(tmp_path, "sandbox", "kill-zero")
    assert observed["result"]["exit_code"] == 137, observed["result"]["exit_code"]
    assert observed["per_task"] == {"synthetic": 0.0}
    assert observed["invalid"] == {}


def test_a_passing_trial_survives_a_later_signal(tmp_path, monkeypatch):
    """Positive evidence is not overruled - the same exception the provider rule makes."""
    results = iter([
        {"verdict": {"passed": True, "score": 1.0}, "trace": "completed", "exit_code": 0},
        {"verdict": {"passed": False, "score": 0.0}, "trace": "partial", "exit_code": -9,
         "stderr": ""}])
    monkeypatch.setattr(runner, "run_one", lambda *a, **k: next(results))
    cache = {}
    result = runner._evaluate(tmp_path, [{"task_id": "synthetic"}], {}, trials=2, cache=cache)
    # The point is that the task stays *measured*: a signalled final trial must not
    # withdraw a task one of whose trials passed. The value is the ordinary mean over
    # both trials, 0.5, not the passing trial alone.
    assert result["per_task"] == {"synthetic": 0.5}
    assert result["invalid"] == {}


def test_the_verifier_still_runs_after_a_signal(tmp_path, monkeypatch):
    """The process ending must not decide measurability (§2.2) - the verifier is consulted."""
    repo = tmp_path / "harness"
    repo.mkdir()
    (repo / "harness.json").write_text(json.dumps({"entrypoint": "agent.py"}))
    (repo / "agent.py").write_text("pass")
    monkeypatch.setattr(runner, "run_process",
                        lambda argv, **kw: subprocess.CompletedProcess(argv, -9, "", "killed"))
    seen = []
    monkeypatch.setattr(runner, "_verify",
                        lambda *a, **k: seen.append(1) or {"kind": "answer", "passed": True,
                                                           "score": 1.0})
    result = runner.run_one(repo, {"task_id": "synthetic"}, sandbox=False)
    assert seen == [1], "a signalled wrapper must still be graded"
    assert result["verdict"]["passed"] is True


def test_stdin_and_completed_output():
    proc = run([sys.executable, "-c",
                "import sys; print(sys.stdin.read()); print('err', file=sys.stderr)"],
               timeout_s=2, input_text="request")
    assert (proc.returncode, proc.stdout, proc.stderr) == (0, "request\n", "err\n")


@pytest.mark.parametrize("declared, caller, expected", [
    (None, None, 3600), (7200, None, 7200), (20, 3, 3), (3, 20, 3)])
def test_agent_deadline_uses_existing_policy(tmp_path, monkeypatch, declared, caller, expected):
    """A caller or dataset bound wins; 3600 is only the fallback when neither declares one."""
    repo = tmp_path / "harness"
    repo.mkdir()
    (repo / "harness.json").write_text(json.dumps({"entrypoint": "agent.py"}))
    (repo / "agent.py").write_text("pass")
    limits = []

    def expire(argv, **kwargs):
        limits.append(kwargs["timeout_s"])
        raise subprocess.TimeoutExpired(argv, kwargs["timeout_s"])

    monkeypatch.setattr(runner, "run_process", expire)
    result = runner.run_one(repo, {"task_id": "synthetic"}, sandbox=False,
                            timeout_s=caller, env={"kind": "files", "agent_timeout_s": declared})
    assert limits == [expected] == [phase_timeout(caller, declared)]
    assert result["runtime_boundary"]["agent_timeout_s"] == expected
