# Task 240 — blocker registry source/provenance audit

Reviewed merged HEAD `0930d99cc882c5a049c98f9123e9427470e7e818` in
`/tmp/hg-codex-240`, initially clean. Scope: Git history, repository reports,
provenance metadata, registry/checker/tests and journal only. External paths
remain unopened citations. No adapter import, dataset payload, network, host
inspection, scorer, runtime, model, GPU or diagnostic execution was used.

Four current statements needed correction; no blocker was closed or reclassified:

| Location | Stale or overbroad observation | Correction and merged evidence |
| --- | --- | --- |
| Machine `agentdojo/production-route-admission` | Present, pinned paths could be read as current authenticated inventory. | [Codex 190](../reports/agentdojo-provenance-codex190-report.md) identifies inherited external metadata, without fresh external inspection or release/runtime custody. Mark that limitation explicitly and cite the report; retain `runtime`. |
| Machine shared `paired-filesystem-quotas` | Missing enforcement could be read as observed host incapability. | [Codex 168](../reports/filesystem-quota-codex168-report.md) found no complete connected production backend, without inspecting host quotas. [Task 233](task-233-quota-readback-authentication.md) remains a proposal with no host inspection. Distinguish source integration from unknown host capability/enforcement; retain `runtime`. |
| Registry guide BFCL paragraph | All pinned evaluator source described as unacquired. | [Task 195](../reports/bfcl-source-provenance-codex195-report.md) and [227](../reports/bfcl-blob-retry-codex227-report.md) acquired partial original code, including the checker. Missing helpers, complete closure, archive binding and independent approval still prevent official full-call admission; retain `external`. Machine observation already reflects task 227. |
| Registry guide 2Wiki paragraph | Fresh wheel/installation acquisition still described as missing. | [Task 226](task-226-ujson-wheel-report.md) acquired the exact wheel and verified offline package installation without native import. Notices, supported image and native/runtime closure remain unresolved; retain `external`. Machine observation already reflects task 226. |

The remaining merged source/provenance findings do not justify further current
observation changes. Review chains were checked in merge order rather than
treating an older acquisition-time report as the latest state:

| Report family / merged review chain | Current disposition retained |
| --- | --- |
| TriviaQA 157 → 196 → 205 → 215 → [225](../reports/triviaqa-hub-linkage-codex225-report.md) | Original evaluator acquisition and normalization/all-alias repair remain closed; v2 identity retained. Historical loader is acquired, but exact Hub/export linkage and full grouping/denominator compatibility remain external/unverified. Failed Hub requests establish no absence. |
| 2Wiki 197 → 206 → 216 → [226](task-226-ujson-wheel-report.md) | Evaluator acquisition stays retired; native dependency and Hub/data custody remain external, mixed-metric recovery remains measurement work. |
| BFCL 166 → 195 → 208 packet → 217 → [227](../reports/bfcl-blob-retry-codex227-report.md) | Partial source integrity supplies neither missing helper closure nor independently approved archive/release/index custody. Function-name scoring remains diagnostic-only. |
| AgentDojo journal 164 → 180 → [190](../reports/agentdojo-provenance-codex190-report.md) | Selected metadata privacy closure stays closed; inherited layout agreement establishes no production-route custody or runtime readiness. |
| AppWorld 155 → 169 → 183 → [229](../reports/appworld-canonical-source-codex229-report.md) | Public generic evaluator is pinned; protected task evaluator/package/image/data custody remain unresolved. Writer preserves supplied facts, but checker/runner still omit original numeric trial IDs, preventing aligned SGC on that route. Historical successful-task and shared gates remain. |
| GAIA 175 → 210 packet → 219 → [228](task-228-gaia-scorer-revision-report.md) | Distinct full scorer revisions remain unresolved after canonical transport failures; no pin correction. Dry compatibility does not close source lock, selected access or lifecycle/runtime gates. |
| LiveCodeBench [198](task-198-livecodebench-provenance-report.md) → [207 packet](task-207-livecodebench-operator-packet.md) | Source-commit signature does not attest local sorted row 740, release/pool/split custody or independent approval. Official smoke comparability remains unresolved. |
| Terminal 211 → 220 → [230](task-230-terminal-public-source-audit.md) | Harbor reference-source metadata is established; exact historical runner binding, selected task scorer, helper/dependency closure and live gates remain open. Task 230 metadata is not a committed complete scorer fixture. |
| [GSM8K provenance](gsm8k-scorer-provenance.md), ScienceWorld [186](../reports/scienceworld-platform-writes-codex186-report.md), Chess [182](../reports/chess-recovery-id-conflict-codex182-report.md) and transport journal | Scorer/protocol distinctions, prevention-vs-live-enforcement boundary and new-run-ID guidance are already represented; historical failures and measurements remain unchanged. |
| Shared 158 / 168 / 170 / 173 / 177 → [221](../reports/scorer-backend-review-codex221-report.md), quota 191 / 222 → [233](task-233-quota-readback-authentication.md) | Standalone composition exists, but production driver/runner integration, trusted observations, complete offline/pristine scoring, artifact export, paired quotas and lifecycle/cleanup remain unresolved. Current wording denies production integration, not all compositional callers. |

All 28 declarations remain represented, including four explicit refusals and the
six dataset-specific journal gaps. The source-only [task-234 snapshot](task-234-diagnostic-readiness.md)
is scoped to its recorded input revision; it supplies no fresh runtime evidence.
Historical report findings and failed acquisition receipts are preserved, even
where later source acquisition supersedes their current-state conclusions.

Validation after the correction:

```sh
mkdir -p .scratch/task240
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_dataset_blockers.py
env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  TMPDIR=/tmp/hg-codex-240/.scratch/task240 python3 -B -m pytest -q \
  -p no:cacheprovider --basetemp=/tmp/harnessgrad-pytest-task240-registry-final \
  tests/quality/test_dataset_blockers.py
git diff --check
```

Checker: valid, **28 datasets / 8 shared blockers / 11 historical records**,
`production_authorized=false`. Existing guarded registry tests: **52 passed in
2.66s**, no skips. Baseline: 52 passed in 3.39s. The initial baseline invocation
had 52 setup errors because `.scratch` did not exist; creating the task-owned
scratch parent resolved them. This was test setup, not benchmark measurement.

An independent in-memory comparison with reviewed HEAD permits only `observed`
and `evidence` changes on the two named machine blockers. It confirms all blocker
IDs, families, statuses, actions, shared references, taxonomy, review fields and
all 11 historical records are identical. Existing tests already enforce source
inventory, evidence locators, runtime/external boundaries and the independently
pinned history; no new tests or production changes are needed. All 33 local
documentation links resolve, and earlier journal content remains an unchanged
prefix. Task-owned `.scratch/task240`, `.scratch/task240-registry-baseline` and
`.scratch/task240-registry-final` were removed and verified absent. This is test
housekeeping, not a backend cleanup receipt. Only current registry documentation,
this receipt and an appended journal entry are delivered for parent review.
