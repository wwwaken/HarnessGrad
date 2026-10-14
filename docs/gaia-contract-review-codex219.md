# GAIA packet / readiness contract review — Task 219

**Disposition: BLOCKED; task-210 clarification committed, task-212 review pending
its source.** No execution or gate closure is authorized.

Reviewed base: commit `82459cfa6d16c323ca40f21db2daf597921aedb3`, tree
`8f8a6b117c9ba234d366fdc083251b698b789f49`, in `/tmp/hg-codex-219` only.
The initial worktree was clean. Inputs were the task-210 packet, current
`eval/policy/gaia_preflight.py`, `eval/policy/gaia_snapshot_attestation.py`,
`eval/admission/lifecycle_receipt.py`, `eval/policy/diagnostic_policy.py`,
`eval/diagnostic_receipt.schema.json`, shared admission source, and repository
documentation/authored tests. Historical receipt pointers were not followed.
No benchmark task, answer, attachment or heldout content was read; no Docker,
network, model, H0, benchmark control or official scorer ran.

## Findings and correction

| Finding | Current contract and disposition |
| --- | --- |
| **Task-212 evidence is missing.** No named readiness matrix was found in the allowed source/docs scope, including ignored filename searches; visible `git log --all` has no task-212/readiness-matrix match. | This is an unavailable input, not a passing review or proof that the matrix never existed. Its path/commit was requested. Do not reconstruct its claims from task 210 or mark joint readiness reconciled. Task-202 reconciliation also stays pending as recorded in task 210. |
| **Packet omits the explicit dry-preflight boundary.** It asks for receipts without distinguishing them from accepted CLI inputs. | The CLI reads source tree metadata and optional paired inline runtime declarations only. It always blocks execution with exit 2, even for matching identities. It does not validate receipt files, authenticate declarations, hold a source lock or authorize reuse. Added this distinction to the packet. |
| **The prose evidence checklist omits the diagnostic-v2 serialization and replay requirements.** | Added required eligible-ID digest, selection/outcomes/coverage, gate/cleanup/snapshot summary fields and explicit lifecycle. The lifecycle freezes scope before execution, seals matching outcome and completed-snapshot evidence, then requires cleanup. `validate_receipt` replays and binds these fields; schema shape validation alone is insufficient. |
| **Unknown counts and no-model N/A need precise representations.** | Unknown eligible counts cannot be encoded as a valid staged receipt, whose eligible count must be positive. Preserve the blocked handoff instead. Model hash/endpoint N/A means null plus explanation, not a string or fabricated identity. Such no-model evidence cannot pass `require_review` for model diagnostic expansion. |
| **Structural publication could be mistaken for production authorization.** The original packet itself grants none. | Added that even `publication_ready=true` retains `production_authorized=false`; hashes/passing summaries do not authenticate observers. The library performs no backend cleanup or lease mutation. Pending GAIA actor-network and artifact/pristine-verifier integration still block execution. |
| **A documentation correction changes the candidate fingerprint.** | The compatibility tool exempts only `reports/GAIA_GATE.md` and `tests/quality/test_gaia_snapshot_attestation.py`. The changed packet, this report and journal are conservatively runtime-affecting entries for comparison. Added an explicit final-candidate comparison/no-reuse note. No exemption or implementation was changed. |

No direct authorization or contradictory execution instruction was found in the
task-210 packet. Its BLOCKED disposition, independent custody/review, fresh run
IDs, invalid/unmeasured failure classifications and staged 1x1 policy remain in
force. The corrections address omissions and ambiguity; they supply no missing
observations. Task-200 source findings remain attributed historical claims, not
newly authenticated source custody. Task 212 cannot yet be assessed.

## Focused validation

Only authored metadata/synthetic regression suites were selected; the real-data
GAIA official-scorer/control suite was excluded. Driver and eval-side tests were
also excluded from this contract-only check. Scratch was kept inside the worktree.

```bash
mkdir -p /tmp/hg-codex-219/.pytest_cache/codex219
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  TMPDIR=/tmp/hg-codex-219/.pytest_cache/codex219 python3 -B -m pytest -q \
  tests/quality/test_gaia_preflight_codex175.py \
  tests/quality/test_gaia_snapshot_attestation.py \
  tests/quality/test_lifecycle_receipt_codex177.py \
  tests/quality/test_diagnostic_policy.py \
  -k 'not driver and not eval_side' \
  --basetemp=/tmp/harnessgrad-pytest-codex219-codex219-pytest -p no:cacheprovider
```

Result: **285 passed, 11 deselected in 2.08s**, exit 0, no skips. The deselections
are the driver/eval-side tests named above. `git diff --check` passed. No new tests
were needed for the prose-only correction; existing tests exercise the referenced
contracts.

This report is not a diagnostic/pilot receipt: real coverage/counts, model and
endpoint binding, runtime observations and cleanup status are unobserved or N/A.
Parent review and integration remain separate.
