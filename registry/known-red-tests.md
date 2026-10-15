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

## The sweep did not cover every file, and `test_integrity.py` was red in `main` the whole time

Found on 2026-10-15 while waiting on a concurrent run: `python3 -m pytest -q tests/quality/test_integrity.py`
is **1 failed, 4 passed** in `main`, and had been since the registry migration.

```
tests/quality/test_integrity.py:46: AssertionError
E       assert not ['registry']
```

`tests/quality/test_integrity.py::test_every_top_level_entry_is_classified` requires every top-level
entry of the checkout to be either in `eval/run/integrity.py`'s `PLATFORM` (hashed as referee-side) or in
its `NOT_PLATFORM` (explicitly not hashed, with a written reason). `1825cd0e` moved the registry out of
`docs/` into a new top-level `registry/` and never said which side it belonged to, so the guard failed.
`registry/` belongs in `NOT_PLATFORM`, on the same argument as `reports/`, and it is now there with that
reason: no path a run executes reads it (`grep -rn registry/dataset-blockers driver.py harnessgrad eval
data methods` returns only tests and tools), and hashing it would fail a certification every time a
blocker was recorded or closed. `test_integrity.py`: **5 passed**.

**Why the sweep missed it, and why that matters more than the one failure.** The sweep was
`for batch in chunks of 12 files: pytest <batch>`. A pytest **collection error aborts the whole batch**
(`Interrupted: 1 error during collection`), so every file *after* the bad one in that batch is silently
never run - and the sweep's per-batch summary then reports the files it did reach, which reads exactly
like a clean run. `test_w_e6fix_cleanup.py` (the deleted `reports/w-e6-evidence/preflight/bindings.json`)
is a confirmed collection error in that sweep, so at least one batch is known to have been truncated.
The per-file baseline pass that followed only re-ran the 25 files the sweep had *named* as failing, which
by construction cannot find a file that was never executed.

**Rule for this file.** A sweep is not evidence of coverage. Chunked sweeps must either run one file per
pytest invocation or keep going past a collection error (`--continue-on-collection-errors`), and the
covered-file list must be compared against `ls tests/quality/test_*.py` rather than inferred from the
absence of failures.

**`tools/quality_sweep.py` now does that**, so the rule does not depend on someone remembering it: one
pytest process per file, a per-file timeout, an outcome recorded even when a file cannot be launched
(`run_one` never raises, which is what keeps the coverage comparison from comparing a list with
itself), a loud note when `--only` makes the run a subset rather than a sweep, and a JSON report
carrying `discovered` / `selected` / `ran` / `missing` / `interrupted`. Exit status is 0 only when every
selected file ran and passed. `tests/quality/test_quality_sweep.py` pins those properties - including
that a launch failure is counted red rather than silently dropped, and that a subset run says out loud
that it is not evidence the suite is green. A per-file pass over all 194 files was launched on 2026-10-15 to check for other
files the chunking skipped; its results are appended below when it settles.

## The strict-decoding crash class: the runnable harnesses are fixed, the referee side is not

Measured 2026-10-15 and reported by the operator: one model-issued shell command printed a non-UTF-8
byte, the harness's `subprocess.run(..., text=True)` decoded it strictly, `UnicodeDecodeError` propagated
out of the harness, and the episode ended as a **zero for a task nobody finished**. The differential is
reproducible in one line:

```
$ python3 -c 'import subprocess; subprocess.run(r"printf \x27before\300\377after\x27", shell=True, capture_output=True, text=True)'
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc0 in position 6: invalid start byte
# with errors="replace": rc 0, stdout 'before\ufffd\uffffafter', and json.dumps still yields valid UTF-8
```

