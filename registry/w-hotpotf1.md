# w-hotpotf1: answer F1 reward with answer EM exactness

FOUND — Reused the scoring, disclosure and guard structure from `wg-w-hotpotqa`,
observed at `eaf3298e1d4cd17db2c7c60b8d0bd9a4ddec1db2`, after reading its diff
against its own merge base. Its three code files had no intervening changes in
this worktree. Exact source-tip, merge-base and diff commands/outputs:
`registry/w-hotpotf1-validation.txt:293`, `registry/w-hotpotf1-validation.txt:301`,
`registry/w-hotpotf1-validation.txt:375`.

FOUND — Published `reward` is answer F1; `correct` remains `bool(em == 1.0)`.
The recorded name is `HotpotQA answer F1 (not official joint)`, with
`reward_metric=answer_f1` and `joint_metrics_role=diagnostic_only`. Answer EM/F1,
support EM/F1 and joint EM/F1 remain in the legacy `official` evidence envelope;
`why` explicitly identifies the reward and disclaims the official joint metric.
Sources: `data/datasets/hotpotqa.py:19`, `data/datasets/hotpotqa.py:52`,
`data/datasets/hotpotqa.py:57`. The shared verifier writes that reward and retains
the envelope in per-task evidence (`data/scaffolds/qa/verify/check.py:278`).

FOUND — The same synthetic prediction, `"answer extra"` against `"answer"`,
receives reward **0** from the source branch and **0.6666666666666666** after
this correction; both retain EM=0 and `correct=false`. One matching token gives
P=1/2, R=1 and F1=2/3. Exact input and outputs:
`registry/w-hotpotf1-validation.txt:323`. Article removal means `"answer"`
against `"The answer"` instead has EM=F1=1, which the guard documents rather
than treating the article as a gold token. Sources:
`data/scaffolds/qa/evidence_scorers.py:32`,
`registry/w-hotpotf1-validation.txt:327`,
`tests/quality/test_qa_evidence_contract.py:113`.

FOUND — The question-only input and goal remain unchanged. Missing evidence
remains a valid prediction with support/joint zero, while the goal still asks
for supporting facts. The disclosure retains the source branch's distinction
between local answer reward and official joint metrics. Sources:
`data/datasets/hotpotqa.py:3`, `data/datasets/hotpotqa.py:49`,
`data/datasets/hotpotqa.py:76`, `data/datasets/hotpotqa.py:78`.
The AST comparison confirms every QASpec keyword and all adapter code outside
the docstring, metric label and scoring function are unchanged against starting
HEAD (`registry/w-hotpotf1-validation.txt:328`).

FOUND — No published reward uses a joint value. The enumerated `joint_em`
search covers exactly the adapter and two changed guards: matches are diagnostic
calculation/evidence and assertions over that evidence. The sole reward-return
AST is `f1`. Exact search/output and AST result:
`registry/w-hotpotf1-validation.txt:339`,
`registry/w-hotpotf1-validation.txt:330`. The guards derive answer, support and
joint expectations and check serialized reward independently of support:
`tests/quality/test_measurement_coverage_hg_b3.py:65`,
`tests/quality/test_measurement_coverage_hg_b3.py:89`.

FOUND — Requested suite totals: **113 passed, 4 skipped before → 124 passed,
4 skipped after**. Exact commands, outputs, skip reasons and immediate removal
of each `/tmp/hotpotf1-*` basetemp are recorded at
`registry/w-hotpotf1-validation.txt:16` and
`registry/w-hotpotf1-validation.txt:215`. The intermediate failed assertion
attempt is retained there too. The blocker checker returns
`{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}`
(`registry/w-hotpotf1-validation.txt:354`).

FOUND — HotpotQA remains closed under reading A; the registry keeps no active
HotpotQA blocker and preserves the historical incomplete/null-effect record.
This is a scoring-policy correction, with no new measurement or requested
registry integration. Sources: `registry/dataset-blockers.json:418`,
`registry/dataset-blockers.json:426`,
`registry/blocker-closure-assessment.md:248`,
`registry/blocker-closure-assessment.md:266`.

ABSENT — Modifications within the enumerated scope of AGENTS.md, registry,
closure assessment, journal, tracked `data/**/verify/check.py` files, and the
dataset-blocker/closure guards: the exact `git diff --name-only` commands return
no paths (`registry/w-hotpotf1-validation.txt:350`,
`registry/w-hotpotf1-validation.txt:630`). Shared scoring formulas are also
byte-identical to starting HEAD (`registry/w-hotpotf1-validation.txt:337`).

UNKNOWN — No model, GPU, network, dataset diagnostic/pilot or upstream scorer
execution was performed. Actual reward distributions, live isolation/cleanup
and downstream aggregate/UI/export metric labeling remain unverified. Four
skipped cases are not passes. The complete unverified scope is in
`registry/w-hotpotf1-validation.txt` under EXPLICITLY NOT VERIFIED.

The most important reviewer uncertainty is whether downstream comparisons
preserve the answer-F1 metric identity and avoid comparing it to historical
joint rewards; coverage here reaches adapter output and the shared per-task
verifier evidence path (`data/scaffolds/qa/verify/check.py:278`).
