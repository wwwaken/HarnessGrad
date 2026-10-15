# Known-red baseline for `tests/quality`

Why this file exists: the phase's acceptance command was a fixed short list of focused files, and
twice a change landed while tests **outside** that list were red - twelve on 2026-10-15 (three stale
pins on withdrawn blockers plus the ujson payload strip) and five ALFWorld-native failures found by a
full sweep the same day. A fixed list is not a gate. This file records what a full sweep finds, so a
future round starts from a known baseline instead of re-discovering it.

## Method

The full directory cannot be collected in one go (`pytest tests/quality --collect-only` does not
complete in 60 s), so the sweep runs `tests/quality/test_*.py` in batches of 12 with a 240 s timeout
per batch and logs every `FAILED`/`ERROR` node id. For each failure, classification asks one
mechanical question first: **was the failing test file or the module it exercises changed by any
commit in this phase?** `git log --oneline 1825cd0e..HEAD -- <path>` answers it. A failure whose file
and module are both untouched since before the phase is pre-existing and is recorded here rather than
attributed to current work.

## Sweep 1 - 2026-10-15, batches 0-24 of 16

| node id | classification |
| --- | --- |
| `test_alfworld_dataset.py::test_the_check_re_materializes_its_inputs` | pre-existing; **not** a defect in the test's subject. The check returns `outcome: unmeasured` with `native_runtime.verified: False` where the test asserts `score == 0.0`. A native runtime that cannot be established must never fall back to a score, so the assertion is the stale part. Measured scope: of `data/runtimes/alfworld-native.json`'s 2,581 files, 2,576 match their recorded SHA-256, 0 drifted, and exactly 5 are absent - all `/scorer/...` paths that are staged into the run namespace rather than present on the host. Test-provisioning, not host drift. |
| `test_alfworld_dataset.py::test_the_sandboxed_check_can_still_write_its_verdict` | same family as above; same unverified native runtime. |
| `test_alfworld_official_scorer.py::test_our_reward_equals_the_official_reduction_on_a_real_win[look_at_obj_in_light]` | same family; needs the provisioned ALFWorld runtime/scorer projection. |
| `test_alfworld_official_scorer.py::test_our_reward_equals_the_official_reduction_on_a_real_win[pick_clean_then_place_in_recep]` | same family. |
| `test_alfworld_official_scorer.py::test_an_empty_episode_is_zero_for_our_check` | same family. |
| `test_candidate_apply.py::test_a_bad_candidate_is_unmeasured_not_scored_zero` | pre-existing. Last touched by `32a6276a`, before this phase; `data/scaffolds/qa/base.py` is untouched by any commit since `1825cd0e`. |
| `test_candidate_apply.py::test_a_failed_step_is_retried_not_the_end_of_the_run` | pre-existing, same reason. |
| `test_candidate_apply.py::test_a_round_that_changed_nothing_does_not_read_as_a_new_candidate` | pre-existing, same reason. |
| `test_candidate_apply.py::test_a_candidate_that_does_not_compile_is_unmeasured_not_zero` | pre-existing, same reason. |
| `test_chess3_diagnostic_actor.py::test_control_sends_at_zero_retains_connection_and_reads_terminal[moves0-solved-reference_complete-2]` | pre-existing. Last touched by `fb546c96`, before this phase. |
| `test_chess3_diagnostic_actor.py::test_control_sends_at_zero_retains_connection_and_reads_terminal[moves1-failed-wrong_move-1]` | pre-existing, same reason. |
| `test_chessbench_puzzles_strict_replay.py::test_materialized_verifier_preserves_both_metrics_and_redacts_reference` | pre-existing; last touched by `03ecb68c`. Confirmed error: `KeyError: 'task_id'` at `data/scaffolds/qa/base.py:340`. |

## What this file is not

It is not a skip list and it does not weaken a test. Every entry above is a **real red** that should
be fixed; the ALFWorld five want an explicit skip for the unprovisioned scorer projection, together
with a decision about whether the sealed closure is meant to verify on the host at all, and the
`KeyError: 'task_id'` wants a genuine diagnosis. Recording them is the honest alternative to the two
bad options: leaving them undocumented, or deleting the assertions.

