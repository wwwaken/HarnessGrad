# Docker resource cleanup receipt — 2026-10-14

Worktree: `/tmp/hg-t6`, starting commit `344d4321eb0d6f2aa1ff2f68062eaa04a60d2ccc`. Inventory captured at 2026-10-14T13:42:42.636499+00:00; cleanup completed at 2026-10-14T13:50:37.109705+00:00. All repository reads, edits and commit work were confined to this registered worktree. Docker metadata and process metadata were inspected read-only before the explicitly listed removals.

Removed **5 orphaned test containers, 3 test networks, and 7 test snapshot images**. Preserved the other **20 matching images, 10 containers, 4 networks, and all 15 volumes**. All removed IDs were verified absent; all other inventoried IDs were verified present. No Docker prune, image force-removal, volume deletion, unrelated process termination, or filesystem cleanup was performed.

## Evidence and ownership rules

The accompanying [machine-readable evidence](docker-resource-cleanup-20261014-evidence.json) contains full IDs, original creation timestamps, all labels returned by Docker, container state/PIDs/mounts, network attachments, image size accounting, process checks, the exact preprinted removal plan, each removal command/result, and preservation verification. Tables below abbreviate IDs to 12 hex characters; volume names are their Docker identifiers (there is no separate volume ID). All displayed timestamps are UTC. Docker does not supply a human creator identity for these resources; a shared Unix account or an `hg-` prefix alone was not treated as ownership proof. No resource was assigned `owned-by-another-user` without that evidence; known external projects are preserved as `unclear` human ownership.

Naming evidence:

