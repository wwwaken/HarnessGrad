# w-fevhub — public upstream producing-execution search

**ABSENT within the retrieved, enumerated scope:** no artifact was found binding the specific Hub export to its producing conversion execution, executable revision, invocation/environment, ID assignment, split/filter/omission decisions, and NEI input revision. **UNKNOWN beyond that scope:** this is not a claim of global nonexistence. Two specifically requested historical objects were not observable after repeated transport failures; they are listed below. The scope, requests and offline search are reproducible from `tests/fixtures/hg_fevhub/requests.md:1`, `tests/fixtures/hg_fevhub/scope.json:1`, and `tests/fixtures/hg_fevhub/search.json:1`.

A producing receipt must bind an executed conversion and its inputs/decisions to this export's output identity. A source declaration, uploaded blob, submodule pin, plausible ancestry, paper recipe, generic JSON loader, or later Parquet build does not supply that execution binding. This is the criterion used for every ABSENT statement here. The existing custody, group mapping, selected manifest and semantic findings are retained as prior evidence, not re-measured (`registry/dataset-blockers.json:348`; `tests/fixtures/hg_wsel/fever.json:1`). No scorer release/version is inferred from a dataset builder version.

## Acquisition and exact scope

Requests use public HTTPS with CA and hostname verification via `ssl.create_default_context()`, without account credentials or a TLS-verification bypass (`tests/fixtures/hg_fevhub/fetch.py:1`). The existing proxy is only an egress transport; source authority remains the HTTPS origin. Every instrumented request URL, HTTP status (or null when none was observed), response entity SHA-256, byte count, headers, redirects and observed UTC times are retained in the matching `.request.json`; `requests.md` indexes them all. A transport exception has no invented HTTP status or response digest. Three preliminary transport-only probes are recorded with their exact commands/errors in the validation ledger; none produced an HTTP response/body. HTTP 400/403 responses are retained and are not zero-result searches. Corrected Zenodo requests are separate receipts.

Exact acquisition commands were `python3 tests/fixtures/hg_fevhub/fetch.py tests/fixtures/hg_fevhub/plan-NN.json`, with the recorded `FEVHUB_PROXY` per batch; the concrete plans and exact outputs are in `registry/w-fevhub-validation.txt`. Offline command: `python3 tests/fixtures/hg_fevhub/audit.py`. It verifies response bytes/digests and decoded Git blob IDs, enumerates every history/tree/text object, and records its exact regex, enumerated file scope and line matches in `search.json`. Absence classification also uses reading the retrieved sources, not merely a keyword count.

Observed offline inventory (`tests/fixtures/hg_fevhub/audit-summary.json:1`; exact stdout in validation):

```json
{
  "http_requests": 226,
  "http_responses": 140,
  "http_200": 134,
  "transport_failures": 86,
  "main_commits": 33,
  "generated_only_commits": 26,
  "main_trees_found": 33,
  "generated_trees_found": 25,
  "hub_card_versions": 7,
  "hub_loader_versions": 4,
  "source_history_versions": {
    "create_nli_dataset-py": 4,
    "aggregate_papelo_nei-py": 3,
    "merge_nli_files-py": 1,
    "README-md": 10
  },
  "search_files": 56,
  "search_matching_lines": 283,
  "verified_base64_blobs": 21
}
```

## 1. Hub refs, export path and historical files

### FOUND — published refs and upload history, not producing execution

Source: `https://huggingface.co/api/datasets/copenlu/fever_gold_evidence/refs` — HTTP **200**, response SHA-256 `ded067e5f31d8e3d9eff8f00e733e59e3f5aa08e92ab792f6163d2b3c722cc9c`; `tests/fixtures/hg_fevhub/hub-refs-retry.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/hub-refs-retry.body:1`:

```text
{"tags":[],"branches":[{"name":"main","ref":"refs/heads/main","targetCommit":"a6b8d891d393e97a4efac791afffb2d7de5e57c6"}],"converts":[{"name":"parquet","ref":"refs/convert/parquet","targetCommit":"fdce48c93b0dd0b5fa2e33d40c8d6405a043cee5"}]}
```

