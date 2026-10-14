# Decision: enforcement-proof requirements are out of scope

**Decision (operator, 2026-10-15), following the `paired-filesystem-quotas` withdrawal of the
same day:** requirements whose *only* content is "prove that some enforcement mechanism is
really in force" are **not** preconditions for running a dataset. Three were reviewed under
that heading and withdrawn:

| Blocker | Where | What it demanded |
| --- | --- | --- |
| `official-scorer-identity` | shared | that source call sites *prove* fresh official evaluator execution and release/runtime identity |
| `snapshot-owned-cleanup` | shared | proof of bounded snapshots, exact owned absence and atomic lease closure |
| `prevent-platform-writes` | `scienceworld` | independent proof that mount enforcement is effective and platform provenance immutable |

## The reasoning, which is one argument applied three times

The platform already **performs** each of these; what was demanded was evidence that the
mechanism *cannot fail*. That is a different and much stronger claim, and it was raised in
each case without a measured failure behind it. The operator's position is that this is
over-defensive: the failure modes are not ones they have encountered in empirical work, and
the cost is that every dataset carries a gate that no amount of ordinary correct operation
can ever close.

The quota withdrawal is the worked example and the reason these three fell with it: the
requirement was not "make cleanup work", it was "prove cleanup cannot leak", and the price of
proving it was a root remount of two shared filesystems.

## What is still done, and must not be read as withdrawn

Withdrawing the *proof* requirement is not withdrawing the *behaviour*:

- scrapers and verifiers still rematerialize inputs, still snapshot, still clean up, and
  still fail closed when they cannot (`eval/admission/runner_admission.py::admit_cleanup`,
  and the lease `quarantine` action when an observation is incomplete);
- each dataset review still records **metric identity** — what the number is and where it
  comes from — because that is what the reviews are for, and `official-scorer-identity`'s own
  `next_action` asked for documentation, not enforcement. The documentation continues; the
  blocker that gated the datasets on *proof* does not;
- the realtime refusal contract is untouched: a declared policy that needs a backend
  observation this checkout cannot supply still refuses before staging.

## What a reader should conclude

These mechanisms are **used, unproven, and accepted**. That is a materially different
statement from "verified", and it must not be upgraded in later summaries. If a mechanism is
ever observed to fail, the failure is the evidence that was missing, and the requirement can
be re-raised with something behind it.

The supporting reviews stay checked in and unedited, including
`docs/filesystem-quota-backends.md`, `reports/scorer-closure-codex170-report.md` and the
lifecycle material in `docs/task-233-quota-readback-authentication.md`.
