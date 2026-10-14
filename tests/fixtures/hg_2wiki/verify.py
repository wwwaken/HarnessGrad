"""Offline custody checks and derived findings, without adapters or dataset access."""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = "2c82417955798e6f00474bcbf49a80c4811d8df1"
B6 = "reports/b6-blocker-evidence/"
INPUTS = [
    B6 + "twowiki-upstream-readme/README.upstream.md",
    B6 + "twowiki-upstream-current-readme/hop-0.body",
    B6 + "twowiki-hub-proxy-revision/hop-0.body",
    B6 + "twowiki-hub-proxy-tree/hop-0.body",
    B6 + "twowiki-hub-proxy-loader/hop-1.body",
    B6 + "twowiki-hub-proxy-witness/hop-0.body",
    "tests/fixtures/upstream_provenance_e2/comparison.json",
    "tests/fixtures/upstream_provenance_e2/twowiki-later-download-followup-head/hop-0.headers",
    "tests/fixtures/twowikimultihopqa_upstream_codex197/LICENSE",
    "data/datasets/twowikimultihopqa.py",
    "data/scaffolds/qa/base.py",
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def derive():
    inputs = []
    for path in INPUTS:
        raw = (ROOT / path).read_bytes()
        assert raw == subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT), path
        inputs.append(dict(path=path, bytes=len(raw), sha256=sha(raw)))
    responses = []
    for directory in sorted(p for p in HERE.iterdir() if p.is_dir()):
        for index, hop in enumerate(read(directory / "receipt.json")):
            assert "error" not in hop and hop["complete"] is True
            body = (directory / f"hop-{index}.body").read_bytes()
            headers = (directory / f"hop-{index}.headers").read_bytes()
            assert len(body) == hop["bytes"] and sha(body) == hop["sha256"]
            assert sha(headers) == hop["headers_sha256"]
            assert hop["transport_proxy"] == "http://172.17.0.1:17890"
            assert hop["tls_certificate_validation"] is True
            responses.append(dict(body_path=str((directory / f"hop-{index}.body").relative_to(ROOT)), **hop))
    license_response = read(HERE / "current-repository-license/hop-0.body")
    license_bytes = base64.b64decode(license_response["content"])
    assert license_bytes == (HERE / "current-repository-license/LICENSE.decoded").read_bytes()
    assert license_bytes == (ROOT / INPUTS[8]).read_bytes()
    assert blob(license_bytes) == license_response["sha"] == "342ce459a34de236d05b2be3f01e5f08f6c712e8"
    assert license_response["license"]["spdx_id"] == "Apache-2.0"
    witness_meta = read(ROOT / INPUTS[5])
    card = (HERE / "witness-card/hop-1.body").read_bytes()
    assert blob(card) == next(s["blobId"] for s in witness_meta["siblings"] if s["rfilename"] == "README.md")
    assert witness_meta["sha"] == "fe713bfbd1afbca1a65246741a75890405d56a3a"
    assert not any(s["rfilename"] == "LICENSE" for s in witness_meta["siblings"])
    text = card.decode()
    frontmatter_counts = [int(n) for n in re.findall(r"num_examples: (\d+)", text.split("---")[1])]
    prose_counts = [int(n.replace(",", "")) for n in re.findall(r"^\| (?:train|validation|test)\s*\|\s*([\d,]+) \|", text, re.M)]
    assert frontmatter_counts == [167454, 12576, 12576]
    assert prose_counts == [113284, 12981, 12995] and prose_counts != frontmatter_counts
    paper = subprocess.check_output(["pdftotext", "-layout", str(HERE / "publisher-paper/hop-0.body"), "-"])
    assert paper == (HERE / "publisher-paper/extracted.txt").read_bytes()
    paper_text = paper.decode()
    paper_counts = []
    for name in ("train-medium", "train-hard", "dev", "test"):
        count = re.search(r"^\s*" + name + r"\s+(?:train|dev|test)\s+([\d,]+)", paper_text, re.M)
        paper_counts.append(int(count[1].replace(",", "")))
    assert paper_counts == [154878, 12576, 12576, 12576]
    assert sum(paper_counts) == 192606 and "Total                         192,606" in paper_text
    page = (HERE / "original-share-page/hop-0.body").read_text()
    assert "<title>Dropbox - Error - Simplify your life</title>" in page
    assert '"edison_page_name":"shared_link_disabled"' in page
    hub = read(ROOT / INPUTS[2])
    artifacts = {s["rfilename"]: s["lfs"] for s in hub["siblings"] if "lfs" in s}
    prior = read(ROOT / INPUTS[6])["twowikimultihopqa"]
    for name, selection in prior["historical_selections"].items():
        compact = json.dumps(selection["selected_task_ids"], separators=(",", ":")).encode()
        assert sha(compact) == selection["selected_ids_sha256_json_compact"]
        assert selection["raw_artifact_binding_authenticated"] is False
    return dict(
        base_commit=BASE, inherited_inputs=inputs, responses=responses,
        repository_license=dict(spdx="Apache-2.0", sha256=sha(license_bytes),
                                blob_sha1=blob(license_bytes), explicit_dataset_alias_grant_obtained=False),
        original_share_page="shared_link_disabled; HTTP 200 HTML error, not an archive",
        paper_claimed_examples=dict(zip(["train-medium", "train-hard", "dev", "test"], paper_counts)),
        paper_claimed_total_examples=sum(paper_counts),
        witness_card=dict(git_blob_sha1=blob(card), frontmatter_examples=frontmatter_counts,
                          prose_examples=prose_counts, counts_conflict=True,
                          apache_2_claim="mirror assertion; no explicit original alias-file grant"),
        hub_advertised_artifacts=artifacts,
        historical_selections=prior["historical_selections"],
        original_release_content_digest_obtained=False,
        original_release_member_digest_mapping_obtained=False,
        alias_id_coverage_attested=False, selected_manifest_linkage_authenticated=False,
        human_approval_required=False, blocker_status="external",
        benchmark_execution=False, dataset_payload_access=False, production_authorized=False,
    )


