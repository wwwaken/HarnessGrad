"""Offline source-integrity and fabricated-input tests; no dataset adapter import.

Run with --basetemp=/tmp/harnessgrad-pytest-twowikimultihopqa-codex197-pytest. Missing source,
license or real ujson fails the gate; nothing is fetched or substituted at runtime.
"""
from __future__ import annotations

import ast
import builtins
import hashlib
import importlib.metadata
import json
import shutil
import socket
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/twowikimultihopqa_upstream_codex197"
COMMIT = "209e761834d1ce055856fc11072c0a5aab47601d"
TREE = "545a956af257f0c79c68c39a358086de7cbf243b"
SOURCES = ("2wikimultihop_evaluate.py", "2wikimultihop_evaluate_v1.1.py")
# Independently acquired bytes, not digests of a local scorer transcription.
PINS = {
    SOURCES[0]: "854b03c487608286d6381379eb32e46d9b845493527d1fe1951d0bf4ec923a40",
    SOURCES[1]: "7c09ee2ec98c7ecb57df79eb68dba22eb381ab58d50e730dfcefafb4dda31458",
    "LICENSE": "b8c1d7752e71597a45121774b6be93df38a81e1b748be15c063c0759f11e00ea",
    "requirements.txt": "16b0bfa1bcdd38c02a0897294846d54f272273e3c7c1201ff73c6a34da4f63bf",
    "git-tree.json": "98a1aa3e453f5ba6b177140381eab7c5d8a2ac6f2c2587aa00952cb625003ebf",
    "git-commit.json": "122564355d667bec2675336633819a8c4df95262cb388332258072d2687add8b",
}


def git_digest(kind, content):
    return hashlib.sha1(kind.encode() + b" " + str(len(content)).encode()
                        + b"\0" + content).hexdigest()


def read_fixture(directory=FIXTURE):
    """Verify the commit/tree/blob chain and license before any source execution."""
    receipt = json.loads((directory / "provenance.json").read_bytes())
    assert receipt["schema_version"] == 1
    assert receipt["repository"] == "https://github.com/Alab-NII/2wikimultihop"
    assert receipt["commit"] == COMMIT and receipt["root_tree"] == TREE
    assert receipt["primary_evaluator"] == SOURCES[1]
    assert receipt["original_evaluator"] == SOURCES[0]
    assert receipt["license"]["path"] == "LICENSE"
    assert receipt["license"]["spdx"] == "Apache-2.0"
    assert receipt["acquisition"]["method"] == "github_git_blob_api"
    assert receipt["acquisition"]["commit_api"].endswith("/git/commits/" + COMMIT)
    assert receipt["acquisition"]["tree_api"].endswith("/git/trees/" + TREE)
    assert set(receipt["files"]) == set(PINS)
    assert {p.name for p in directory.iterdir()} == set(PINS) | {"README.md", "provenance.json"}
    contents = {}
    for name, expected in PINS.items():
        content = (directory / name).read_bytes()
        assert hashlib.sha256(content).hexdigest() == expected, name
        assert receipt["files"][name]["sha256"] == expected, name
        assert receipt["files"][name]["bytes"] == len(content), name
        contents[name] = content
    commit = json.loads(contents["git-commit.json"])
    tree = json.loads(contents["git-tree.json"])
    assert commit["sha"] == COMMIT and commit["tree"]["sha"] == tree["sha"] == TREE
    assert tree["truncated"] is False
    ordered = sorted(tree["tree"], key=lambda e: (
        e["path"] + ("/" if e["type"] == "tree" else "")).encode())
    tree_bytes = b"".join(
        (("40000" if e["mode"] == "040000" else e["mode"]) + " " + e["path"]).encode()
        + b"\0" + bytes.fromhex(e["sha"]) for e in ordered)
    assert git_digest("tree", tree_bytes) == TREE
    entries = {e["path"]: e for e in tree["tree"]}
    for name in (*SOURCES, "LICENSE", "requirements.txt"):
        blob = git_digest("blob", contents[name])
        assert blob == entries[name]["sha"] == receipt["files"][name]["git_blob_sha1"]
        assert entries[name]["size"] == len(contents[name])
    return contents


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("network access is forbidden in the offline code-only gate")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


@pytest.fixture(params=SOURCES, ids=("original", "v1.1"))
def upstream(request):
    content = read_fixture()[request.param]
    assert importlib.metadata.version("ujson") == "5.10.0", "install the pinned real dependency"
    namespace = {"__name__": "_twowiki_upstream_codex197", "__file__": str(FIXTURE / request.param)}
    # Compile the entire exact source, preserving its real ujson import and all functions.
    exec(compile(content, namespace["__file__"], "exec"), namespace)
    return request.param, namespace


def fabricated_row(identifier="SYNTHETIC-197-A"):
    return {"_id": identifier, "answer": "fictional azure", "answer_id": "SYNTHETIC-Q197",
            "supporting_facts": [["Synthetic Document A", 0], ["Synthetic Document B", 1]],
            "evidences": [["invented subject", "imaginary relation", "fabricated object"]],
            "evidences_id": []}


