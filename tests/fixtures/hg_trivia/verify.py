#!/usr/bin/env python3
"""Offline byte custody and metadata comparisons; no acquired code is executed."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESPONSES = HERE / "responses"
PRIOR = ROOT / "tests/fixtures/external_provenance_b5/responses"
PAIRS = {
    "hub-revision": "triviaqa-mirror-revision",
    "hub-root-tree": "triviaqa-mirror-tree",
    "hub-selected-tree": "triviaqa-selected-tree",
    "hub-commits": "triviaqa-mirror-commits",
    "hub-discussion-8": "triviaqa-conversion-discussion",
    "hub-predecessor-tree": "triviaqa-predecessor-tree",
    "hub-input-tree": "triviaqa-input-tree",
    "hub-predecessor-loader": "triviaqa-predecessor-loader",
    "hub-added-selected-tree": "triviaqa-added-tree",
    "hub-initial-commits": "triviaqa-conversion-initial-commits",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def git_hash(kind, content):
    return hashlib.sha1(kind.encode() + b" " + str(len(content)).encode() + b"\0" + content).hexdigest()


def body(name):
    return (RESPONSES / f"{name}.body").read_bytes()


def parsed(name):
    return json.loads(body(name))


def review():
    receipts = sorted(RESPONSES.glob("*.receipt.json"))
    require(len(receipts) == 13, "expected 13 preserved requests")
    for path in receipts:
        receipt = json.loads(path.read_bytes())
        require(receipt["status"] == 200, f"unsuccessful response: {path.name}")
        require(receipt["url"] == receipt["response_url"], "unexpected redirect")
        require(receipt["url"].startswith(("https://huggingface.co/", "https://raw.githubusercontent.com/")), "unexpected origin")
        require(receipt["proxy"] == "http://172.17.0.1:17890", "unexpected proxy")
        content = (RESPONSES / receipt["body"]).read_bytes()
        require(len(content) == receipt["size_bytes"], f"response size: {path.name}")
        require(sha256(content) == receipt["sha256"], f"response hash: {path.name}")
        require(sha256((RESPONSES / receipt["headers"]).read_bytes()) == receipt["headers_sha256"], "headers hash")
    comparisons = []
    for current, previous in PAIRS.items():
        require(body(current) == (PRIOR / f"{previous}.body").read_bytes(), f"mirror mismatch: {current}")
        comparisons.append({"origin_response": current, "prior_mirror_response": previous,
                            "recomputed_sha256": sha256(body(current)), "byte_identical": True})
    revision = parsed("hub-revision")
    require(revision["sha"] == "0f7faf33a3908546c6fd5b73a660e0f8ff173c2f", "wrong revision")
    card = revision["cardData"]
    config = next(x for x in card["configs"] if x["config_name"] == "rc.nocontext")
    info = next(x for x in card["dataset_info"] if x["config_name"] == "rc.nocontext")
    root = parsed("hub-root-tree")
    recursive = parsed("hub-recursive-tree")
    require("\nlink:" not in (RESPONSES / "hub-recursive-tree.headers").read_text().lower(), "pagination must be followed")
    require(len(recursive) == 150, "recursive tree changed")
    paths = [x["path"] for x in recursive]
    require(len(set(paths)) == len(paths), "duplicate path")
    require([x for x in recursive if "/" not in x["path"]] == root, "root listing mismatch")
    subtree_hashes = {}
    for directory in [x for x in root if x["type"] == "directory"]:
        name = directory["path"]
        entries = [x for x in recursive if str(Path(x["path"]).parent) == name]
        content = b"".join(b"100644 " + Path(x["path"]).name.encode() + b"\0" + bytes.fromhex(x["oid"])
                           for x in sorted(entries, key=lambda x: x["path"]))
        computed = git_hash("tree", content)
        require(computed == directory["oid"], f"incomplete or inconsistent directory: {name}")
        subtree_hashes[name] = computed
    selected = parsed("hub-selected-tree")
    require([x for x in recursive if str(Path(x["path"]).parent) == "rc.nocontext"] == selected, "selected tree mismatch")
    root_bytes = b"".join((b"40000" if x["type"] == "directory" else b"100644") + b" "
                          + x["path"].encode() + b"\0" + bytes.fromhex(x["oid"])
                          for x in sorted(root, key=lambda x: x["path"] + ("/" if x["type"] == "directory" else "")))
    # These are reconstructed canonical LFS pointers, NOT fetched payload bytes.
    for entry in recursive:
        if "lfs" in entry:
            pointer = ("version https://git-lfs.github.com/spec/v1\n"
                       f"oid sha256:{entry['lfs']['oid']}\nsize {entry['lfs']['size']}\n").encode()
            require(len(pointer) == entry["lfs"]["pointerSize"], "pointer size mismatch")
            require(git_hash("blob", pointer) == entry["oid"], "pointer blob mismatch")
    loader = body("hub-predecessor-loader")
    loader_entry = next(x for x in parsed("hub-predecessor-tree") if x["path"] == "trivia_qa.py")
    require(git_hash("blob", loader) == loader_entry["oid"], "loader tree/blob mismatch")
    pins = {}
    for name, relative in {
        "upstream-scorer": "tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py",
        "upstream-license": "tests/fixtures/triviaqa_upstream/LICENSE",
    }.items():
        require(body(name) == (ROOT / relative).read_bytes(), f"upstream fixture mismatch: {name}")
        pins[name] = {"sha256": sha256(body(name)), "git_blob_sha1": git_hash("blob", body(name))}
    return {"http_200_responses": len(receipts), "mirror_comparisons": comparisons,
            "hub_revision": revision["sha"], "config": config, "declared_info": info,
            "recursive_entries": len(recursive), "root_tree_reconstructed_sha1": git_hash("tree", root_bytes),
            "subtree_hashes": subtree_hashes,
            "predecessor_loader": {"sha256": sha256(loader), "git_blob_sha1": git_hash("blob", loader)},
            "upstream_source_matches": pins,
            "adapter_sha256": sha256((ROOT / "data/datasets/triviaqa.py").read_bytes()),
            "execution_provenance": "not established by these metadata/source checks",
            "production_authorized": False}


if __name__ == "__main__":
    result = review()
    if sys.argv[1:] == ["--write-derived"]:
        directory = HERE / "views"
        directory.mkdir(exist_ok=True)
        for path in sorted(RESPONSES.glob("*.body")):
            try:
                value = json.loads(path.read_bytes())
            except (ValueError, UnicodeDecodeError):
                continue
            (directory / f"{path.stem}.json").write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
        (HERE / "review.json").write_text(json.dumps(result, indent=2) + "\n")
        print("Derived JSON views and review.json written from retained responses.")
    else:
        require(not sys.argv[1:], "only --write-derived is supported")
        require(json.loads((HERE / "review.json").read_bytes()) == result, "derived review changed")
        for path in (HERE / "views").glob("*.json"):
            require(json.loads(path.read_bytes()) == parsed(path.stem), f"derived view mismatch: {path.name}")
        print(json.dumps(result, indent=2))
