"""Offline native-input consistency controls using actual local released records.

Only command checks and verifier dispatch run. Game engines, SQL queries, candidate
programs and workbook comparisons are intercepted by structural spies. Their zero
rewards are test sentinels, never benchmark measurements. Baseline collection does
not import the new helper, so the exact final tests also exercise original HEAD.
"""
from __future__ import annotations

import copy
import hashlib
import importlib
import importlib.util
import json
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from eval.verification import verifier

DATASETS = ("alfworld", "bird_minidev", "ds1000", "jericho", "livecodebench",
            "scienceworld", "spreadsheetbench")


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("w-tbi2 controls must stay offline")
    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket.socket, "connect_ex", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "")


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def entries(spec):
    return {e["path"]: e for e in spec["inputs"]}


def entry_sha(entry):
    return (hashlib.sha256(entry["content"].encode()).hexdigest()
            if "content" in entry else sha(entry["from"]))


def digest_inventory(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@pytest.fixture(scope="module", params=DATASETS)
def case(request):
    name = request.param
    module = importlib.import_module(f"data.datasets.{name}")
    if name == "ds1000":
        first, other = module.included_indices()[:2]
        selected_id, other_id = module.task_id(first), module.task_id(other)
        spec, foreign = module.verify_for(first), module.verify_for(other)
        # At baseline this input exists only in actor SETUP. Stage that actual
        # released context for direct controls; contract/rematerialization tests
        # still explicitly require it in trusted VERIFY after the change.
        context = lambda i: next(e for e in module.setup_for(i)["files"] if e["path"] == "context.json")
        payloads = {"context.json": context(first)}
        substitutes = {"context.json": context(other)}
        csvs = sorted(module.SEABORN_DIR.glob("*.csv"))
        assert len(csvs) == 4
        for index, csv in enumerate(csvs):
            path = "seaborn-data/" + csv.name
            payloads[path] = {"path": path, "from": str(csv)}
            substitutes[path] = {"path": path, "from": str(csvs[(index + 1) % len(csvs)])}
    elif name == "livecodebench":
        first, other = module._INDEXED[:2]
        selected_id, other_id = module.task_id(first["index"]), module.task_id(other["index"])
        spec, foreign = module._verify(first), module._verify(other)
        payloads, substitutes = {"tests.json": entries(spec)["tests.json"]}, {"tests.json": entries(foreign)["tests.json"]}
    else:
        records = module._ensure() if hasattr(module, "_ensure") else module._RECORDS
        assert records, name
        first = records[0]
        other = next(r for r in records[1:] if r["db_id"] != first["db_id"]) if name == "bird_minidev" else records[1]
        build = module._verify if name == "bird_minidev" else module._verifier
        spec, foreign = build(first), build(other)
        selected_id, other_id = first["task_id"], other["task_id"]
        if name == "alfworld":
            paths = [module.GAME_IN_WORKDIR]
            substitutes = {paths[0]: entries(foreign)[paths[0]]}
        elif name == "bird_minidev":
            paths = ["gold.sql", "database.sqlite"]
            substitutes = {p: entries(foreign)[p] for p in paths}
        elif name == "jericho":
            paths = [module.GAME_FILE, first["rom"]]
            substitutes = {paths[0]: entries(foreign)[paths[0]], paths[1]: entries(foreign)[other["rom"]]}
        elif name == "scienceworld":
            paths = [module.TASK_IN_WORKDIR, "scienceworld.jar"]
            package = Path(importlib.util.find_spec("scienceworld").origin).parent
            payloads = {"scienceworld.jar": {"path": "scienceworld.jar", "from": str(package / "scienceworld.jar")}}
            # World JAR is shared across tasks. Authenticate it separately with
            # a different, real staged JRE JAR, never claim a foreign-task world.
            other_jar = next(module.JRE_STAGED.rglob("*.jar"))
            substitutes = {paths[0]: entries(foreign)[paths[0]], paths[1]: {"path": paths[1], "from": str(other_jar)}}
        else:
            paths = ["golden.xlsx", "task.json"]
            substitutes = {p: entries(foreign)[p] for p in paths}
        payloads = {p: entries(spec).get(p, locals().get("payloads", {}).get(p)) for p in paths}
    expected_files = {p: entry_sha(e) for p, e in payloads.items()}
    foreign_files = {p: entry_sha(e) for p, e in substitutes.items()}
    assert all(expected_files[p] != foreign_files[p] for p in payloads), (name, expected_files, foreign_files)
    return SimpleNamespace(name=name, module=module, task_id=selected_id,
                           foreign_task_id=other_id, spec=spec, foreign=foreign,
                           payloads=payloads, substitutes=substitutes,
                           files=expected_files, foreign_files=foreign_files)


def write_entry(work, path, entry):
    target = work / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if "content" in entry:
        target.write_text(entry["content"], encoding="utf-8")
    else:
        shutil.copyfile(entry["from"], target)


def stage(case, work):
    for entry in case.spec["inputs"]:
        if "from" in entry and Path(entry["from"]).is_dir():
            continue  # spies never launch the JRE or DS-1000 seaborn program
        write_entry(work, entry["path"], entry)
    for path, entry in case.payloads.items():
        write_entry(work, path, entry)
    if case.name == "spreadsheetbench":
        shutil.copyfile(work / "golden.xlsx", work / case.module.RESULT_WORKBOOK)


def load_check(case):
    # Import only dependency-free native wrapper libraries, never their engines.
    asset = ROOT / "data/datasets" / case.name
    for dirname in (asset / "lib", asset):
        sys.path.insert(0, str(dirname))
    spec = importlib.util.spec_from_file_location(f"w_tbi2_check_{case.name}", asset / "verify/check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_spies(case, check, work, monkeypatch, *, replace_after=False):
    calls = []
    def consume(paths):
        actual = {p: sha(v) for p, v in paths.items()}
        calls.append(actual)
        if replace_after:
            for p, e in case.substitutes.items():
                write_entry(work, p, e)
            # A second read of private consumer paths must still see authenticated
            # inputs despite replacement of actor-workdir paths at the boundary.
            assert {p: sha(v) for p, v in paths.items()} == actual
        return actual

    if case.name == "alfworld":
        def replay(path, actions, budget):
            consume({next(iter(case.payloads)): Path(path)})
            return {"won": False, "records": []}
        monkeypatch.setattr(check.gym_env, "replay", replay)
    elif case.name == "bird_minidev":
        def connect(path):
            consume({"database.sqlite": Path(path)})
            return SimpleNamespace(close=lambda: None)
        def query(conn, sql):
            calls.append({"gold.sql": hashlib.sha256(sql.encode()).hexdigest()})
            return []
        monkeypatch.setattr(check.sqlite3, "connect", connect)
        monkeypatch.setattr(check, "run_query", query)
    elif case.name == "ds1000":
        def process(argv, **kwargs):
            program = json.loads(Path(argv[-1]).read_text())
            original = json.loads(case.payloads["context.json"]["content"])["code_context"]
            foreign = json.loads(case.substitutes["context.json"]["content"])["code_context"]
            calls.append({"program_context": "selected" if program.startswith(original) else "foreign" if program.startswith(foreign) else "unknown"})
            csv_root = Path(kwargs["env"]["SEABORN_DATA"])
            csv_paths = {p: csv_root / Path(p).name for p in case.payloads if p.startswith("seaborn-data/")}
            consume(csv_paths)
            if replace_after:
                write_entry(work, "context.json", case.substitutes["context.json"])
                assert program.startswith(original)
            return subprocess.CompletedProcess(argv, 0, json.dumps({"passed": False, "result": "w-tbi2 spy; no execution"}), "")
        monkeypatch.setattr(check.subprocess, "run", process)
    elif case.name == "jericho":
        def game(root, **kwargs):
            paths = {case.module.GAME_FILE: kwargs.get("config_path", Path(root) / case.module.GAME_FILE),
                     next(p for p in case.payloads if p != case.module.GAME_FILE): kwargs.get("rom_path", Path(root) / next(p for p in case.payloads if p != case.module.GAME_FILE))}
            consume(paths)
            return SimpleNamespace(get_max_score=lambda: 100)
        monkeypatch.setattr(check.jer_env, "load_game", game)
        # `replay` reports its steps *and* the crash that stopped it (w-jerlook). This stub
        # replays nothing and stops for no failure, which is what an empty log produces.
        monkeypatch.setattr(check.jer_env, "replay",
                            lambda *a: {"steps": [], "failure": None})
    elif case.name == "scienceworld":
        monkeypatch.setattr(check, "_point_at_the_jvm", lambda root: work)
        def task(root, **kwargs):
            consume({case.module.TASK_IN_WORKDIR: kwargs.get("config_path") or Path(root) / case.module.TASK_IN_WORKDIR,
                     "scienceworld.jar": kwargs.get("server_path") or work / "scienceworld.jar"})
            return SimpleNamespace(close=lambda: None, get_goal_progress=lambda: "w-tbi2 spy; no JVM")
        monkeypatch.setattr(check.scw_env, "load_task", task)
    elif case.name == "spreadsheetbench":
        monkeypatch.setattr(check, "workbook_has_formulas", lambda p: False)
        def compare(golden, candidate, instruction_type, answer_position):
            consume({"golden.xlsx": Path(golden)})
            calls.append({"answer_position": answer_position, "instruction_type": instruction_type})
            return False, "w-tbi2 spy; no workbook comparison"
        monkeypatch.setattr(check, "compare_workbooks", compare)
    else:
        # Missing solution still passes through released-test parsing and the
        # unchanged measured-zero branch. Spy on that branch instead of running
        # the upstream executor or generating a fabricated candidate program.
        measure = check._measure
        def measured(args, *values):
            calls.append({"test_count": values[2]})
            if replace_after:
                write_entry(work, "tests.json", case.substitutes["tests.json"])
            return measure(args, *values)
        monkeypatch.setattr(check, "_measure", measured)
    return calls


def invoke(case, work, monkeypatch, *, spec=None, substitute=None, replace_after=False, staged=False):
    if not staged:
        stage(case, work)
    if substitute:
        write_entry(work, substitute, case.substitutes[substitute])
    monkeypatch.chdir(work)
    check = load_check(case)
    calls = install_spies(case, check, work, monkeypatch, replace_after=replace_after)
    argv = (spec or case.spec)["argv"][2:]
    monkeypatch.setattr(sys, "argv", ["check.py", *argv])
    code = check.main() if case.name in ("bird_minidev", "ds1000", "livecodebench") else check.main(argv)
    evidence = json.loads((work / "verifier/evidence.json").read_text())
    return code, evidence, calls


def test_selected_spec_pins_every_actual_input(case):
    expected = {"task_id": case.task_id, "path": "native-inputs", "files": case.files,
                "sha256": digest_inventory(case.files)}
    print(json.dumps({"dataset": case.name, "selected": expected,
                      "foreign_task_id": case.foreign_task_id,
                      "substitution_sha256": case.foreign_files,
                      "substitution_sources": {p: e.get("from", "released-record inline projection") for p, e in case.substitutes.items()}}, sort_keys=True))
    assert case.spec.get("scorer_input") == expected
    assert set(case.files) <= entries(case.spec).keys()
    argv = case.spec["argv"]
    assert argv[argv.index("--task-id") + 1] == case.task_id
    assert argv[argv.index("--scorer-input-sha256") + 1] == expected["sha256"]
    assert json.loads(argv[argv.index("--scorer-input-files") + 1]) == case.files


def test_matching_check_records_consumed_input(case, tmp_path, monkeypatch):
    code, evidence, calls = invoke(case, tmp_path, monkeypatch)
    assert code in (0, 1)
    assert calls
    assert evidence.get("scorer_input") == {"task_id": case.task_id, "path": "native-inputs",
            "sha256": digest_inventory(case.files), "files": case.files,
            "expected_sha256": digest_inventory(case.files), "verified": True}


def test_each_foreign_payload_is_refused_before_boundary(case, tmp_path, monkeypatch):
    outcomes = []
    for index, path in enumerate(case.payloads):
        work = tmp_path / str(index)
        work.mkdir()
        with monkeypatch.context() as patch:
            code, evidence, calls = invoke(case, work, patch, substitute=path)
        print(json.dumps({"dataset": case.name, "case": "foreign-payload", "path": path,
                          "foreign_task_id": case.foreign_task_id if not ((case.name == "scienceworld" and path == "scienceworld.jar") or path.startswith("seaborn-data/")) else None,
                          "exit": code, "scorer_calls": len(calls), "measured": evidence.get("measured"),
                          "scorer_input": evidence.get("scorer_input")}, sort_keys=True))
        outcomes.append((code, evidence, calls, work))
    for code, evidence, calls, work in outcomes:
        assert code == 3
        assert evidence["measured"] is False
        assert "scorer input" in evidence["error"]
        assert not calls
        assert not (work / "verifier/reward.txt").exists()


def test_replacing_original_after_authentication_preserves_private_inputs(case, tmp_path, monkeypatch):
    code, evidence, calls = invoke(case, tmp_path, monkeypatch, replace_after=True)
    assert code in (0, 1)
    assert calls
    assert evidence.get("scorer_input", {}).get("files") == case.files
    assert evidence["scorer_input"]["verified"] is True
    assert all(sha(tmp_path / p) == case.foreign_files[p] for p in case.payloads)


@pytest.mark.parametrize("fault", ["missing", "foreign-task", "foreign-digest", "foreign-files", "unverified"])
def test_native_dispatch_refuses_broken_consumption_receipt(case, tmp_path, monkeypatch, fault):
    receipt = {**case.spec.get("scorer_input", {}), "expected_sha256": digest_inventory(case.files), "verified": True}
    if fault == "foreign-task":
        receipt["task_id"] = case.foreign_task_id
    elif fault == "foreign-digest":
        receipt["sha256"] = digest_inventory(case.foreign_files)
    elif fault == "foreign-files":
        receipt["files"] = case.foreign_files
    elif fault == "unverified":
        receipt["verified"] = False
    evidence = {} if fault == "missing" else {"scorer_input": receipt}
    monkeypatch.setattr(verifier, "_verify_inner", lambda *a, **kw: {"kind": "command", "score": 0.0, "passed": False, "evidence": evidence})
    result = verifier._verify(tmp_path, case.spec, "", sandbox=False, timeout_s=5, task_id=case.task_id)
    assert result.get("unmeasured")
    assert result.get("score") is None


def test_foreign_spec_cannot_be_used_for_selected_task(case, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(verifier, "_verify_inner", lambda *a, **kw: calls.append(True) or {"score": 0.0})
    result = verifier._verify(tmp_path, case.foreign, "", sandbox=False, timeout_s=5, task_id=case.task_id)
    assert result.get("unmeasured")
    assert result.get("score") is None
    assert not calls


def test_dispatch_requires_independent_selected_task(case, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(verifier, "_verify_inner", lambda *a, **kw: calls.append(True) or {"score": 0.0})
    result = verifier._verify(tmp_path, case.spec, "", sandbox=False, timeout_s=5)
    assert result.get("unmeasured")
    assert result.get("score") is None
    assert not calls


@pytest.mark.parametrize("mode", ["matching", "foreign-payload", "unbound-check"])
def test_real_materialization_check_and_dispatch(case, tmp_path, monkeypatch, mode):
    stage(case, tmp_path)
    spec = copy.deepcopy(case.spec)
    # Filter only runtime directories unused by boundary spies; all actual
    # scorer inputs, check scripts and helper files retain real materialization.
    spec["inputs"] = [e for e in spec["inputs"] if not ("from" in e and Path(e["from"]).is_dir())]
    # The sealed runtime requires sandbox=True; exercise identity binding on the
    # generic route that reaches this test's process boundary spy.
    spec.pop("native_runtime", None)
    if mode == "unbound-check":
        for flag in ("--task-id", "--scorer-input-sha256", "--scorer-input-files"):
            if flag in spec["argv"]:
                index = spec["argv"].index(flag)
                del spec["argv"][index:index + 2]
    results = []
    def process(argv, **kwargs):
        with monkeypatch.context() as patch:
            code, evidence, calls = invoke(case, tmp_path, patch, spec=spec, staged=True,
                    substitute=next(iter(case.payloads)) if mode == "foreign-payload" else None)
            results.append((code, evidence, calls))
        return subprocess.CompletedProcess(argv, code, "", "")
    monkeypatch.setattr(verifier.subprocess, "run", process)
    result = verifier._verify(tmp_path, spec, "", sandbox=False, timeout_s=5, task_id=case.task_id)
    code, evidence, calls = results[0]
    print(json.dumps({"dataset": case.name, "case": f"dispatch-{mode}", "exit": code,
                      "score": result.get("score"), "unmeasured": result.get("unmeasured"),
                      "scorer_calls": len(calls), "scorer_input": evidence.get("scorer_input")}, sort_keys=True))
    if mode == "matching":
        assert result.get("score") == 0.0
        assert not result.get("unmeasured")
        assert calls
    else:
        assert result.get("score") is None
        assert result.get("unmeasured")
        if mode == "foreign-payload":
            assert code == 3
            assert not calls
        else:
            assert calls
            assert evidence.get("scorer_input", {}).get("verified") is False


def test_ds1000_context_is_trusted_rematerialized_input(tmp_path, monkeypatch):
    module = importlib.import_module("data.datasets.ds1000")
    first, other = module.included_indices()[:2]
    spec = module.verify_for(first)
    selected = next(e for e in module.setup_for(first)["files"] if e["path"] == "context.json")
    foreign = next(e for e in module.setup_for(other)["files"] if e["path"] == "context.json")
    write_entry(tmp_path, "context.json", foreign)
    verifier._materialize(tmp_path, [e for e in spec["inputs"] if e["path"] == "context.json"], verifier.PLATFORM_ROOT)
    assert sha(tmp_path / "context.json") == entry_sha(selected)


def test_input_binding_preserves_scoring_valueerror(case, tmp_path):
    """An authentication wrapper must not turn scoring failures into refusals."""
    helper = importlib.import_module("data.scaffolds.scorer_input")
    for path, entry in case.payloads.items():
        write_entry(tmp_path, path, entry)
    args = SimpleNamespace(task_id=case.task_id,
                           scorer_input_sha256=digest_inventory(case.files),
                           scorer_input_files=json.dumps(case.files),
                           evidence_file=tmp_path / "verifier/evidence.json")
    def score(inputs, receipt):
        raise ValueError("w-tbi2 scoring failure sentinel")
    with pytest.raises(ValueError, match="scoring failure sentinel"):
        helper.run_bound(args, {p: tmp_path / p for p in case.payloads}, score)
