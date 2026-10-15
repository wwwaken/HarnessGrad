# w-adaptfid1: BFCL irrelevance parsing and 2Wiki evidence routing

Implemented the two adapter changes with fabricated regression inputs. The final
regression suite passes all 29 cases; the full permitted suite remains red on 23
historical BFCL custody checks. Exact commands/output are in the validation transcript
(registry/w-adaptfid1-validation.txt:1257; registry/w-adaptfid1-validation.txt:1492).

## FOUND: scoring behavior and regression results

BFCL now counts a line only when it is a bare/dotted ASCII identifier or contains an
identifier-shaped call. Other prose contributes no predicted function. `NONE`, no-tool
markers, blank output, namespace normalization, case and duplicate behavior remain;
a call-shaped line stays verbatim so `compute(x=3)` still fails a simple name-only task.
Arguments are neither parsed nor executed. Accepted/rejected forms are documented in
`data/datasets/bfcl_v3.py:199`; the unchanged name-only comparison and explicit
nonofficial metric are at `data/datasets/bfcl_v3.py:224`. The existing call-syntax
rejection is pinned by `tests/quality/test_bfcl_selected.py:159`.

For empty irrelevance gold, the fabricated prose `there is no suitable function`
scored **0 before / 1 after**. It still scores 0 for nonempty simple gold. Named tools
and call-shaped lines still score 0 on irrelevance. Tests cover mixed prose/tool lines
and the platform markers (`tests/quality/test_bfcl_adaptfid1.py:7`,
`tests/quality/test_bfcl_adaptfid1.py:23`,
`tests/quality/test_bfcl_adaptfid1.py:31`; pre-fix failure output:
registry/w-adaptfid1-validation.txt:1060; post-fix output: registry/w-adaptfid1-validation.txt:1254).

2Wiki declares **`EVIDENCE_AWARE = True`**, matching the marker convention used by
FEVER and HotpotQA (`data/datasets/twowikimultihopqa.py:88`,
`data/datasets/fever.py:23`, `data/datasets/hotpotqa.py:33`). The shared verifier thus
calls its structured scorer (`data/scaffolds/qa/verify/check.py:251`).
The shared schema permits only answer and `predicted_evidence` support pairs; it cannot
carry 2Wiki's evidence triples (`data/scaffolds/qa/prediction.py:9`,
`data/scaffolds/qa/prediction.py:22`). I chose **named refusal for that pair schema**,
using `twowiki_prediction_json_pair_schema_unsupported` rather than inventing a
pair-to-triple conversion (`data/datasets/twowikimultihopqa.py:485`).

For correct-answer shared submissions with empty, correct or wrong evidence pairs,
the old check returned legacy reward **1**. The fixed check returns **exit 3,
measured=false, no reward file**, with the named reason, even if a legacy answer file
also exists. Shared structured answer-only objects now get **Joint F1=0**, answer F1=1,
because support/triples are missing. These are observed via the actual shared check
entry point on fabricated gold (`tests/quality/test_twowiki_adaptfid1.py:42`,
`tests/quality/test_twowiki_adaptfid1.py:53`; registry/w-adaptfid1-validation.txt:1060;
registry/w-adaptfid1-validation.txt:1254).

The supported `answer.txt` cases remain legacy text reward 1, full JSON Joint F1 reward
1, and answer-only JSON Joint F1 reward 0 in the synthetic regressions
(`tests/quality/test_twowiki_adaptfid1.py:65`). Existing materialized-verifier coverage
also ran (`tests/quality/test_twowikimultihopqa_structured.py:285`;
registry/w-adaptfid1-validation.txt:1261).

## FOUND: before/after suite counts and remaining failures

| Execution | Passed | Failed | Skipped | Deselected |
| --- | ---: | ---: | ---: | ---: |
| Existing BFCL + 2Wiki + harness-decoding, before | 254 | 0 | 11 | 2 |
| Final 29 regressions against original HEAD sources | 19 | 10 | 0 | 0 |
| Final 29 regressions against fixed sources | 29 | 0 | 0 | 0 |
| All discovered BFCL + 2Wiki + harness-decoding, after | 260 | 23 | 11 | 2 |

