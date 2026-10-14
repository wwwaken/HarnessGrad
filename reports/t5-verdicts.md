# T5 isolated failure investigation

All seven requested files pass when run alone after the fixes: **167 passed, 0 failed, 0 skipped**.
Baseline: **140 passed, 21 failed, 0 skipped**. Nineteen failures were stale contract assertions; two were genuine test defects. A further real platform cleanup defect was exposed and fixed during verification. No failure is classified environmental.

## Scope and reproduction

Worktree: `/tmp/hg-t5`, starting commit `344d432`. Only the seven authorized test files were executed, sequentially and individually. Every invocation, full traceback, captured output, exit code and JUnit result is saved under [t5-evidence](t5-evidence/). Each invocation uses its own external basetemp beneath `/mnt/20t/xubuqiang/.hg-pytest/t5/`; no whole-suite run occurred.

The requested external basetemp parent initially did not exist. The first invocations therefore produced setup errors before tmp_path tests could run. Those logs are preserved as `initial-temp-parent-error-*`; the parent was created and all seven files rerun as `baseline-*`. The verdict table uses the valid baseline, not those invocation errors.

The task-local [scope guard](t5-evidence/scope_guard/sitecustomize.py) filters only the excluded adapter paths from integrity snapshot traversal and rejects attempts to open/import them. It is inherited by driver subprocesses through PYTHONPATH. Without it, ordinary driver/evaluate integrity snapshots would read every adapter. The excluded paths were never read, imported, edited or executed. Production integrity/admission code was not weakened; this guard is invocation support for the user's explicit scope restriction. Runs under this guard are scoped test evidence, not complete platform integrity certification.

Reproduce the final file invocations with `python reports/t5-evidence/run_files.py fresh-review`; choose a fresh phase name to preserve existing logs and basetemps. The script records the exact commands and daemon state after each file.

## Proven current contracts

**A — runtime admission:** commit `008348bcf0de7fabf47e962e082cabd9380184cd`, “refuse tasks without enforced runtime observations.” Current `eval/run/runner.py::_refuse_unobserved_policies` runs before resource allocation in `run_one`, and before score-cache lookup in `evaluate`. Exec defaults, container state and declared native network/resource policies return a structured invalid/unmeasured receipt with `backend_observation_unavailable`; they do not execute the actor or produce a score. No caller-supplied observer override exists. [Independent refusal probes](t5-evidence/policy-refusal-probes.json) show the exact receipts for all four affected environment shapes.

**B — staged default:** commit `547f539`, “Enforce staged diagnostic policy and preserve evidence receipts.” Current `driver.py` defaults `--sampling` to `diagnostic`, requiring `--policy-evidence`. Local authored metadata fixtures must explicitly select `--sampling all`; this does not authorize production H0.

**C — teardown:** already-absent owned resources should not cause a cleanup error. Docker 29.2.1 reports `Error response from daemon: network NAME not found`, whereas older replies contain `No such network`. [Direct daemon proof](t5-evidence/docker29-network-missing.txt) creates a unique task-owned network, deletes it once successfully, and captures the exact second-delete failure. Before the fix both `remove_network` and `RunningServices.stop` misclassified that reply. Real failures for active endpoints, missing plugins and a different network remain errors.

## Per-test verdict table

Names below are the **original failing node names**, so the table maps directly to the baseline logs. Updated tests sometimes have new names matching their current contract. Every linked baseline contains the full exact failure text.