**Fixed here:** the eight `base_harness/` sites, which are the code `driver.py --harness <name>` actually
copies and runs - `loop/agent.py:685`, `loop_plain/agent.py:242`, `loop_rrsi_parse/agent.py:273`,
`cli_agent/agent.py:158`, `oracle/agent.py:71`, `dsh_agent/agent.py:419`, `codex_agent/agent.py:104` now
pass `errors="replace"`. `errors="replace"` rather than `surrogateescape`, deliberately: the harness writes
its trace as UTF-8, and surrogates would make the trace write itself fail. `tests/quality/test_harness_decoding.py`
pins the property over `base_harness/` and carries one written exemption
(`dsh_agent/agent.py:202`, the platform-authored Node loader probe whose single JSON line is parsed
immediately).

**Not fixed, and deliberately not a drive-by edit - the referee side keeps the same strict decode:**

* `eval/` (11 sites): `run/runner.py:506` (the no-sandbox harness run), `verification/verifier.py:722`
  (the check process), `containers/sandbox.py:463` (the native sandbox run),
  `containers/container.py:231,277,650`, `containers/harness_runtime.py:159,173`,
  `verification/native_runtime.py:119`, `admission/pilot_admission.py:273`,
  `policy/gaia_snapshot_attestation.py:111`. A check or CLI that prints non-UTF-8 crashes the *platform's*
  decode here, which is the same class of outcome - a task nobody finished - reached from the other side.
* `data/` (23 sites): the per-dataset `control.py` / `oracle_harness/agent.py` helpers, and four
  `verify/check.py` files (`ds1000`, `spreadsheetbench`, `agentdojo`). **`data/*/verify/check.py` are
  scored artefacts whose digests are recorded as custody in `registry/`** - `registry/w-spreadrt-runtime.md`
  and the parent's post-fix note pin `data/datasets/spreadsheetbench/verify/check.py` at
  `5c247413...` - so changing one is a scorer-identity change that needs its own reviewed pass with the
  custody records updated, not a sweep.
* `harnessgrad/` (6) and `tools/` (21) are tooling and lower risk; `current_harness/` (3) and `legacy/` are
  **derived or historical records** and must not be edited.

The guard's docstring carries the same scope and the reason it stops at `base_harness/`;
`EXCEPTIONS` is asserted non-empty and asserted to still match a real site, so the exemption cannot rot.

## The per-file pass found six files the chunked sweep never ran - all now fixed

The per-file pass launched on 2026-10-15 (one pytest invocation per `tests/quality/test_*.py`, results in
`/tmp/hg-allper.log` at the time of writing) confirmed that the chunked sweep's coverage gap was not
academic. Beyond `test_integrity.py`, six files were red in `main` and none had been reported:

| file | was | cause | now |
| --- | --- | --- | --- |
| `test_agentdojo_metadata_privacy.py` | 6 failed | `14c3a764` added `"immutable": True` to `agentdojo.SETUP`/`VERIFY`, and this privacy control pins the exact selected-lookup metadata | 63 passed |
| `test_data_layout.py` | 1 failed | `data/runtimes/` (the sealed-runtime pins, added by the native-closure work) was never classified, so every adapter importing `data.runtimes.NATIVE_PINS` was an unclassified data directory | 7 passed |
| `test_import_direction.py` | 2 failed | the same: `adapter-data: data.datasets.X -> data.runtimes` was not an allowed edge | 10 passed |
| `test_jericho_dataset.py` | 2 failed | one pinned "every content entry carries a payload", but the scorer-input shim (`63606f42`) ships two deliberately empty `__init__.py` markers; the other expected the phrase "game file", and the input binding now refuses the missing file first and names it | 16 passed |
| `test_quiesce_evidence.py` | 8 failed | the same absent `tests/fixtures/hg_wpristine/closure/sh` as `test_quiesce2_regressions.py` | 2 passed, 8 skipped |

**The two classification fixes are decisions, not cosmetics.** `data/runtimes/__init__.py` is pure data
with no imports, shared by adapters exactly like `data.scaffolds`; the guards now allow
`data.scaffolds.*` **and** `data.runtimes.*` for adapter code and classify `runtimes` as infrastructure,
with the reason written at both sites. `test_agentdojo_metadata_privacy.py` keeps its exact-comparison
property and simply includes the documented contract flag.