def perfect_prediction(row):
    return {"answer": {row["_id"]: row["answer"]},
            "sp": {row["_id"]: row["supporting_facts"]},
            "evidence": {row["_id"]: row["evidences"]}}


def evaluate(upstream, tmp_path, monkeypatch, capsys, rows, predictions, aliases=()):
    name, namespace = upstream
    gold = tmp_path / "SYNTHETIC-gold.json"
    prediction = tmp_path / "SYNTHETIC-prediction.json"
    alias = tmp_path / "SYNTHETIC-alias.jsonl"
    gold.write_text(json.dumps(rows), encoding="utf-8")
    prediction.write_text(json.dumps(predictions), encoding="utf-8")
    alias.write_text("".join(json.dumps(a) + "\n" for a in aliases), encoding="utf-8")
    allowed = {p.resolve() for p in (gold, prediction, alias)}
    original_open = builtins.open

    def synthetic_only_open(file, mode="r", *args, **kwargs):
        assert Path(file).resolve() in allowed, "evaluator attempted a non-synthetic read"
        assert mode == "r", "evaluator attempted a write"
        return original_open(file, mode, *args, **kwargs)

    with monkeypatch.context() as guard:
        guard.setattr(builtins, "open", synthetic_only_open)
        args = [str(prediction), str(gold)]
        if name == SOURCES[1]:
            args.append(str(alias))
        namespace["eval"](*args)
    output = capsys.readouterr().out
    return json.loads(output[output.index("{"):])


def test_exact_source_license_and_commit_tree_provenance():
    assert len(read_fixture()) == 6


@pytest.mark.parametrize("name", PINS)
def test_source_license_and_metadata_drift_fail_closed(name, tmp_path):
    target = tmp_path / "fixture"
    shutil.copytree(FIXTURE, target)
    path = target / name
    path.write_bytes(path.read_bytes() + b"\nSYNTHETIC-DRIFT\n")
    with pytest.raises(AssertionError, match=name):
        read_fixture(target)


def test_missing_license_fails_closed(tmp_path):
    target = tmp_path / "fixture"
    shutil.copytree(FIXTURE, target)
    (target / "LICENSE").unlink()
    with pytest.raises(AssertionError):
        read_fixture(target)


def test_dependency_import_closure():
    contents = read_fixture()
    receipt = json.loads((FIXTURE / "provenance.json").read_bytes())
    for name in SOURCES:
        parsed = ast.parse(contents[name])
        imports = {n.module.split(".")[0] for n in parsed.body if isinstance(n, ast.ImportFrom)}
        imports.update(a.name.split(".")[0] for n in parsed.body if isinstance(n, ast.Import) for a in n.names)
        version_key = "stdlib_v1_1" if name == SOURCES[1] else "stdlib_v1_0"
        assert imports == set(receipt["dependencies"][version_key]) | {"ujson"}
    assert contents["requirements.txt"].decode().splitlines() == ["spacy", "tqdm", "ujson", "torch==1.1.0", "joblib"]
    assert importlib.metadata.version("ujson") == "5.10.0"
    assert not importlib.metadata.requires("ujson"), "new transitive dependency needs review"
    dependency = receipt["dependencies"]["external_runtime"]["ujson"]
    assert dependency["version"] == "5.10.0" and dependency["runtime_requires_dist"] == []
    metadata = receipt["dependencies"]["release_artifact_metadata"]
    assert metadata["payloads_fetched"] is False and metadata["requires_dist"] is None
    assert {a["filename"]: a["digests"]["sha256"] for a in metadata["artifacts"]} == {
        "ujson-5.10.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl":
            "f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1",
        "ujson-5.10.0.tar.gz": "b3cd8f3c5d8c7738257f1018880444f7b7d9b66232c64649f562d7ba86ad4bc1",
    }


def test_existing_transcription_region_matches_without_importing_adapter():
    source = read_fixture()[SOURCES[1]].decode()
    region = source[source.index("def normalize_answer(s):"):source.index("if __name__ == '__main__':")]
    adapter = (ROOT / "data/twowikimultihopqa.py").read_text(encoding="utf-8")
    assert adapter.count(region) == 1
    # This proves only the transcribed region, not wrapper behavior or any dataset identity.


@pytest.mark.parametrize("prediction,gold,expected", [
    ("The Fictional Azure!", "fictional azure", (1.0, 1.0, 1.0)),
    ("invented invented azure", "invented azure", (0.8, 2 / 3, 1.0)),
    ("yes", "yes invented", (0, 0, 0)),
    ("invented no", "no", (0, 0, 0)),
    ("", "", (0, 0, 0)),
])
def test_answer_f1_normalization_multiset_and_sentinel_rules(upstream, prediction, gold, expected):
    assert upstream[1]["f1_score"](prediction, gold) == pytest.approx(expected)


