"""Offline original-source identity and synthetic semantics; no adapter/data import."""
from __future__ import annotations

import ast
import hashlib
import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from tests.quality.test_triviaqa_official_scorer import read_upstream_fixture

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/triviaqa_upstream"
COMMIT = "ca43b5820b107f3970cf4b7d67f7db7a98117b79"
SOURCE_SHA256 = "51785a3bc2e02a8f1ebf9db3aa18834c6a5daa5089ee5d435c99e0babf4be682"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("source provenance tests are offline")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


def git_hash(kind, content):
    return hashlib.sha1(kind.encode() + b" " + str(len(content)).encode()
                        + b"\0" + content).hexdigest()


def tree_entries(content):
    """Read acquired Git tree bytes, without fetching any referenced payload."""
    entries = {}
    offset = 0
    while offset < len(content):
        end = content.index(b"\0", offset)
        mode, name = content[offset:end].split(b" ", 1)
        object_id = content[end + 1:end + 21]
        assert len(object_id) == 20
        entries[name.decode()] = (mode.decode(), object_id.hex())
        offset = end + 21
    assert offset == len(content)
    return entries


def test_acquired_source_commit_tree_license_and_helpers():
    source = read_upstream_fixture()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA256
    receipt = json.loads((FIXTURE / "provenance.json").read_text())
    assert receipt["commit"] == COMMIT
    assert receipt["license_spdx"] == "Apache-2.0"
    assert receipt["acquisition"]["method"] == "github_git_objects"
    for name, pins in receipt["evidence"].items():
        path = FIXTURE / name
        assert path.resolve().is_relative_to(FIXTURE.resolve())
        content = path.read_bytes()
        assert hashlib.sha256(content).hexdigest() == pins["sha256"], name
        if "git_object_type" in pins:
            assert git_hash(pins["git_object_type"], content) == pins["git_object_sha1"]

    commit = (FIXTURE / "evidence/commit.git").read_bytes()
    assert git_hash("commit", commit) == COMMIT
    api_commit = json.loads((FIXTURE / "evidence/git_commit_response.json").read_text())
    assert api_commit["sha"] == COMMIT
    # Recover signed commit bytes from GitHub's payload/signature; no PGP claim.
    verification = api_commit["verification"]
    header, message = verification["payload"].split("\n\n", 1)
    signature = "gpgsig " + verification["signature"].replace("\n", "\n ")
    assert (header + "\n" + signature + "\n\n" + message).encode() == commit
    root_tree = (FIXTURE / "evidence/root_tree.git").read_bytes()
    assert commit.splitlines()[0] == b"tree " + git_hash("tree", root_tree).encode()
    roots = tree_entries(root_tree)
    subtrees = {}
    for directory in ("evaluation", "utils"):
        content = (FIXTURE / f"evidence/{directory}_tree.git").read_bytes()
        assert roots[directory] == ("40000", git_hash("tree", content))
        subtrees[directory] = tree_entries(content)
        assert subtrees[directory]["__init__.py"] == (
            "100644", "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")
    assert "NOTICE" not in roots
    assert set(receipt["files"]) == {
        "evaluation/triviaqa_evaluation.py", "utils/dataset_utils.py",
        "utils/utils.py", "LICENSE", "requirements.txt"}
    for name, pins in receipt["files"].items():
        parent, _, basename = name.rpartition("/")
        entries = subtrees[parent] if parent else roots
        assert entries[basename] == ("100644", pins["git_blob_sha1"])
        assert pins["source_url"] == f'{receipt["repository"]}/blob/{COMMIT}/{name}'
    license_text = (FIXTURE / "LICENSE").read_text()
    assert "Version 2.0, January 2004" in license_text
    assert "Copyright 2017 Kenton Lee" in license_text
    commit_response = json.loads((FIXTURE / "evidence/commit_response.json").read_text())
    assert commit_response["sha"] == COMMIT
    assert any(receipt["license_statement"]["text"] in entry.get("patch", "")
               for entry in commit_response["files"] if entry["filename"] == "README.md")


def test_original_evaluator_import_closure_is_stdlib_and_acquired_helpers():
    read_upstream_fixture()
    imports = set()
    for name in ("evaluation/triviaqa_evaluation.py", "utils/dataset_utils.py",
                 "utils/utils.py"):
        for node in ast.walk(ast.parse((FIXTURE / name).read_bytes())):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module)
    assert imports == {"__future__", "collections", "string", "re", "sys",
                       "argparse", "utils.dataset_utils", "utils.utils", "utils", "json"}
    assert (FIXTURE / "requirements.txt").read_text().splitlines() == [
        "tensorflow>=0.11", "nltk", "tqdm", "jinja2"]