Source: `https://huggingface.co/api/datasets/copenlu/fever_gold_evidence/commits/main` — HTTP **200**, response SHA-256 `fbc07fcbcc423a25c9164f5b432a4fae8d9268b2b76160a91a6798b647fbf33e`; `tests/fixtures/hg_fevhub/hub-commits.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/hub-commits.body:1`:

```text
"id":"a6b8d891d393e97a4efac791afffb2d7de5e57c6","title":"Upload 3 files","message":""
```

Source: `https://huggingface.co/api/datasets/copenlu/fever_gold_evidence/commits/main` — HTTP **200**, response SHA-256 `fbc07fcbcc423a25c9164f5b432a4fae8d9268b2b76160a91a6798b647fbf33e`; `tests/fixtures/hg_fevhub/hub-commits.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/hub-commits.body:1`:

```text
"id":"c85bd16b7a9cdfb7ccc2f6b03f5cb540f550f2b5","title":"Delete fever_gold_evidence.py","message":""
```

The main commit endpoint returned 33 entries with no next-page Link header. All 33 recursive trees were retrieved; their exact commit IDs, full messages, body filenames and entries are enumerated under `main_history` in `scope.json:1`. The union of paths is exactly `.gitattributes`, `README.md`, `fever_gold_evidence.py`, `train.jsonl`, `valid.jsonl`, `test.jsonl` (reproduce with `audit.py`; structural inventory in `scope.json:1`). No export payload was retrieved. The former Python file is a dataset loader, not a receipt recording an export-producing run:

Source: `https://huggingface.co/datasets/copenlu/fever_gold_evidence/raw/e715a7f0e9c6f585ec4a7f9e9bc9097ce17b8103/fever_gold_evidence.py` — HTTP **200**, response SHA-256 `ce60125f769038a360a85ba7af5d295f55c71a8a065f0401507576f93bc34a6f`; `tests/fixtures/hg_fevhub/hub-loader-e715a7f0e9c6f585ec4a7f9e9bc9097ce17b8103.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/hub-loader-e715a7f0e9c6f585ec4a7f9e9bc9097ce17b8103.body:83`:

```text
VERSION = datasets.Version("1.1.0")
```

Source: `https://huggingface.co/datasets/copenlu/fever_gold_evidence/raw/e715a7f0e9c6f585ec4a7f9e9bc9097ce17b8103/fever_gold_evidence.py` — HTTP **200**, response SHA-256 `ce60125f769038a360a85ba7af5d295f55c71a8a065f0401507576f93bc34a6f`; `tests/fixtures/hg_fevhub/hub-loader-e715a7f0e9c6f585ec4a7f9e9bc9097ce17b8103.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/hub-loader-e715a7f0e9c6f585ec4a7f9e9bc9097ce17b8103.body:145`:

```text
for key, row in enumerate(f):
                data = json.loads(row)
                yield key, data
```

### FOUND — old card recovered exactly from the public PR diff

Direct requests for the old card failed, but the complete old-file hunk in `https://huggingface.co/datasets/copenlu/fever_gold_evidence/discussions/1/files.diff` was retrieved (HTTP 200; response SHA-256 `4ecb31536a6c9352f5527fe336435f95f444553c1414191b6be101057c022989`; `tests/fixtures/hg_fevhub/hub-pr-diff.body:1`). `audit.py` preserves original CRLF bytes while removing diff prefixes, then verifies the recovered 5,352 bytes against the observed Git blob `4a5ce872c186404a8ebdc7f860479eaeec0a08b4`. Recovered SHA-256: `17e98ee1f0047aa9a7f1474e53f466d2272a789d96c668b8d10728ab91cb4f3e`; verbatim excerpt `tests/fixtures/hg_fevhub/hub-pr-diff.old-card.txt:72`: `[Needs More Information]`. This is source-byte recovery, not execution recovery. All seven distinct historical card blobs are now recovered (`scope.json:1` → `hub_text_objects`).

This loader enumerates example keys while yielding already existing JSON rows; the excerpt does not authenticate how the uploaded string IDs or `original_id` fields were assigned. Its `1.1.0` is a loader declaration, not a scorer release or an observed successful build (`hub-loader-e715a7f0e9c6f585ec4a7f9e9bc9097ce17b8103.body:83`, same source above).

### ABSENT — producing receipt in the retrieved Hub history/text scope

