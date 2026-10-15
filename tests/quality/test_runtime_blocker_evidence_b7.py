"""Live, no-model proofs for only Jericho and ScienceWorld's local runtime gaps.

Run under the read-only platform guard documented in reports/runtime-blockers-b7.md.
All disposable state and receipts go outside the checkout. No admission hook is patched.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from eval.containers import sandbox
from eval.run.integrity import diff, snapshot
from eval.run.runner import _refuse_unobserved_policies, run_one
from eval.policy.runtime_policy import stage_agent_runtime
from harnessgrad import methods


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mounts(raw):
    rows = []
    for line in raw.splitlines():
        fields = line.split()
        split = fields.index("-")
        rows.append({"target": fields[4], "options": fields[5].split(","),
                     "root": fields[3], "device": fields[2],
                     "fstype": fields[split + 1], "source": fields[split + 2]})
    return rows


def effective(raw, path):
    candidates = [row for row in mounts(raw)
                  if Path(path).is_relative_to(Path(row["target"]))]
    # Equal-length entries: the final overmount wins.
    return sorted(candidates, key=lambda row: len(row["target"]))[-1]


@pytest.fixture
def evidence_root(tmp_path):
    assert not tmp_path.resolve().is_relative_to(ROOT)
    # These are *evidence reproduction* tests: the receipts they check were gathered under a
    # launch that puts the platform behind a read-only bind ("the documented outer bwrap
    # guard"), and the probe below only means anything in that mode. So the guard is a
    # precondition of the run, not a property this test can establish on its own.
    #
    # Stated loudly rather than asserted: on this host `/mnt/20t` is mounted
    # `rw,nosuid,nodev,relatime`, so a plain `pytest` run is *not* guarded and an assertion
    # here would fail for a reason that has nothing to do with what is being tested. A bare
    # failure would be read as "the boundary is broken", which is the opposite of true. Run
    # under the guard to exercise these.
    guard = effective(Path("/proc/self/mountinfo").read_text(), ROOT)
    if "ro" not in guard["options"]:
        pytest.skip(
            "requires the documented outer bwrap guard: the platform mount "
            f"({guard['target']}) is {','.join(guard['options'])}, not read-only, so the "
            "read-only-boundary receipts cannot be reproduced here. Run under the guard.")
    with pytest.raises(OSError) as error:
        fd = os.open(ROOT / "eval/containers/sandbox.py", os.O_WRONLY)
        os.close(fd)
    assert error.value.errno == 30
    return tmp_path


def observer(work, *, inspect_paths=()):
    """An immutable-parent collector outside every subject's mounted trees."""
    code = (ROOT / "tests/quality/runtime_boundary_observer_b7.py").read_text()
    output = work / "parent-receipts"
    script = work / "observe-bwrap"
    script.write_text(f"#!{sys.executable}\n" + code +
                      f"\nimport sys\nraise SystemExit(observe(['/usr/bin/bwrap', *sys.argv[1:]], "
                      f"Path({str(output)!r}), inspect_paths={tuple(map(str, inspect_paths))!r}))\n")
    script.chmod(0o700)
    return script, output


def execute(plan, work, label, *, cwd):
    wrapper, output = observer(work)
    command = [str(wrapper), *plan[1:]]
    proc = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                          env=clean_env(), timeout=45)
    assert proc.returncode == 0, proc.stderr
    receipts = list(output.glob("*.json"))
    assert len(receipts) == 1
    receipt = json.loads(receipts[0].read_text())
    assert receipt["namespaces"]["mnt"] != receipt["observer_namespaces"]["mnt"]
    assert receipt["cleanup"] == {"bwrap_reaped": True, "child_absent": True}
    receipt["stdout"] = proc.stdout
    receipt["stderr"] = proc.stderr
    receipt["label"] = label
    if label != "old verifier root /":
        assert receipt["receipt_directory_visible"] is False
    return receipt, json.loads(proc.stdout)


def clean_env():
    return {"PATH": f"{Path(sys.executable).parent}:/usr/bin:/bin", "HOME": "/tmp",
            "TMPDIR": "/tmp", "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1"}


def save(work, name, value):
    path = work / name
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(f"B7_RECEIPT {path}")


