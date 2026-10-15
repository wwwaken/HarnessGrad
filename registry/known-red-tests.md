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
