"""Offline byte, Git-tree, ordered-row and static scorer custody checks.

No adapter or upstream module is imported or executed. Installed source files are
checked against their preserved observation, not reread from mutable dataset roots.
"""
import ast
import base64
import copy
import csv
import hashlib
import io
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
E1 = REPO / "tests/fixtures/hg_e1_review"
REWOO_REVISION = "9cd0283043ff4be0c9d614fda2789d143ca6ffd1"
BIGBENCH_REVISION = "092b196c1f8f14a54bbc62f24759d43bde46dd3b"


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def git_sha(kind, raw):
    return hashlib.sha1(kind.encode() + b" " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def literal(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)


def function(tree, name):
    return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)


def verify_tree(path, commit_path, expected_revision):
    commit, tree = read_json(commit_path), read_json(path)
    assert commit["sha"] == expected_revision
    assert tree["sha"] == commit["commit"]["tree"]["sha"]
    assert tree["truncated"] is False
    by_path = {entry["path"]: entry for entry in tree["tree"]}
    assert len(by_path) == len(tree["tree"])
    children = {"": []}
    expected = {"": tree["sha"]}
    for entry in tree["tree"]:
        parent, _, basename = entry["path"].rpartition("/")
        children.setdefault(parent, []).append((basename, entry))
        if entry["type"] == "tree":
            children.setdefault(entry["path"], [])
            expected[entry["path"]] = entry["sha"]
    # Git sorts a directory as though its name ended in '/'. Reconstruct every
    # directory object from its immediate children, including the root object.
    for parent, entries in children.items():
        assert parent in expected
        raw = b"".join(
            entry["mode"].lstrip("0").encode() + b" " + basename.encode() + b"\0" + bytes.fromhex(entry["sha"])
            for basename, entry in sorted(entries, key=lambda item: (item[0] + ("/" if item[1]["type"] == "tree" else "")).encode())
        )
        assert git_sha("tree", raw) == expected[parent], parent
    return by_path, {"revision": expected_revision, "root_tree_sha1": tree["sha"], "reconstructed_trees": len(children)}


def contents(api_path, decoded_path, tree, revision):
    payload = read_json(api_path)
    raw = base64.b64decode(payload["content"])
    assert payload["encoding"] == "base64"
    assert len(raw) == payload["size"]
    assert raw == decoded_path.read_bytes()
    assert git_sha("blob", raw) == payload["sha"] == tree[payload["path"]]["sha"]
    assert revision in payload["download_url"]
    return raw, {"path": payload["path"], "size_bytes": len(raw), "sha256": sha256(raw), "git_blob_sha1": payload["sha"]}


class NormalizeStringContract(ast.NodeTransformer):
    """Compare normalizer ASTs after explicitly listed harmless string changes."""
    def visit_FunctionDef(self, node):
        node.returns = None
        for arg in node.args.args:
            arg.annotation = None
        if isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            node.body = node.body[1:]
        # Upstream caches punctuation in a local variable; adapter inlines it.
        if node.name == "remove_punc":
            assigns = [n for n in node.body if isinstance(n, ast.Assign)]
            if assigns:
                assert len(assigns) == 1 and ast.unparse(assigns[0]) == "exclude = set(string.punctuation)"
                node.body.remove(assigns[0])
        return self.generic_visit(node)

    def visit_Name(self, node):
        if node.id == "exclude":
            return ast.parse("set(string.punctuation)", mode="eval").body
        return node

    def visit_Call(self, node):
        node = self.generic_visit(node)
        # Adapter coerces s with str(s). For the documented string-only domain,
        # this is the identity. Do not claim equality on arbitrary object input.
        if isinstance(node.func, ast.Name) and node.func.id == "str":
            assert len(node.args) == 1 and isinstance(node.args[0], ast.Name) and node.args[0].id == "s"
            return node.args[0]
        return node