**The quiesce_evidence skip is deliberately narrow.** The first attempt put the condition on the module's
*autouse* fixture, which skipped all ten tests including the two that do not seal the packet - coverage
lost to make a failure disappear. The condition is now a helper called by exactly the two sealing tests,
so `2 passed, 8 skipped` is the honest state and the two still run.

Also confirmed benign or environmental: `test_claims_doc.py` exits `rc=5` (no tests ran, one module-level
skip), and `test_appworld_official_scorer.py` needs more than the pass's 300 s per-file budget.

`test_console.py`'s `test_the_curve_is_on_disk_before_the_run_ends` was **flaky by construction** and is
fixed here: it gave the driver a **6-second** window to write its first curve point while the box was
carrying a 40-job dataset pass, so a slow start failed a test whose property - *the curve is on disk
while the run is still going* - still held. The deadline is now 120 s and the wait loop also stops when
the process exits, so a real durability failure still reports through the same two assertions without
being confused with a slow start. 13 passed, in 19.8 s.

## A seventh sweep-missed red, and it is production: jericho's own control was broken

`test_dataset_controls.py::test_the_control_reaches_one_and_the_noop_reaches_zero[jericho]` failed in
`main` - the per-file pass found it, the chunked sweep did not. The oracle replays 17 reference commands
and the control then reports `reward -1` with `measured: null`, which the test correctly refuses:

```
E  AssertionError: jericho --oracle exited 1; a dataset whose own control fails is not gradeable:
E    task acorncourt (17 reference commands) / mode oracle / reward -1
E  stderr='CONTROL FAILED: expected reward 1, got -1'
```

**Cause.** `data/datasets/jericho/control.py:120` called the platform verifier without the selected task:

```python
verdict = _verify(workdir, verifier, "", sandbox=True, timeout_s=..., env=...)
```

`63606f42` made `_verify_existing` refuse a spec whose `scorer_input` binding does not match the `task_id`
it was called with (`eval/verification/verifier.py:525-530`), so with `task_id` omitted the binding
comparison failed, the verdict came back `unmeasured` with `score: null`, and this helper turned that into
its own `reward -1` sentinel. The platform was right to refuse; the helper was the stale caller - the same
class of omission `w-identcall` fixed on the test side and `w-scorerstub` fixed in
`data/datasets/alfworld/control.py`.

**Fix.** `task_id=record["task_id"]` is now passed, with the reason in a comment. This is the **only**
production caller of the platform `_verify` that omitted it (`grep -rn '_verify(' data/` finds three
adapter-local functions with a different signature and this one call site), and the control returns to
reward 1 for the oracle and 0 for the noop: `1 passed`.

## The per-file pass is complete: 14 red files, all accounted for

The pass over all 194 `tests/quality/test_*.py` files finished on 2026-10-15 (`ALLPER_DONE`). Fourteen
files reported a non-zero exit, and every one is accounted for:

* **twelve fixed** - the seven above plus `test_console.py`, `test_dataset_controls.py` and
  `test_quiesce_evidence.py` (all in the table earlier in this file);
* **one recorded limit** - `test_we5_equivalence.py`, the preserved archive that exists nowhere, already
  enumerated above;
* **one explained, not a defect** - `test_unified_budget.py` failed inside the pass because the *parent*
  was merging 18 commits into `main` while it ran, and `driver.py`'s integrity check correctly refused a
  checkout that changed under it (`PlatformTampered`). Re-run in a quiet tree afterwards:
  `test_unified_budget.py` + `test_console.py` = **16 passed in 204 s**.

Two method notes worth keeping. First, a per-file pass is itself a *writer-sensitive* measurement: any
commit to `main` during it invalidates the driver-based files in it, which is how `test_unified_budget.py`
appeared red. Second, the honest end state of this file is not "no reds" - `test_we5_equivalence.py` and
`test_external_provenance_b5.py` are red for recorded, enumerated reasons, and `test_isolation.py` carries
the known pre-existing failure.

## A shared assertion constant is a pin whose blast radius is every importer