| File / original failing test | Verdict | Evidence and resolution |
|---|---|---|
| [test_container.py](t5-evidence/baseline-test_container.log) :: `test_a_working_harness_scores_full_marks` | stale | Exit 2, both e01/e02 invalid at admission with `backend_observation_unavailable`. Contract A requires invalid/unmeasured, not 1.0. Assert exact receipts, no actor output and no curve. |
| same :: `test_an_idle_harness_scores_zero` | stale | Exit 2 for the same admission receipt. Contract A prohibits treating an unexecuted idle actor as a measured zero. |
| same :: `test_a_harness_cannot_grade_itself_in_a_container` | stale | Exit 2 before actor execution under A. Pin refusal; keep the existing direct restored-check/cheated-check positive and negative controls. The old driver test only selected train e01/e02, not its documented e03 cheat task. |
| same :: `test_the_curve_records_the_environment` | stale | Expected exit 0, got 2 under A. Assert environment metadata remains pinned and that no curve is published for unmeasured tasks. |
| same :: `test_the_run_record_and_the_curve_agree_about_the_image` | stale | Expected exit 0, got 2 under A. Assert metadata matches the actual resolved image digest and no curve exists. |
| same :: `test_no_sandbox_does_not_disable_the_container` | stale | Exit 2 under A even with `--no-sandbox`. Retain header assertions and require admission refusal; the flag cannot authorize an unobserved backend. |
| [test_services.py](t5-evidence/baseline-test_services.log) :: `test_a_service_that_is_not_healthy_refuses_the_task` | stale | Exact mismatch: `'admission' != 'health'`. A precedes health checks. Assert no service allocation, exact admission receipt and empty per_task. Direct daemon health-wait/failure/cleanup tests remain strict. |
| same :: `test_the_same_task_scores_when_its_service_is_healthy` | stale | Expected empty invalid map, received s01 admission refusal with `env.exec_defaults` and `env.network`. Under A, a healthy service cannot authorize the backend. |
| same :: `test_reap_removes_a_service_container_a_crash_left_running` | real — test | `ServiceUnavailable: ... network with name hg-reaped-crash-s01 already exists`. The [before inventory](t5-evidence/docker-networks-before.txt) and [containers](t5-evidence/docker-containers-before.txt) show that exact network and its already-running orders container before this task. The test hard-coded `reaped-crash`. Fix: UUID namespace, verify owned live container/network, keep strict reaping assertions and add finally cleanup. No removal of the old namespace was used to fix the test. |
| same :: `test_a_healthy_service_run_names_the_service_in_its_header` | stale | Header already contains `services[orders]`; only expected exit 0 fails, actual exit 2 from A. Keep header assertion and pin invalid receipts/no curve. |
| same :: `test_the_declared_environment_reaches_the_curve` | stale | Expected exit 0, actual 2 from A. Preserve service name/digest/network/seed assertions in run metadata; require no curve. |
| same :: `test_a_containerised_harness_gets_its_model_and_not_the_internet` | stale | `answer == ''`, not `http://...`, because A returns before gateway allocation. Assert exact production refusal; retain every original gateway, byte-count, upstream and internet-isolation assertion in a separately named synthetic HTTP backend regression. |
| same :: `test_a_remote_model_with_an_offline_network_is_refused` | real — test | Expected `not on this host`, actually `backend is 'openai' but HG_AGENT_MODEL is unset`. Its extra_env specifies backend/base/key but omits the model, so it depends on a host config. Fix supplies an explicit synthetic model; the unchanged remote-network refusal assertion now passes. This is not a missing machine API key verdict. |
| [test_container_state.py](t5-evidence/baseline-test_container_state.log) :: `test_the_oracle_control_passes` | stale | Expected score 1.0, verdict is `{}` because A returned invalid before the oracle/snapshot backend. Pin complete container-state refusal and prohibit allocation; do not run a real reference solution through an admission bypass. Also strengthen the formerly vacuous no-leak test to require the refusal receipt. |
| [test_web_gateway.py](t5-evidence/baseline-test_web_gateway.log) :: `test_declared_task_gets_web_url_and_undeclared_task_cannot_reach_live_gateway` | stale | Expected exit 0, got None from A. First assert exact refusals and absent recording; then retain every original gateway liveness, search, isolation and recording assertion in the authored synthetic backend fixture. |
| same :: `test_driver_writes_real_run_meta_before_task_launch[searxng-http://127.0.0.1:19999]` | stale | Expected the metadata sentinel exception; actual stderr: `refusing staged policy: staged runs require --policy-evidence with passing dataset gates`. Contract B. Add explicit local `--sampling all`; retain every metadata assertion and the before-launch sentinel. |
| same :: `test_driver_writes_real_run_meta_before_task_launch[none-None]` | stale | Identical gate and correction under B; no provider request or paid endpoint is used. |
| [test_jericho_runtime_admission.py](t5-evidence/baseline-test_jericho_runtime_admission.log) :: `test_live_backend_is_refused_before_staging_or_execution` | stale | `DID NOT RAISE ValueError`: A now returns structured invalid before the older native-backend exception. Keep the allocation tripwire and assert the full refusal instead. |
| [test_jericho_runtime_boundaries.py](t5-evidence/baseline-test_jericho_runtime_boundaries.log) :: `test_runner_refuses_unsandboxed_declared_isolation` | stale | `DID NOT RAISE ValueError`: A returns earlier. Require exact refusal and no new workspace entries. |
| same :: `test_agent_projection_network_denial_and_trusted_verifier_end_to_end` | stale | Expected actor exit 0, got None under A. Pin refusal first; preserve all original projection, read-only package, network denial, trusted verifier and timeout assertions in the synthetic backend half. |
| [test_appworld_service_diagnosis.py](t5-evidence/baseline-test_appworld_service_diagnosis.log) :: `test_runner_mounts_dependency_overlay_once` | stale | `assert ([])`: the mocked launch is never called because A refuses exec defaults. Assert exact refusal and zero calls, then exercise the mocked command builder with every original unique-mount, PYTHONPATH and trace assertion retained. |
| [verification discovery](t5-evidence/revised-test_services.log) :: crash-reap finally cleanup | real — platform | Added finally cleanup exposed C: every reap assertion passes, but `stop()` reports the already-removed network as an error. Fix shares the network-removal helper and recognizes Docker 29's exact owned-network reply; five new negative/positive cases and a real reap-then-stop test pass. |