def test_joint_f1_is_harmonic_mean_of_product_precision_recall(upstream, tmp_path, monkeypatch, capsys):
    row = fabricated_row()
    prediction = perfect_prediction(row)
    prediction["answer"][row["_id"]] = "fictional"
    prediction["sp"][row["_id"]] = row["supporting_facts"][:1]
    prediction["evidence"][row["_id"]] = row["evidences"] + [["wrong subject", "wrong relation", "wrong object"]]
    metrics = evaluate(upstream, tmp_path, monkeypatch, capsys, [row], prediction)
    assert len(metrics) == 16
    assert (metrics["f1"], metrics["sp_f1"], metrics["evi_f1"]) == (66.67, 66.67, 66.67)
    assert (metrics["joint_prec"], metrics["joint_recall"], metrics["joint_f1"]) == (50.0, 25.0, 33.33)
    assert metrics["joint_f1"] != round((2 / 3) ** 3 * 100, 2)


@pytest.mark.parametrize("channel", ("answer", "sp", "evidence"))
def test_missing_channel_disables_joint_without_changing_denominator(upstream, tmp_path, monkeypatch, capsys, channel):
    row = fabricated_row()
    prediction = perfect_prediction(row)
    prediction[channel] = {}
    metrics = evaluate(upstream, tmp_path, monkeypatch, capsys, [row], prediction)
    assert metrics["joint_em"] == metrics["joint_f1"] == 0
    assert metrics["f1"] == (0 if channel == "answer" else 100)


def test_gold_denominator_and_extra_prediction_ids(upstream, tmp_path, monkeypatch, capsys):
    row = fabricated_row()
    missing = fabricated_row("SYNTHETIC-197-MISSING")
    prediction = perfect_prediction(row)
    prediction["answer"]["SYNTHETIC-EXTRA"] = "ignored"
    metrics = evaluate(upstream, tmp_path, monkeypatch, capsys, [row, missing], prediction)
    assert set(metrics.values()) == {50.0}


def test_empty_support_and_evidence_have_em_one_f1_zero(upstream, tmp_path, monkeypatch, capsys):
    row = fabricated_row()
    row["supporting_facts"] = row["evidences"] = []
    metrics = evaluate(upstream, tmp_path, monkeypatch, capsys, [row], perfect_prediction(row))
    assert metrics["f1"] == metrics["joint_em"] == 100
    assert metrics["sp_f1"] == metrics["evi_f1"] == metrics["joint_f1"] == 0


def test_v1_1_aliases_and_demonyms_are_version_specific(upstream, tmp_path, monkeypatch, capsys):
    row = fabricated_row()
    row["evidences_id"] = [["SYNTHETIC-S", "imaginary relation", "SYNTHETIC-O"]]
    prediction = perfect_prediction(row)
    prediction["answer"][row["_id"]] = "synthetic azurefolk"
    prediction["evidence"][row["_id"]] = [["subject alias", "imaginary relation", "object alias"]]
    aliases = [
        {"Q_id": "SYNTHETIC-Q197", "aliases": ["invented teal village"], "demonyms": ["synthetic azurefolk"]},
        {"Q_id": "SYNTHETIC-S", "aliases": ["subject alias"], "demonyms": []},
        {"Q_id": "SYNTHETIC-O", "aliases": ["object alias"], "demonyms": []},
    ]
    metrics = evaluate(upstream, tmp_path, monkeypatch, capsys, [row], prediction, aliases)
    expected = 100 if upstream[0] == SOURCES[1] else 0
    assert metrics["f1"] == metrics["evi_f1"] == metrics["joint_f1"] == expected


def test_v1_1_answer_alias_maxima_are_independent(upstream, tmp_path, monkeypatch, capsys):
    row = fabricated_row()
    row["answer"] = "invented"
    prediction = perfect_prediction(row)
    prediction["answer"][row["_id"]] = "invented azure"
    aliases = [{"Q_id": "SYNTHETIC-Q197", "aliases": ["invented azure teal"], "demonyms": []}]
    metrics = evaluate(upstream, tmp_path, monkeypatch, capsys, [row], prediction, aliases)
    if upstream[0] == SOURCES[1]:
        assert metrics["f1"] == 80 and metrics["prec"] == metrics["recall"] == 100
        assert metrics["joint_f1"] == 100
    else:
        assert metrics["f1"] == metrics["joint_f1"] == 66.67


def test_v1_1_evidence_alias_alternatives_can_exceed_one(upstream, tmp_path, monkeypatch, capsys):
    row = fabricated_row()
    row["evidences_id"] = [["SYNTHETIC-S", "imaginary relation", "SYNTHETIC-O"]]
    prediction = perfect_prediction(row)
    prediction["evidence"][row["_id"]] = row["evidences"] + [["subject alias", "imaginary relation", "fabricated object"]]
    aliases = [{"Q_id": "SYNTHETIC-S", "aliases": ["subject alias"], "demonyms": []}]
    metrics = evaluate(upstream, tmp_path, monkeypatch, capsys, [row], prediction, aliases)
    if upstream[0] == SOURCES[1]:
        assert metrics["evi_recall"] == 200
        assert metrics["evi_f1"] == metrics["joint_f1"] == 133.33
    else:
        assert metrics["evi_f1"] == metrics["joint_f1"] == 66.67
