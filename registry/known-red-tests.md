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
