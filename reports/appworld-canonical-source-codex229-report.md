# AppWorld canonical public source and production evidence gap — Task 229

2026-10-14. Isolated worktree `/tmp/hg-codex-229`, base
`61e7f82245c76e7c833740216940d1fcaf3b76be`.

The public source matching the local Dockerfile's requested package is
**AppWorld `v0.1.3.post1`, commit
`66ad8099e12188ece0d3fe45e661dbc01880813b`** in
[StonyBrookNLP/appworld](https://github.com/StonyBrookNLP/appworld).
The pinned public evaluator establishes metric names, success aggregation and
percentage scale. It does not identify the actual installed production scorer
or authenticate the protected task-specific evaluators. The production trial
identity gap remains open. No scorer, adapter, writer or registry was changed.

## Authoritative, code-only acquisition

The [official release](https://github.com/StonyBrookNLP/appworld/releases/tag/v0.1.3.post1)
describes a small installation/dependency fix and warns that `main` is ahead of
the release. The public tag ref names annotated tag object
`efac79081936323733f68fd78260dab6981f195a`; official GitHub Git-ref advertisement
peels that tag to the commit above. The commit metadata names root tree
`bbe398b91767a9a068add36eb84bdf936eed372f`.
The package's pinned `pyproject.toml:1–5` and `__init__.py:9` both declare
`0.1.3.post1`. Package metadata identifies `appworld.dev` and this repository.
This is the release matching the build declaration, not a claim about whichever
code a mutable branch or a deployed container currently contains.

[Preserved evidence](../docs/evidence/appworld-codex229/source-provenance.json)
includes exact public source/license bytes, original GitHub contents-API
responses, release/tag/commit and nonrecursive tree metadata, acquisition URLs,
HTTP response dates, SHA-256 digests and Git blob identities. Raw-host requests
failed with connection resets; those failures are retained in
`fetch-receipt.json`. Successful requests used the official GitHub contents API
with the exact commit, not a mirror or a branch fallback. The tag-object API
request then hit HTTP 403 rate limiting; its failed acquisition is recorded.
A public `git ls-remote` request to the official repository acquired only the
tag and peeled commit ref advertisements. The tag object itself is not acquired
or rehashed; this limit is explicit in the manifest.

The offline checker checks the saved ref/peeled-commit advertisements and commit
metadata, reconstructs all four directory-tree identities, and verifies
root/subtrees → eight original file blobs. Origin
authentication relies on the preserved GitHub HTTPS acquisition; these local
hashes are integrity checks, not an independent signature or custodian approval.
Only individually allowlisted public code, documentation, API metadata and Git
ref metadata were fetched. No repository archive, bundle, task payload, wheel or container was
acquired; no upstream source was imported or executed.

## Release, data and license boundaries

| Axis | Pinned public evidence | Current local adapter and remaining limit |
| --- | --- | --- |
| Code/package | `pyproject.toml:3`, package `__init__.py:9`: `0.1.3.post1` | `data/appworld/Dockerfile:4` requests that version. Adapter header says `0.1.3`. No wheel hash or image-to-source attestation establishes actual installed bytes. |
| Data/database version | `download.py:10–16` names the official S3 `data-0.1.0.bundle`; `common/constants.py:28` declares `DB_VERSION="0.1.0"` | `data/appworld.py:327–338` declares the same URL/version and SHA-256 `fd9f9608c2ec71ed0ac25c3633a738b9129a318a129e31230425b9188e508250`. The pinned public download code supplies no bundle checksum. This local checksum and actual contents were not independently authenticated. |
| Public code license | Original `LICENSE`, `pyproject.toml:20`, `README.md:1152–1155`: Apache-2.0 | Applies to this public source projection, including generic evaluator utilities. |
| Protected portion | `README.md:1157–1160`: Apache-2.0 **plus an additional encrypted-public-redistribution requirement** for task/app/API-specific bundles | A blanket unqualified Apache-2.0 description of task data/evaluation payloads would omit the documented condition. No protected bundle license bytes or payloads were opened. |
| Per-task scorer | `evaluator.py:501–516` obtains the task's evaluation module and invokes its `evaluate` using task-specific inputs | Public generic evaluator source is acquired; protected `ground_truth/evaluation.py`, supporting artifacts, release custody and installed dependency/runtime closure remain outside this review. |

All upstream paths/lines in this report refer to exact files in
[the evidence directory](../docs/evidence/appworld-codex229/). Source files are
stored as `.py.txt` to distinguish inert evidence from runnable local code.
No task-specific evaluator is transcribed, inferred or replaced.

## Metric and split mapping

| Canonical public source | Current local mapping | Comparability boundary |
| --- | --- | --- |
| `TestTracker.success`: `pass_count == num_tests` (`evaluator.py:191–193`) | Checker `data/appworld/verify/check.py:59–75` writes Boolean `success`, metric `appworld.task_goal_completion` / `TGC`, and reward 1 or 0 | TGC is strict task completion, not the fraction of unit tests passed. Generic `passed`, task means and progress scores do not establish this evidence. |
| `task_goal_completion`: mean of task successes, multiplied by 100, with rounding (`evaluator.py:333–372`) | `eval/appworld_reporting.py:155–162,184–215`: **TGC**, fraction of measured selected task/trial cells | Public output is a percentage; local output is an unrounded fraction. Compare only after matching coverage/protocol and upstream rounding, rather than treating equal field names as identical reports. |
| `scenario_goal_completion`: mean of each scenario's minimum task success (`evaluator.py:337–368`) | `appworld.scenario_goal_completion` / **SGC**; same-trial conjunction over local `_1`, `_2`, `_3` groups (`eval/appworld_reporting.py:164–182`) | For Boolean successes, minimum means all variants pass. Upstream README `843` assumes all variations are supplied. Public generic code does not itself fix their number or encode repeated-trial alignment. Local fixed-three and trial policies are explicit local constraints; release-wide membership is not authenticated here. |
| Source split `test_normal`; README calls the test sets Normal and Challenge (`README.md:849–853`) | **Test-N**, harness `eval` side | This verifies the long-name/source-key mapping. The abbreviated display spelling is declared locally, not a separately acquired paper-table label. |
| Source split `test_challenge` | **Test-C**, harness `eval` side | Keep separate from Test-N; a combined eval score is not either official split score. |
| Source splits `train`, `dev` | Train, Dev; both on harness `train` side | Upstream distinguishes training uses from dev tuning/error analysis. The merged harness side does not erase the original source split. |

`task.py:236–269` loads the named split file and can check requested per-scenario
variant counts. `task.py:276–288` derives scenario identity from the task ID's
generator prefix and variant from its suffix. These are code contracts, not an
inspection of any split file or task membership.

The upstream parser strips tags and requires exactly one underscore; the local
reporter's accepted scenario grammar is broader. No source-only ID comparison
can certify actual release membership. Upstream `evaluator.py:528–529` writes
the package version into its evaluation `version.txt`, despite naming the local
variable `git_hash_file_path`; that file alone would not establish a commit.

The local declared counts are 90 train / 57 dev / 168 Test-N / 417 Test-C
(732 total); the harness partition is 147 train-side / 585 eval-side. These are
adapter constants, **not freshly verified release counts**. Paper-era counts in
the adapter header are also unverified here. No task or split-manifest payload
was read to reconcile them.

Upstream documentation illustrates short keys `tgc`/`sgc`
(`README.md:661–675`), while the actual pinned `Metric` implementation returns
`task_goal_completion`/`scenario_goal_completion` (`evaluator.py:369–375`). It
also reads older `strict`/`grouped_strict` report keys as fallbacks
(`evaluator.py:423–429`). Use actual pinned implementation names for a source
identity; the local `appworld.*` namespace is a HarnessGrad identity, not an
upstream serialized field name. README example count fields also do not appear
in that implementation's aggregate dictionary. No reporting keys were changed
from inference.

Local incomplete selections, missing/invalid/unmeasured cells or unaligned
trials withhold SGC; nonmeasured cells are excluded with coverage reported
separately. Upstream aggregation over the supplied dictionary does not impose
all those local guards. A selected, incomplete or train-side report is not a
full official Test-N/Test-C result, even if its measured fraction is defined.

## Exact production writer evidence gap

The [local source audit](../docs/appworld-local-adapter-audit-codex229.md) gives
line-level producer, writer and reporter evidence. Parent inspection confirmed:

1. The AppWorld checker supplies metric/measured/Boolean success/task/split
   facts, but no original numeric trial identity or canonical source pin.
2. `eval/runner.py:917–926` knows the trial index but neither passes it into
   `run_one` nor adds it to the returned verdict. Failed provider trials can be
   skipped (`948–959`); copied histories contain survivors without added
   original IDs (`1096–1098`). Positions therefore cannot recover identity.
3. `harnessgrad/records.py:506–523` preserves supplied identities and evidence
   and marks anonymous verdicts `trial_aligned=false`, including single-trial
   verdicts. This is correct preservation, but it cannot create missing facts.
   The current route can retain measured TGC; newly saved anonymous cells
   cannot establish same-trial SGC. No production receipt was inspected.
4. Current progress output lacks sufficient scorer evidence; event emission
   was not independently audited here. The separate trusted
   runner's string `trial_id` does not bridge this saved numeric-trial contract.

The unresolved requirement is a trusted producer-to-writer binding of each
selected task's **original one-based trial identity** and actual scorer facts,
including explicit invalid/unmeasured cells. A separate bound receipt must
identify effective package/wheel and image/source hashes, protected evaluator
artifact identity, data/split/selected-manifest custody, model/harness hashes,
endpoint, eligible/selected/task/trial coverage, limits/budgets, and lifecycle,
snapshot and cleanup outcomes. The eight public-file pins supply none of those
production observations. They are not inserted as though measured by a running
writer. No gate is retired and no diagnostic, pilot or H0 is authorized.

## Validation

Run the inert, offline custody check from this worktree:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/evidence/appworld-codex229/verify_custody.py
git diff --cached --check
```

This check reads only the pinned public-source evidence directory, reconstructs
Git tree/blob hashes and validates stored metadata. It executes no AppWorld
code, official task, model, H0, scorer, Docker service or dataset adapter.
Result: **PASS — 32 pinned files, four reconstructed Git trees and eight public
code/docs blobs**. All 27 local report links resolve within this worktree.
The unique task-229 journal entry records these results. Earlier reported
test/benchmark outcomes remain historical claims and are not revalidated here.