Exact outputs: registry/w-adaptfid1-validation.txt:46,
registry/w-adaptfid1-validation.txt:1250, registry/w-adaptfid1-validation.txt:1257,
registry/w-adaptfid1-validation.txt:1492.
The 11 skips come from the existing BFCL `_RECORDS` guard; its message is not a
filesystem inventory. The two deselections are the real 2Wiki platform-control cases,
excluded explicitly to obey the no-dataset-run constraint (same transcript blocks).

All 23 final failures are historical BFCL source pin checks: 22 in the containment
suite and one in reachability. They stop at old bytes/digests; no frozen receipt was
rewritten. The pin gate is at `tests/fixtures/hg_bfclcontain/control.py:78`; the graph
comparison is at `tests/quality/test_bfclguard_reachability.py:51`; the exact failed
node IDs and observed digests are retained in registry/w-adaptfid1-validation.txt:1261.
The final BFCL source digest is
`4c022a4cd6dfaa502fa48082e5f4509b7724d72edfb5476d2d668344f9a5b381`
(28,684 bytes), while both frozen inventories retain
`de8f7efb844c39fa79632d42171d537e488f055dae7b5e1bceb583368e3bce17`
(28,188 bytes), observed in registry/w-adaptfid1-validation.txt:1535.

## FOUND / ABSENT / UNKNOWN: verifier custody and scope

**FOUND:** Before editing I searched registry references with
`rg -l -F 'data/scaffolds/qa/verify/check.py' registry -g '*.json' -g '*.md' -g '!w-*-validation*'`.
The reproducible full tracked-registry audit then enumerated `git ls-files registry`
(114 tracked files) and reported every path-reference match
(registry/w-adaptfid1-validation.txt:1518). Historical BFCL fixture inventories pin the
shared verifier, whose actual and pinned digest agree:
`ec603e0d7fc655473dde92260d70cefefc0dd107eaa0d9273df1e7eeb0d0763c`
(14,936 bytes; registry/w-adaptfid1-validation.txt:1535). No verifier edit was
needed; this is the unchanged digest, not a new custody attestation.

**ABSENT in the enumerated scope:** The exact verifier path does not occur in
`registry/dataset-blockers.json`. Its current SHA256 literal occurs in none of those
114 tracked registry files. This is only a literal path/digest search, not a claim
that all possible custody representations are absent
(registry/w-adaptfid1-validation.txt:1533).

**FOUND:** The audit compared HEAD bytes for every tracked `data/**/verify/check.py`,
`data/aggregation_policies.json`, blocker index, journal and AGENTS.md: all unchanged.
Only `parse_prediction` and `score_prediction` differ among adapter function/class ASTs;
all task-rendering/input functions, including `_goal`, are unchanged
(registry/w-adaptfid1-validation.txt:1496). Aggregation remains the declared measured-task arithmetic
mean and, for 2Wiki corpus metrics, ordered macro mean over gold rows
(`data/aggregation_policies.json:6`, `data/aggregation_policies.json:32`).

**UNKNOWN / not verified:** Newly edited BFCL bytes have no successor historical
containment/reachability receipt; the lexical call-shape rule is not a full upstream
AST-equivalence proof. No model/GPU/network, new dataset/driver run, production/H0
measurement or runtime enforcement claim is supplied. Full exclusions are listed in
`registry/w-adaptfid1-validation.txt` under “Explicitly NOT verified”.

The blocker index itself was untouched; its checker returned exactly
`{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}`
(registry/w-adaptfid1-validation.txt:1557). No blocker/status update or proposal is needed for this
adapter-only fix.

**Primary reviewer uncertainty:** certify the changed BFCL parser with fresh successor
source-custody evidence before treating the historical containment/reachability
findings as applicable to it; retain the old inventories and their red checks as evidence.
