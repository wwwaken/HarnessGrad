# Task 20: DGM and HyperAgents archive alignment

This branch keeps the existing method entrypoints runnable and adds method local
pure components under `methods/dgm/` and `methods/hyperagents/`. No platform
protocol, driver, evaluator, schema, or main checkout files were changed.

## Pinned source and exact findings

| Method | Original behavior | Restored here | Pending / deliberate gap |
|---|---|---|---|
| DGM | `methods_src/dgm` commit `bd7c0773c8f7d17549a3b67e7d783c47f7fba407`; `DGM_outer.py:56-109` samples parents with replacement using `sigmoid(10*(score-.5))/(1+children)`, `:174-188` defaults to `keep_all`, `:192-219` escalates full evaluation from eligible archive scores; `self_improve_step.py:28-32` uses o1 diagnosis and the coding agent uses Claude 3.5 Sonnet | `methods/dgm/archive.py` has immutable nodes, multiple `parent_refs`, child counts, seeded sampling, parallel sampling, and separate `keep_all` / initial-score `keep_better`; `methods/dgm/staged_eval.py` tracks small→medium→full and budget consumption; run records diagnosis/editor role refs, selected parent and deployment status | Original DGM's diagnosis prompt sees gold/private patch and test logs. These cross the platform exam boundary and are intentionally withheld. The trusted runtime still owns actual deployment. |
| HyperAgents | `methods_src/hyperagents` local source (no `.git` checkout); `utils/gl_utils.py:32-59,511-584` has staged fraction, agent/ensemble max, and `random/latest/best/score_prop/score_child_prop`; `select_next_parent.py:49-57` computes statistics then uses uniform `random.choice`; `generate_loop.py:587-589` overrides Polyglot meta to Claude 3.5 Sonnet | `methods/hyperagents/archive.py` preserves selector branches, seeded multi-child sampling, immutable parent refs, independent task/meta patch identities and rollback identities; `staged_eval.py` records staged fraction without rescaling raw score; run records task/meta refs, Polyglot meta override, selection vs pending deployment | Docker generation loop, multi-domain aggregation, ensemble max and actual runtime rollback/deployment remain pending platform capabilities. `HG_HYPERAGENTS_SELECT=random` explicitly selects the uniform branch. |

## Semantic decisions

Archive membership is separate from parent eligibility. DGM `keep_all` retains a
compiled low-scoring or rejected node for auditability, while rejected or
unmeasured nodes are excluded from the next parent candidate set. `keep_better`
compares against the original score minus `noise_leeway`, matching the source;
it does not compare against the best node. Parent draws are seeded and sample
with replacement so multiple children can share a parent. Node and artifact
objects are frozen; a child carries explicit parent references and an artifact
identity rather than mutating an ancestor.

Staged evaluation is represented as a schedule and an observed evaluation record.
Scores remain study scores until a trusted full evaluation; HyperAgents' staged
fraction is metadata and is never multiplied into a raw score. A scheduler returns
the next stage and consumes the stage budget once, with truncation explicit.

Selection and deployment are different fields. A method can nominate one or more
parents or children, but `deployed_node` stays null with
`pending_trusted_runtime` until the platform runtime confirms deployment. This
avoids turning method-reported selection into a platform fact.

DGM has two upstream roles: `o1-2024-12-17` diagnosis and Claude 3.5 Sonnet
editing. The platform port records the role and marks diagnosis as
`not_invoked_in_platform_port`; it does not copy private gold inputs. HyperAgents
task and meta patches are independent. A task-only patch cannot silently become a
meta patch, and rollback is represented as a separate identity.

## Focused offline evidence

`tests/quality/test_archive_alignment.py` covers multiple parents/children,
deterministic seeded draws, child-count weighting, keep-all versus keep-better,
staged→full budget consumption, random/best/uniform selector branches, raw staged
score handling, task-only/meta-only patch identity, and rollback identity.

The focused command passed:

```text
38 passed in 16.10s
```

This is offline component evidence only. It is not a DGM, HyperAgents, SWE-bench,
Polyglot, or other benchmark outcome, and no mock score is advertised as a real
benchmark result.

## Requests to Task 18 / trusted runtime

1. Accept immutable `parent_refs[]` and artifact IDs in the event envelope, with
   multiple parents and sibling children preserved rather than linearized.
2. Expose staged/partial/full evaluation completeness and budget consumption as
   platform facts; keep method-reported score and platform-measured score separate.
3. Add typed selection (`selected_node_ids[]`) versus deployment events, including
   zero, multiple, tentative, and rollback outcomes.
4. Preserve task/meta role refs and patch identity (including independent rollback)
   through archive lineage. The runtime should not infer deployment from a method's
   selection report.
5. Provide an explicit trusted capability for DGM diagnosis and HyperAgents
   generation rollback when those loops are enabled; until then these ports report
   `pending_trusted_runtime`.

## Compatibility limits

Old stdin/stdout method ports remain available. Their existing one-call editor is
still the shared editing shell; the new components do not claim to reproduce
upstream Docker scaffolds, foundation-model performance, or private exam signals.
The old adapter records method-reported scores as such. A future runtime can consume
the new fields without changing the method-specific selection algorithms.