- `eval/services.py` is a compatibility alias, not the implementation. [eval/services.py:1](../eval/services.py#L1) points to `eval/service/services.py`.
- Network: `label(f"hg-{run_id}-{task_id}")`, labelled `harnessgrad.run` and `harnessgrad.task`: [eval/service/services.py:249](../eval/service/services.py#L249).
- Service container: `label(f"hg-{run_id}-{task_id}-{name}")`, with run/task/service labels: [eval/service/services.py:383](../eval/service/services.py#L383).
- Harness container and snapshot: `hg-<run>-<task>` and `hg-snapshot:<run>-<task>`: [eval/containers/container_state.py:51](../eval/containers/container_state.py#L51) and [eval/containers/container_state.py:52](../eval/containers/container_state.py#L52). Container creation adds run/task labels at [eval/containers/container.py:783](../eval/containers/container.py#L783); snapshots inherit them.
- Verifier container: `hg-verify-<run>-<task>`: [eval/verification/verifier.py:251](../eval/verification/verifier.py#L251).
- Oracle IDs: `oracle-test-<os.getpid()>`, with comments identifying the older fixed ID: [tests/quality/test_container_state.py:379](../tests/quality/test_container_state.py#L379). Leak-control IDs: `leak-test-<os.getpid()>`, with older fixed-ID evidence: [tests/quality/test_container_state.py:422](../tests/quality/test_container_state.py#L422).
- The exact `reaped-crash`/`s01` service fixture: [tests/quality/test_services.py:448](../tests/quality/test_services.py#L448). Its orphan container also bound a path containing `test_services/test_reap_removes_a_service_co0/rec/s01/orders`, matching this test.

## How resources were established as unreferenced

1. This worktree has **no `runs/` directory**. The available `reports/` and `docs/` were searched with fixed run identifiers; there were no matches. The exact command, searched identifiers, exit code 1 and empty output are recorded under `reference_scope` in the evidence. Other checkouts and frozen evidence trees were not opened. Therefore absence of references is established only within the permitted checkout, and historical experiment snapshots were deliberately preserved.

2. The deleted resources are specifically attributable to tests. These tests call `run_one` or `services.start` directly, use temporary recordings, and do not create persistent run directories: [tests/quality/test_container_state.py:379](../tests/quality/test_container_state.py#L379), [tests/quality/test_container_state.py:422](../tests/quality/test_container_state.py#L422), [tests/quality/test_services.py:448](../tests/quality/test_services.py#L448). `run_one` documents the throwaway lifecycle at [eval/run/runner.py:137](../eval/run/runner.py#L137). This code provenance, rather than the absence of a worktree run directory alone, supports cleanup of the test resources. No claim is made that inaccessible external historical receipts were globally searched.

3. `/proc/*/cmdline` and `ps` were checked for live pytest/run controllers. All process argument lists were readable; none matched a live test controller. Some root/kernel process working directories were inaccessible; this limitation did not prevent reading their argument lists. Original test owner PIDs `3399750`, `2025544`, `3289083`, `3264105`, and `3235052` no longer existed, including immediately before removal. The older fixed-ID tests have no encoded owner PID; their attribution relies on the documented historical names, run/task labels, lack of a live controller, and age.

4. `docker top` showed the two orphan oracle verifiers running only `sleep infinity`; the service-test container ran only `/opt/fake_service.py`. No verifier/check subprocess remained. Here an owning process means a run/test controller: residual container processes are the leaked workload, not evidence that the original test is still alive. The GAIA service ran SearXNG workers and was preserved. Original controller absence does not itself authorize deleting unrelated services.

5. Immediately before removal, full IDs and labels were re-inspected, original PID absence and controller checks were repeated, all network users and image consumers were verified to be in the exact removal set, and image tags were unchanged. Containers were removed first, then networks, then images. Images were removed without `--force`; container removal did not use `--volumes`.

## Image inventory and classification

Scope: every image whose repository/tag includes `hg-` or `harnessgrad`. Docker image-inspect `Size` and `docker system df -v` report different accounting on this daemon; both are retained, and neither is claimed as actual disk space reclaimed. Shared image layers must not be summed as physical recovery.

| Name/tag | ID | Created UTC | Inspect bytes | df total / shared / unique | Creator/provenance labels | Classification | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hg-snapshot:oracle-test-3399750-cancel-async-tasks | f8d854518cbb | 2026-10-13T08:01:03+00:00 | 44622388 | 182MB / 136.5MB / 45.92MB | harnessgrad.run=oracle-test-3399750; harnessgrad.task=cancel-async-tasks; com.docker.compose.project=harbor-build-cancel-async-tasks; com.docker.compose.service=task | owned-by-a-test-run | removed — LEAKED test resource |
| harnessgrad/appworld-service:20261009-clean2 | db09e34ec903 | 2026-10-09T09:15:55+00:00 | 156920267 | 874MB / 544MB / 329.7MB | none identifying creator | unclear | preserved — see preserved list |
| harnessgrad/appworld-service:20261009-clean | 4c5fe8dde77c | 2026-10-09T08:59:44+00:00 | 156920240 | 874MB / 544MB / 329.7MB | none identifying creator | unclear | preserved — see preserved list |
| harnessgrad/appworld-service:20261009-secure2 | 9b39b96f1efe | 2026-10-09T08:20:11+00:00 | 158737535 | 906MB / 371.3MB / 534.4MB | none identifying creator | unclear | preserved — see preserved list |
| hg-verdict-symlink-test:latest | 578a60e5344c | 2026-10-09T05:38:48+00:00 | 45601713 | 187MB / 141.5MB / 45.63MB | none identifying creator | unclear | preserved — see preserved list |
| harnessgrad/appworld-service:20261009-final2 | f3cb916b9bdc | 2026-10-09T03:50:50+00:00 | 159917668 | 934MB / 572.7MB / 361.4MB | none identifying creator | unclear | preserved — see preserved list |
| harnessgrad/appworld-service:20261009-final | 6d383e307a1d | 2026-10-09T03:49:24+00:00 | 129092673 | 702MB / 572.7MB / 129.1MB | none identifying creator | unclear | preserved — see preserved list |
| harnessgrad/appworld-service:20261009 | 6fa2d092db0d | 2026-10-09T03:27:57+00:00 | 129092626 | 702MB / 572.7MB / 129.2MB | none identifying creator | unclear | preserved — see preserved list |
| harnessgrad/appworld-agent:20261009 | d3a04ec8e295 | 2026-10-09T03:27:01+00:00 | 45534461 | 187MB / 141.2MB / 45.58MB | none identifying creator | unclear | preserved — see preserved list |
| harnessgrad/appworld:20261008 | 91cf774386e0 | 2026-10-08T16:12:43+00:00 | 159857902 | 934MB / 141.2MB / 792.6MB | none identifying creator | unclear | preserved — see preserved list |
| harnessgrad/gaia:20261008 | 9cc27f813e59 | 2026-10-08T13:59:12+00:00 | 102621041 | 423MB / 87.67MB / 335.4MB | none identifying creator | unclear | preserved — see preserved list |
| hg-snapshot:oracle-test-2025544-cancel-async-tasks | 183947fa5af5 | 2026-10-07T06:38:44+00:00 | 44622402 | 182MB / 136.5MB / 45.92MB | harnessgrad.run=oracle-test-2025544; harnessgrad.task=cancel-async-tasks; com.docker.compose.project=harbor-build-cancel-async-tasks; com.docker.compose.service=task | owned-by-a-test-run | removed — LEAKED test resource |
| harnessgrad/tau-bench:20261006 | beda1b01f43c | 2026-10-06T11:27:05+00:00 | 46091804 | 192MB / 141.2MB / 50.65MB | harnessgrad.dataset=tau_bench; harnessgrad.provenance=data/tau_bench/PROVENANCE.json (upstream sierra-research/tau-bench @ 59a200c) | unclear | preserved — see preserved list |
| hg-snapshot:full-b-cobol-modernization | 7b74f7159e7b | 2026-10-06T01:33:16+00:00 | 163636387 | 618MB / 449.5MB / 168.2MB | harnessgrad.run=full-b; harnessgrad.task=cobol-modernization; com.docker.compose.project=harbor-build-cobol-modernization; com.docker.compose.service=task | owned-by-this-platform | preserved — see preserved list |
| hg-snapshot:leak-test-3289083-cancel-async-tasks | fa21c5a9e8cd | 2026-10-05T23:37:39+00:00 | 44622330 | 182MB / 136.5MB / 45.91MB | harnessgrad.run=leak-test-3289083; harnessgrad.task=cancel-async-tasks; com.docker.compose.project=harbor-build-cancel-async-tasks; com.docker.compose.service=task | owned-by-a-test-run | removed — LEAKED test resource |
| hg-snapshot:leak-test-3264105-cancel-async-tasks | 2576941e00ca | 2026-10-05T23:28:16+00:00 | 44622332 | 182MB / 136.5MB / 45.91MB | harnessgrad.run=leak-test-3264105; harnessgrad.task=cancel-async-tasks; com.docker.compose.project=harbor-build-cancel-async-tasks; com.docker.compose.service=task | owned-by-a-test-run | removed — LEAKED test resource |
| hg-snapshot:leak-test-3235052-cancel-async-tasks | c1482e9c187e | 2026-10-05T23:19:45+00:00 | 44622339 | 182MB / 136.5MB / 45.91MB | harnessgrad.run=leak-test-3235052; harnessgrad.task=cancel-async-tasks; com.docker.compose.project=harbor-build-cancel-async-tasks; com.docker.compose.service=task | owned-by-a-test-run | removed — LEAKED test resource |
| hg-snapshot:leak-test-cancel-async-tasks | ca6c7bfce191 | 2026-10-05T23:08:22+00:00 | 44622332 | 182MB / 136.5MB / 45.91MB | harnessgrad.run=leak-test; harnessgrad.task=cancel-async-tasks; com.docker.compose.project=harbor-build-cancel-async-tasks; com.docker.compose.service=task | owned-by-a-test-run | removed — LEAKED test resource |
| hg-snapshot:oracle-test-cancel-async-tasks | 76f73cf333a7 | 2026-10-05T22:48:00+00:00 | 44622378 | 182MB / 136.5MB / 45.91MB | harnessgrad.run=oracle-test; harnessgrad.task=cancel-async-tasks; com.docker.compose.project=harbor-build-cancel-async-tasks; com.docker.compose.service=task | owned-by-a-test-run | removed — LEAKED test resource |
| hg-snapshot:v8-rrsi-filter-js-from-html | 39b0052d2065 | 2026-10-05T08:13:05+00:00 | 378236689 | 1.48GB / 1.097GB / 379.3MB | harnessgrad.run=v8-rrsi; harnessgrad.task=filter-js-from-html; com.docker.compose.project=harbor-build-filter-js-from-html; com.docker.compose.service=task | owned-by-this-platform | preserved — see preserved list |
| hg-snapshot:codex-rrsi-filter-js-from-html | ffd8f8328a97 | 2026-10-05T04:03:24+00:00 | 378244692 | 1.48GB / 1.097GB / 379.5MB | harnessgrad.run=codex-rrsi; harnessgrad.task=filter-js-from-html; com.docker.compose.project=harbor-build-filter-js-from-html; com.docker.compose.service=task | owned-by-this-platform | preserved — see preserved list |
| hg-snapshot:local-cap32-cancel-async-tasks | bd7d47224f1d | 2026-10-04T07:16:50+00:00 | 45784613 | 187MB / 136.5MB / 50.31MB | com.docker.compose.project=harbor-build-cancel-async-tasks; com.docker.compose.service=task | owned-by-this-platform | preserved — see preserved list |
| hg-snapshot:local-cap12-break-filter-js-from-html | 5c0108ce348c | 2026-10-04T07:15:10+00:00 | 382632527 | 1.49GB / 1.109GB / 383.6MB | com.docker.compose.project=harbor-build-break-filter-js-from-html; com.docker.compose.service=task | owned-by-this-platform | preserved — see preserved list |
| hg-snapshot:deepseek-focus-1-headless-terminal | c5a8489d6a66 | 2026-10-02T17:26:10+00:00 | 66012189 | 242MB / 165.2MB / 77.11MB | com.docker.compose.project=harbor-build-headless-terminal; com.docker.compose.service=task | owned-by-this-platform | preserved — see preserved list |
| hg-snapshot:deepseek-nearwin-1-build-pmars | 5f68d4334ea7 | 2026-10-02T14:36:05+00:00 | 294441791 | 1.08GB / 157.5MB / 921.7MB | com.docker.compose.project=harbor-build-build-pmars; com.docker.compose.service=task | owned-by-this-platform | preserved — see preserved list |
| harnessgrad-task-loop:demo | 9792dc939cfe | 2026-09-29T02:44:14+00:00 | 57411542 | 254MB / 141.2MB / 112.5MB | none identifying creator | unclear | preserved — see preserved list |
| harnessgrad-fake-service:demo | 3a3d25e5d250 | 2026-09-29T02:03:47+00:00 | 45535225 | 187MB / 141.2MB / 45.56MB | none identifying creator | owned-by-this-platform | preserved — see preserved list |

For every `hg-snapshot:*` row, the generator citation is [eval/containers/container_state.py:52](../eval/containers/container_state.py#L52). Test snapshot rows additionally cite the corresponding oracle/leak test generators above; historical experiment rows are platform-owned but not proven leaked. `hg-verdict-symlink-test` has no matching generator in the inspected code and remains `unclear`.

## Container inventory and classification

| Name | ID | Created UTC | State/PID | Writable bytes | Creator/provenance labels | Classification | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hg-reaped-crash-s01-orders | 78fe394d0a32 | 2026-10-14T11:24:36+00:00 | running; PID 2157054 | 4096 | harnessgrad.run=reaped-crash; harnessgrad.task=s01; harnessgrad.service=orders | owned-by-a-test-run | removed |
| hg-verify-oracle-test-3399750-cancel-async-tasks | 5879bae64277 | 2026-10-13T08:01:04+00:00 | running; PID 3402108 | 139264 | harnessgrad.run=oracle-test-3399750; harnessgrad.task=cancel-async-tasks; com.docker.compose.project=harbor-build-cancel-async-tasks; com.docker.compose.service=task | owned-by-a-test-run | removed |
| hg-oracle-test-3399750-cancel-async-tasks | 7b4ec762d9a0 | 2026-10-13T08:00:55+00:00 | exited; PID 0 | 1314816 | harnessgrad.run=oracle-test-3399750; harnessgrad.task=cancel-async-tasks; com.docker.compose.project=harbor-build-cancel-async-tasks; com.docker.compose.service=task | owned-by-a-test-run | removed |
| hg-gaia-searxng-isolated | 96e58c84a90f | 2026-10-12T15:02:05+00:00 | running; PID 1660088 | 425984 | harnessgrad.run=gaia-searxng-isolated | unclear | preserved |
| ael-searxng | 8116f026c64b | 2026-10-09T03:06:21+00:00 | running; PID 1905284 | 499712 | com.docker.compose.project=searxng; com.docker.compose.service=searxng; com.docker.compose.project.working_dir=/mnt/20t/xubuqiang/Efficient-Multi-Agent-System/Agent-Evolving-Library/deploy/searxng; com.docker.compose.project.config_files=/mnt/20t/xubuqiang/Efficient-Multi-Agent-System/Agent-Evolving-Library/deploy/searxng/docker-compose.yml | unclear | preserved |
| hg-verify-oracle-test-2025544-cancel-async-tasks | f79f1f947b93 | 2026-10-07T06:38:45+00:00 | running; PID 2036584 | 95465472 | harnessgrad.run=oracle-test-2025544; harnessgrad.task=cancel-async-tasks; com.docker.compose.project=harbor-build-cancel-async-tasks; com.docker.compose.service=task | owned-by-a-test-run | removed |
| hg-oracle-test-2025544-cancel-async-tasks | 0d0f279f67d6 | 2026-10-07T06:38:37+00:00 | exited; PID 0 | 1318912 | harnessgrad.run=oracle-test-2025544; harnessgrad.task=cancel-async-tasks; com.docker.compose.project=harbor-build-cancel-async-tasks; com.docker.compose.service=task | owned-by-a-test-run | removed |
| past-bench-agent-SM01_CONTROL_003-3548603-1789576142293985669 | c4a0a886408c | 2026-09-16T16:29:02+00:00 | exited; PID 0 | 225280 | app=past-bench; role=agent; run_id=SM01_CONTROL_003-3548603-1789576142293985669 | unclear | preserved |
| past-bench-agent-SM01_LEARN_B_001-3521409-1789572234770818413 | 819d71b9a017 | 2026-09-16T15:23:54+00:00 | exited; PID 0 | 225280 | app=past-bench; role=agent; run_id=SM01_LEARN_B_001-3521409-1789572234770818413 | unclear | preserved |
| past-bench-agent-EP01_I01_recall_cold-3394291-1789544704716920672 | efa0bce84a42 | 2026-09-16T07:45:04+00:00 | exited; PID 0 | 225280 | app=past-bench; role=agent; run_id=EP01_I01_recall_cold-3394291-1789544704716920672 | unclear | preserved |
| past-bench-agent-SM01_EVAL_NEAR_001-2-1789540198704997950 | 105cb69612bd | 2026-09-16T06:29:58+00:00 | exited; PID 0 | 225280 | app=past-bench; role=agent; run_id=SM01_EVAL_NEAR_001-2-1789540198704997950 | unclear | preserved |
| past-bench-agent-SM01_CONTROL_003-9-1789529026204335277 | b62f1052fdc1 | 2026-09-16T03:23:46+00:00 | exited; PID 0 | 225280 | app=past-bench; role=agent; run_id=SM01_CONTROL_003-9-1789529026204335277 | unclear | preserved |
| past-bench-agent-SM01_LEARN_A_001-14-1789526457921756857 | 12cfcef3b105 | 2026-09-16T02:40:57+00:00 | exited; PID 0 | 225280 | app=past-bench; role=agent; run_id=SM01_LEARN_A_001-14-1789526457921756857 | unclear | preserved |
| past-bench-agent-SM01_COLD_001-6-1789525911486143133 | 10fa46abdab7 | 2026-09-16T02:31:51+00:00 | exited; PID 0 | 225280 | app=past-bench; role=agent; run_id=SM01_COLD_001-6-1789525911486143133 | unclear | preserved |
| memos-neo4j | 31b42e2235c0 | 2026-06-22T06:36:38+00:00 | running; PID 813943 | 555167744 | none identifying creator | unclear | preserved |

Oracle harness and verifier rows cite [eval/containers/container_state.py:51](../eval/containers/container_state.py#L51) and [eval/verification/verifier.py:251](../eval/verification/verifier.py#L251) respectively, with the oracle test generator above. The `reaped-crash` service row cites [eval/service/services.py:383](../eval/service/services.py#L383) and [tests/quality/test_services.py:448](../tests/quality/test_services.py#L448). The GAIA service has a run label but no task label and no proven matching task/service generator; its bind-source metadata points into the frozen GAIA controls checkout. That path was recorded, not opened.

## Network inventory and classification

| Name | ID | Created UTC | Creator/provenance labels | Live endpoints | Classification | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| bridge | 70b7f49f2cf3 | 2026-10-06T17:59:03+00:00 | none identifying creator | memos-neo4j, hg-gaia-searxng-isolated, hg-verify-oracle-test-2025544-cancel-async-tasks | unclear | preserved |
| hg-oracle-test-2025544-cancel-async-tasks | e6977c7f196d | 2026-10-07T06:38:36+00:00 | harnessgrad.run=oracle-test-2025544; harnessgrad.task=cancel-async-tasks | none | owned-by-a-test-run | removed |
| hg-oracle-test-3399750-cancel-async-tasks | 29818c9093b1 | 2026-10-13T08:00:54+00:00 | harnessgrad.run=oracle-test-3399750; harnessgrad.task=cancel-async-tasks | hg-verify-oracle-test-3399750-cancel-async-tasks | owned-by-a-test-run | removed |
| hg-reaped-crash-s01 | f3a07effd833 | 2026-10-14T11:24:36+00:00 | harnessgrad.run=reaped-crash; harnessgrad.task=s01 | hg-reaped-crash-s01-orders | owned-by-a-test-run | removed |
| host | afc012dc7827 | 2026-03-05T13:00:30+00:00 | none identifying creator | ael-searxng | unclear | preserved |
| none | 48474429c7c0 | 2026-03-05T13:00:30+00:00 | none identifying creator | none | unclear | preserved |
| searxng_default | 5b5da34683f1 | 2026-03-11T11:13:01+00:00 | com.docker.compose.project=searxng | none | unclear | preserved |

All three test networks match [eval/service/services.py:249](../eval/service/services.py#L249) and their cited test generators. Stopped containers can retain network configuration even when absent from the live endpoint list; both forms of reference were checked. Network disk size is not meaningful/not supplied.

## Volume inventory

| Name = ID | Created UTC | Docker-reported size | Creator/provenance labels | Container users | Disposition |
| --- | --- | --- | --- | --- | --- |
| 2f124b6424bef8d7782da959c14394d160f28f5c08db16753ca64d6b9658144f | 2026-03-11T11:24:26+00:00 | 0B | com.docker.volume.anonymous= | none | unclear; preserved |
| 3d5758babb42389d998a589dc52008329fb975884f0defb5523957e71d4c166a | 2026-03-11T11:30:28+00:00 | 0B | com.docker.volume.anonymous= | none | unclear; preserved |
| 3e07453baa32b955e149ac464844940bf961a8ee46ca4db98c050c0fe928b928 | 2026-03-11T11:11:13+00:00 | 0B | com.docker.volume.anonymous= | none | unclear; preserved |
| 6cdd273e4c6a895f82a06f6b10efa29f00b655b2ea33097556a6fd732833e211 | 2026-03-11T11:00:36+00:00 | 0B | com.docker.volume.anonymous= | none | unclear; preserved |
| 7ef236b8575cd1569eaddab3c75dd4933f271614367b1cd9c963ecc6fc0b33d1 | 2026-10-12T15:02:05+00:00 | 0B | com.docker.volume.anonymous= | hg-gaia-searxng-isolated | unclear; preserved |
| 9be6e5a91b38fec566e4dd6b01c5fd5798c0a4c1d164a61af64017e50ad498f5 | 2026-03-11T11:11:13+00:00 | 0B | com.docker.volume.anonymous= | none | unclear; preserved |
| 58ded3d233130777425dafae3a0ae81dbe24e07561977c8d1da286c5e28606de | 2026-03-11T11:00:36+00:00 | 0B | com.docker.volume.anonymous= | none | unclear; preserved |
| 138bc53dc4a88b450dac4ed530c36d7e1a2c6cc7bf9244a8eeeff963dd5add4f | 2026-03-11T11:09:01+00:00 | 0B | com.docker.volume.anonymous= | none | unclear; preserved |
| 895eb330afeb6b493c26f17256466bde76c0c70089a9c649b84b78182d27deb0 | 2026-03-11T11:24:26+00:00 | 0B | com.docker.volume.anonymous= | none | unclear; preserved |
| 261860f54f3110916dc27b0a73ed7d2aeeff05772620629a6417aaf883512bd2 | 2026-10-09T03:06:21+00:00 | 0B | com.docker.volume.anonymous= | ael-searxng | unclear; preserved |
| bb239e97df4d8332c037261d2b412c91dbf89c93ddf2b2bf2b76e37a1031ac90 | 2026-03-11T11:30:28+00:00 | 0B | com.docker.volume.anonymous= | none | unclear; preserved |
| d1eb7bd98f19e01b85aac1be3e4d7e8ff35f8233a3e2dfeb1158a1bad77deff0 | 2026-03-11T11:09:01+00:00 | 0B | com.docker.volume.anonymous= | none | unclear; preserved |
| d35f972823e259112a63f0ea905014083860a35d54b8745e8495b697038ab619 | 2026-10-12T15:02:05+00:00 | 0B | com.docker.volume.anonymous= | hg-gaia-searxng-isolated | unclear; preserved |
| d356be297c1958220dbe3e4da12feca77d2feb8cd58b10fa346d0684b1510106 | 2026-10-09T03:06:21+00:00 | 0B | com.docker.volume.anonymous= | ael-searxng | unclear; preserved |
| lightmem-latest_structmem-data | 2026-08-20T19:43:04+00:00 | 134.5MB | com.docker.compose.project=lightmem-latest; com.docker.compose.volume=structmem-data | none | unclear; preserved |

No volume is `hg-` prefixed or carries a platform run/task label. Four anonymous volumes are attached to SearXNG services. The unlinked anonymous volumes and `lightmem-latest_structmem-data` were preserved: neither unlinked state nor age proves platform ownership. Volume contents were not opened.

## Exact removal list and results

This exact set was printed and written into the evidence at 2026-10-14T13:50:00.013390+00:00, before removal. Each command returned 0. Full IDs are recorded here as well as in the evidence.

| Kind | Name | Full ID | Recorded bytes | Result |
| --- | --- | --- | --- | --- |
| container | hg-reaped-crash-s01-orders | 78fe394d0a32579ead03fd76d165b46a0e89e60d12e3425a76b88907c50db187 | 4096 | removed; verified absent |
| container | hg-verify-oracle-test-3399750-cancel-async-tasks | 5879bae642773fc6fa01fb9d4206621defd68e65ad19f5d79133fe392ea0a125 | 139264 | removed; verified absent |
| container | hg-oracle-test-3399750-cancel-async-tasks | 7b4ec762d9a0603a2bde75187e9eca84f41e66c8eb86eb528b620dc7a087cbca | 1314816 | removed; verified absent |
| container | hg-verify-oracle-test-2025544-cancel-async-tasks | f79f1f947b93616e9f9c483833ea20991512271e58487d3bac712767f83ae9b1 | 95465472 | removed; verified absent |
| container | hg-oracle-test-2025544-cancel-async-tasks | 0d0f279f67d6c21d90c43ab735a19be834327fe0d82ea4da961f1f4e13a46ca9 | 1318912 | removed; verified absent |
| network | hg-oracle-test-2025544-cancel-async-tasks | e6977c7f196de6b99f278cfa92685416e8ae74e48e4492de757369042267ccbf | N/A | removed; verified absent |
| network | hg-oracle-test-3399750-cancel-async-tasks | 29818c9093b168a98bc415526e0fb7074bfb89e94306e1a7b6cbb6a38e2f2772 | N/A | removed; verified absent |
| network | hg-reaped-crash-s01 | f3a07effd8330eb3d09ad56817581b4701f16fa44433419504acac8e64fdd9f0 | N/A | removed; verified absent |
| image | hg-snapshot:oracle-test-3399750-cancel-async-tasks | sha256:f8d854518cbb9921d00fa73c92a133f7dda38baa3d145556f8f19726a2bcda64 | 44622388 | removed; verified absent |
| image | hg-snapshot:oracle-test-2025544-cancel-async-tasks | sha256:183947fa5af59a47d1aae727526e77a6ce0a0744fe9957998abda204532ad7a9 | 44622402 | removed; verified absent |
| image | hg-snapshot:leak-test-3289083-cancel-async-tasks | sha256:fa21c5a9e8cd3dbc35303d21e56a4f09ba39bdcbe95976279fc8377c34799e71 | 44622330 | removed; verified absent |
| image | hg-snapshot:leak-test-3264105-cancel-async-tasks | sha256:2576941e00ca86e693e4c07add43bef958cb9ae7cd7bf7df2ee8e716ead35c5f | 44622332 | removed; verified absent |
| image | hg-snapshot:leak-test-3235052-cancel-async-tasks | sha256:c1482e9c187e9734506d6a85caa7d587b070c46c2507985fe1d74d6b06ddfc67 | 44622339 | removed; verified absent |
| image | hg-snapshot:leak-test-cancel-async-tasks | sha256:ca6c7bfce191c1a8e089bfdf3a9120038f8d99d0796cac6824d4e9eb2ade4f80 | 44622332 | removed; verified absent |
| image | hg-snapshot:oracle-test-cancel-async-tasks | sha256:76f73cf333a7df962a9d2354d8075d7c9a5e168efdeada46d686f8ca64143c9e | 44622378 | removed; verified absent |

Commands: `docker container rm --force <full-id>`, then `docker network rm <full-id>`, then `docker image rm <full-id>`. Exact per-resource commands, timestamps, stdout and stderr are in `removal_results`. All test resources had been inventoried, attributed, and printed first.

## Exact preserved list and reasons

| Kind | Name | ID | Classification | Reason |
| --- | --- | --- | --- | --- |
| image | harnessgrad/appworld-service:20261009-clean2 | db09e34ec903 | unclear | Provisioned service/agent/task image, not a disposable per-task snapshot; no identified creator or proof of non-use. |
| image | harnessgrad/appworld-service:20261009-clean | 4c5fe8dde77c | unclear | Provisioned service/agent/task image, not a disposable per-task snapshot; no identified creator or proof of non-use. |
| image | harnessgrad/appworld-service:20261009-secure2 | 9b39b96f1efe | unclear | Provisioned service/agent/task image, not a disposable per-task snapshot; no identified creator or proof of non-use. |
| image | hg-verdict-symlink-test:latest | 578a60e5344c | unclear | No creator/run label and no generator found in the inspected code. Test-looking name alone does not establish ownership or disposal authorization. |
| image | harnessgrad/appworld-service:20261009-final2 | f3cb916b9bdc | unclear | Provisioned service/agent/task image, not a disposable per-task snapshot; no identified creator or proof of non-use. |
| image | harnessgrad/appworld-service:20261009-final | 6d383e307a1d | unclear | Provisioned service/agent/task image, not a disposable per-task snapshot; no identified creator or proof of non-use. |
| image | harnessgrad/appworld-service:20261009 | 6fa2d092db0d | unclear | Provisioned service/agent/task image, not a disposable per-task snapshot; no identified creator or proof of non-use. |
| image | harnessgrad/appworld-agent:20261009 | d3a04ec8e295 | unclear | Provisioned service/agent/task image, not a disposable per-task snapshot; no identified creator or proof of non-use. |
| image | harnessgrad/appworld:20261008 | 91cf774386e0 | unclear | Provisioned service/agent/task image, not a disposable per-task snapshot; no identified creator or proof of non-use. |
| image | harnessgrad/gaia:20261008 | 9cc27f813e59 | unclear | Provisioned service/agent/task image, not a disposable per-task snapshot; no identified creator or proof of non-use. |
| image | harnessgrad/tau-bench:20261006 | beda1b01f43c | unclear | Provisioned service/agent/task image, not a disposable per-task snapshot; no identified creator or proof of non-use. |
| image | hg-snapshot:full-b-cobol-modernization | 7b74f7159e7b | owned-by-this-platform | Historical experiment snapshot. No local runs directory, so external run/receipt references cannot be ruled out; not proven leaked. |
| image | hg-snapshot:v8-rrsi-filter-js-from-html | 39b0052d2065 | owned-by-this-platform | Historical experiment snapshot. No local runs directory, so external run/receipt references cannot be ruled out; not proven leaked. |
| image | hg-snapshot:codex-rrsi-filter-js-from-html | ffd8f8328a97 | owned-by-this-platform | Historical experiment snapshot. No local runs directory, so external run/receipt references cannot be ruled out; not proven leaked. |
| image | hg-snapshot:local-cap32-cancel-async-tasks | bd7d47224f1d | owned-by-this-platform | Historical experiment snapshot. No local runs directory, so external run/receipt references cannot be ruled out; not proven leaked. |
| image | hg-snapshot:local-cap12-break-filter-js-from-html | 5c0108ce348c | owned-by-this-platform | Historical experiment snapshot. No local runs directory, so external run/receipt references cannot be ruled out; not proven leaked. |
| image | hg-snapshot:deepseek-focus-1-headless-terminal | c5a8489d6a66 | owned-by-this-platform | Historical experiment snapshot. No local runs directory, so external run/receipt references cannot be ruled out; not proven leaked. |
| image | hg-snapshot:deepseek-nearwin-1-build-pmars | 5f68d4334ea7 | owned-by-this-platform | Historical experiment snapshot. No local runs directory, so external run/receipt references cannot be ruled out; not proven leaked. |
| image | harnessgrad-task-loop:demo | 9792dc939cfe | unclear | Provisioned service/agent/task image, not a disposable per-task snapshot; no identified creator or proof of non-use. |
| image | harnessgrad-fake-service:demo | 3a3d25e5d250 | owned-by-this-platform | Reusable test service image, explicitly built once. Provisioned cache is not a per-task resource leak. |
| container | hg-gaia-searxng-isolated | 96e58c84a90f | unclear | Live SearXNG service with harnessgrad.run=gaia-searxng-isolated and a bind source in frozen GAIA controls evidence. No task label or matching task/service name generator; preserve running infrastructure. |
| container | ael-searxng | 8116f026c64b | unclear | Running SearXNG Compose service; creator project path is Agent-Evolving-Library, outside this platform. |
| container | past-bench-agent-SM01_CONTROL_003-3548603-1789576142293985669 | c4a0a886408c | unclear | Labels app=past-bench and role=agent identify another project; the human creator is unverified. Preserve stopped evidence. |
| container | past-bench-agent-SM01_LEARN_B_001-3521409-1789572234770818413 | 819d71b9a017 | unclear | Labels app=past-bench and role=agent identify another project; the human creator is unverified. Preserve stopped evidence. |
| container | past-bench-agent-EP01_I01_recall_cold-3394291-1789544704716920672 | efa0bce84a42 | unclear | Labels app=past-bench and role=agent identify another project; the human creator is unverified. Preserve stopped evidence. |
| container | past-bench-agent-SM01_EVAL_NEAR_001-2-1789540198704997950 | 105cb69612bd | unclear | Labels app=past-bench and role=agent identify another project; the human creator is unverified. Preserve stopped evidence. |
| container | past-bench-agent-SM01_CONTROL_003-9-1789529026204335277 | b62f1052fdc1 | unclear | Labels app=past-bench and role=agent identify another project; the human creator is unverified. Preserve stopped evidence. |
| container | past-bench-agent-SM01_LEARN_A_001-14-1789526457921756857 | 12cfcef3b105 | unclear | Labels app=past-bench and role=agent identify another project; the human creator is unverified. Preserve stopped evidence. |
| container | past-bench-agent-SM01_COLD_001-6-1789525911486143133 | 10fa46abdab7 | unclear | Labels app=past-bench and role=agent identify another project; the human creator is unverified. Preserve stopped evidence. |
| container | memos-neo4j | 31b42e2235c0 | unclear | Running external Neo4j service with no platform creator label. |
| network | bridge | 70b7f49f2cf3 | unclear | Docker built-in network or external SearXNG Compose network; not generated by the platform task lifecycle. |
| network | host | afc012dc7827 | unclear | Docker built-in network or external SearXNG Compose network; not generated by the platform task lifecycle. |
| network | none | 48474429c7c0 | unclear | Docker built-in network or external SearXNG Compose network; not generated by the platform task lifecycle. |
| network | searxng_default | 5b5da34683f1 | unclear | Docker built-in network or external SearXNG Compose network; not generated by the platform task lifecycle. |
| volume | 2f124b6424bef8d7782da959c14394d160f28f5c08db16753ca64d6b9658144f | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | 3d5758babb42389d998a589dc52008329fb975884f0defb5523957e71d4c166a | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | 3e07453baa32b955e149ac464844940bf961a8ee46ca4db98c050c0fe928b928 | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | 6cdd273e4c6a895f82a06f6b10efa29f00b655b2ea33097556a6fd732833e211 | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | 7ef236b8575cd1569eaddab3c75dd4933f271614367b1cd9c963ecc6fc0b33d1 | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | 9be6e5a91b38fec566e4dd6b01c5fd5798c0a4c1d164a61af64017e50ad498f5 | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | 58ded3d233130777425dafae3a0ae81dbe24e07561977c8d1da286c5e28606de | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | 138bc53dc4a88b450dac4ed530c36d7e1a2c6cc7bf9244a8eeeff963dd5add4f | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | 895eb330afeb6b493c26f17256466bde76c0c70089a9c649b84b78182d27deb0 | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | 261860f54f3110916dc27b0a73ed7d2aeeff05772620629a6417aaf883512bd2 | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | bb239e97df4d8332c037261d2b412c91dbf89c93ddf2b2bf2b76e37a1031ac90 | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | d1eb7bd98f19e01b85aac1be3e4d7e8ff35f8233a3e2dfeb1158a1bad77deff0 | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | d35f972823e259112a63f0ea905014083860a35d54b8745e8495b697038ab619 | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | d356be297c1958220dbe3e4da12feca77d2feb8cd58b10fa346d0684b1510106 | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |
| volume | lightmem-latest_structmem-data | same as name | unclear | Anonymous or external Compose volume; no platform creator label. Unreferenced anonymous volumes are not ownership evidence. |

All images outside the requested name filter, Docker build cache, host/GPU processes, and filesystem evidence were left untouched. No external project was treated as owned by this platform on the basis of a shared account. The seven historical run snapshots remain a follow-up inventory item requiring inspection of their actual run receipts; this cleanup does not certify the host as leak-free.

## Free space

| Measurement | Filesystem available bytes | Filesystem free bytes |
| --- | --- | --- |
| Initial inventory | 132047839232 | 232057659392 |
| Immediately before deletion | 132032778240 | 232042598400 |
| Immediately after deletion | 132143570944 | 232153391104 |
| Follow-up | 132141645824 | 232151465984 |

Docker root: `/var/lib/docker`, on the same root filesystem as this worktree. Immediate available-space change: **+110,792,704 bytes** (105.66 MiB). Concurrent workloads and asynchronous Docker storage reclamation mean this observed delta is not an isolated measurement of bytes reclaimed by deletion. The removed image inspect sizes sum to 312,356,501 bytes; removed container writable sizes sum to 98,242,560 bytes. These are different metrics and not an additive physical-space claim.

## Cleanup-path defect and focused validation

Before the fix, `services.start` acquired a task network and then called `service_env` outside its `except BaseException` cleanup boundary. A configuration-loading error or interrupt could escape while leaving that network behind. The call now runs inside the existing cleanup boundary: [eval/service/services.py:365](../eval/service/services.py#L365). This is a separate proven code defect; the receipt does not claim it caused the historical orphan resources.

Added [test_service_start_cleanup.py](../tests/quality/test_service_start_cleanup.py), which injects configuration failure after mocked network creation and verifies release of that exact network while preserving the original exception. It covers both `RuntimeError` and `KeyboardInterrupt`. All Docker operations are mocked. The two cases failed before the fix and passed after it. This tests a platform lifecycle property, not the host being clean.

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p no:cacheprovider tests/quality/test_service_start_cleanup.py
2 passed
```

The whole test suite was not run. No excluded dataset file/directory was read, imported, modified or executed. No model calls or GPU work were launched. `git diff --check` passed.
