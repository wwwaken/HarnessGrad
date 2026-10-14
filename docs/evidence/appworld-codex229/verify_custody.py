#!/usr/bin/env python3
"""Verify this public-source projection offline; never import upstream code."""
import base64
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PIN = "66ad8099e12188ece0d3fe45e661dbc01880813b"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git_hash(kind, body):
    header = kind.encode() + b" " + str(len(body)).encode() + b"\0"
    return hashlib.sha1(header + body).hexdigest()


def main():
    manifest = load("source-provenance.json")
    require(manifest["source_commit"] == PIN, "source pin changed")
    for name, expected in manifest["inventory_sha256"].items():
        require(Path(name).name == name, "inventory must stay in this directory")
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        require(actual == expected, f"SHA-256 mismatch: {name}")

    tag = load("tag-v0.1.3.post1-api.json")
    release = load("release-v0.1.3.post1-api.json")
    commit = load("commit-api.json")
    require(tag["ref"] == "refs/tags/v0.1.3.post1", "wrong tag")
    require(tag["object"]["type"] == "tag", "unexpected tag object")
    require(tag["object"]["sha"] == "efac79081936323733f68fd78260dab6981f195a",
            "annotated tag changed")
    advertised = dict(line.split()[::-1] for line in (ROOT / "tag-ls-remote.txt").read_text().splitlines())
    require(advertised == {"refs/tags/v0.1.3.post1": tag["object"]["sha"],
                           "refs/tags/v0.1.3.post1^{}": PIN}, "peeled tag mismatch")
    require(load("tag-ls-remote-receipt.json")["exit_code"] == 0, "failed ref acquisition")
    require(commit["sha"] == PIN, "wrong commit metadata")
    require(release["tag_name"] == "v0.1.3.post1", "wrong release")
    require(release["html_url"] == manifest["release_url"], "wrong release origin")

    trees = {}
    for prefix, name in [("", "root"), ("src", "src"),
                         ("src/appworld", "appworld"),
                         ("src/appworld/common", "common")]:
        tree = load(f"tree-{name}-api.json")
        require(tree.get("truncated") is False, f"truncated tree: {name}")
        # Git orders tree entries as if directory names end in '/'.
        entries = sorted(tree["tree"], key=lambda e: (
            e["path"] + ("/" if e["type"] == "tree" else "")).encode())
        body = b"".join(
            e["mode"].lstrip("0").encode() + b" " + e["path"].encode()
            + b"\0" + bytes.fromhex(e["sha"]) for e in entries)
        require(git_hash("tree", body) == tree["sha"], f"tree hash mismatch: {name}")
        trees[prefix] = tree
    require(commit["commit"]["tree"]["sha"] == trees[""]["sha"], "root tree mismatch")
    for parent, component, child in [("", "src", "src"),
                                     ("src", "appworld", "src/appworld"),
                                     ("src/appworld", "common", "src/appworld/common")]:
        entry = next(e for e in trees[parent]["tree"] if e["path"] == component)
        require(entry["type"] == "tree" and entry["sha"] == trees[child]["sha"],
                f"directory linkage mismatch: {child}")

    for row in manifest["public_files"]:
        body = (ROOT / row["path"]).read_bytes()
        api = load(row["path"] + ".contents-api.json")
        source = Path(row["source_path"])
        entry = next(e for e in trees[str(source.parent) if str(source.parent) != "." else ""]["tree"]
                     if e["path"] == source.name)
        require(entry["type"] == "blob", f"not a blob: {source}")
        require(git_hash("blob", body) == row["git_blob_sha"] == api["sha"] == entry["sha"],
                f"blob linkage mismatch: {source}")
        require(api["path"] == row["source_path"], f"contents path mismatch: {source}")
        require(base64.b64decode(api["content"]) == body, f"contents bytes mismatch: {source}")
        require(hashlib.sha256(body).hexdigest() == row["sha256"], f"source digest mismatch: {source}")
    print(f"PASS: {len(manifest['inventory_sha256'])} pinned files; 4 Git trees; "
          f"{len(manifest['public_files'])} public code/docs blobs; no upstream code executed")


if __name__ == "__main__":
    main()