No new skip/xfail was introduced. The existing environment-gated tests all ran: final skip count is zero. Test-local admission stubs only exercise authored synthetic fixtures or mocked Docker commands **after** pinning actual production refusal. They never expose a production admission override, create measured benchmark receipts or authorize H0.

## Docker and prerequisite evidence

[Docker version](t5-evidence/docker-version-before.txt): client and server 29.2.1, server API 1.53. [Complete initial image inventory](t5-evidence/docker-images-before.txt) and [focused image inspection](t5-evidence/required-images.txt) prove the Python demo, fake-service and cancel-async-tasks images exist locally. The driver also resolves and runs the derived exec image during boundary preflight. Tests execute native bubblewrap and installed Jericho probes successfully. No environmental verdict is inferred from a traceback, and no keys were printed or paid endpoints contacted. No AppWorld runtime installation or dataset access was needed by its synthetic diagnosis file.

The initial daemon contained the old crash service/network and two old oracle namespaces. They were still present after the last baseline file, and absent by the end of the revised container file. This task issued no explicit prune or deletion of those pre-existing resources; its visible reap calls used `probe`, `reaped-run`, or the newly generated UUID namespace, never those old oracle/crash IDs. The daemon is shared and mutable: the disappearance is an unattributed daemon-state change, not evidence that this task repaired the test by removing the colliding network. [Historical daemon events](t5-evidence/docker-network-destroy-events.jsonl) are preserved but do not identify the deleting client. [Final containers](t5-evidence/docker-containers-after.txt), [networks](t5-evidence/docker-networks-after.txt) and [images](t5-evidence/docker-images-after.txt) record the final state. No synthetic run resources remain; only task-created networks/containers/images were intentionally cleaned by this task's probes/tests.

## Individual reruns

| File | Valid baseline | Final individual run | Exact final log |
|---|---:|---:|---|
| test_container.py | 6 failed, 20 passed | 26 passed | [log](t5-evidence/revised-test_container.log) |
| test_services.py | 7 failed, 30 passed | 43 passed | [log](t5-evidence/preserved-backends-test_services.log) |
| test_container_state.py | 1 failed, 18 passed | 19 passed | [log](t5-evidence/revised-test_container_state.log) |
| test_web_gateway.py | 3 failed, 40 passed | 43 passed | [log](t5-evidence/preserved-backends-test_web_gateway.log) |
| test_jericho_runtime_admission.py | 1 failed, 12 passed | 13 passed | [log](t5-evidence/revised-test_jericho_runtime_admission.log) |
| test_jericho_runtime_boundaries.py | 2 failed, 15 passed | 17 passed | [log](t5-evidence/revised-test_jericho_runtime_boundaries.log) |
| test_appworld_service_diagnosis.py | 1 failed, 5 passed | 6 passed | [log](t5-evidence/revised-test_appworld_service_diagnosis.log) |

The extra baseline service failure relative to the prompt is the independently reproduced unset-model fixture defect. The six added final service cases are the five cleanup reply cases plus the preserved synthetic model-gateway backend regression.

## Focused commits

- `08b1fcb` — isolate crash reaping and declare the remote model fixture.
- `764c081` — accept Docker 29 missing-network cleanup replies; keep genuine errors strict.
- `f5117e0` — pin current fail-closed runtime admission and staged-default contracts, preserving synthetic backend assertions.

No change was made to runtime admission, observer authorization, dataset adapters, secrets or the main checkout. The remaining production limitation is deliberate: policy-bearing tasks are invalid/unmeasured until a trusted runtime observer exists. These passing tests do not certify production H0.