Scope: all 33 main commit messages and trees, the seven recovered distinct card blobs and four retrieved distinct loader blobs, the public refs response, Hub discussion listing and discussion #1 plus its diff. Exact per-object inventory: `scope.json:1` (`main_history`, `cards`, `loaders`, `hub_text_objects`); exact requests in plans 01/04/05/09/11/13/14/15. No receipt satisfying the defined execution binding is in these retrieved texts; the tree inventories contain no other script/metadata/receipt file path. This does not classify unreceived card/loader contents as absent.

### FOUND — dataset card and public metadata declarations

Source: `https://huggingface.co/datasets/copenlu/fever_gold_evidence/raw/main/README.md` — HTTP **200**, response SHA-256 `dc0584ae6c41d2c4c9184241d52992b1261de0e9c3557ccb33310abf49fef8bd`; `tests/fixtures/hg_fevhub/hub-card.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/hub-card.body:65`:

```text
For *NEI* claims, we extract evidence sentences with the system in "Christopher Malon. 2018. Team Papelo: Transformer Networks at FEVER.
```

Source: `https://huggingface.co/datasets/copenlu/fever_gold_evidence/raw/main/README.md` — HTTP **200**, response SHA-256 `dc0584ae6c41d2c4c9184241d52992b1261de0e9c3557ccb33310abf49fef8bd`; `tests/fixtures/hg_fevhub/hub-card.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/hub-card.body:88`:

```text
### Data Splits

[Needs More Information]
```

Source: `https://huggingface.co/api/datasets/copenlu/fever_gold_evidence?blobs=true` — HTTP **200**, response SHA-256 `f10e7a4ca1b60fd101ee72b7cf958bf06f5cf8f7757c007e170588a8a415f6eb`; `tests/fixtures/hg_fevhub/hub-metadata-full.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/hub-metadata-full.body:1`:

```text
"sha":"a6b8d891d393e97a4efac791afffb2d7de5e57c6"
```

### ABSENT — checked build-metadata filename

The exact current path `dataset_infos.json` returned HTTP 404, body `Entry not found`, response SHA-256 `f36668ddf22403a332f978057d527cf285b01468bc3431b04094a7bafa6aba59`, URL `https://huggingface.co/datasets/copenlu/fever_gold_evidence/raw/main/dataset_infos.json` (`tests/fixtures/hg_fevhub/hub-dataset-info.body:1`; `hub-dataset-info.request.json:1`). This is absence at that path, not absence of all server metadata.

## 2. Generated ref and datasets-server records

### FOUND — later generated artifacts and JSON-builder metadata

Source: `https://huggingface.co/api/datasets/copenlu/fever_gold_evidence/commits/refs%2Fconvert%2Fparquet` — HTTP **200**, response SHA-256 `e4576389f63786446a2d8e4475fc8e96b783174628fded69cb73226aa56dbbb0`; `tests/fixtures/hg_fevhub/hub-parquet-commits.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/hub-parquet-commits.body:1`:

```text
"id":"25edf9fb27b68317a9578b05c64d4ae3ef4b2b0d","title":"Update parquet files","message":""
```

Source: `https://datasets-server.huggingface.co/info?dataset=copenlu%2Ffever_gold_evidence` — HTTP **200**, response SHA-256 `a0342ee859fc4e9cf1a6a9f12795490b9c2eb89a78a7bda375bcb6451cd86534`; `tests/fixtures/hg_fevhub/server-info.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/server-info.body:1`:

```text
"builder_name":"json","dataset_name":"fever_gold_evidence","config_name":"default","version":{"version_str":"0.0.0","major":0,"minor":0,"patch":0}
```

Source: `https://datasets-server.huggingface.co/info?dataset=copenlu%2Ffever_gold_evidence` — HTTP **200**, response SHA-256 `a0342ee859fc4e9cf1a6a9f12795490b9c2eb89a78a7bda375bcb6451cd86534`; `tests/fixtures/hg_fevhub/server-info.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/server-info.body:1`:

```text
"hf://datasets/copenlu/fever_gold_evidence@a6b8d891d393e97a4efac791afffb2d7de5e57c6/valid.jsonl":{"num_bytes":6471611,"checksum":null}
```