Sweep 1 is still running; later batches append to this table. `SWEEP_DONE` in the sweep log marks the
end of a pass, and this file should be rewritten from the log rather than hand-edited.

## Packet-gap audit - 2026-10-15

Each `tests/fixtures/**/SHA256SUMS` was reconciled against the files on disk. **Manifests disagree about
path convention** - some store paths relative to the manifest's own directory, some relative to the
repository root - and a first pass that assumed only the former reported nonsense such as
`hg_whp3: 4045 missing / 0 present` for a packet that is in fact 4041/4045 present. The corrected
audit accepts either convention; the numbers below are from the corrected run.

    packets with a real gap: 38
    manifest entries present: 15,330
    manifest entries missing:  1,626

**The decisive split is whether the packet is tracked at all**, because `tests/fixtures/hg_*/` is
blanket-ignored and a packet whose files were never force-added looks identical in a fresh checkout to
one whose files were removed afterwards:

| kind | packets | missing entries | reading |
| --- | --- | --- | --- |
| **entirely untracked** (`git ls-files` returns nothing for the packet) | 32 | 1,460 | Its `SHA256SUMS` is a **working-tree note, not repository evidence**. Git never held these files, and 0 tracked files in the pre-rewrite backup `5e8fcfd` confirms they were never committed in either history. The largest are `hg_wtbdep` (685), `hg_woffscorer` (208+19+11) and `hg_woffscorer2` (131). |
| **partially tracked** (some files committed) | 6 | 166 | These are repository evidence with a real hole. By size: `external_provenance_b5` 87 missing / 147 present / 148 tracked, `e3_bfcl_source` 24/63/64, `hg_wprov` 22/92/1, `upstream_provenance_e2` 15/32/33, `hg_trivia` 13/40/1, `hg_bfcl` 5/16/2. |

**Cause of the 1,460 is undetermined and is not attributed.** Untracked material leaves no trace in
git, so "never materialised here" and "removed later" are indistinguishable from the repository alone,
exactly the shape the workers recorded for the Reasoning Gym and HotpotQA receipts. What *is* measured
is that they were never committed in either history.

**The one with test impact is `external_provenance_b5`, and it is mechanically restorable.** All 87 of
its missing entries are `responses/*.body`; the packet is fully tracked; the 100 matching
`responses/*.receipt.json` files are present and each records the request URL, method, headers, UTC
times, status, response headers, byte count and SHA-256; and `SHA256SUMS` pins every body. One body is
recorded with the SHA-256 of the empty string, which is what its `HEAD` request legitimately produces.
Restoration is therefore a replay-and-verify operation, and `w-b5restore` is doing it.

**Test impact.** Most of these packets are not read by the suite. The ones that are fail without a skip
guard: `test_external_provenance_b5.py` (6 failures, all `FileNotFoundError` on
`responses/*.body`) and `test_ds1000_official_scorer.py` / `test_dgm_rule.py` (1 each, not yet
diagnosed). The two `hg_wujson` checks that depend on gone artifacts now **skip explicitly** instead
(commit earlier in this phase).

## Sweep 1 - continuing

Batches 0-60 of 16 done. Failures so far: the five ALFWorld-native, four `test_candidate_apply`, two
`test_chess3_diagnostic_actor`, one `test_chessbench_puzzles_strict_replay`, six
`test_external_provenance_b5`, one `test_ds1000_official_scorer`, one `test_dgm_rule` - **20 in total,
all in files untouched by any commit in this phase**, and all but the last three classified above.

## Worktree-only failures - do not mistake these for regressions

Two `tests/quality/test_isolation.py` tests behave differently in a fresh worktree than in the main
checkout, and both were checked against `main` before being attributed:

* `test_snapshot_covers_the_referee_not_the_candidate` asserts `.env` is in the snapshot inventory.
  `.env` is gitignored, so it exists only in the main checkout; this test **passes on `main` and fails
  in a worktree**. A worktree run must not read that as a regression.
* `test_the_harness_cannot_read_the_platform_or_its_answers` fails **on `main` as well**
  (`AssertionError: 平台的沙箱里还有东西:None`) and is therefore pre-existing, not worktree-specific.

## Fixed this phase, recorded so the pins are not "restored" by mistake

A lost reward file used to be published as `score: 0.0`. The branch, its false parity comment, the
reproduced fault injection and the corrected assertions are in `registry/w-vfix-validation.txt`.
`test_exec_verdict_missing_new_reward_is_zero` was renamed to `..._is_unmeasured_not_zero`, and three
security-property tests that had asserted `score == 0.0` incidentally now assert the property they were
written for. Reverting any of those to `0.0` would restore an infrastructure-failure-as-zero defect.

## Sweep 1 continued - the `docs/` deletion and a stale copy list, both fixed

The sweep's later batches found **21 more failures** that turned out to be two mechanical regressions
rather than mysteries, and both are now fixed (see `registry/w-docs2-validation.txt` and the
`docs:` commit):

* **The bulk `docs/` deletion contradicted the `.gitignore` whitelist.** `.gitignore` narrows `/docs/*`
  to 23 whitelisted paths meant to be kept; 17 of them had been deleted, leaving the ignore rules
  disagreeing with the tree. Sixteen distinct files are restored from `1825cd0e^`, which took
  `test_onboarding_doc.py` from 11 failed to **11 passed**.
* **One more deliverable was not whitelisted at all.** `docs/musique-output-contract.md` is opened by
  `test_musique_official_scorer.py` as a contract but was neither present nor whitelisted, which is why
  the sixteen-file pass missed it; it is restored, whitelisted and force-added, taking that file from
  10 failed to **106 passed**.
* **A staged-platform copy list was stale.** `test_parallel_tasks.py` copies an explicit list of
  `data/scaffolds/` modules into a minimal platform and never gained `scorer_isolation.py`, which
  `2c7e4ca7` added *before* this phase; the staged platform could not import
  `eval/verification/isolation.py`. The list now names it: 1 failed -> **12 passed**.

**Method warning for the scan that finds these.** A naive scan for referenced-but-missing `docs/*`
paths returns 168 hits and most are **false positives**: `docs/openapi/*`, `docs/standard/*`,
`docs/function_call*/*` and `docs/tutorial/*` are *third-party package* paths inside AppWorld and
friends, and `docs/dataset-blockers.json` / `docs/dataset-reviews/*` appear in historical records that
describe the registry's **old** location. Restore only what a test proves it needs, one file at a time,
and re-run that test.
* **Worktree runs lie about payload-dependent tests.** Running the same files in a fresh worktree
  produced `test_ordinary_run_receipt_codex237: 1 failed, 78 errors` where the sweep saw a single
  failure, because gitignored fixtures do not exist there. Triage in the main checkout, or copy the
  packets in first.

## `test_spreadsheetbench_classification_w_spread2.py` - 21 failures, pre-existing

`21 failed / 21 passed`. The exact cause is `scorer input does not belong to selected task` at
`eval/verification/verifier.py:524-528`: the spec carries a `scorer_input` binding with a `task_id`,
while the test calls `_verify(work, spec, "", ...)` with an empty one. **Not caused by this phase:**
the admission landed in `63606f42` (2026-10-15 11:13), which is *after* the test file's last commit
`5d15f54a` (05:27), and both are ancestors of `1825cd0e`. The repair needs a decision - the fixture
carrying the selected identity or the test supplying it - so it is recorded rather than patched with 21
blind assertion edits.

## Sweep triage, round 101 - the `reports/` deletion and a rate-limited restoration

