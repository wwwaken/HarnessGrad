# Reports move verification

Verified in `/tmp/hg-ref-8` against baseline commit `6c539d8` (cleanup reference rewrite: `ad57926`). No model, H0, benchmark, GPU, network or external archive execution was performed.

## Outcome

- All 65 tracked report/evidence files are present under `reports/`.
- Walked **848 tracked files**: 110 Markdown, 306 JSON and 432 Python. Searched every file for explicit report paths and every one of the 65 moved basenames, including references in strings, keys, comments, code blocks and plain text.
- At baseline, **179 explicit report-file path occurrences** resolved to **45 distinct real files**. The corrected GAIA token brings the final count to **180**, all resolving. Five additional lexical matches were prose (`reports/results` or `reports/receipts`), not file references. Markdown destinations were resolved from their containing document; repository path strings were resolved from the repository root.
- Also checked every relative Markdown link in the moved reports, including sibling links and links back into the repository. Of **110 link occurrences**, **24 were broken**. All 24 are fixed below; the final check passes all 110 targets (109 file references and one directory reference). URL fragments were retained; fragment/line accuracy was not audited.
- Fixed one stale repository-root path token in the GAIA contract description. No active reference still requires a moved file at the old root. Historical/ambiguous strings retained below are explicitly distinguished.
- The blocker checker passes. **74 repository evidence locators across 38 files** independently matched literal expected text. **10 external-reference entries remain unverified**; the checker deliberately skips their existence/content checks, and opening them would exceed the requested workspace. Thus an assertion that *every* evidence locator is a verified file is not supported.
- Both the tracked root inventory and physical root inventory, excluding Git's administrative `.git` file, equal the requested nine files.

## Exact broken references corrected

Only link destinations and the one path token changed; surrounding prose, link labels and fragments were preserved. Locations refer to the baseline and remain on the same lines.

