# BFCL Simple AST contract review — codex166

Status: **blocked on pinned public evaluator source in the authorized workspace**.
The current scorer still grades function names. No official full-call AST scorer
was implemented or claimed by this review.

## Scope and provenance

- Worktree: `/tmp/hg-codex-166`, initially clean, at
  `10e983fc5fcb006c5afdbce1ef851dad71e953f2`.
- Reviewed adapter SHA-256:
  `237d0ca00f53be54b51845767ecc5b69b79bc8ec956a937416b416b9e4d55d79`.
- Existing fabricated privacy test SHA-256:
  `098c0cf2f37a4ca81eee5bda4db4d8270e29600c91af5f727ccd73b078db342e`.
- No downloads, release question/answer payload reads, heldout reads, model calls,
  endpoint access, or H0 runs. All test payloads were fabricated; platform-control
  tests replace `eval.runner.run_one` with a local stub.
- Filesystem inventory stayed inside the worktree, did not follow symlinks, and
  inspected filenames rather than dataset contents. Test scratch files stayed in
  `.tmp-bfcl-codex166` and were removed after validation.

## Observed scorer behavior

1. [`score()`](../data/bfcl_v3.py#L205) computes
   `sorted(bare_name(predicted)) == sorted(bare_name(expected))`. This is actually
   **multiset equality**, despite the evidence label saying “set equality”:
   duplicates change the result. `bare_name()` drops namespace prefixes.
2. [`parse_prediction()`](../data/bfcl_v3.py#L187) reads one name per line and accepts
   empty/no-tool markers. It does not parse call syntax or argument ASTs.
3. [`_record_from_row()`](../data/bfcl_v3.py#L446) extracts only gold function names
   and discards reference argument alternatives. Trusted verifier gold therefore
   lacks the information needed to check full calls. The goal and released
   reference submission are likewise name-only.
4. The returned metric explicitly says “not the official BFCL score.” Its further
   claim that acceptable-value lists make full-call scoring undecidable is
   unsupported: such lists alone do not establish impossibility. The adapter's
   prose and existing data-shape tests are not evidence for the official AST
   matching rules.

An in-memory fabricated probe used the same `synthetic.compute` schema with an
integer `x`, once with reference `[{"compute": {"x": [3]}}]` and once with
`[{"compute": {"x": [99]}}]`. Assertions passed:

| Probe | Observed result |
| --- | --- |
| Converted gold for the two different references | Identical |
| Prediction `compute` | Reward 1 |
| Prediction `synthetic.compute` | Reward 1 |
| Prediction `compute(x=3)` | Reward 0 |
| Prediction `compute` twice | Reward 0 |
| Adapter release cache after probe | Still empty |

These are scorer observations on fabricated inputs, not benchmark scores or
claims about official AST equivalence.

## Source availability and blocker

The adapter declares the public `ShishirPatil/gorilla` release tag `v1.3`, URL
`https://codeload.github.com/ShishirPatil/gorilla/tar.gz/refs/tags/v1.3`, and archive
SHA-256
`57854157e82aed5723a1458d2a4ac426e3256959ded4a20ddc4d627c22edb7fe`.
This is a declared release pin, not a locally verified evaluator contract.

The worktree inventory contained 384 Python source filenames. The only
BFCL/Gorilla/AST-evaluator/archive filename candidates were `data/bfcl_v3.py`,
`tests/quality/test_bfcl_selected.py`, and `tests/quality/test_bfcl_v3_dataset.py`.
There were no symlinks, public release archives, or evaluator source packages.
Code searches also found no vendored BFCL AST evaluator. The configured external
dataset root `/mnt/20t/xubuqiang/datasets/bfcl-v3` was deliberately not inspected
under the instruction to work only in this worktree. Source availability outside
the authorized workspace is **unverified**, not asserted absent.

Consequently, this review cannot establish the pinned official Simple parser,
type/value comparison, optional-argument, namespace, and call-count rules. A
handwritten approximation would not establish official semantics.

To close the blocker, stage the public evaluator source and its transitive
code-only dependencies inside this worktree, with trusted provenance binding
their file hashes to the declared archive digest. No questions, answer files, or
heldout payloads are needed for that source review. Then implement and test the
source-derived contract using fabricated inputs, retaining name equality only as
an explicitly diagnostic legacy metric. That change must also retain full-call
reference/schema information in trusted selected verifier inputs, update the
submission contract, and preserve selected byte-span reads, lazy imports, and
redaction on measured and unmeasured paths. Neither an official AST contract nor
production H0 authorization is established by the current synthetic controls.

## Validation and focused change

Executed from the worktree:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m pytest -q \
  -p no:cacheprovider \
  --basetemp=/tmp/hg-codex-166/.tmp-bfcl-codex166 \
  tests/quality/test_bfcl_selected.py
```

Result: **55 passed**. These existing tests guard selected spans, full-pool
avoidance, import/scoring payload isolation, and private gold redaction. The
data-dependent `test_bfcl_v3_dataset.py` suite was not run.

The separate fabricated probe above passed all six assertions with release reads
guarded. This commit changes only this report; scorer behavior, selected-only
loading, privacy boundaries, and historical receipts remain unchanged.