* **`test_quiesce2_regressions.py`** failed with `FileNotFoundError` on `reports/w-quiesce2-evidence/audit.py`. That packet, and the `reports/w-quiesce-evidence/` tree its `audit.py` loads in turn, were removed by the bulk `reports/` deletion while a test still loads them by path. Both are restored from `1825cd0e^` (85 + 98 files, 0.70 MB + 0.59 MB, no file at or above 1 MB) and are tracked. Same class as the `docs/` whitelist contradiction: a bulk deletion removing evidence that tests load.
* That audit then reaches `tests/fixtures/hg_wpristine/closure/sh`, recorded in the packet's `SHA256SUMS` as `b3c1009e1b5c927e...` and **absent everywhere**: not on disk, and not in git in either the current or the pre-rewrite history, because that whole packet has zero tracked files. Nothing can be reconstructed from a digest, so the check now **skips explicitly** naming the absent file and its digest, following the B6/ujson convention. 1 failed -> 17 passed, 1 skipped.
* **`tests/fixtures/external_provenance_b5`**: 12 of 87 missing bodies are restored and independently verified, and the residue is **enumerated per body with a reason**. 70 of the 75 are HTTP 403 with `X-RateLimit-Remaining: 0` - **transient** unauthenticated GitHub rate limiting on a shared IP, not unobtainable. A first long-interval retry immediately restored and verified `responses/bfcl-blob-base_oss_handler.body` (23,199 bytes, digest match), so the rest are being retried at 120 s intervals in the background.
* **`test_livecodebench_official_scorer.py`** is slow enough that a single-file run does not finish in 60 s, and **`test_qa_dataset_contract.py`** takes minutes; both need a background run to triage rather than a foreground one.

## Correcting the sweep: batches that hit their timeout produce spurious failures

Three of the sweep's batches exited `rc=124`, meaning the 240 s per-batch timeout killed pytest rather
than pytest finishing. Failures reported from those batches are **not** reliable: the in-flight tests
are disrupted and appear in the summary.

Confirmed case: `test_qa_dataset_contract.py` was listed with **6 failures** by the sweep, but run on its
own in the main checkout it is **133 passed, 12 skipped, rc=0** in 152 s. A 12-file batch containing it
cannot fit in 240 s, so the batch was killed mid-file. The same caveat applies to anything else reported
from batch 12, 36 or 72 until it is re-run alone.

Two consequences for how this file is used: read the `=== batch N rc=` line before trusting that batch's
failures, and re-run every failure **on its own** before classifying it. `test_livecodebench_official_scorer.py`
is in the same position - a single-file run does not finish in 60 s, so it needs a background run to
triage rather than a foreground one.

## Two more `reports/` paths the bulk deletion broke, and what the restore does and does not verify

The sweep's last batch (`180`) died on a **collection error**, not a test failure, which is why it read
as `rc=2` with no tests run:

* `reports/w-chess3-control/` (2 files) is loaded by `test_chess3_diagnostic_actor.py`, which copies it
  into a workdir. Removed by the bulk deletion; restored from `1825cd0e^`.
* `reports/w-e6-evidence/` (829 files, 4.02 MB, largest 473,039 bytes) is pinned by
  `test_w_e6fix_cleanup.py`, which reads `preflight/bindings.json` at import time. Restored whole from
  `1825cd0e^` rather than as the single file the test reads, because the packet carries its own
  `SHA256SUMS` and a one-file tree would be a receipt that cannot be checked at all.

`python3 -m pytest -q tests/quality/test_w_e6fix_cleanup.py` -> **8 passed**, and
`test_chess3_diagnostic_actor.py` no longer fails on the missing directory. The chess3 runs then reach a
**different, real** failure (`KeyError: 'task_id'`) which is recorded below with the rest of that class.

**The restored packet's `SHA256SUMS` does not verify completely, and the residue is not reconstructible
from this restoration.** `sha256sum -c reports/w-e6-evidence/SHA256SUMS` reports 4 files that cannot be
read and 2 digest mismatches:

* absent and never tracked: `reports/w-e6-20261015T032920Z-72d6bfb0/samples.jsonl`,
  `.../033109Z-e7153160/appworld/recordings-retained/cf6abd2_2/appworld/service.log` (and the `032920Z`
  twin), and `reports/w-e6-lifecycle.md` - artifacts that lived only on disk;