| Source | Original destination | Correct destination |
| --- | --- | --- |
| `reports/appworld-canonical-source-codex229-report.md:28` | `docs/evidence/appworld-codex229/source-provenance.json` | `../docs/evidence/appworld-codex229/source-provenance.json` |
| `reports/appworld-canonical-source-codex229-report.md:60` | `docs/evidence/appworld-codex229/` | `../docs/evidence/appworld-codex229/` |
| `reports/appworld-canonical-source-codex229-report.md:110` | `docs/appworld-local-adapter-audit-codex229.md` | `../docs/appworld-local-adapter-audit-codex229.md` |
| `reports/bfcl-ast-contract-codex166-report.md:24` | `data/bfcl_v3.py#L205` | `../data/bfcl_v3.py#L205` |
| `reports/bfcl-ast-contract-codex166-report.md:28` | `data/bfcl_v3.py#L187` | `../data/bfcl_v3.py#L187` |
| `reports/bfcl-ast-contract-codex166-report.md:30` | `data/bfcl_v3.py#L446` | `../data/bfcl_v3.py#L446` |
| `reports/bfcl-blob-retry-codex227-report.md:7` | `tests/fixtures/bfcl_ast_source/retry-codex227/provenance.json` | `../tests/fixtures/bfcl_ast_source/retry-codex227/provenance.json` |
| `reports/bfcl-blob-retry-codex227-report.md:93` | `tests/fixtures/bfcl_ast_source/retry-codex227/verification.json` | `../tests/fixtures/bfcl_ast_source/retry-codex227/verification.json` |
| `reports/bfcl-source-provenance-codex195-report.md:22` | `tests/fixtures/bfcl_ast_source/candidate-codex195/provenance.json` | `../tests/fixtures/bfcl_ast_source/candidate-codex195/provenance.json` |
| `reports/bfcl-source-provenance-codex195-report.md:35` | `tests/fixtures/bfcl_ast_source/candidate-codex195/README.md` | `../tests/fixtures/bfcl_ast_source/candidate-codex195/README.md` |
| `reports/bfcl-source-provenance-codex195-report.md:56` | `tests/fixtures/bfcl_ast_source/candidate-codex195/CUSTODIAN_REQUEST.md` | `../tests/fixtures/bfcl_ast_source/candidate-codex195/CUSTODIAN_REQUEST.md` |
| `reports/filesystem-quota-codex168-report.md:20` | `docs/filesystem-quota-backends.md` | `../docs/filesystem-quota-backends.md` |
| `reports/quota-backend-scope-codex238-report.md:14` | `README.md` | `../README.md` |
| `reports/quota-backend-scope-codex238-report.md:15` | `docs/filesystem-quota-backends.md` | `../docs/filesystem-quota-backends.md` |
| `reports/quota-backend-scope-codex238-report.md:22` | `docs/task-211-terminal-operator-backend-packet.md` | `../docs/task-211-terminal-operator-backend-packet.md` |
| `reports/quota-backend-scope-codex238-report.md:23` | `docs/task-222-quota-administrator-checklist.md` | `../docs/task-222-quota-administrator-checklist.md` |
| `reports/quota-backend-scope-codex238-report.md:24` | `docs/runner-admission-contract.md` | `../docs/runner-admission-contract.md` |
| `reports/quota-backend-scope-codex238-report.md:25` | `docs/task-233-quota-readback-authentication.md` | `../docs/task-233-quota-readback-authentication.md` |
| `reports/quota-backend-scope-codex238-report.md:43` | `docs/task-211-terminal-operator-backend-overview.html` | `../docs/task-211-terminal-operator-backend-overview.html` |
| `reports/quota-backend-scope-codex238-report.md:45` | `docs/task-233-quota-readback-overview.html` | `../docs/task-233-quota-readback-overview.html` |
| `reports/runner-admission-codex-158-report.md:23` | `docs/runner-admission-contract.md` | `../docs/runner-admission-contract.md` |
| `reports/triviaqa-scorer-provenance-codex157-report.md:14` | `tests/fixtures/triviaqa_upstream/README.md` | `../tests/fixtures/triviaqa_upstream/README.md` |
| `reports/twowikimultihopqa-provenance-codex197-report.md:17` | `tests/fixtures/twowikimultihopqa_upstream_codex197/README.md` | `../tests/fixtures/twowikimultihopqa_upstream_codex197/README.md` |
| `reports/twowikimultihopqa-provenance-codex197-report.md:101` | `tests/quality/test_twowikimultihopqa_provenance_codex197.py` | `../tests/quality/test_twowikimultihopqa_provenance_codex197.py` |
| `reports/GAIA_GATE.md:67` | Exact repository path token `GAIA_GATE.md` | `reports/GAIA_GATE.md` (matches `eval/gaia_snapshot_attestation.py:23`) |

## Remaining old-name references

The basename search produced 49 baseline candidates without a `reports/` qualifier. Valid report-sibling links/file mentions, external archive citations and upstream AppWorld output examples are not references to a missing repository-root file. In particular, `report.md` at `reports/GAIA_GATE.md:23` and `reports/runner-admission-codex-158-report.md:13` denotes the existing sibling `reports/report.md`; the inherited-report name was preserved.

These four exact strings retain historical or ambiguous root-path semantics and were not rewritten:

| Source | Retained string | Reason |
| --- | --- | --- |
| `reports/filesystem-quota-codex168-report.md:32` | `> filesystem-quota-codex168-test-result.txt 2>&1` | Recorded historical test command from its original worktree; the retained output now exists at `reports/filesystem-quota-codex168-test-result.txt`. |
| `reports/triviaqa-review-codex215-report.md:96` | `> triviaqa-review-codex215-test-result.txt 2>&1` | Recorded historical test command; output now exists at `reports/triviaqa-review-codex215-test-result.txt`. |
| `reports/triviaqa-scorer-review-codex205-report.md:82` | `> triviaqa-scorer-review-codex205-test-result.txt 2>&1` | Recorded historical test command; output now exists at `reports/triviaqa-scorer-review-codex205-test-result.txt`. |
| `reports/filesystem-quota-codex168-source-evidence.json:133` | `"result_path": "filesystem-quota-codex168-test-result.txt"` | Historical evidence metadata has no declared path base or repository consumer. Resolves beside the JSON; fails if treated as repository-root-relative. Preserved rather than guessing or altering the pinned historical inventory. |

