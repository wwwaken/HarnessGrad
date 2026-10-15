"""Audit real captured controls offline; altered copies are negative test inputs."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "reports/w-quiesce-evidence"
if not EVIDENCE.is_dir():
    pytest.skip("reports/w-quiesce-evidence is internal (see .gitignore) and absent from this clone",
                allow_module_level=True)
if not (ROOT / "tests/fixtures/hg_wpristine").is_dir():
    pytest.skip("tests/fixtures/hg_wpristine is internal (see .gitignore) and absent from this clone",
                allow_module_level=True)

SPEC = importlib.util.spec_from_file_location("quiesce_audit", EVIDENCE / "audit.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


@pytest.fixture(autouse=True)
def historical_code_root(tmp_path, monkeypatch):
    """Audit the immutable receipt against its historical code, not today's code.

    The preserved auditor still checks every recorded SHA-256. No historical
    receipt, seal or audit script is changed when production code advances.
    """
    historical = tmp_path / "historical-code"
    launch = AUDIT.load(EVIDENCE / "final-control/launch.json")
    archive = ROOT / "reports/w-quiesce2-evidence/before-source"
    for name, pin in launch["source_hashes"].items():
        raw = (archive / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == pin
        target = historical / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    fixture = historical / "tests/fixtures/hg_wpristine"
    fixture.parent.mkdir(parents=True)
    shutil.copytree(ROOT / "tests/fixtures/hg_wpristine", fixture)
    monkeypatch.setattr(AUDIT, "REPO", historical)


def test_preserved_packet_establishes_only_its_bounded_claims():
    result = AUDIT.audit(EVIDENCE / "final-control")
    assert result == json.loads((EVIDENCE / "audit.json").read_text())
    assert result["source_limitation_demonstrated"]
    assert not result["source_quiescence_established"]
    assert not result["dataset_equivalence_established"]
    assert result["production_measured"] == 4
    assert result["direct_reference_measured"] == 1
    assert result["production_unmeasured"] == 2
    assert result["created"] == result["removed"] == 6


def test_partial_first_attempt_is_preserved_and_attributed():
    packet = EVIDENCE / "first-attempt"
    launch = AUDIT.load(packet / "launch.json")
    assert AUDIT.sha(EVIDENCE / "first-driver-executed.py") == launch["source_hashes"]["reports/w-quiesce-evidence/collect.py"]
    verdict = AUDIT.load(packet / "working-control/verdict.json")
    assert verdict["outcome"] == "measured" and verdict["score"] == 0.0
    direct = packet / "pre-state"
    calls = AUDIT.load(direct / "docker-calls.json")
    assert [c["argv"][1] for c in calls] == ["create", "inspect", "rm", "inspect"]
    info = json.loads(calls[1]["stdout"])[0]
    assert info["Config"]["Env"] == ["HOME=/tmp", "TMPDIR=/tmp", "PATH=/control-scorer"]
    assert calls[2]["returncode"] == 0 and calls[3]["returncode"] == 1


@pytest.fixture
def packet(tmp_path):
    target = tmp_path / "packet"
    shutil.copytree(EVIDENCE / "final-control", target)
    return target


def reseal(packet):
    # These hashes belong only to deliberately corrupted temporary audit inputs.
    # Semantic checks must catch a bad claim even when its local file seal matches.
    path = packet / "SHA256SUMS"
    path.write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(packet).as_posix()}\n"
                   for p in sorted(packet.rglob("*")) if p.is_file() and p != path))


def test_packet_hash_change_refuses_before_semantic_claims(packet):
    (packet / "source-aba-attempt-01/source-after.bin").write_bytes(b"42\n")
    with pytest.raises(AssertionError):
        AUDIT.audit(packet)


@pytest.mark.parametrize("change", ["different-source", "missing-interval", "reverse-interval",
                                    "post-answer", "completion", "refusal-was-measured", "different-mount"])
def test_resealed_false_claims_are_rejected(packet, change):
    if change == "different-source":
        path = packet / "post-export-attempt-01/binding.json"
        raw = AUDIT.load(path)
        raw["source"] += "-different"
    elif change in {"missing-interval", "reverse-interval"}:
        path = packet / "source-aba-attempt-01/events.json"
        raw = AUDIT.load(path)
        event = next(e for e in raw if e["event"] == "source_write_42")
        if change == "missing-interval":
            # Erase both observations of the changed source, leaving endpoints only.
            for e in raw:
                if e["event"] in {"before_start", "after_start"}:
                    AUDIT.inventory_answer(e["source_inventory"])["sha256"] = AUDIT.sha(packet / "source-aba-attempt-01/source-before.bin")
        else:
            event["monotonic_ns"] = 0
    elif change == "post-answer":
        path = packet / "post-export-attempt-01/events.json"
        raw = AUDIT.load(path)
        event = next(e for e in raw if e["event"] == "export_return")
        AUDIT.inventory_answer(event["projection_inventory"])["sha256"] = AUDIT.sha(packet / "changed-answer-attempt-01/export-answer.bin")
    elif change == "completion":
        path = packet / "pre-state-attempt-01/docker-calls.json"
        raw = AUDIT.load(path)
        event = next(c for c in raw if c["argv"][1] == "start")
        event["stdout"] += "completed_check=fail\n"
    elif change == "refusal-was-measured":
        path = packet / "projection-tamper/verdict.json"
        raw = AUDIT.load(path)
        raw["score"], raw["outcome"] = 0.0, "measured"
    else:
        path = packet / "pre-state-attempt-01/docker-calls.json"
        raw = AUDIT.load(path)
        event = next(c for c in raw if c["argv"][1] == "inspect" and c["returncode"] == 0)
        info = json.loads(event["stdout"])
        next(m for m in info[0]["Mounts"] if m["Destination"] == "/control-input")["Source"] += "-different"
        event["stdout"] = json.dumps(info)
    path.write_text(json.dumps(raw))
    reseal(packet)
    with pytest.raises(AssertionError):
        AUDIT.audit(packet)