`w-jerichoadm` narrowed `eval/run/runner.py:_refuse_unobserved_policies` so that a declaration is a
refused field only when *this process* does not apply it, and correctly corrected the guard pins it was
briefed on - four files, reported as 115 passed / 3 skipped, and independently reproduced by the parent.
Eight further tests still failed at integration, in `test_container.py` (6) and `test_services.py` (2),
because both import `EXEC_POLICY_FIELDS` from `tests/quality/policy_assertions.py`, and that constant
still named `env.agent_timeout_s` and `env.verify_timeout_s`. The same constant is imported by
`test_container_state.py`, `test_jericho_runtime_admission.py`, `test_web_gateway.py` and
`test_appworld_service_diagnosis.py` as well, so the stale set had a blast radius of six files and none
of them was in the worker's scope or its report.

`EXEC_POLICY_FIELDS` is now the four fields these fixtures are actually refused for - `env.cpus`,
`env.exec_defaults`, `env.memory_mb`, `env.network` - with the two timeout fields' absence explained
beside it (`eval/run/runner.py:41-72`: they flow through `phase_timeout` to the platform's own subprocess
deadlines, so they are not evidence a backend must supply). Verified after the fix:
`test_container.py test_services.py test_container_state.py test_verifier.py test_sandbox.py
test_parallel_tasks.py` = **136 passed**.

**Method note.** "N guard files pass" is only as wide as the files that were run. When a change moves a
value that a shared test module exports, grep for the symbol rather than for the files in the brief:
`grep -rn "EXEC_POLICY_FIELDS" tests/` would have found all six importers in one command.

## Closing the last journal-coverage blocker emptied a non-vacuity assertion

`test_every_journal_coverage_dataset_points_to_its_migrated_review` asserted `covered` was non-empty so
the guard could not become vacuous. All six journal-coverage blockers are now closed
(`fever`, `physicsquestions`, `reasoning_gym`, `sportsunderstanding`, `spreadsheetbench`, `strategyqa`),
so the live set is empty and that assertion had nothing left to assert.

It was **replaced, not deleted**: the guard now fails on a future journal-coverage blocker whose review
identity was never mapped (rather than raising `KeyError`), asserts every migrated review identity still
names a published dataset, and asserts there are still exactly six of them - which is what keeps the
parametrized content check below it from shrinking silently. The substitution is recorded in
`registry/w-close7-validation.txt` because editing a guard to fit a closure is the exact move that can
hide a defect.

## The definitive sweep, 2026-10-15 - 191/191 files, every red accounted for

`tools/quality_sweep.py --timeout 400` over all 191 `tests/quality/test_*.py` at `ce5c1dae`, on a
**frozen** tree (the earlier attempt was killed at 13/191 because the parent had committed to `main`
during it, and `data/`/`tests/` are hashed `PLATFORM` paths). Result: `discovered 191, selected 191,
ran 191, missing [], interrupted false`, 9 red files, 68.7 minutes wall. The point of the count is that
`ran == selected == discovered`: a sweep whose covered list is shorter than its selected list is not
evidence, which is the failure this tool exists to prevent.

Nine reds, in four classes:

* **Two load-induced, both verified green in isolation.** `test_appworld_official_scorer.py` hit the
  sweep's own 400 s cap (rc 124) after 7 passing tests - it spawns one appworld-venv subprocess per
  covered task with a 180 s internal timeout, and the operator's 40-job AgentDojo pass had load average
  above 15. `test_chessbench_stepwise_runner.py` failed 2 socket-deadline tests under the same load and is
  **18 passed in 31.84 s** when re-run alone. Neither is a defect; both are re-run in a quiet tree and the
  re-run is the record.
* **Three caused by merges earlier the same day**, all in *guards* rather than in product code, and all
  fixed: `test_gaia_snapshot_attestation.py` (7) and `test_gaia_preflight_codex175.py` (1) from the two
  field/decoding changes, plus `test_jericho_runtime_admission.py` (1) which encoded the pre-`w-jerichoadm`
  contract for `network: "none"`. See the two sections above.
