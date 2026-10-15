"""Selected-source endpoint observations; Docker double, real bounded export/scorer."""
import os
import json
import importlib.util
from pathlib import Path
import subprocess

import pytest

from eval.containers import container
from eval.admission import artifact_admission as artifacts
from eval.verification import verifier
from test_scorer_isolation_option_b import actor, docker_double, scorer


@pytest.mark.parametrize("restore_mtime", [False, True])
def test_source_aba_is_unmeasured(tmp_path, scorer, docker_double, monkeypatch, restore_mtime):
    source = actor(tmp_path)
    answer = source / "answer.txt"
    before = answer.stat()
    original = container.docker

    def docker(*args, **kwargs):
        if args[0] == "start":
            answer.write_text("changed")  # Same length; remains changed through scoring.
        result = original(*args, **kwargs)
        if args[0] == "start":
            answer.write_text("correct")
            if restore_mtime:
                os.utime(answer, ns=(before.st_atime_ns, before.st_mtime_ns))
        return result

    monkeypatch.setattr(container, "docker", docker)
    verdict = verifier._verify(source, scorer, "", sandbox=False, timeout_s=5, task_id="t")
    assert docker_double.started and answer.read_text() == "correct"
    assert verdict["score"] is None and verdict["outcome"] == "unmeasured"
    observation = verdict["scorer_isolation_evidence"]["source_observation"]
    assert observation["status"] == "difference_observed"
    assert observation["quiescence_established"] is False
    assert observation["before"]["files"][0]["sha256"] == observation["after"]["files"][0]["sha256"]
    assert observation["before"]["files"][0]["st_ctime_ns"] != observation["after"]["files"][0]["st_ctime_ns"]


@pytest.mark.parametrize("change", ["content", "size", "replace", "chmod", "missing", "symlink", "oversize"])
def test_source_changes_refuse_measurement(tmp_path, scorer, docker_double, monkeypatch, change):
    source = actor(tmp_path)
    answer = source / "answer.txt"
    original = container.docker

    def docker(*args, **kwargs):
        result = original(*args, **kwargs)
        if args[0] == "start":
            if change == "replace":
                replacement = source / "replacement"
                replacement.write_text("correct")
                replacement.replace(answer)
            elif change == "chmod":
                answer.chmod(0o400)
            elif change in {"missing", "symlink"}:
                answer.unlink()
                if change == "symlink":
                    answer.symlink_to(source / "unselected.py")
            else:
                answer.write_text({"content": "changed", "size": "x", "oversize": "x" * 17}[change])
        return result

    monkeypatch.setattr(container, "docker", docker)
    verdict = verifier._verify(source, scorer, "", sandbox=False, timeout_s=5)
    assert docker_double.started and verdict["score"] is None
    assert verdict["outcome"] == "unmeasured"
    observation = verdict["scorer_isolation_evidence"]["source_observation"]
    assert observation["status"] == ("probe_unavailable" if change in {"missing", "symlink", "oversize"} else "difference_observed")
    assert observation["quiescence_established"] is False
    assert verdict["scorer_isolation_evidence"]["cleanup"]["removed"]


@pytest.mark.parametrize("change_unselected", [False, True])
def test_unchanged_selected_files_and_binding_scope(tmp_path, scorer, docker_double, monkeypatch, change_unselected):
    source = actor(tmp_path)
    original = container.docker

    def docker(*args, **kwargs):
        if args[0] == "start" and change_unselected:
            (source / "unselected.py").write_text("deliberately outside probe scope")
        return original(*args, **kwargs)

    monkeypatch.setattr(container, "docker", docker)
    verdict = verifier._verify(source, scorer, "", sandbox=False, timeout_s=5, task_id="t")
    assert verdict["score"] == 1.0 and verdict["outcome"] == "measured"
    evidence = json.loads(json.dumps(verdict))["scorer_isolation_evidence"]
    observation = evidence["source_observation"]
    assert observation["status"] == "no_change_observed" and not observation["quiescence_established"]
    assert observation["before"]["files"] == observation["after"]["files"]
    assert observation["before"]["finished_monotonic_ns"] <= observation["after"]["started_monotonic_ns"]
    assert observation["export_content_matches_before"] is True
    assert [row["path"] for row in observation["before"]["files"]] == ["answer.txt"]
    binding = evidence["execution_binding"]
    assert binding["task_id"] == "t" and binding["selected_task_checked"]
    assert binding["runtime_export_run_id"] == evidence["export"]["run_id"] == evidence["cleanup"]["container"]
    assert binding["outer_run_id"] is None and binding["trial_id"] is None
    assert binding["outer_run_trial_binding"] == "not_provided"


