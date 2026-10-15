"""Offline routing controls for authenticated native config/ROM/JAR overrides.

The libraries are real; native constructors are spies. Every task/config value and
payload byte comes from provisioned local records. No engine or scorer executes.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import socket
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def denied(*_args, **_kwargs):
        raise AssertionError("network forbidden by engine-input routing controls")
    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "")


def library(name, filename):
    path = ROOT / "data" / "datasets" / name / "lib" / filename
    spec = importlib.util.spec_from_file_location(f"w_tbi2_paths_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def jericho_records():
    package = importlib.util.find_spec("jericho")
    assert package is not None and package.origin
    table = Path(package.origin).parent / "game_info.py"
    roms = Path("/mnt/20t/xubuqiang/datasets/jericho/z-machine-games-master/jericho-game-suite")
    records = []
    for node in ast.parse(table.read_text()).body:
        if not isinstance(node, ast.Assign):
            continue
        try:
            row = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            continue
        if isinstance(row, dict) and "rom" in row and (roms / row["rom"]).is_file():
            records.append((node.targets[0].id, row))
    records.sort(key=lambda item: item[0])
    selected, foreign = [row for _, row in records[:2]]
    return roms, selected, foreign


def jericho_config(row):
    return json.dumps({"task_id": Path(row["rom"]).stem, "rom": row["rom"],
                       "seed": int(row.get("seed") or 0)}).encode()


def scienceworld_records():
    fold = json.loads((ROOT / "data/datasets/scienceworld/test_fold.json").read_text())
    return fold["tasks"][:2]


def scienceworld_config(row):
    return json.dumps({"task_name": row["task_name"], "variation": row["variation"],
                       "simplifications": ""}).encode()


def world_jar():
    package = importlib.util.find_spec("scienceworld")
    assert package is not None and package.origin
    path = (Path(package.origin).parent / "scienceworld.jar").resolve()
    assert path.is_file()
    return path


def test_jericho_real_loader_consumes_config_and_rom_overrides(tmp_path, monkeypatch):
    lib = library("jericho", "jer_env.py")
    roms, selected, foreign = jericho_records()
    work = tmp_path / "work"
    private = tmp_path / "private"
    work.mkdir()
    private.mkdir()
    selected_config = private / lib.GAME_FILENAME
    selected_config.write_bytes(jericho_config(selected))
    (work / lib.GAME_FILENAME).write_bytes(jericho_config(foreign))
    selected_rom = private / selected["rom"]
    selected_rom.write_bytes((roms / selected["rom"]).read_bytes())
    (work / foreign["rom"]).write_bytes((roms / foreign["rom"]).read_bytes())
    consumed = {}
    sentinel = object()

    def make_env_spy(rom, *, seed):
        consumed.update(rom=Path(rom), bytes=Path(rom).read_bytes(), seed=seed)
        return sentinel

    monkeypatch.setattr(lib, "make_env", make_env_spy)
    print(json.dumps({"route": "jericho-real-loader", "selected_task": Path(selected["rom"]).stem,
                      "foreign_workdir_task": Path(foreign["rom"]).stem,
                      "selected_config": identity(selected_config.read_bytes()),
                      "selected_rom": identity(selected_rom.read_bytes()),
                      "expected_seed": int(selected.get("seed") or 0)}, sort_keys=True))
    result = lib.load_game(work, config_path=selected_config, rom_path=selected_rom)
    assert result is sentinel
    assert consumed == {"rom": selected_rom, "bytes": selected_rom.read_bytes(),
                        "seed": int(selected.get("seed") or 0)}


def test_scienceworld_real_loader_consumes_config_and_jar_overrides(tmp_path, monkeypatch):
    lib = library("scienceworld", "scw_env.py")
    selected, foreign = scienceworld_records()
    work = tmp_path / "work"
    private = tmp_path / "private"
    work.mkdir()
    private.mkdir()
    selected_config = private / lib.TASK_FILENAME
    selected_config.write_bytes(scienceworld_config(selected))
    (work / lib.TASK_FILENAME).write_bytes(scienceworld_config(foreign))
    jar = world_jar()
    consumed = {}

    class ConstructorSentinel:
        def load(self, name, variation, simplifications, *, generateGoldPath):
            consumed.update(name=name, variation=variation, simplifications=simplifications,
                            generate_gold=generateGoldPath)

    sentinel = ConstructorSentinel()

    def make_env_spy(workdir, *, step_budget, server_path=None):
        consumed.update(workdir=workdir, budget=step_budget, jar=server_path)
        return sentinel

    monkeypatch.setattr(lib, "make_env", make_env_spy)
    print(json.dumps({"route": "scienceworld-real-loader",
                      "selected_task": f"{selected['task_name']}/{selected['variation']}",
                      "foreign_workdir_task": f"{foreign['task_name']}/{foreign['variation']}",
                      "selected_config": identity(selected_config.read_bytes()),
                      "selected_jar": identity(jar.read_bytes())}, sort_keys=True))
    result = lib.load_task(work, config_path=selected_config, server_path=jar,
                           step_budget=lib.STEP_BUDGET)
    assert result is sentinel
    assert consumed == {"workdir": work, "budget": lib.STEP_BUDGET, "jar": jar,
                        "name": selected["task_name"], "variation": int(selected["variation"]),
                        "simplifications": "", "generate_gold": False}


def test_scienceworld_real_factory_forwards_explicit_jar_to_constructor(tmp_path, monkeypatch):
    lib = library("scienceworld", "scw_env.py")
    jar = world_jar()
    jre = Path("/mnt/20t/xubuqiang/datasets/scienceworld/jre") / lib.JRE_DIRNAME
    assert (jre / "bin/java").is_file()
    monkeypatch.setattr(lib, "java_home", lambda _work: jre)
    consumed = {}
    sentinel = object()

    def constructor_spy(task_name, server_path, *, envStepLimit):
        consumed.update(task_name=task_name, server_path=server_path, budget=envStepLimit)
        return sentinel

    fake_package = types.ModuleType("scienceworld")
    fake_package.ScienceWorldEnv = constructor_spy
    monkeypatch.setitem(sys.modules, "scienceworld", fake_package)
    print(json.dumps({"route": "scienceworld-real-factory", "selected_jar_path": str(jar),
                      "selected_jar": identity(jar.read_bytes()),
                      "declared_step_budget": lib.STEP_BUDGET}, sort_keys=True))
    result = lib.make_env(tmp_path, server_path=jar, step_budget=lib.STEP_BUDGET)
    assert result is sentinel
    assert consumed == {"task_name": "", "server_path": str(jar), "budget": lib.STEP_BUDGET}