* **Three red for recorded, enumerated reasons, unchanged by this sweep.** `test_we5_equivalence.py`
  (the preserved packet that exists nowhere), `test_external_provenance_b5.py` (71 raw bodies not yet
  restored; the replay is paused so it cannot write `tests/fixtures/` beside a running driver), and
  `test_isolation.py` (the known pre-existing failure).
* **One red that is a missing internal artefact**, below.

## `docs/claims.md` was deleted and is recoverable, not lost

`test_claims_doc.py` exits **5** (no tests collected) because `docs/claims.md` - the group's research
register, gitignored by the `/docs/*` narrowing and never committed - is absent. The module-level
`pytest.skip("docs/claims.md is internal ... and absent from this clone")` fires, so pytest reports
`1 skipped` and returns 5.

**It is recoverable, and was recovered and verified.** Three byte-identical copies (44,827 B, SHA-256
prefix `baa79fb748f9b4bd`, mtime 2026-10-13 22:08:40) survived inside staged-platform copies made by
`test_the_driver_exits_nonzero_0`:

* `/mnt/20t/xubuqiang/.hg-pytest/main-s8/bt/test_the_driver_exits_nonzero_0/platform/docs/claims.md`
* `/mnt/20t/xubuqiang/.hg-pytest/main-s8c/bt/test_the_driver_exits_nonzero_0/platform/docs/claims.md`
* `/mnt/20t/xubuqiang/.hg-pytest/race/test_isolation/test_the_driver_exits_nonzero_0/platform/docs/claims.md`

Copied into a throwaway worktree at HEAD, the guard is **11 passed** - the recovered register satisfies
every invariant it checks (attribution, claim, refutation condition, confounds, experiment, status, and
the scope-separation rules), so it is the genuine register and not a stub or a fixture. Restored into the
main checkout afterwards; because it is gitignored, `git status` still shows nothing, so the restore
cannot be committed by accident.

**Method note.** A pytest basetemp is not only a scratch directory: the staged-platform tests copy the
whole platform into it, which makes an old `--basetemp` the last surviving copy of an untracked internal
document. Before concluding that a deleted untracked file is unrecoverable, enumerate the basetemps -
`/mnt/20t/xubuqiang/.hg-pytest/` held three.

## Correction: the per-file pass's "14 red files, all accounted for" is not what its own log says

The definitive sweep (191/191, above) forced a re-read of the per-file pass that preceded it. That pass is
`/tmp/hg-allper.sh`, still on disk: one `timeout 300 python3 -m pytest -q` per file, appending any non-zero
exit to `/tmp/hg-allper.log`, which ends `ALLPER_DONE`. Its log holds **14 non-zero entries** - 12 `rc=1`,
1 `rc=124`, 1 `rc=5` - and the entry for `test_appworld_official_scorer.py` is:

```
tests/quality/test_appworld_official_scorer.py | rc=124 | .......
```