Absolute external `report.md` citations were preserved: `docs/adapter-integration-journal.md:162,207,227,237,285,376,405`; `docs/dataset-blockers.json:587`; `docs/task-234-diagnostic-readiness.json:734`; `docs/task-236-diagnostic-readiness.json:861`; `docs/task-243-diagnostic-readiness.json:409`; `tests/fixtures/dataset_blockers/history-codex178.json:131`; and `reports/report.md:14,15`. AppWorld examples at `docs/evidence/appworld-codex229/README.md:564,716,1101` name upstream evaluation outputs, not the moved root report.

The five prose-only matches were `docs/adapter-integration-journal.md:90,687`, `docs/task-236-diagnostic-readiness.md:104`, `reports/triviaqa-review-codex215-report.md:36` and `reports/triviaqa-source-acquisition-codex196-report.md:75`. No prose was rewritten. Historical hash snapshots were not refreshed to claim that corrected Markdown bytes match an earlier review revision.

## Blocker evidence verification

Independently traversed every nested evidence object in `docs/dataset-blockers.json`, checked repository paths with `is_file()`, and tested `locator in file.read_text()`. All 74 repository entries pass. `tools/check_dataset_blockers.py` separately returns:

```json
{"valid": true, "datasets": 28, "shared_blockers": 8, "historical_records": 11, "production_authorized": false}
```

The following ten external entries are intentionally not opened. JSON pointers identify exact evidence objects; repeated paths are distinct entries. Except for the first entry, their locator is the descriptive statement `Journal citation only; external receipt not opened during this review.`, not an independently checked quotation from an external file. The first locator is `metadata-only path inventory: _src, runtime, agent_runtime, prepared` and refers to a directory, not a file.

| JSON pointer | External path |
| --- | --- |
| `/datasets/0/blockers/0/evidence/3` | `/mnt/20t/xubuqiang/datasets/agentdojo` |
| `/datasets/3/historical_runs/0/evidence/1` | `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/101/deliverables/receipt.md` |
| `/datasets/5/historical_runs/0/evidence/1` | `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/qa-h0-archive-v4/index.json` |
| `/datasets/5/historical_runs/1/evidence/1` | `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/qa-h0-archive-v4/index.json` |
| `/datasets/6/historical_runs/0/evidence/1` | `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/chess/interruption-audit.md` |
| `/datasets/6/historical_runs/1/evidence/1` | `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/chess/interruption-audit.md` |
| `/datasets/7/historical_runs/0/evidence/1` | `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/61/report.md` |
| `/datasets/9/historical_runs/0/evidence/1` | `/mnt/20t/xubuqiang/Study/gaia-h0-launch-v2-evidence/GAIA_H0_V2_RECEIPT.json` |
| `/datasets/9/historical_runs/1/evidence/1` | `/mnt/20t/xubuqiang/Study/gaia-h0-launch-v3/runs/gaia-validation-pilot-h0-20261117-v3/events.jsonl` |
| `/datasets/11/historical_runs/0/evidence/1` | `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/qa-h0-incomplete-index.json` |

## Root inventory

Exactly nine project files; `.git` is the worktree administration file:

```text
.env.example
.gitignore
AGENTS.md
DOWNLOADS.md
INTERFACE.md
LICENSE
README.md
driver.py
install.sh
```

## Focused validation

Ran from the worktree with temporary files confined to `.scratch/reports-move-verification/`:

```sh
env TMPDIR=/tmp/hg-ref-8/.scratch/reports-move-verification/tmp PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/quality/test_dataset_blockers.py tests/quality/test_gaia_snapshot_attestation.py --basetemp=/tmp/hg-ref-8/.scratch/reports-move-verification/pytest -p no:cacheprovider
env PYTHONDONTWRITEBYTECODE=1 python tools/check_dataset_blockers.py
git diff --check
```

Results: **140 passed in 3.50s**, checker exit 0, whitespace check clean. A final independent path/existence pass confirms all scoped Markdown destinations, explicit report-file paths and the nine-file root inventory. The 848-file baseline excludes this newly written findings report, whose examples intentionally quote the original defects. Scratch scan records are local audit output, not new benchmark receipts.
