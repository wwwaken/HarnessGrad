---
template: doc
title: T5 failure investigation
subtitle: Seven isolated files, exact evidence, focused fixes
lang: en
---
## A Result

All seven files pass individually: 167 passed, zero failed, zero skipped.

The valid baseline had 21 failures: 19 stale assertions and two test defects.
Verification exposed one further platform defect in Docker network cleanup.

[Read the complete per-test verdict table and evidence](t5-verdicts.md).

## B Proven causes

| Cause | Evidence | Change |
|---|---|---|
| Runtime admission changed | Commit 008348b returns invalid receipts before execution | Assert exact receipts and forbid unmeasured curves |
| Diagnostic sampling became the default | Commit 547f539 requires staged evidence | Select all explicitly for the authored metadata fixture |
| Crash test reused an old namespace | Docker listed hg-reaped-crash-s01 before testing | Use a unique namespace and finally cleanup |
| Remote model fixture omitted its model | Driver reported HG_AGENT_MODEL unset | Supply an explicit synthetic model |
| Docker 29 changed missing-network wording | A second removal reports network NAME not found | Accept that exact owned-network reply |

No failure has an environmental verdict. Docker and required images were present.

## C Final isolated runs

| File | Passed | Failed | Skipped |
|---|---|---|---|
| test_container.py | 26 | 0 | 0 |
| test_services.py | 43 | 0 | 0 |
| test_container_state.py | 19 | 0 | 0 |
| test_web_gateway.py | 43 | 0 | 0 |
| test_jericho_runtime_admission.py | 13 | 0 | 0 |
| test_jericho_runtime_boundaries.py | 17 | 0 | 0 |
| test_appworld_service_diagnosis.py | 6 | 0 | 0 |

## D Evidence and limits

[Exact baseline failure text](t5-evidence/exact-baseline-failures.md) preserves every traceback.
[Image inspections](t5-evidence/required-images.txt) prove the required images existed locally.
[Docker cleanup proof](t5-evidence/docker29-network-missing.txt) captures the changed daemon message.

All tests ran alone with external basetemps. The whole suite never ran.
A task-local guard excluded the forbidden adapter from integrity traversal.
Synthetic backend tests preserve the original boundary assertions after checking production refusal.
Production admission still requires a trusted observer.

Pre-existing Docker resources disappeared during the task; the deleting client is unknown.
The report records that shared-daemon change and preserves before/after inventories.