def identity():
    files = ("data/datasets/jericho.py", "data/datasets/jericho/control.py",
             "data/datasets/jericho/runtime.py", "data/datasets/scienceworld.py",
             "eval/containers/sandbox.py", "eval/verification/verifier.py",
             "eval/run/runner.py", "harnessgrad/methods.py",
             "tests/quality/runtime_boundary_observer_b7.py",
             "tests/quality/test_runtime_blocker_evidence_b7.py")
    return {"git_head": subprocess.check_output(
                ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
            "files_sha256": {name: digest(ROOT / name) for name in files},
            "python": sys.executable, "python_sha256": digest(sys.executable),
            "bwrap": "/usr/bin/bwrap", "bwrap_sha256": digest("/usr/bin/bwrap"),
            "bwrap_version": subprocess.check_output(["/usr/bin/bwrap", "--version"], text=True).strip()}


def test_parent_observer_detects_effective_mount_regression(evidence_root):
    """ScienceWorld's actual native harness/verifier/method mount plans, live."""
    work = evidence_root
    before = snapshot(ROOT)
    platform_guard = effective(Path("/proc/self/mountinfo").read_text(), ROOT)
    workspace = work / "work/workspace"
    task = work / "task"
    workspace.mkdir(parents=True)
    task.mkdir()
    source = workspace / "agent.py"
    source.write_text("# external source canary\n")
    artifact = task / "artifact.txt"
    artifact.write_text("frozen artifact\n")
    verdict = task / "verifier"
    verdict.mkdir()
    # Open without truncate: a misconfiguration is observable but writes no bytes.
    probe = task / "probe.py"
    probe.write_text('''import errno, json, os, pathlib, tempfile
def writable(path):
    try:
        fd = os.open(path, os.O_WRONLY); os.close(fd)
        return 'OPENED_WRITABLE'
    except OSError as exc:
        return errno.errorcode[exc.errno]
out = {}
for key, path in json.loads(os.environ['PROBE_TARGETS']).items():
    out[key] = writable(path)
with tempfile.TemporaryDirectory() as scratch:
    p = pathlib.Path(scratch) / 'temporary'; p.write_text('temporary')
    out['private_tmp'] = p.read_text()
pathlib.Path('verifier/observed.txt').write_text('verdict writable')
out['verdict'] = pathlib.Path('verifier/observed.txt').read_text()
out['platform_driver_visible'] = pathlib.Path(os.environ['PLATFORM_DRIVER']).exists()
print(json.dumps(out, sort_keys=True))
''')
    targets = {"source": str(source), "artifact": str(artifact),
               "platform_source": str(ROOT / "eval/containers/sandbox.py")}
    env = {**clean_env(), "PROBE_TARGETS": json.dumps(targets),
           "PLATFORM_DRIVER": str(ROOT / "driver.py")}
    records = []
    for phase in ("harness", "verifier", "method"):
        phase_work = work / phase
        phase_work.mkdir()
        options = dict(platform=ROOT, work_root=workspace.parent, repo=workspace,
                       task_dir=task, env=env)
        if phase == "verifier":
            options.update(task_dir_writable=False, writable_paths=(verdict,))
        if phase == "method":
            # Use the real method-plan helper without editing global source/config.
            old = os.environ.get("HARNESSGRAD_WORK_ROOT")
            os.environ["HARNESSGRAD_WORK_ROOT"] = str(workspace.parent)
            try:
                options.update(methods._method_sandbox_plan(
                    workspace, [sys.executable, str(ROOT / "methods/echo_base/run.py")],
                    task, readonly=(workspace,)))
            finally:
                if old is None:
                    os.environ.pop("HARNESSGRAD_WORK_ROOT")
                else:
                    os.environ["HARNESSGRAD_WORK_ROOT"] = old
            targets["method_source"] = str(ROOT / "methods/echo_base/run.py")
            options["env"] = {**env, "PROBE_TARGETS": json.dumps(targets)}
        plan = sandbox.command([sys.executable, str(probe)], **options)
        receipt, seen = execute(plan, phase_work, phase, cwd=task)
        assert seen["source"] == "EROFS"
        assert seen["platform_source"] == "ENOENT"
        assert seen["platform_driver_visible"] is False
        assert seen["artifact"] == ("EROFS" if phase == "verifier" else "OPENED_WRITABLE")
        assert seen["private_tmp"] == "temporary"
        assert seen["verdict"] == "verdict writable"
        assert "ro" in effective(receipt["mountinfo"], source)["options"]
        assert effective(receipt["mountinfo"], ROOT)["fstype"] == "tmpfs"
        if phase == "method":
            assert seen["method_source"] == "EROFS"
            assert "ro" in effective(receipt["mountinfo"], targets["method_source"])["options"]
            receipt["method_source_sha256"] = digest(targets["method_source"])
            assert receipt["parent_source_views"][targets["method_source"]]["sha256"] == digest(targets["method_source"])
        assert str(ROOT / "driver.py") not in receipt["parent_source_views"]
        records.append(receipt)
    # Misconfigure the *same* verifier plan: last writable binds expose external
    # source/artifact canaries. Never expose the real platform writable.
    negative_work = work / "negative"
    negative_work.mkdir()
    fake = work / "disposable-platform"
    (fake / "eval/containers").mkdir(parents=True)
    fake_source = fake / "eval/containers/sandbox.py"
    fake_source.write_text("# disposable provenance canary\n")
    (fake / "driver.py").write_text("# disposable driver canary\n")
    fake_method = fake / "methods/echo_base/run.py"
    fake_method.parent.mkdir(parents=True)
    fake_method.write_text("# disposable method canary\n")
    negative_env = {**env, "PROBE_TARGETS": json.dumps(targets)}
    plan = sandbox.command([sys.executable, str(probe)], platform=ROOT,
                           work_root=workspace.parent, repo=workspace, task_dir=task,
                           env=negative_env, task_dir_writable=False,
                           writable_paths=(verdict,))
    split = plan.index("--")
    plan[split:split] = ["--bind", str(workspace), str(workspace),
                        "--bind", str(task), str(task), "--bind", str(fake), str(ROOT)]
    negative, seen = execute(plan, negative_work, "deliberately writable", cwd=task)
    assert {seen[key] for key in ("source", "artifact", "platform_source")} == {"OPENED_WRITABLE"}
    assert seen["platform_driver_visible"] is True
    assert seen["method_source"] == "OPENED_WRITABLE"
    assert negative["parent_source_views"][str(ROOT / "driver.py")]["sha256"] == digest(fake / "driver.py")
    assert "rw" in effective(negative["mountinfo"], source)["options"]
    # Also prove the provenance detector notices a real change outside the checkout.
    frozen = snapshot(fake)
    fake_source.write_text("# deliberately changed external canary\n")
    provenance_negative = diff(frozen, snapshot(fake))
    assert provenance_negative["modified"] == ["eval/containers/sandbox.py"]
    after = snapshot(ROOT)
    assert before == after
    save(work, "scienceworld-b7.json", {
        "scope": "live native mount enforcement; no ScienceWorld episode/model or admission authorization",
        "platform_guard": platform_guard, "guard_open_errno": "EROFS",
        "platform_before": before, "platform_after": after,
        "platform_manifest_sha256": hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest(),
        "positive": records, "negative": negative, "negative_provenance": provenance_negative,
        "identity": identity(), "model": None, "endpoint": None,
        "coverage": {"benchmark_episodes": 0, "native_phases": ["harness", "verifier", "method"],
                     "negative_mount_controls": 1, "negative_provenance_controls": 1},
        "limits": {"probe_timeout_s": 30, "jobs": 1, "concurrency": 1, "paid_calls": 0},
        "comparability": "Local native mount evidence only; no score or container/runtime-wide attestation.",
        "production_authorized": False})


def test_jericho_selected_runtime_and_control_have_parent_receipts(evidence_root):
    work = evidence_root
    import data.datasets.jericho as adapter
    import jericho.game_info as official

    # Only an already documented train/study game is selected; never print actions.
    selected = official.acorncourt
    assert not adapter._is_eval("acorncourt")
    record = {"task_id": "acorncourt", "rom": selected["rom"],
              "path": adapter.games_dir() / selected["rom"], "seed": int(selected["seed"]),
              "walkthrough": [a for a in selected["walkthrough"].split("/") if a]}
    setup, verify, env = adapter._setup(record), adapter._verifier(record), adapter._env()
    package = Path(env["agent_runtime"]["package_dir"])
    package_before = {str(path): digest(path) for path in sorted(package.glob('*')) if path.is_file()}
    public = [entry["path"] for entry in setup["files"]]
    assert not any("walkthrough" in entry or "game_info" in entry for entry in public)
    assert adapter.LOG_FILE not in [entry["path"] for entry in verify["inputs"]]
    before = snapshot(ROOT)
    wrapper, observations = observer(work, inspect_paths=(package,))
    controls = []
    for mode in ("noop", "oracle"):
        episode = work / mode
        command = [sys.executable, str(ROOT / "data/datasets/jericho/control.py"),
                   f"--{mode}", "--task-id", "acorncourt", "--workdir", str(episode)]
        run_env = {**clean_env(), "HG_BWRAP": str(wrapper)}
        proc = subprocess.run(command, cwd=work, env=run_env, capture_output=True,
                              text=True, timeout=330)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        evidence = json.loads((episode / "verifier/evidence.json").read_text())
        reward = float((episode / "verifier/reward.txt").read_text())
        assert evidence["measured"] is True
        assert reward == (1 if mode == "oracle" else 0)
        controls.append({"command": command, "stdout": proc.stdout, "stderr": proc.stderr,
                         "reward": reward, "score": evidence["score"],
                         "max_score": evidence["max_score"], "moves": evidence["moves"],
                         "measured": evidence["measured"]})
    observed = [json.loads(path.read_text()) for path in observations.glob("*.json")]
    assert len(observed) == len(record["walkthrough"]) + 3
    agents, verifiers = [], []
    for item in observed:
        cmd = item["command"]
        assert item["exit_code"] == (1 if "check.py" in cmd and "noop" in item["cwd"] else 0)
        assert item["cleanup"] == {"bwrap_reaped": True, "child_absent": True}
        assert item["namespaces"]["mnt"] != item["observer_namespaces"]["mnt"]
        assert item["receipt_directory_visible"] is False
        assert effective(item["mountinfo"], ROOT)["fstype"] == "tmpfs"
        assert "ro" in effective(item["mountinfo"], package)["options"]
        if "check.py" in cmd:
            verifiers.append(item)
            # f27be1f's actual call uses .control, never the '/' fallback.
            assert str(work / ("noop" if "noop" in item["cwd"] else "oracle") / ".control") in cmd
            assert effective(item["mountinfo"], "/tmp")["fstype"] == "tmpfs"
            assert "rw" in effective(item["mountinfo"], "/tmp")["options"]
            assert "ro" in effective(item["mountinfo"], item["cwd"])["options"]
            assert "rw" in effective(item["mountinfo"], Path(item["cwd"]) / "verifier")["options"]
            assert item["parent_source_views"][str(package / "game_info.py")]["sha256"] == package_before[str(package / "game_info.py")]
        else:
            agents.append(item)
            assert item["namespaces"]["net"] != item["observer_namespaces"]["net"]
            assert str(package / "game_info.py") not in item["parent_source_views"]
        assert item["parent_source_views"][str(package / "libfrotz.so")]["sha256"] == package_before[str(package / "libfrotz.so")]
    assert len(verifiers) == 2 and len(agents) == len(record["walkthrough"]) + 1
    # The same real installed runtime with and without its projection. No reference
    # values are emitted; the negative probe exposes only presence of the API/data.
    visibility = []
    for projected in (True, False):
        case = work / f"projection-{projected}"
        case.mkdir()
        task = case / "task"
        task.mkdir()
        control_root = case / "control"
        control_root.mkdir()
        probe = task / "probe.py"
        probe.write_text('''import importlib.util, json, pathlib, jericho
from jericho import defines
try:
    jericho.FrotzEnv.__new__(jericho.FrotzEnv).get_walkthrough()
    available = True
except RuntimeError:
    available = False
except AttributeError:
    available = True
print(json.dumps({'reference_module': importlib.util.find_spec('jericho.game_info') is not None,
                  'reference_bindings': bool(defines.BINDINGS_DICT), 'walkthrough_api': available,
                  'bytecode': (pathlib.Path(jericho.__file__).parent / '__pycache__').exists()}, sort_keys=True))
''')
        overlay = stage_agent_runtime(env["agent_runtime"], case / "projection") if projected else None
        plan = sandbox.command([sys.executable, str(probe)], platform=ROOT, work_root=control_root,
                               repo=control_root, task_dir=task, env=clean_env(), network="none",
                               package_overlays=(overlay,) if overlay else ())
        receipt, seen = execute(plan, case, f"projection={projected}", cwd=task)
        assert seen["reference_module"] is (not projected)
        assert seen["reference_bindings"] is (not projected)
        assert seen["walkthrough_api"] is (not projected)
        if projected:
            assert seen["bytecode"] is False
            view = receipt["parent_source_views"]
            assert str(package / "game_info.py") not in view
            assert view[str(package / "libfrotz.so")]["sha256"] == package_before[str(package / "libfrotz.so")]
        visibility.append(receipt)
    # Old '/' work-root misconfiguration is reproduced without changing control.py.
    case = work / "old-root-negative"
    case.mkdir()
    task = case / "task"
    task.mkdir()
    plan = sandbox.command([sys.executable, "-c", "import errno,json,tempfile; "
        "\ntry:\n tempfile.TemporaryDirectory(); print(json.dumps({'tempfile':'CREATED'}))"
        "\nexcept OSError as e:\n print(json.dumps({'tempfile':errno.errorcode[e.errno]}))"],
        platform=ROOT, work_root=Path("/"), repo=task, task_dir=task,
        task_dir_writable=False, env=clean_env())
    old_root, seen = execute(plan, case, "old verifier root /", cwd=task)
    assert "ro" in effective(old_root["mountinfo"], "/tmp")["options"]
    assert seen["tempfile"] == "ENOENT"
    # The platform applies the adapter's deadlines/network. A separate unsupported
    # native CPU declaration must still refuse before staging execution.
    assert _refuse_unobserved_policies({"task_id": "acorncourt"}, env, verify) is None
    admission_env = {**env, "cpus": 2}
    refused = run_one(work / "uncreated-harness", {"task_id": "acorncourt", "goal": "control"},
                      env=admission_env, verifier=verify)
    assert refused["invalid"]["receipt"]["production_authorized"] is False
    assert refused["invalid"]["receipt"]["reason"] == "backend_observation_unavailable"
    assert "score" not in refused and "verdict" not in refused
    assert refused["invalid"]["receipt"]["policy_fields"] == ["env.cpus"]
    assert before == snapshot(ROOT)
    assert package_before == {str(path): digest(path) for path in sorted(package.glob('*')) if path.is_file()}
    manifest = {"task_id": "acorncourt", "rom": record["rom"], "seed": record["seed"],
                "reference_commands": len(record["walkthrough"]), "split": "train/study",
                "rom_sha256": digest(record["path"]), "setup_paths": public,
                "verify_input_paths": [entry["path"] for entry in verify["inputs"]],
                "agent_runtime_paths": [entry["path"] for entry in env["agent_runtime"]["files"]]}
    cleanup = []
    for episode in (work / "noop", work / "oracle"):
        shutil.rmtree(episode)
        cleanup.append({"path": str(episode), "absent": not episode.exists()})
    save(work, "jericho-b7.json", {
        "selected_metadata": manifest,
        "selected_manifest_sha256": hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest(),
        "controls": controls, "parent_observations": observed,
        "projection_controls": visibility, "old_root_negative": old_root,
        "admission": refused["invalid"]["receipt"],
        "admission_env": admission_env,
        "platform_before": before, "platform_after": snapshot(ROOT),
        "package_sha256": {str(path): digest(path) for path in sorted(package.glob('*')) if path.is_file()},
        "identity": identity(), "cleanup": cleanup,
        "metric": "game score / game get_max_score(); released reference control, not model effect",
        "coverage": {"eligible": 56, "selected": 1, "tasks": ["acorncourt"],
                     "trials_per_control": 1, "controls": 2, "invalid": 0, "unmeasured": 0},
        "source_archive_sha256_declared": adapter.ARCHIVE_SHA256,
        "source_archive_reverified": False,
        "limits": {"agent_timeout_s": 300, "verify_timeout_s": 300, "jobs": 1,
                   "observer_timeout_s": 30, "concurrency": 1, "paid_calls": 0,
                   "additional_byte_inode_quotas": None},
        "comparability": "One selected train/study game's local controls; no production/H0 or global release/dependency attestation.",
        "model": None, "endpoint": None, "production_authorized": False})