`server-info.request.json`, `server-parquet.request.json` and `server-splits.request.json` each record `x-revision: a6b8d891d393e97a4efac791afffb2d7de5e57c6` (all `tests/fixtures/hg_fevhub/`, line 1). `/info` is reachable: its reported source path/revision and JSON-builder result are FOUND. They describe consumption of the uploaded export, not the conversion that originally produced it. Its `0.0.0` belongs to the JSON dataset builder and says nothing about scorer version.

### ABSENT — original producing-run receipt within retrieved generated/build records

Scope: both pages of `refs/convert/parquet` commit metadata (59 unique commits: the 33 main ancestors and 26 generated-only commits), 25 retrieved generated-only recursive inventories, current expanded Parquet tree, `/info`, `/parquet`, and `/splits` response bodies/headers. There are no further named generated refs in the retrieved refs response. Pagination links and termination are preserved in `hub-parquet-commits.request.json` and `hub-parquet-history-page2.request.json`; generated commits/inventories and exact paths are in `scope.json:1`. Retrieved inventories expose `.gitattributes`, directories, Parquet files and DuckDB indexes, with no producing-run receipt or conversion script file. No Parquet or DuckDB payload/footer was downloaded or inspected; their embedded contents are UNKNOWN. Neither a later Parquet conversion nor its commit date authenticates the original FEVER-to-JSON producing execution.

## 3. Producer project source, histories, releases and discussions

### FOUND — converter/aggregation/merge source and examples

Source: `https://api.github.com/repos/copenlu/fever-adversarial-attacks/contents/README.md?ref=aaa126ec4f3cf7163f69b82a0a0976d2579a04a6` — HTTP **200**, response SHA-256 `815e78c0ba09c909200ed2ffc11b50f8afbfd3e3fb81bce9b28c5fe4dd4f3500`; `tests/fixtures/hg_fevhub/gh-history-README-md-aaa126ec4f3cf7163f69b82a0a0976d2579a04a6.request.json:1`. Base64-decoded Git source SHA-256 `374052abccfd55c67e5d1a94f3c05b82de4426f2ce1c5e9efdd9c5daa7164a34`; verbatim excerpt `tests/fixtures/hg_fevhub/gh-history-README-md-aaa126ec4f3cf7163f69b82a0a0976d2579a04a6.decoded.txt:43`:

```text
Where paper_train.jsonl is an example path to a FEVER's dataset file in jsonl format, and wiki-pages is an example path to the Wikipedia dump from the FEVER dataset.
```

Source: `https://api.github.com/repos/copenlu/fever-adversarial-attacks/contents/README.md?ref=aaa126ec4f3cf7163f69b82a0a0976d2579a04a6` — HTTP **200**, response SHA-256 `815e78c0ba09c909200ed2ffc11b50f8afbfd3e3fb81bce9b28c5fe4dd4f3500`; `tests/fixtures/hg_fevhub/gh-history-README-md-aaa126ec4f3cf7163f69b82a0a0976d2579a04a6.request.json:1`. Base64-decoded Git source SHA-256 `374052abccfd55c67e5d1a94f3c05b82de4426f2ce1c5e9efdd9c5daa7164a34`; verbatim excerpt `tests/fixtures/hg_fevhub/gh-history-README-md-aaa126ec4f3cf7163f69b82a0a0976d2579a04a6.decoded.txt:50`:

```text
python scripts/aggregate_papelo_nei.py --dataset_dirs data/fever/train_nei.sentences.p5.s5.jsonl --wiki_dir data/wiki-pages/wiki-pages/ --output_paths data/train_nei_nli.jsonl
```

Source: `https://api.github.com/repos/copenlu/fever-adversarial-attacks/issues/5/comments?per_page=100` — HTTP **200**, response SHA-256 `b724d4363060b976e1f6c818a952522a708ab3438ad82505825c2ed0328139ba`; `tests/fixtures/hg_fevhub/gh-comments-5.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/gh-comments-5.body:1`:

```text
Hi, the readme has been updated with the corresponding link to the dataset ([https://huggingface.co/datasets/copenlu/fever_gold_evidence](https://huggingface.co/datasets/copenlu/fever_gold_evidence))
```