def scope():
    old = json.loads(subprocess.check_output(["git", "show", f"{BASE}:docs/dataset-blockers.json"], cwd=ROOT))
    new = read(ROOT / "docs/dataset-blockers.json")
    normalized = copy.deepcopy(new)
    before = next(d for d in old["datasets"] if d["dataset"] == "twowikimultihopqa")
    after = next(d for d in normalized["datasets"] if d["dataset"] == "twowikimultihopqa")
    a = next(b for b in before["blockers"] if b["id"] == "hub-data-provenance")
    b = next(b for b in after["blockers"] if b["id"] == "hub-data-provenance")
    assert b["status"] == a["status"] == "external"
    assert b["evidence"][:len(a["evidence"])] == a["evidence"]
    for key in ("observed", "next_action", "evidence"):
        b[key] = a[key]
    assert normalized == old, "Unrelated registry change"
    journal = "docs/adapter-integration-journal.md"
    previous = subprocess.check_output(["git", "show", f"{BASE}:{journal}"], cwd=ROOT)
    current = (ROOT / journal).read_bytes()
    assert current.startswith(previous) and current[len(previous):].count(b" - w-2wiki\n") == 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    evidence = derive()
    scope()
    if args.write:
        (HERE / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
        files = sorted(p for p in HERE.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
        (HERE / "SHA256SUMS").write_text("".join(f"{sha(p.read_bytes())}  {p.relative_to(HERE)}\n" for p in files))
    else:
        assert read(HERE / "evidence.json") == evidence
        expected = set()
        for line in (HERE / "SHA256SUMS").read_text().splitlines():
            digest, path = line.split("  ", 1)
            assert sha((HERE / path).read_bytes()) == digest, path
            expected.add(path)
        actual = {str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file() and p.name != "SHA256SUMS"}
        assert actual == expected
    print(json.dumps(dict(valid=True, raw_responses=len(evidence["responses"]),
                          inherited_inputs=len(evidence["inherited_inputs"]),
                          paper_claimed_examples=evidence["paper_claimed_total_examples"],
                          witness_counts_conflict=True, blocker_status="external",
                          human_approval_required=False, dataset_payload_access=False,
                          registry_scope="only target observed/next_action and appended evidence",
                          journal="append only")))