def test_source_change_between_baseline_and_export_never_starts(tmp_path, scorer, docker_double, monkeypatch):
    source = actor(tmp_path)
    original = artifacts.export_state

    def export(*args, **kwargs):
        (source / "answer.txt").write_text("changed")
        result = original(*args, **kwargs)
        (source / "answer.txt").write_text("correct")
        return result

    monkeypatch.setattr(artifacts, "export_state", export)
    verdict = verifier._verify(source, scorer, "", sandbox=False, timeout_s=5)
    assert verdict["score"] is None and not docker_double.started and not docker_double.calls
    observation = verdict["scorer_isolation_evidence"]["source_observation"]
    assert observation["status"] == "difference_observed"
    assert observation["export_content_matches_before"] is False


@pytest.mark.parametrize("failure", ["timeout", "cleanup"])
def test_source_observed_after_execution_failure_without_losing_cause(tmp_path, scorer, docker_double, monkeypatch, failure):
    source = actor(tmp_path)
    original = container.docker
    docker_double.cleanup_failure = failure == "cleanup"

    def docker(*args, **kwargs):
        if args[0] == "start" and failure == "timeout":
            (source / "answer.txt").write_text("changed")
            raise subprocess.TimeoutExpired(args, 5)
        return original(*args, **kwargs)

    monkeypatch.setattr(container, "docker", docker)
    verdict = verifier._verify(source, scorer, "", sandbox=False, timeout_s=5)
    assert verdict["score"] is None
    observation = verdict["scorer_isolation_evidence"]["source_observation"]
    assert "after" in observation
    assert observation["status"] == ("difference_observed" if failure == "timeout" else "no_change_observed")
    assert verdict["outcome"] == ("timeout" if failure == "timeout" else "unmeasured")
    assert ("timed out" if failure == "timeout" else "cleanup failed") in verdict["unmeasured"]


def test_missing_baseline_never_claims_no_change_or_starts(tmp_path, scorer, docker_double):
    source = actor(tmp_path)
    (source / "answer.txt").unlink()
    verdict = verifier._verify(source, scorer, "", sandbox=False, timeout_s=5)
    assert verdict["score"] is None and not docker_double.calls
    assert verdict["scorer_isolation_evidence"]["source_observation"]["status"] == "probe_unavailable"


def test_wrong_task_still_refuses_before_source_probe(tmp_path, scorer, docker_double):
    verdict = verifier._verify(actor(tmp_path), scorer, "", sandbox=False, timeout_s=5, task_id="other")
    assert verdict["score"] is None and "task differs" in verdict["unmeasured"]
    assert not docker_double.calls
    assert "source_observation" not in verdict["scorer_isolation_evidence"]


def test_transient_directory_swap_is_explicitly_outside_file_probe_scope(tmp_path, scorer, docker_double, monkeypatch):
    """A same-UID namespace writer can hide changed path bytes from both probes."""
    source = actor(tmp_path)
    substitute, parked = tmp_path / "substitute", tmp_path / "parked"
    substitute.mkdir()
    (substitute / "answer.txt").write_text("changed")
    original = container.docker

    def docker(*args, **kwargs):
        if args[0] == "start":
            source.rename(parked)
            substitute.rename(source)
            assert (source / "answer.txt").read_text() == "changed"
        try:
            return original(*args, **kwargs)
        finally:
            if args[0] == "start":
                source.rename(substitute)
                parked.rename(source)

    monkeypatch.setattr(container, "docker", docker)
    verdict = verifier._verify(source, scorer, "", sandbox=False, timeout_s=5)
    observation = verdict["scorer_isolation_evidence"]["source_observation"]
    assert verdict["score"] == 1.0 and observation["status"] == "no_change_observed"
    assert not observation["quiescence_established"]
    assert observation["before"]["files"] == observation["after"]["files"]


def test_real_daemon_packets_establish_only_the_recorded_scope():
    evidence = Path(__file__).resolve().parents[2] / "reports/w-quiesce2-evidence"
    spec = importlib.util.spec_from_file_location("quiesce2_audit", evidence / "audit.py")
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    result = audit.audit(evidence)
    assert result == json.loads((evidence / "audit.json").read_text())
    assert result["demonstrated_mutation_detected_after"]
    assert not result["source_quiescence_established"]
    assert not result["native_outer_run_trial_binding"]