Source: `https://api.github.com/repos/copenlu/fever-adversarial-attacks/issues/3/comments?per_page=100` — HTTP **200**, response SHA-256 `56baf74f4c4b33dd39a279452e126df5e723eb8714baad19aabc2ba0713f1d50`; `tests/fixtures/hg_fevhub/gh-comments-3.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/gh-comments-3.body:1`:

```text
you can get and use either the paper's or the shared task's splits as indicated on the FEVER's website https://fever.ai/data.html
```

Source: `https://api.github.com/repos/copenlu/fever-adversarial-attacks/contents/scripts/create_nli_dataset.py?ref=15858b4c977375148751f6591643c05db7aee1df` — HTTP **200**, response SHA-256 `b546cf66a1c9c8b4020dd9cd04a3ad5cf8e5f00239dae99f6722b8b46f61e7a0`; `tests/fixtures/hg_fevhub/gh-history-create_nli_dataset-py-15858b4c977375148751f6591643c05db7aee1df.request.json:1`. Base64-decoded Git source SHA-256 `09054c04a53eb5f3f035d94fd2fe8a271a57bf69c5768eadd0535497f8cec884`; verbatim excerpt `tests/fixtures/hg_fevhub/gh-history-create_nli_dataset-py-15858b4c977375148751f6591643c05db7aee1df.decoded.txt:72`:

```text
nli_line = line.copy()
                    nli_line['evidence'] = sentences
```

The converter, aggregation, merge and README histories contain respectively 4, 3, 1 and 10 entries. Each history response and each source version at those returned revisions is retained, including base64 response bytes and decoded text; their Git blob SHA-1s are verified against the GitHub response (`audit-summary.json:1`; `scope.json:1` → `source_histories`; `gh-history-*.request.json:1`). The current master tree is `aaa126ec4f3cf7163f69b82a0a0976d2579a04a6`; the four published branch tips/trees are retained (`gh-tree.body:1`, `gh-branches.body:1`, and `gh-tree-<branch-sha>.body:1`). This authenticates source availability and history, not the executed producer revision.

### ABSENT — project execution receipt and published releases in enumerated scope

Scope: the 50-entry master commit listing (no next Link), the four branch-tip recursive trees (each untruncated), all 18 returned versions of the three scripts/README, `.gitmodules`, `requirements.txt`, all 8 listed issues/PR bodies and all 6 comments from issues 1/3/4/5 (other listed issues report zero comments), release/tag listings and current Actions run listing. Exact queries are plans 03/06/07; `gh-commits.request.json:1`, `gh-issues.body:1`, `gh-comments-{1,3,4,5}.body:1` and `scope.json:1` enumerate the retrieved scope. No run receipt with the required output/input/execution binding was found. This does not cover every historical blob in the project, PR review events, deleted logs or submodule contents recursively.

Source: `https://api.github.com/repos/copenlu/fever-adversarial-attacks/releases?per_page=100` — HTTP **200**, response SHA-256 `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`; `tests/fixtures/hg_fevhub/gh-releases.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/gh-releases.body:1`:

```text
[]
```

Source: `https://api.github.com/repos/copenlu/fever-adversarial-attacks/tags?per_page=100` — HTTP **200**, response SHA-256 `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`; `tests/fixtures/hg_fevhub/gh-tags.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/gh-tags.body:1`:

```text
[]
```

Source: `https://api.github.com/repos/copenlu/fever-adversarial-attacks/actions/runs?per_page=100` — HTTP **200**, response SHA-256 `a2790a384d7d281e7395679000c35d27768d89dbd7052f725b8f4688beb59915`; `tests/fixtures/hg_fevhub/gh-actions.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/gh-actions.body:1`:

```text
{"total_count":0,"workflow_runs":[]}
```

These are the producer project's release/tag/visible-run query results; they are not fresh queries about the already pinned scorer. Empty current Actions listings do not prove that no expired or deleted job ever ran.

## 4. NEI aggregation input and revision

### FOUND — input schema/recipe and source pins