* digest mismatch: `tests/fixtures/hg_we6/audit_packet.py` and `tests/fixtures/hg_we6/source_audit.py`.
  Both were **added after** the packet was written (`git show 1825cd0e^:<path>` -> *exists on disk but not
  in that tree*), so the packet pins versions of two fixtures that have since evolved. The packet is a
  historical record of the fixtures at collection time, not a claim that today's copies match; nothing is
  edited to make the digests agree.

## The `scorer_input.task_id` binding broke callers that build a record by hand

`63606f42` ("Bind QA scorer inputs to selected task identities") made `QASpec.verifier()` read
`record["task_id"]` and emit a `--task-id`/`--gold-sha256` pair plus a `scorer_input` binding. It updated
the adapters and added its own guard test (156 passed at that commit), but callers that construct a
minimal record - `verify_for({"gold": gold})` - were left behind, and they now raise
`KeyError: 'task_id'` at `data/scaffolds/qa/base.py:340`. Measured in the main checkout, this is the single
cause of:

| file | result |
| --- | --- |
| `test_chess3_diagnostic_actor.py` | 2 failed |
| `test_chessbench_selected_control.py` | 7 errors (fixture setup) |
| `test_chessbench_stepwise_runner.py` | 15 errors (fixture setup) |
| `test_chessbench_puzzles_strict_replay.py` | 1 failed |

`test_spreadsheetbench_classification_w_spread2.py` is the same class with a different symptom - the test
supplies an empty `task_id`, so `_verify` refuses with `scorer input does not belong to selected task`
before the scorer runs. The binding is deliberate and its guard test
(`tests/quality/test_task_bound_scorer_inputs_w_tbi.py`) is the authority, so the repair is to give these
callers the selected identity rather than to relax the binding.

