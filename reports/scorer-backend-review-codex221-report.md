# Task 221: scorer backend review

Reviewed `eval/scorer_backend.py` and its task-213 tests from commit
`49905c7203b1321ef8414034f8c14384cbf6ebba`, on worktree base
`82459cf`. Work stayed in `/tmp/hg-codex-221`. Review and validation used
source code, inert local fixture bytes and fabricated observations only. No
production execution, dataset reads, provider calls, GPU work or backend queries
were performed.

## Finding and narrow fix

**P2: a missing runtime observation masked a contradictory resource-policy pin.**
The resources stage tested `runtime_policy is None or runtime_observed is None`
before checking a supplied policy against `runtime_policy_sha256`. A supplied
policy with a mismatching pin therefore returned `unknown` /
`resources_evidence_unavailable` when the observation was absent. The documented
contract classifies contradictions as `blocked`.

The check now validates a supplied policy's pin before handling a missing
observation. The same request returns `blocked` / `resources_contract_refused`.
Missing policies and missing observations with matching policy pins still remain
unknown. Both refusal statuses were already unmeasured and unauthorized; this
fix corrects failure classification, not an execution-authorization bypass.

Added one regression in `tests/quality/test_scorer_backend_codex213.py`, using
the existing refusal helper to verify the fixed code, exact sanitized receipt,
false authorization/publication flags and absence of input mutation. It failed
against the original implementation with `resources_evidence_unavailable` and
passes after the fix. No other concrete bug was identified in this scoped review.

## API and receipt assessment

- The public surface requires all 15 independent inputs as keyword arguments.
  Pins and binding are caller inputs; incoming receipts cannot supply defaults.
  The check composes validation and local byte reads without exporting state,
  executing a scorer, provisioning resources or advancing lifecycle.
- Lifecycle validation replays the supplied events, checks the scope pin and
  complete adapter/run/trial/manifest binding, and requires a passed `quiesce`
  checkpoint. Earlier stages, tampered facts and unsuccessful quiescence are
  refused. A successful preflight leaves that checkpoint unchanged.
- Resource observations bind to the same lifecycle binding, require the
  independently pinned policy, and pass the existing resource/network/filesystem
  gate. Its filesystem policy must also equal the task contract's quota policy.
- Scorer admission checks independent bundle and contract pins, their shared
  source/image/scorer declarations, exact closure bytes, export bytes and seals,
  and the supplied pristine runtime configuration and read-only mounts. Local
  trees are rechecked on each call; old preflight receipts are not accepted as
  validation inputs.
- Export evidence binds run, task, source and task contract, and the backend
  records its digest. It does **not** bind trial or the quiescence checkpoint;
  that association is an explicitly documented trusted-orchestration obligation.
- Resource observations include a binding and observation hash. Artifact runtime
  inspection has no common runtime-instance identifier with those observations,
  and the returned runtime receipt summarizes checked configuration rather than
  hashing the entire inspection. Their same-instance association, freshness and
  observer authenticity remain caller obligations, as the module documents.
- Passing receipts retain `measured=false`, `production_authorized=false`,
  `execution_authorized=false` and `publication_ready=false`. Refusals contain
  fixed stage/reason codes without rejected input evidence. A pass establishes
  supplied-evidence consistency, not official scorer execution, source/ABI
  completeness, ownership, immutability through use, durable persistence,
  snapshot completion or cleanup.

## Test quality and validation

The original 32 backend tests passed before changes. They exercise real shared
validators with inert bytes, imported autouse subprocess/socket guards, public
signature checks, receipt shape and input immutability, lifecycle replay/binding,
quota composition, independent pins, missing evidence, export run binding and
repeated local-byte verification. The positive expected-receipt test recomposes
the same validators, so it establishes composition consistency rather than an
independent oracle for each validator. The behavioral negative tests provide
the more useful boundary checks. The missing-observation/policy-pin combination
was absent and is now covered. These tests cannot establish production observer
freshness, actual enforcement, runtime ownership/association or cleanup.

Validation commands and results:

```text
python -m pytest -q tests/quality/test_scorer_backend_codex213.py --basetemp=/tmp/hg-codex-221/.pytest-tmp-codex221
32 passed in 0.27s

python -m pytest -q tests/quality/test_scorer_backend_codex213.py::test_policy_pin_mismatch_stays_blocked_when_runtime_observation_is_missing --basetemp=/tmp/hg-codex-221/.pytest-tmp-codex221-regression
1 failed in 0.04s (before implementation fix; expected regression failure)

python -m pytest -q tests/quality/test_scorer_backend_codex213.py tests/quality/test_scorer_admission_codex173.py tests/quality/test_scorer_bundle_codex170.py --basetemp=/tmp/hg-codex-221/.pytest-tmp-codex221-focused
104 passed in 0.30s

git diff --check
passed
```

Task-owned temporary fixture directories were removed after validation. This
report and the focused code/test change are delivered in the accompanying commit;
parent review and integration remain separate.