def test_unmodified_full_source_on_synthetic_inputs(tmp_path):
    read_upstream_fixture()
    # A fresh interpreter avoids collisions with unrelated local 'utils' modules.
    # -I/-S/-B disable environment/site imports and fixture bytecode writes.
    code = r'''
import contextlib, copy, io, json, pathlib, runpy, socket, sys
def no_network(*args, **kwargs):
    raise AssertionError("network forbidden in original-source synthetic test")
socket.socket.connect = no_network
socket.socket.connect_ex = no_network
socket.create_connection = no_network
fixture, temporary = map(pathlib.Path, sys.argv[1:])
sys.path.insert(0, str(fixture))
from evaluation import triviaqa_evaluation as evaluator
from utils import dataset_utils

gold = {"NormalizedAliases": ["fictional azure city"],
        "HumanAnswers": ["The Invented Blue Town!"]}
assert evaluator.normalize_answer("The_A-Team") == "team"
assert evaluator.normalize_answer("don't") == "don t"
assert evaluator.normalize_answer("red’blue") == "red blue"
assert evaluator.exact_match_score("Invented Blue Town", "The Invented Blue Town!")
assert evaluator.f1_score("fictional azure", "fictional azure city") == 0.8
assert evaluator.f1_score("", "") == 0
try:
    evaluator.metric_max_over_ground_truths(evaluator.exact_match_score, "", [])
except ValueError:
    pass
else:
    raise AssertionError("empty alias reduction must retain upstream ValueError")
metrics = evaluator.evaluate_triviaqa(
    {"synthetic-q1": gold, "synthetic-q2": gold},
    {"synthetic-q1": "Invented Blue Town", "extra": "ignored"}, mute=True)
assert metrics == {"exact_match": 50.0, "f1": 50.0, "common": 1,
                   "denominator": 2, "pred_len": 2, "gold_len": 2}

def page(name, verified):
    return {"Filename": name, "DocPartOfVerifiedEval": verified}
data = {"Version": 1.0, "Domain": "Web", "VerifiedEval": False, "Data": [
    {"QuestionId": "synthetic-q1", "Answer": gold,
     "QuestionPartOfVerifiedEval": True,
     "EntityPages": [page("doc-a", True)],
     "SearchResults": [page("doc-b", False), page("doc-a", True)]},
    {"QuestionId": "synthetic-q2", "Answer": gold,
     "QuestionPartOfVerifiedEval": False,
     "EntityPages": [], "SearchResults": [page("doc-c", True)]}]}
web_gold = dataset_utils.get_key_to_ground_truth(data)
assert set(web_gold) == {"synthetic-q1--doc-a", "synthetic-q1--doc-b", "synthetic-q2--doc-c"}
assert evaluator.evaluate_triviaqa(web_gold, {"synthetic-q1--doc-a": "Invented Blue Town"},
                                 mute=True)["denominator"] == 3
wiki = copy.deepcopy(data)
wiki["Domain"] = "Wikipedia"
assert set(dataset_utils.get_key_to_ground_truth(wiki)) == {"synthetic-q1", "synthetic-q2"}
for row in wiki["Data"]:
    row["EntityPages"] = row["SearchResults"] = []
assert len(dataset_utils.get_key_to_ground_truth(wiki)) == 2
web_without_context = copy.deepcopy(wiki)
web_without_context["Domain"] = "Web"
assert dataset_utils.get_key_to_ground_truth(web_without_context) == {}

data["VerifiedEval"] = True
dataset_file = temporary / "synthetic-dataset.json"
dataset_file.write_text(json.dumps(data))
filtered = dataset_utils.read_triviaqa_data(str(dataset_file))
assert set(dataset_utils.get_key_to_ground_truth(filtered)) == {"synthetic-q1--doc-a"}
wiki["VerifiedEval"] = True
dataset_file.write_text(json.dumps(wiki))
filtered_wiki = dataset_utils.read_triviaqa_data(str(dataset_file))
assert set(dataset_utils.get_key_to_ground_truth(filtered_wiki)) == {"synthetic-q1"}
# The CLI selects a supplied file, with no config, context, or split argument.
prediction_file = temporary / "synthetic-predictions.json"
prediction_file.write_text(json.dumps({"synthetic-q1": "Invented Blue Town"}))
sys.argv = [str(fixture / "evaluation/triviaqa_evaluation.py"),
            "--dataset_file", str(dataset_file), "--prediction_file", str(prediction_file)]
output = io.StringIO()
with contextlib.redirect_stdout(output):
    runpy.run_path(sys.argv[0], run_name="__main__")
assert "'exact_match': 100.0" in output.getvalue()
assert "'f1': 100.0" in output.getvalue()
print("original-source synthetic checks passed")
'''
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-B", "-c", code, str(FIXTURE), str(tmp_path)],
        cwd=tmp_path, text=True, capture_output=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "original-source synthetic checks passed"