A **second, independent** chessbench break is in that same guard test: `4556a9a5` ("native runtime:
generalise the sealed closure to scienceworld and chessbench_puzzles") gave `chessbench_puzzles` a
`native_runtime`, so `_verify(..., sandbox=False)` now short-circuits at
`eval/verification/verifier.py:474-475` with `native runtime requires sandbox=True`. Four cases in
`test_task_bound_scorer_inputs_w_tbi.py` fail with `IndexError: list index out of range` because the
intercepted `subprocess.run` is never called, and 12 cases in
`test_task_bound_native_inputs_w_tbi2.py` fail for the same reason. This is **not** a hole in the binding:
the `task_id` check at `verifier.py:525-530` runs on the native route too, before the sealed runtime is
admitted. The guard tests need to exercise the generic route (drop `native_runtime`) or the sandbox route,
not to have the binding relaxed.

## The `hg_we5` packet's central archive exists nowhere, so its completeness check cannot pass

`tests/quality/test_we5_equivalence.py` is **22 passed / 1 failed**, and the failure is
`test_complete_packet_including_wal_and_retained_attempts`: `audit.validate()` raises
`FileNotFoundError` on `tests/fixtures/hg_we5/preserved-initial-evidence.zip` at the first
sealed-member check (`tests/fixtures/hg_we5/verify.py:97`).

**Why it cannot be repaired.** `tests/fixtures/hg_we5/preserve_initial.py` writes that archive with
`zipfile.ZipFile(..., "x", ZIP_DEFLATED, strict_timestamps=False)` and then
`shutil.rmtree(old)` deletes the tree it archived, so the archive was the only copy of the
preserved initial evidence. `preservation.json` (63,330 bytes, present) records the archive's
digest and every member's digest, but a digest is not content. And this is not only a seal
problem: `verify.py:161-166` re-verifies the archive's digest and then reads **every member out of
the archive** to compare against `preservation.json`, so the packet's own substantive check needs
the file, not just its digest. Skipping the seal would not help.

Enumeration of the absence, so the claim is reproducible:

* `ls tests/fixtures/hg_we5/` - 18 entries, neither `preserved-initial-evidence.zip` nor
  `preserved-initial-partial.zip` among them; `SHA256SUMS:575-576` pins both, and
  `preserved-initial-evidence/` (the pre-archive tree) is absent too, because `preserve_initial.py`
  deleted it.
* `git log --all -- tests/fixtures/hg_we5/preserved-initial-evidence.zip` and
  `git ls-tree -r <rev> -- <path>` over the current and the pre-rewrite history return nothing:
  the whole packet is internal and `.gitignore`d, so it was never tracked.
* `find /mnt/20t/xubuqiang /tmp -maxdepth 6 -name 'preserved-initial*'` returns nothing, and the
  packet's own staged copy in a `test_isolation.py` work root
  (`/tmp/hg-iso4/.../platform/tests/fixtures/hg_we5/`) contains the same 18 entries without the
  archives. That staged copy is however how `verify.py` itself was restored byte-identically after
  an experiment touched it: its digest is `466332d9c0926aa5...`, matching `SHA256SUMS:591`.

**A second, independent staleness in the same packet, found while measuring the first.**
`evidence/source-pins.json` pins 21 sources and **6 no longer match**: five were rewritten by
`63606f42` (the `data.scaffolds.scorer_input` dependency) and `4556a9a5` - `data/datasets/bird_minidev.py`,
`data/datasets/bird_minidev/verify/check.py`, `data/datasets/spreadsheetbench.py`,
`data/datasets/spreadsheetbench/verify/check.py`, `data/scaffolds/qa/verify/check.py` - and the sixth,
`tests/fixtures/hg_wpristine/closure/sh`, is the file that exists nowhere at all, already recorded
above for `w-quiesce2-evidence`. So even with the archive present the packet would need a
pin-drift disposition before it could validate.

**Do not edit `tests/fixtures/hg_we5/verify.py` to skip any of this.** The packet seals its own
checker (`SHA256SUMS:591`), so an edit invalidates a seal that is itself the record of what
produced the packet. Both options were tried and rejected: adding a skip to its seal loop, and
replacing that loop in the test while letting `validate(seals=False)` run the rest - the second
reaches `verify.py:161` and fails on the same absent archive regardless. The test is left
unmodified and failing, which is the honest state; the enumeration above is the record. This is a
limit of a preserved evidence packet, not an open platform requirement, so it is deliberately not
entered in `registry/withdrawn-requirements.md`.

## The B5 body restoration invalidates any dataset run that is executing while it writes

The B5 replay writes bodies into the tracked tree (`tests/fixtures/external_provenance_b5/responses/*.body`).
`driver.py`'s run-integrity check hashes protected paths around every method call, so a replay that
writes during a run makes the run fail **correctly**:

```
FAILING RUN: protected files changed during method call:
  tests/fixtures/external_provenance_b5/responses/bfcl-blob-multi_turn_checker.body
PlatformTampered: {'added': [...], 'removed': [], 'modified': []}
```

Measured consequence, 2026-10-15: with the replay running, `test_dgm_rule.py::test_a_batch_becomes_one_curve_point_per_child`
failed with `driver exited 3` and `test_candidate_apply.py::test_a_half_finished_step_is_not_a_measurement`
failed with `"step failed" not in combined`, and `test_isolation.py`'s autouse
`_the_shared_checkout_is_never_edited` teardown raised `added: [...bfcl-blob-model_config.body]`. All three
pass once the replay is stopped, so none of them is a code defect. The replay also explains at least one
earlier sweep failure (`test_stop_semantics.py`, 1 failed in the sweep, **4 passed** run alone with the
replay stopped) and is a plausible contributor to others.

**Rule for this tree:** do not run the B5 replay concurrently with pytest or with any dataset run. The
replay is left **paused** (`kill -STOP`) rather than killed, so its 71 remaining bodies can be resumed with
`kill -CONT` when nothing else is executing; the residue and its per-body reasons are enumerated in
`reports/w-b5restore-replay2-20261015.jsonl`.
