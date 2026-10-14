"""Derive metadata-only review facts; never imports adapters or opens external files."""
import ast
import base64
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(relative):
    return json.loads((HERE / relative).read_bytes())


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_digest(kind, data):
    return hashlib.sha1(kind.encode() + b" " + str(len(data)).encode() + b"\0" + data).hexdigest()


def literals(path):
    result = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    try:
                        result[target.id] = ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        pass
    return result


def tree_digest(entries):
    ordered = sorted(entries, key=lambda e: (e["path"] + ("/" if e["type"] == "tree" else "")).encode())
    data = b"".join(
        (("40000" if e["mode"] == "040000" else e["mode"]) + " " + e["path"]).encode()
        + b"\0" + bytes.fromhex(e["sha"]) for e in ordered)
    return git_digest("tree", data)


def build():
    # Each response hop is individually pinned; failures have no invented body hash.
    responses = []
    for directory in sorted(HERE.iterdir()):
        receipt_file = directory / "receipt.json"
        if not receipt_file.is_file():
            continue
        for index, receipt in enumerate(json.loads(receipt_file.read_bytes())):
            record = dict(receipt, acquisition=directory.name, hop=index)
            if "status" in receipt:
                body = directory / f"hop-{index}.body"
                headers = directory / f"hop-{index}.headers"
                assert receipt["complete"] is True
                assert len(body.read_bytes()) == receipt["bytes"]
                assert sha256(body.read_bytes()) == receipt["sha256"]
                assert sha256(headers.read_bytes()) == receipt["headers_sha256"]
                record["body_path"] = str(body.relative_to(ROOT))
            responses.append(record)

    ujson_tree = load("ujson-source-tree/hop-0.body")
    ujson_commit = load("ujson-immutable-commit/hop-0.body")
    assert ujson_commit["sha"] == ujson_tree["sha"] == "59875e089937c8b05c2f4b474530e3a9ec706a56"
    assert not ujson_tree["truncated"]
    assert tree_digest([e for e in ujson_tree["tree"] if "/" not in e["path"]]) == ujson_commit["tree"]["sha"]
    prefix = "deps/double-conversion/"
    vendored = [{**e, "path": e["path"][len(prefix):]} for e in ujson_tree["tree"]
                if e["path"].startswith(prefix) and "/" not in e["path"][len(prefix):]]
    assert tree_digest(vendored) == "629e1ff9b56216eb1423941ad615573354a857e4"

    lcb_tree = json.loads((ROOT / "docs/task-198-livecodebench-evidence/github-pinned-tree.json").read_bytes())
    twowiki_tree = json.loads((ROOT / "tests/fixtures/twowikimultihopqa_upstream_codex197/git-tree.json").read_bytes())
    source_specs = {
        "twowiki-upstream-readme": (twowiki_tree, "README.md", "README.upstream.md"),
        "ujson-license": (ujson_tree, "LICENSE.txt", "decoded.source"),
        "ujson-setup": (ujson_tree, "setup.py", "decoded.source"),
        "ujson-double-conversion-license": (ujson_tree, "deps/double-conversion/LICENSE", "decoded.source"),
        "lcb-loader": (lcb_tree, "lcb_runner/benchmarks/code_generation.py", "decoded.source"),
        "lcb-executor": (lcb_tree, "lcb_runner/evaluation/testing_util.py", "decoded.source"),
        "lcb-metrics": (lcb_tree, "lcb_runner/evaluation/compute_code_generation_metrics.py", "decoded.source"),
        "lcb-pass-k": (lcb_tree, "lcb_runner/evaluation/pass_k_utils.py", "decoded.source"),
        "lcb-license": (lcb_tree, "LICENSE", "decoded.source"),
    }
    sources = {}
    for name, (tree, upstream_path, local_path) in source_specs.items():
        response = load(f"{name}/hop-0.body")
        decoded = base64.b64decode(response["content"], validate=False)
        entry = next(e for e in tree["tree"] if e["path"] == upstream_path)
        assert git_digest("blob", decoded) == entry["sha"] == response["sha"]
        assert len(decoded) == entry["size"]
        assert (HERE / name / local_path).read_bytes() == decoded
        sources[name] = dict(upstream_path=upstream_path, git_blob_sha1=entry["sha"],
                             sha256=sha256(decoded), bytes=len(decoded))

    twowiki = literals(ROOT / "data/datasets/twowikimultihopqa.py")
    lcb = literals(ROOT / "data/datasets/livecodebench.py")
    for name, adapter, files in (
        ("twowiki", twowiki, {"data/dev.json": twowiki["DATA_SHA256"], "data/id_aliases.json": twowiki["ALIAS_SHA256"]}),
        ("lcb", lcb, lcb["_FILES"]),
    ):
        metadata = load(f"{name}-hub-proxy-revision/hop-0.body")
        assert metadata["sha"] == adapter["REVISION"]
        siblings = {entry["rfilename"]: entry for entry in metadata["siblings"]}
        for path, digest in files.items():
            assert siblings[path]["lfs"]["sha256"] == digest
        loader_name = "2wikimultihopqa.py" if name == "twowiki" else "code_generation_lite.py"
        folder = "twowiki-hub-proxy-loader" if name == "twowiki" else "lcb-hub-proxy-builder"
        code = (HERE / folder / "hop-1.body").read_bytes()
        assert git_digest("blob", code) == siblings[loader_name]["blobId"]
        sources[folder] = dict(upstream_path=loader_name, git_blob_sha1=git_digest("blob", code), sha256=sha256(code), bytes=len(code))

    pyproject = (HERE / "lcb-pyproject-proxy/hop-0.body").read_bytes()
    assert git_digest("blob", pyproject) == next(e["sha"] for e in lcb_tree["tree"] if e["path"] == "pyproject.toml")
    witness = load("twowiki-hub-proxy-witness/hop-0.body")
    assert witness["sha"] == twowiki["WITNESS_REVISION"]
    assert next(e for e in witness["siblings"] if "validation-" in e["rfilename"])["lfs"]["sha256"] == twowiki["WITNESS_SHA256"]

    receipt_dir = HERE / "preserved-receipts"
    custody = load("preserved-receipts/custody.json")
    for item in custody["files"]:
        data = (receipt_dir / item["path"]).read_bytes()
        assert sha256(data) == item["sha256"] and len(data) == item["bytes"]
    imposed_split = load("preserved-receipts/twowiki-imposed-split.json")
    split_digest = sha256(json.dumps({side: sorted(imposed_split[side]) for side in ("train", "eval")}, sort_keys=True).encode())
    runs = {}
    for kind in ("original", "recovery"):
        curve = load(f"preserved-receipts/twowiki-{kind}-curve.jsonl")
        meta = load(f"preserved-receipts/twowiki-{kind}-run-meta.json")
        selected = curve["sampling"]["task_ids"]
        assert curve["run_id"] == meta["run_id"]
        assert meta["split_sha"] == split_digest
        assert curve["split"] == meta["split"] == imposed_split
        assert set(selected) <= set(imposed_split["train"])
        assert curve["n_scored"] == len(curve["per_task"]) == len(curve["per_task_trials"])
        assert all(len(values) == curve["n_trials"] == meta["trials"] for values in curve["per_task_trials"].values())
        assert sum(curve["per_task"].values()) / curve["n_scored"] == curve["score"]
        runs[kind] = dict(
            run_id=curve["run_id"], selected_count=len(selected), scored_tasks=curve["n_scored"],
            recorded_trial_values=sum(map(len, curve["per_task_trials"].values())),
            trials_per_scored_task=curve["n_trials"], invalid_tasks=curve["n_invalid"],
            historical_score=curve["score"], harness_sha=curve["identity"]["harness_sha"],
            platform_content_sha=meta["platform"]["content_sha"], platform_dirty=meta["platform"]["dirty"],
            recorded_evaluation_trials=curve["cost"]["evaluation_trials"],
            agent_endpoint=meta["config"]["agent"]["base_url"], jobs=meta["jobs"],
            split_sha256=split_digest, selected_ids_sha256_json_compact=sha256(json.dumps(selected, separators=(",", ":")).encode()),
            per_trial_metric_identity_bound=False, immutable_image_bound=False, trusted_cleanup_bound=False,
        )
    original = load("preserved-receipts/twowiki-original-curve.jsonl")
    recovery = load("preserved-receipts/twowiki-recovery-curve.jsonl")
    assert set(recovery["sampling"]["task_ids"]) == set(original["invalid"])
    assert set(original["per_task"]).isdisjoint(recovery["per_task"])
    assert set(original["per_task"]) | set(recovery["per_task"]) == set(original["sampling"]["task_ids"])
    launch = load("preserved-receipts/lcb-smoke-launch.json")
    assert launch["launch_executed"] is False and launch["H0_authorized"] is False

    policies = json.loads((ROOT / "data/aggregation_policies.json").read_bytes())
    review = dict(
        schema_version=1, scope="b6 metadata/code and preserved receipts only",
        responses=responses, sources=sources, preserved_receipts=custody,
        twowiki_runs=runs,
        denominator_policies={name: policies[name] for name in ("twowikimultihopqa", "musique", "livecodebench")},
        disposition={
            "twowikimultihopqa/hub-data-provenance": "partial closure; canonical Hub artifact hashes established; rights, original-release hash/alias completeness and selected-manifest custody remain external",
            "twowikimultihopqa/ujson-native-offline-closure": "partial closure; exact vendored tree/license acquired and supplemental notices carried; supported image/native runtime remain external",
            "twowikimultihopqa/recovery-comparability": "review closed; original and recovery are separately identified; comparable combined official metric rejected",
            "livecodebench/row-attestation": "partial closure; canonical Hub release metadata/builder acquired; local row/catalog/pool/split custody and reviewer approval remain external",
            "livecodebench/smoke-scorer-comparability": "review closed; external-process variant remains incomparable; no historical smoke promoted to official execution",
        },
        production_authorized=False, model_calls=0, benchmark_execution=False,
        payload_access=False, historical_receipts_rewritten=False,
    )
    (HERE / "review.json").write_text(json.dumps(review, indent=2) + "\n")
    print("Verified responses, Git blob/tree linkage, canonical Hub pins, and separate preserved run coverage.")


if __name__ == "__main__":
    build()