Source: `https://api.github.com/repos/copenlu/fever-adversarial-attacks/contents/README.md?ref=aaa126ec4f3cf7163f69b82a0a0976d2579a04a6` — HTTP **200**, response SHA-256 `815e78c0ba09c909200ed2ffc11b50f8afbfd3e3fb81bce9b28c5fe4dd4f3500`; `tests/fixtures/hg_fevhub/gh-history-README-md-aaa126ec4f3cf7163f69b82a0a0976d2579a04a6.request.json:1`. Base64-decoded Git source SHA-256 `374052abccfd55c67e5d1a94f3c05b82de4426f2ce1c5e9efdd9c5daa7164a34`; verbatim excerpt `tests/fixtures/hg_fevhub/gh-history-README-md-aaa126ec4f3cf7163f69b82a0a0976d2579a04a6.decoded.txt:48`:

```text
python fever2018-retrieval/src/scripts/retrieval/ir.py --db data/fever/fever.db --model data/index/fever-tfidf-ngram\=2-hash\=16777216-tokenizer\=simple.npz --in-file data/fever-data/train_nei.jsonl --out-file data/fever/train_nei.sentences.p5.s5.jsonl --max-page 2 --max-sent 2
```

Source: `https://api.github.com/repos/copenlu/fever-adversarial-attacks/contents/scripts/aggregate_papelo_nei.py?ref=15858b4c977375148751f6591643c05db7aee1df` — HTTP **200**, response SHA-256 `713cb7a67843ad6cf2608010dded916181d0c9fd435019414b08e375a90e4fa7`; `tests/fixtures/hg_fevhub/gh-history-aggregate_papelo_nei-py-15858b4c977375148751f6591643c05db7aee1df.request.json:1`. Base64-decoded Git source SHA-256 `cf9d2d241577666b8cd7a52d041d3b09863d24dce8c503e3ce98c36f471a69fd`; verbatim excerpt `tests/fixtures/hg_fevhub/gh-history-aggregate_papelo_nei-py-15858b4c977375148751f6591643c05db7aee1df.decoded.txt:49`:

```text
for predicted_sent in line['predicted_sentences'][:1]:
```

Source: `https://api.github.com/repos/copenlu/fever-adversarial-attacks/git/trees/master?recursive=1` — HTTP **200**, response SHA-256 `1bb7a8632d0ccd24ac7db47e8d11755c83fc68cabbe8fd34489f8f39acfe004d`; `tests/fixtures/hg_fevhub/gh-tree.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/gh-tree.body:1`:

```text
"path":"builders/papelo-NEC-labs-america","mode":"160000","type":"commit","sha":"780734e40f75d7b6d5f57cac74acf65cff17dc5b"
```

Source: `https://api.github.com/repos/copenlu/fever-adversarial-attacks/contents/.gitmodules?ref=aaa126ec4f3cf7163f69b82a0a0976d2579a04a6` — HTTP **200**, response SHA-256 `d8b08094901d135042771f4d126474d31b2c6046947c0a00e870831616858558`; `tests/fixtures/hg_fevhub/gh-gitmodules.request.json:1`. Base64-decoded Git source SHA-256 `1df171b682472a53b69f0752de140785db2de32c5dc22e81a1460cc3514595e7`; verbatim excerpt `tests/fixtures/hg_fevhub/gh-gitmodules.decoded.txt:11`:

```text
path = builders/papelo-NEC-labs-america
	url = git@github.com:necla-ml/fever2018.git
```

Source: `https://api.github.com/repos/necla-ml/fever2018/git/trees/780734e40f75d7b6d5f57cac74acf65cff17dc5b?recursive=1` — HTTP **200**, response SHA-256 `4534dd4114e28dc7e7a0ab84152f720988c93d51f9ced84a2390ec8293b70207`; `tests/fixtures/hg_fevhub/papelo-tree.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/papelo-tree.body:1`:

```text
"path":"fever2018-retrieval","mode":"160000","type":"commit","sha":"90a07fe85b418de5ab62de8eaa2572df0d93f51e"
```

Source: `https://api.github.com/repos/necla-ml/fever2018/contents/README.md?ref=780734e40f75d7b6d5f57cac74acf65cff17dc5b` — HTTP **200**, response SHA-256 `48a7efdaf72525cc3b5e6bd7236bad76d86ccd42bb13e79c5a324d6581ccf3b9`; `tests/fixtures/hg_fevhub/papelo-readme.request.json:1`. Base64-decoded Git source SHA-256 `a0fed973fc17777109faaa6cc6743025b267a7b95ffaf45cc51f20685f33966f`; verbatim excerpt `tests/fixtures/hg_fevhub/papelo-readme.decoded.txt:42`:

```text
If you don't care about reproducing the original results, we recommend you
omit the `--compat` flag, which reproduces earlier behavior.
```

The parent Gitlink and nested retrieval Gitlink are published source revisions. The example command names a training retrieval output; it is not a published validation-input object/revision, and no observed execution links either Gitlink to the Hub export. The Papelo README's recipe and `--compat` discussion are additional declarations, not evidence about the actual producer's flags or environment.

### ABSENT — authenticated NEI input artifact/revision in the searched scope

Scope: the Hub trees/text/metadata scope in sections 1–2; all producer script/README versions and issue/comments/releases in section 3; the 12-entry untruncated Papelo tree at `780734e40f75d7b6d5f57cac74acf65cff17dc5b` and its README; and the five exact Zenodo searches in section 5. No hash-bound Papelo retrieval output file, validation NEI input manifest, selected retrieval sentence inventory, or input-to-export producing receipt was found there. The Git trees contain no checked-in `train_nei.sentences.p5.s5.jsonl`/validation retrieval payload. Recipe paths and code revisions are FOUND; specific aggregation input bytes/revision and actual retrieval parameters are UNKNOWN. Thus “NEI input revision published” is **ABSENT only in this enumerated retrieved scope**, while public availability elsewhere remains UNKNOWN.

## 5. Paper and artifact records

### FOUND — primary paper records and method description

Source: `https://aclanthology.org/2020.emnlp-main.256.bib` — HTTP **200**, response SHA-256 `b1c8e0e2911aaca80efb6a4d2746976db293d31b8cda298a65de2a1c8322421d`; `tests/fixtures/hg_fevhub/paper-bib.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/paper-bib.body:2`:

```text
title = "Generating Label Cohesive and Well-Formed Adversarial Claims"
```

Source: `https://arxiv.org/html/2009.08205v1` — HTTP **200**, response SHA-256 `9b6d484ae24711a9a530145d7eeafcc621c699501bd063b439d0a5b47eb6aff3`; `tests/fixtures/hg_fevhub/paper-html.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/paper-html.body:1203`:

```text
When there is more than one annotation of different evidence sentences for an instance, we include them as separate instances in the datasets.
```

The peer-reviewed ACL page/BibTeX, its PDF (digest/pointer retained outside git with `paper-pdf.txt` extraction), the project-linked arXiv abstract and arXiv HTML were retrieved (`paper-page.request.json:1`, `paper-bib.request.json:1`, `paper-pdf.request.json:1`, `paper-arxiv.request.json:1`, `paper-html.request.json:1`). The paper states its method; it does not provide a hash/revision-bound execution of the later Hub upload. The ACL page was checked for artifact/attachment links; its published paper-specific PDF and video link do not constitute a conversion receipt (`paper-page.body:30`). Video contents were not retrieved. The unrelated exploratory `2020.acl-main.602` response is retained as `direct-paper.*` and is excluded from the FEVER evidence/search scope.

### ABSENT — exact Zenodo queries and paper-record receipt scope

Each of the following corrected public Zenodo API queries used `size=25` and returned exactly `"hits": {"hits": [], "total": 0}`. This proves zero returned indexed matches for those queries only, not that no differently named/unindexed artifact exists:

Source: `https://zenodo.org/api/records?q=%22fever-adversarial-attacks%22&size=25` — HTTP **200**, response SHA-256 `25eeef38fac515da4475144bfc5637af1e3b1bc91645615f2eccd31dfe7d871f`; `tests/fixtures/hg_fevhub/zenodo-project-public.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/zenodo-project-public.body:1`:

```text
"hits": {"hits": [], "total": 0}
```

Source: `https://zenodo.org/api/records?q=%22Generating%20Label%20Cohesive%20and%20Well-Formed%20Adversarial%20Claims%22&size=25` — HTTP **200**, response SHA-256 `f85d70da31d83213b4287b7a7ac4732c01bf2f16ef5541be95d72b5557450627`; `tests/fixtures/hg_fevhub/zenodo-title-public.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/zenodo-title-public.body:1`:

```text
"hits": {"hits": [], "total": 0}
```

