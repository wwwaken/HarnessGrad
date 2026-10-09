# RRSI fidelity alignment

This branch pins the audited upstream source at `Study/RRSI` commit
`e4d1a7a0388e02b388bc40eb0a125fcfc7123f8d`. The checkout has unrelated local
uncommitted probe files; those are outside this change. The HarnessGrad entry
point remains a **port**. The restored pure components below do not claim native
RRSI reproduction until the scaffold, model, evaluator, split, and runtime loop
match an upstream instance.

## Native phase map

| phase | upstream evidence | current port / fidelity core |
|---|---|---|
| select context | `rrsi/loop.py:233-288` | port reconstructs history from the platform channel |
| execute incumbent/candidates | `rrsi/evaluate.py:28-41,122-128`; `loop.py:299-302` | evaluator remains a platform axis; no native `k` loop in the port |
| organize feedback | `rrsi/analyst.py:28-38,52-102,121-197`; `rrsi/digester.py:28-35,75-109` | role templates are preserved in `fidelity.py`; current one-candidate entry point does not dispatch native digesters |
| propose changes | `rrsi/loop.py:273-297`; `rrsi/propose.py:28-43,60-137` | old prompt remains runnable; full role contract is available in `ROLE_PROMPTS` |
| build and validate | `rrsi/critic.py:28-40,50-147`; `loop.py:498-576` | port keeps deterministic/model critic and bounded repair; smoke is platform-owned |
| evaluate candidates | `rrsi/loop.py:290-302,578-605` | pending trusted study-only `evaluate_many` |
| select/deploy | `rrsi/selection.py:28-39,81-137`; `loop.py:304-344` | `select_candidates` restores admissibility, pool argmax, and incumbent retention offline |
| stop/continue | `rrsi/driver.py:28-34,54-99` | platform loop owns continuation; no native frontier/worktree loop in the port |

The native defaults are `T=20, k=2, m=2, b_min=1, b_max=4, w=3,
m_draft=1, beta0=.10, beta1=40, w_s=100, w_c=15, w_n=.5, n_prune=4`, with
proposer, analyst, and critic defaulting to `claude-opus-4-8`
(`rrsi/config.py:56-85`). Domain files may override these and the policy model;
this work does not silently select an API model.

## Independent restored components

`methods/rrsi/fidelity.py` contains only deterministic, offline functionality:

* separate digester, analyst, proposer, and pre-evaluation critic templates;
* calibration from repeated unchanged-base scores or a labeled multi-trial
  score spread (`delta = z * sqrt(2) * sd`), with no one-trial zero-band guess;
* RRSI's floor, two cost branches, structural novelty, gate handling, and
  stable highest-score selection over an `m`-candidate pool;
* `parent_id == incumbent_id` and `winner_id is None` when every candidate is
  rejected or inadmissible.

The module has no task IDs, traces, evaluator, or held-out dataset handle.
Callers must supply study-side measurements. This makes the held-out boundary
testable: no role prompt or selection function can receive exam data implicitly.

## Capability request before deployment

Task18/runtime needs a typed study-only interface equivalent to:

```text
evaluate_many(parent_ref, candidate_artifacts[], study_task_ids, k)
  -> [{candidate_id, per_task_trials, aggregate_score, token_cost, missing}]
select_deploy(incumbent_id, measurements, rule_config)
  -> {selected_id | null, retained_incumbent, decisions[]}
```

The runtime must stage all candidates from the same incumbent, expose only
`study_task_ids` to proposer/critic/evaluator, and permit `selected_id=null`
to retain the incumbent. A rejected or unevaluated candidate must be unable to
become the next parent. Held-out evaluation should be a separate post-selection
operation whose results are absent from all role prompts and decisions.

## Offline validation

```text
PYTHONPATH=methods pytest -q tests/quality/test_rrsi_fidelity.py tests/quality/test_rrsi.py
20 passed in 0.45s
```

The fixtures prove that a higher-scoring candidate can lose to a critic gate or
cost rule, that all rejected candidates retain the incumbent, that calibration
uses the expected square-root-two factor, that role prompts remain distinct,
and that the existing mode-A port's train-side rule, pruning, critic, and
trajectory behavior remain covered.
