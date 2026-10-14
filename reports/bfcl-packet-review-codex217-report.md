# Task 217 — BFCL packet and candidate provenance review

**Result: narrow documentation/test correction; production remains blocked.**
Reviewed the Task 208 operator packet and retained v1.3/V3 candidate metadata
against the local source contract and selected-reader source. Work stayed in
`/tmp/hg-codex-217`, based on `82459cfa6d16c323ca40f21db2daf597921aedb3`.

## Findings and correction

- The packet already denied production/H0 authorization, kept independent source
  receipt approval separate from index/storage approval, and treated the archive
  digest/member bindings and full checker/runtime closure as unresolved. The
  candidate still has its deliberately inadmissible schema and explicit
  `status=blocked`, `custodian_approved=false`, `measured=false`,
  `production_authorized=false`. No approval or official full-call metric closure
  was established.
- The packet linked the exact receipt schema but did not enumerate its top-level,
  review and entrypoint fields. It now names them and clarifies that the gate
  validates commit shape and declared edges, while independent review must
  establish the specific commit, dependency discovery and symbol definitions.
- The index handoff omitted the `tasks` container and exact `question`/`answer`
  keys, ID format and span type/bounds. Those are now explicit and labeled as
  local limits; this adds no index admission implementation or payload access.
- Upstream tag/release/ownership claims remain retained Task 195 observations.
  Metadata response digests are recorded, but response bodies are not retained
  with the candidate. The packet now states that this handoff cannot independently
  reverify those observations offline. Earlier 403/timeouts remain failed
  acquisition attempts, not measurements or scorer receipts.
- Added a source-contract regression that reads only candidate metadata, checks
  its blocked/incomplete flags, and confirms refusal even with its locally
  computed integrity digest before projected source reads or inventory. This
  digest is used only for the refusal test and supplies no independent approval.

## Validation

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  TMPDIR=/tmp/hg-codex-217/.scratch/bfcl-codex217/tmp \
  python3 -m pytest -q -p no:cacheprovider \
  --basetemp=.scratch/bfcl-codex217/pytest \
  tests/quality/test_bfcl_ast_source_contract.py \
  tests/quality/test_dataset_blockers.py
```

**87 passed**. Only source-contract and registry tests ran; the selected-reader
suite and dataset-loading tests did not run.

The explicit unpinned source gate exited **2** with
`status=blocked`, `reason=bfcl_ast_source_contract_refused`, `measured=false`,
`production_authorized=false`. Source-only registry validation exited **0**:
28 datasets, 8 shared blockers, 11 historical records,
`production_authorized=false`. Scratch was confined to this worktree and removed.

Candidate bytes/provenance, approved-fixture absence, production adapter/scorer,
source-gate implementation, registry and earlier receipts are unchanged. No
dataset payload, answers, heldout, archive or external dataset root was opened;
no network, installation, upstream evaluator execution, model/GPU run or pilot
was used. These checks provide no runtime, custody or benchmark measurement
authorization. Parent review of the exact diff and commit remains required.