Source: `https://zenodo.org/api/records?q=%22fever_gold_evidence%22&size=25` — HTTP **200**, response SHA-256 `8bea6a559d4369f2ed3d37d76892702adcda79b29a89b885147d670eaf8e7c2d`; `tests/fixtures/hg_fevhub/zenodo-nei-public.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/zenodo-nei-public.body:1`:

```text
"hits": {"hits": [], "total": 0}
```

Source: `https://zenodo.org/api/records?q=%222009.08205%22&size=25` — HTTP **200**, response SHA-256 `05bb4e9636fb68f09855abd8fc8a5dcde295d461f649c7e40e1a120d551ef7aa`; `tests/fixtures/hg_fevhub/zenodo-arxiv.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/zenodo-arxiv.body:1`:

```text
"hits": {"hits": [], "total": 0}
```

Source: `https://zenodo.org/api/records?q=%222020.emnlp-main.256%22&size=25` — HTTP **200**, response SHA-256 `8f77333fba7003a154a5d1ef24fe996770034ca88bcb5d5cc65ee651c1156c21`; `tests/fixtures/hg_fevhub/zenodo-doi.request.json:1`. verbatim excerpt `tests/fixtures/hg_fevhub/zenodo-doi.body:1`:

```text
"hits": {"hits": [], "total": 0}
```

No producing receipt or hash-bound NEI input is present in the retrieved ACL page/BibTeX/paper text and arXiv abstract/HTML or those five Zenodo result sets. Exact queries, statuses, bodies and digests are retained above and in plans 07/10/12. The initial `size=100` requests returned HTTP 400 validation errors and are not evidence of zero matches (`zenodo-{project,title,nei}.request.json:1`).

## 6. Explicit UNKNOWN scope and decision

The following historical objects were requested repeatedly but never yielded an HTTP response and remain UNKNOWN; neither is classified ABSENT:

- Generated-ref tree at `ad8321607bcad0e534c243ec8c108a5787cea6c8`. Attempt receipts: `parquet-tree-ad8321607bcad0e534c243ec8c108a5787cea6c8{,-retry2,-retry3,-alt,-final}.request.json:1`.
- Historical Hub loader at `1776db7e9abab525eae8e59c5015e3589dfe371b`, Git blob `ab71339be067bc98bcad7df12a12c0e05fc6b521`, 7,897 bytes (tree entry in `hub-tree-1776db7e9abab525eae8e59c5015e3589dfe371b-retry.body:1`; attempts `hub-loader-1776db7e9abab525eae8e59c5015e3589dfe371b{,-retry,-retry2,-retry3,-alt,-final}.request.json:1`).

All these filenames are under `tests/fixtures/hg_fevhub/`; brace notation enumerates actual filenames, not a single path. Machine-readable states appear in `scope.json:1` (`generated_history` and `hub_text_objects`). Other UNKNOWNs: unadvertised/private/deleted refs and logs, producer machines/accounts, unindexed artifacts, public artifacts under other names, video content, export/Parquet/DuckDB payload metadata, other historical project blobs, and nested submodule contents beyond the published Gitlinks/README examined here. The failed direct requests for historical card blob `4a5ce872c186404a8ebdc7f860479eaeec0a08b4` remain in the request ledger, but its complete contents are FOUND via the authenticated PR diff recovery above. No producer was contacted.

**Answer:** no qualifying execution-binding artifact was retrieved; it is ABSENT over the specific retrieved scope above. Converter code and example commands are published, as are Papelo source pins. The aggregation input file/revision and its execution-to-export linkage are not authenticated by those declarations. Global public-record absence remains UNKNOWN, especially for the two unreceived objects.

**Standing-limit argument:** this search establishes a bounded public-source absence and an upstream evidence dependency; it does not establish the categorical operator claim that no further work in this repository can satisfy the requirement. Two historical objects remain unread, and an unindexed artifact or producer-held record may still provide the binding. Recover those named objects and obtain a maintainer-published run/input manifest or an explicit scope/requirement decision before treating the historical producing-execution clause as a standing limit. A fresh local conversion cannot authenticate a historical execution. No source or custody finding here closes metric comparability, restores omitted evidence groups, authenticates historical NEI inputs, establishes runtime scoring, or authorizes a diagnostic (`registry/dataset-blockers.json:376`).
