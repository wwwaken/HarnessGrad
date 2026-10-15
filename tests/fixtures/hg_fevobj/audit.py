#!/usr/bin/env python3
"""Check response custody and enumerate only newly received metadata, offline."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
LOADER_COMMIT = "1776db7e9abab525eae8e59c5015e3589dfe371b"
TREE_COMMIT = "ad8321607bcad0e534c243ec8c108a5787cea6c8"


def read_json(path):
    return json.loads(path.read_text())


def write_json(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def verify_bytes(path, receipt):
    body = path.read_bytes()
    assert len(body) == receipt["bytes"], path
    assert hashlib.sha256(body).hexdigest() == receipt["sha256"], path


def main():
    plans = [item for plan in sorted(ROOT.glob("plan-*.json")) for item in read_json(plan)]
    assert len({item[0] for item in plans}) == len(plans)
    receipts = []
    hops = []
    for name, url, proxy in plans:
        path = ROOT / (name + ".request.json")
        row = read_json(path)
        assert row["url"] == url and row["proxy"] == (proxy or None)
        if row["body"] is not None:
            verify_bytes(ROOT / row["body"], row)
        else:
            assert row["status"] is None and row["bytes"] is None and row["sha256"] is None
            assert row.get("error"), path
        for index, hop in enumerate(row["redirects"]):
            body = bytes.fromhex(hop["body_hex"])
            target = ROOT / (name + ".redirect-" + str(index) + ".body")
            if target.exists():
                assert target.read_bytes() == body
            else:
                target.write_bytes(body)
            verify_bytes(target, hop)
            hops.append(dict(request=name, body=target.name, status=hop["status"],
                             url=hop["url"], bytes=hop["bytes"], sha256=hop["sha256"]))
        receipts.append(row)
    assert {p.stem.removesuffix(".request") for p in ROOT.glob("*.request.json")} == {x[0] for x in plans}
    index = ["# w-fevobj — complete request inventory", "",
             "Generated offline from plans and immutable per-attempt receipts. No new requests.", ""]
    for row in receipts:
        index.extend(["## " + row["name"], "", "Command: " + row["command"],
                      "", "Exact URL: " + row["url"], "",
                      "Receipt: tests/fixtures/hg_fevobj/" + row["name"] + ".request.json:1",
                      "", "Proxy: " + str(row["proxy"]) + "; exact request headers: "
                      + json.dumps(row["request_headers"], sort_keys=True), "",
                      "Final HTTP status: " + json.dumps(row["status"]) + "; response bytes: "
                      + json.dumps(row["bytes"]) + "; response SHA-256: "
                      + (row["sha256"] or "null") + ".", ""])
        if row["body"]:
            index.extend(["Raw response: tests/fixtures/hg_fevobj/" + row["body"] + "", ""])
        else:
            index.extend(["No HTTP response/body observed. Exact error: " + row["error"], ""])
        for hop in (x for x in hops if x["request"] == row["name"]):
            index.extend(["Automatically followed redirect: " + json.dumps(hop, sort_keys=True),
                          "", "All redirect headers, location and lossless body hex: same request receipt.", ""])
    (ROOT / "requests.md").write_text("\n".join(index))

    prior = REPO / "tests/fixtures/hg_fevhub"
    tree_name = "hub-tree-" + LOADER_COMMIT + "-retry"
    prior_receipt = read_json(prior / (tree_name + ".request.json"))
    verify_bytes(prior / (tree_name + ".body"), prior_receipt)
    entry = next(x for x in read_json(prior / (tree_name + ".body"))
                 if x["path"] == "fever_gold_evidence.py")
    loader = next(x for x in receipts if x["name"] == "loader-resolve-download-proxy")
    assert loader["status"] == 200 and loader["bytes"] == entry["size"]
    blob = subprocess.check_output(["git", "hash-object", str(ROOT / loader["body"])],
                                   cwd=REPO, text=True).strip()
    assert blob == entry["oid"]
    headers = dict((k.lower(), v) for k, v in loader["response_headers"])
    assert headers["x-repo-commit"] == LOADER_COMMIT
    assert headers["etag"].strip('"') == blob

    generated = next(x for x in receipts if x["name"] == "generated-tree-expand-proxy")
    assert generated["status"] == 200 and ("/tree/" + TREE_COMMIT + "?") in generated["url"]
    gh = dict((k.lower(), v) for k, v in generated["response_headers"])
    assert "link" not in gh, "Pagination requires further retrieval"
    tree = read_json(ROOT / generated["body"])
    assert len({x["path"] for x in tree}) == len(tree)
    assert all(x["type"] in ("directory", "file") for x in tree)
    assert any(x["lastCommit"]["id"] == TREE_COMMIT for x in tree)
    files = [x for x in tree if x["type"] == "file"]
    paths = [x["path"] for x in files]
    assert sorted(paths) == [".gitattributes", "default/test/0000.parquet",
                             "default/test/index.duckdb", "default/train/0000.parquet",
                             "default/validation/0000.parquet"]
    write_json("object-bindings.json", dict(
        loader=dict(state="FOUND", commit=LOADER_COMMIT, tree_receipt=str((prior / (tree_name + ".request.json")).relative_to(REPO)),
                    tree_entry=entry, response=loader["body"], response_sha256=loader["sha256"], git_blob_sha1_observed=blob),
        generated_tree=dict(state="FOUND", commit=TREE_COMMIT, response=generated["body"],
                            response_sha256=generated["sha256"], binding="HTTPS commit-addressed API response; no local Git commit/tree recomputation",
                            pagination_link_observed=False, returned_entries=tree),
        redirect_bodies=hops,
        producing_execution_receipt=dict(state="ABSENT", scope="Full recovered loader text and generated API listing/headers; listed binary payloads and .gitattributes body not read",
                                         historical_values="UNKNOWN")))
    summary = dict(valid=True, request_attempts=len(receipts),
                   final_http_200=sum(x["status"] == 200 for x in receipts),
                   no_http_response=sum(x["status"] is None for x in receipts),
                   redirect_http_responses=len(hops), loader_bytes=loader["bytes"],
                   loader_git_blob_sha1=blob, generated_tree_bytes=generated["bytes"],
                   generated_tree_entries=len(tree), generated_tree_files=len(files),
                   generated_tree_directories=len(tree) - len(files), generated_file_paths=paths)
    write_json("audit-summary.json", summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