That is a **300 s timeout after 7 passing tests**, not a failure, and it is the same signature the sweep saw
at its own 400 s cap. The narrative written at the time ("Fourteen red files, all accounted for: twelve
fixed...; one recorded limit - `test_we5_equivalence.py`; one explained - `test_unified_budget.py`") does not
match: the timeout and the `rc=5` skip are not in that accounting, and `test_external_provenance_b5.py` and
`test_isolation.py` - both `rc=1` in the log - are instead described in a later section as deliberately
red. So the pass's *count* was right and its *accounting* was not.

The lesson is the same one the sweep tool exists for, one level down: **a bounded per-file pass cannot
distinguish "this file is red" from "this file did not finish", and a summary that folds the two together
reads clean.** Anything a pass timed out must be re-run with a cap larger than its runtime before it is
called green. Both timeouts in this history needed that, and one of them had a real defect behind it.

## `test_appworld_official_scorer.py::test_platform_control_arms` - 2 long-standing failures, policy-level

With a cap large enough to finish (5400 s; the file needs **1264 s**), the file is `2 failed, 30 passed`:

```
FAILED test_appworld_official_scorer.py::test_platform_control_arms[--oracle-1.0]
FAILED test_appworld_official_scorer.py::test_platform_control_arms[--noop-0.0]
control refused: verifier did not produce a measured official test result
```

**Not a regression from this phase's merges.** The same command fails identically in a worktree at
`207c5224`, which is *before* both `w-jerichoadm` (which narrowed the refusal table) and `w-decode2`. It
was also invisible to the pass above because it timed out there.

The cause is structural, not a bug in either file. The test runs
`data/datasets/appworld/control.py --oracle|--noop --task-id e85d92a_1 --platform --no-sandbox`, and
AppWorld's `ENV` declares `kind: "exec"`, `cpus`, `memory_mb` and `network: "services"`. Admission refuses
every one of those on the native path, so `run_one` returns no verdict at all:

```
policy_fields: ["env.cpus", "env.exec_defaults", "env.memory_mb", "env.network"]
stage: admission, reason: backend_observation_unavailable, measured: false
```

`--no-sandbox` is what makes it unsatisfiable: a service-backed `exec` task cannot be run without the
container and service machinery that the very same declarations describe. Three honest resolutions, none
taken here because choosing between them is a judgement about what the control is for:

1. run the arm with the sandbox (the images are pinned by digest, so this is the real path the control is
   meant to exercise);
2. assert the refusal instead of a score, which turns the test into a guard on admission rather than on the
   scorer; or
3. pass a diagnostic authorization, which makes it a staged diagnostic rather than an ordinary control.

It is left **red and unmodified** on purpose: rewriting a guard to match a refusal would hide the fact that
the platform can no longer run this control shape at all, and that is the thing a reader needs to see.

## Second definitive sweep, 2026-10-15 - 193 files, and the cap that had been hiding a result

Re-run on frozen `f66cd83f` after the operator's `59cbf662` and the `w-banhung` integration, with
`--timeout 1800` instead of 400. Result: `discovered 193, selected 193, ran 193, missing [], interrupted
false`, **5 red**, 89.1 minutes. The per-scope count rose from 191 to 193 because
`test_signal_termination.py` and `test_timeout_w_banhung.py` are new; both ran green in it (10 and 32
passed), as did the four files repaired in the first sweep: `test_claims_doc.py` **11 passed** (the restored
register turned a skip into real assertions), `test_gaia_snapshot_attestation.py` **88 passed** (was 7
failed), `test_gaia_preflight_codex175.py` and `test_jericho_runtime_admission.py`.

**The cap change is the point.** `test_appworld_official_scorer.py` ran to completion for the first time -
1538.6 s - and reported `2 failed, 12 passed`. At the old 400 s cap it was `rc=124` with seven dots and no
result, which is how two genuine failures stayed invisible through an entire per-file pass. **A per-file
timeout is not a red and must never be counted as one or as a pass; it is a file whose result is unknown.**

The five reds, all previously recorded and none new:

| file | result | standing |
| --- | --- | --- |
| `test_appworld_official_scorer.py` | 2 failed, 12 passed (1538.6 s) | the long-standing `test_platform_control_arms` admission conflict, filed above |
| `test_chessbench_stepwise_runner.py` | 2 failed, 16 passed (28.8 s) | load-induced: **18 passed in 31.8 s** when re-run alone. Both are socket-deadline tests (`test_reconnect_cannot_reset_session_allowance`, `test_trickled_partial_frame_cannot_extend_absolute_socket_deadline`), i.e. wall-clock assertions measured on a machine that was running the operator's 40-job pass |
| `test_external_provenance_b5.py` | 5 failed, 1 passed | 71 raw bodies still unrestored; the replay is paused because it writes `tests/fixtures/` while a sweep reads it |
| `test_isolation.py` | 1 failed, 15 passed (184.2 s) | known pre-existing |
| `test_we5_equivalence.py` | 1 failed, 22 passed | the preserved packet that exists nowhere; enumerated limit |

Zero unexplained reds across 193 files, and `ran == selected == discovered` - which is the only property
that makes the number mean anything.