def verify():
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        assert sha256((ROOT / name).read_bytes()) == expected, name
    for reference in read_json(ROOT / "inherited-references.json"):
        raw = (REPO / reference["path"]).read_bytes()
        assert len(raw) == reference["size_bytes"] and sha256(raw) == reference["sha256"]
    failures = []
    for path in sorted(ROOT.glob("*.receipt.json")):
        receipt = read_json(path)
        raw = (ROOT / receipt["body"]).read_bytes()
        assert len(raw) == receipt["bytes"] and sha256(raw) == receipt["sha256"]
        if receipt["status"] is None:
            assert receipt["body_kind"] == "transport-failure-sentinel" and raw == b""
        else:
            assert receipt["body_kind"] == "http-response-body"
        if receipt["status"] != 200:
            failures.append({"receipt": path.name, "error": receipt["error"], "artifact_acquired": False})
    rewoo_tree, rewoo_identity = verify_tree(ROOT / "rewoo-tree.body", E1 / "rewoo-commit.body", REWOO_REVISION)
    bigbench_tree, bigbench_identity = verify_tree(ROOT / "bigbench-tree.body", E1 / "bigbench-head.body", BIGBENCH_REVISION)
    archive = (E1 / "rewoo-archive.body").read_bytes()
    archive_receipt = read_json(E1 / "rewoo-archive.receipt.json")
    assert archive_receipt["status"] == 200 and archive_receipt["sha256"] == sha256(archive)
    observations = read_json(ROOT / "installed-observations.json")
    for observation in observations:
        if observation["preserved_as"]:
            raw = (ROOT / observation["preserved_as"]).read_bytes()
            assert len(raw) == observation["size_bytes"] and sha256(raw) == observation["sha256"]
    summary = {"valid": True, "rewoo": rewoo_identity, "bigbench": bigbench_identity, "installed_archive_sha256": sha256(archive), "datasets": {}, "preserved_failed_requests": failures}
    mapping = [("physicsquestions", "physics_question.csv", "rewoo-physics-api", 53), ("strategyqa", "strategy_qa.csv", "rewoo-strategy-api", 2290), ("sportsunderstanding", "sports_understanding.csv", "rewoo-sports-api", 1000)]
    with tarfile.open(fileobj=io.BytesIO(archive)) as handle:
        evaluator, evaluator_identity = contents(ROOT / "rewoo-evaluator-api.body", ROOT / "rewoo-Evaluator.py", rewoo_tree, REWOO_REVISION)
        assert evaluator == handle.extractfile(f"ReWOO-{REWOO_REVISION}/utils/Evaluator.py").read() == (ROOT / "rewoo-evaluator-raw-proxy.body").read_bytes()
        for observation in observations:
            if observation["kind"] == "installed-declared-archive":
                assert observation["sha256"] == sha256(archive) and observation["size_bytes"] == len(archive)
            if observation["kind"] == "installed-unused-evaluator":
                assert observation["sha256"] == sha256(evaluator) and observation["size_bytes"] == len(evaluator)
        for name, member, api, expected_count in mapping:
            raw, identity = contents(ROOT / (api + ".body"), ROOT / ("installed-" + member), rewoo_tree, REWOO_REVISION)
            adapter = ast.parse((ROOT / ("adapter-" + name + ".py")).read_text())
            assert literal(adapter, "CSV_PATH") == f"ReWOO-{REWOO_REVISION}/data/bigbench/{member}"
            assert raw == handle.extractfile(literal(adapter, "CSV_PATH")).read()
            assert literal(adapter, "REWOO_SHA256") == sha256(archive)
            assert literal(adapter, "REWOO_COMMIT") == REWOO_REVISION
            rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"), newline="")))
            assert len(rows) == expected_count == literal(adapter, "N_TOTAL")
            imports = [ast.unparse(n) for n in adapter.body if isinstance(n, (ast.Import, ast.ImportFrom))]
            assert all("ReWOO" not in n and "bigbench" not in n and "pyarrow" not in n for n in imports)
            identity.update({"runtime_csv_path": f"/mnt/20t/xubuqiang/datasets/{name}/" + literal(adapter, "CSV_PATH"), "installed_bytes_match_archive_and_revision_blob": True, "row_count": len(rows), "adapter_imports": imports, "installed_evaluator_or_bigbench_package_used": False, "actual_selected_run_manifest_authenticated": False})
            summary["datasets"][name] = identity
    summary["rewoo_evaluator"] = evaluator_identity
    strategy = ast.parse((ROOT / "adapter-strategyqa.py").read_text())
    upstream = ast.parse(evaluator.decode())
    normalized = [NormalizeStringContract().visit(copy.deepcopy(function(t, "normalize_answer"))) for t in (strategy, upstream)]
    assert ast.dump(normalized[0], include_attributes=False) == ast.dump(normalized[1], include_attributes=False)
    metrics = function(upstream, "get_metrics")
    assigns = {n.targets[0].id: ast.unparse(n.value) for n in metrics.body if isinstance(n, ast.Assign)}
    assert assigns["norm_label"] == "normalize_answer(label)" and assigns["norm_pred"] == "normalize_answer(pred)" and assigns["em"] == "norm_pred == norm_label"
    assert ast.unparse(function(strategy, "exact_match").body[-1].value) == "normalize_answer(prediction) == normalize_answer(ground_truth)"
    summary["datasets"]["strategyqa"]["normalizer_ast_matches_for_string_inputs"] = True
    physics, physics_identity = contents(E1 / "bigbench-task-api.body", E1 / "bigbench-physics-task.json", bigbench_tree, BIGBENCH_REVISION)
    task = json.loads(physics)
    examples = [e for e in task["examples"] if e["input"].strip()]
    rows = list(csv.DictReader(io.StringIO((ROOT / "installed-physics_question.csv").read_text(), newline="")))
    assert len(rows) == len(examples) == 53 and len(task["examples"]) == 54
    for row, example in zip(rows, examples):
        assert row["input"] == example["input"]
        assert ast.literal_eval(row["target"][len("Can be one of "):]) == example["target"]
    summary["datasets"]["physicsquestions"]["bigbench_task"] = physics_identity
    summary["datasets"]["physicsquestions"]["ordered_bigbench_nonblank_pairs_match"] = 53
    sports, sports_identity = contents(ROOT / "bigbench-sports-api.body", ROOT / "bigbench-sports-task.json", bigbench_tree, BIGBENCH_REVISION)
    assert sports == (ROOT / "bigbench-sports-raw-proxy.body").read_bytes()
    task = json.loads(sports)
    assert task["metrics"] == ["multiple_choice_grade"] and task["preferred_score"] == "multiple_choice_grade"
    rows = list(csv.DictReader(io.StringIO((ROOT / "installed-sports_understanding.csv").read_text(), newline="")))
    assert len(rows) == len(task["examples"]) == 1000
    for row, example in zip(rows, task["examples"]):
        assert row["input"] == task["task_prefix"] + " " + example["input"]
        scores = example["target_scores"]
        assert set(scores) == {"plausible", "implausible"} and sorted(scores.values()) == [0, 1]
        assert row["target"] == max(scores, key=scores.get)
    source, scorer_identity = contents(E1 / "bigbench-metrics-api.body", E1 / "bigbench-task-metrics.py", bigbench_tree, BIGBENCH_REVISION)
    scorer = function(ast.parse(source.decode()), "measure_multiple_choice_grade")
    loop = next(n for n in scorer.body if isinstance(n, ast.For))
    assert ast.unparse(loop.body[0]) == "choice = sample['choice'][argmax(sample['log_prob'])]"
    assert ast.unparse(loop.body[1]) == "count += sample['target_scores'][choice]"
    summary["datasets"]["sportsunderstanding"].update({"bigbench_task": sports_identity, "ordered_bigbench_prefix_and_winner_pairs_match": 1000, "official_scorer": scorer_identity, "official_metric_uses_choice_logprob_argmax": True, "adapter_free_text_word_boundary_metric_equivalence_established": False})
    summary["hub_revision_or_export_bytes_used"] = False
    summary["production_runtime_or_offline_pristine_verifier_evidence_established"] = False
    return summary


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
