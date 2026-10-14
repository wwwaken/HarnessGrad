# Adapter Integration Journal

This is the repository record of what each dataset taught the platform.

An adapter is not complete when it loads. It is complete when its scorer, runtime, split, evidence, privacy and resource boundaries are understood and recorded. Every new adapter entry must link the evidence artifacts, the platform change, the validation command and the commit that carries the change.

Current planning supersedes historical sizing advice below: follow
[`AGENTS.md`](../AGENTS.md#staged-pilot-policy), first a one-task/one-trial
diagnostic after all dataset gates pass, then a separate review of its valid
measured receipt before any expansion. Temporary reruns of blocked/incomplete
datasets preselect `min(30, ceil(10% * eligible))` tasks, `trials=1`, `jobs=1`.
Historical “Remaining gates” and “Future pilots” advice about a capped-pilot
default, AppWorld 9x3 or Chess 50×3 expansion is superseded for sizing only;
those entries, run IDs, receipts, scores and incomplete statuses remain intact.
AppWorld's successful measured task gate remains unresolved; its measured-zero
smokes are retained, with no task tuning or budget increase authorized here.

## `data/` split complete: scaffolds and datasets separated — 2026-10-14 — ds, ds2, ds3, ds4

- Scope: the structural split in `docs/data-split-plan.md`, Stages A → C → D (Stage B landed earlier as `ad25c7d` and `5cb804e`). No dataset, model, endpoint or pilot execution. Every historical run and archive untouched.
- Result: `data/scaffolds/` holds the shared code (`registry`, `command_control`, `command_oracle_harness`, `qa`, `aggregation`); `data/datasets/` holds 28 adapters with 14 reviewed asset directories; the fixtures (`demo.py`, `probe_set.py`, `broken_service.py`, `verify_*.py`) and the two JSON schemas stay at the top level. **Zero `data.<name>` compatibility shims were created**, per §7: the only three external imports live in frozen receipts, and receipts are not a compatibility obligation. Stage A's temporary scaffold shims existed only between A and C and were deleted in C, which is the only window in which `data.qa`, `data.registry` and `data.command_control` resolved at the old paths.
- **28 published names and their order are unchanged.** Verified by loading `registry.published()` (28, alphabetical), by `tools/check_dataset_blockers.py` (`valid: true`, 28 datasets, 8 shared blockers, 11 historical records) and by `tests/quality/test_data_layout.py`, whose expectation list is hardcoded precisely so it cannot be derived from the discovery it is checking.
- **Three defects the move created, all found by review rather than by a worker, and all fixed.** These are the reason the plan insisted the suite stay green at each step and the reason a wide mechanical move still needs a human:
  1. **`data/tau_bench/db/{airline,retail}.json` (4.2 MB) were stranded.** They are generated artifacts git has never tracked — `.gitignore` ignores `data/datasets/tau_bench/db/` — so `git mv` could not carry them, and the adapter resolves `ASSETS = Path(__file__).parent / "tau_bench"` then `DB_DIR = ASSETS / "db"`. tau_bench would have looked for its databases at a path that did not exist. **No test covered `DB_DIR`**, so nothing would have said so. The files were moved to the new location and both now resolve at 1.18 MB and 3.05 MB.
  2. **`git mv` left empty directories** at `data/qa/`, `data/alfworld/`, `data/appworld/`, `data/jericho/`, `data/nestful/`, `data/reasoning_gym/`, `data/scienceworld/` and `data/spreadsheetbench/`. Git does not track directories, so these were filesystem husks that kept the old paths "present" for anything that checks existence — including the acceptance test. Removed.
  3. **Two surfaces Stage D missed.** `tests/quality/test_musique_official_scorer.py` wrote its fabricated adapter to the old flat `data/inert_qa.py`, so the shared verifier resolved `data.datasets.inert_qa` and exited 3; and `tests/quality/test_boundaries.py`'s opaque-argument rule began firing on `data/scaffolds/registry.py`, because rewriting `import_module(f"data.{name}")` into `import_module(module_name(name))` removed the quote the rule used to let through. Both repaired without weakening: the registry exemption is now earned by a new test asserting that resolver only ever yields `data.datasets.*` and never `methods`/`base_harness`, so pointing it at a method fails there first.
- The acceptance test was wrong once and was corrected, not relaxed: its adapter-import check keyed on "is this root a local name", which flagged `jericho`, `reasoning_gym` and `tau_bench` (third-party distributions that share a dataset's name) and `eval.policy.appworld_reporting` (a `data -> eval` edge governed by `test_import_direction.py`). It now checks the boundary the split exists to create: no adapter imports another adapter, and an adapter's only `data.*` dependency is `data.scaffolds.*`.
- Supporting evidence, all kept: `docs/data-layout-open-items.md` (t3/ds3 — `pinchbench/` holds a feasibility inventory added by `ceb4a55` and its integration-versus-abandonment decision is still unrecorded, so it was deliberately left in place; tau_bench's 4/33/173 classification corroborated, 205 payload hashes matched, no unclassified file) and `reports/stage-d-surface-inventory.md` with its machine-readable twin (902 reference lines, 94 flagged for human decision). The inventory's guard test was written against the pre-split tree and retired once Stage D landed, because after the move it can only describe the old layout; `tests/quality/test_data_layout.py` pins the same boundary against the new one.
- Validation: Stage A **92 passed**; Stage C **126 passed, 9 skipped**; Stage D **214 passed, 10 skipped**; acceptance test **7/7**; focused ten files all green; `--registry-only` **244 passed**; blocker checker and registry publication both correct. The post-merge full suite ran **155 files in 1229 s** and classified **one REAL failure** (`test_appworld_official_scorer.py`, 2 failed, which fails identically on the pre-split tree and on an unrelated branch) and **six load-sensitive files** (`candidate_apply`, `identity_and_verdicts`, `split`, `stop_semantics`, `trials_and_unmeasured`, `unified_budget`, each passing alone). Real failures across the tree are down from 12 before this work to 1.
- Known residual, recorded rather than fixed here: `data/scaffolds/qa/control.py` still decides by module name in `module.__name__.endswith("fever")`. The split did not break it — `endswith` reads the last component, which is still `fever` — but it is the same shape as §3.1, and the guard that removed the `data.bfcl_v3` literal cannot see a bare name like this one. That is the next hardening candidate.
- Commits: `947dd85` (A), `6e042af` (C), `026fb35` (D), `0a19dd5` and `f7dfece` (acceptance test and its correction), `ad905e9` (open items), `feeddb8` and `522e4d3` (surface inventory, and the retirement of its pre-split guard), `aa25da1` (the two missed surfaces).

## The container failures were stale contracts, plus one real cleanup bug — 2026-10-14 — t5

- Scope: the eight files that failed even when re-run alone. Seven were container/runtime files; `test_web_gateway.py` was the seventh. No dataset, model, endpoint or pilot execution.
- Verdict, with the counts: **167 passed, 0 failed, 0 skipped** across the seven files, from a baseline of **21 failures -- 19 stale contract assertions and 2 real test bugs. No environmental verdict on this host**, which is the important part: docker 29.2.1, the images and the `.env` keys are all present, so "no docker" would have been a false explanation.
- **What "stale" means here, and why this is not a weakening.** `008348b refuse tasks without enforced runtime observations` deliberately made the driver fail closed for a task whose declared policy needs a backend observation this checkout cannot supply. `test_container.py` and `test_container_state.py` still asserted the *previous* outcome -- a completed round, `score == 1.0`, a `train_score`, a populated `per_task`. Those assertions now pin the refusal instead, through a new [policy_assertions](../tests/quality/policy_assertions.py) helper that is **stricter than what it replaced**: it matches the entire `invalid` dict field by field (schema `harnessgrad.runner-policy-refusal.v1`, `stage=admission`, `status=blocked`, `reason=backend_observation_unavailable`, `measured=False`, `production_authorized=False`, `observation=unknown`, and the exact `policy_fields`), `exit_code is None`, empty answer/trace/stderr, `model_gateway is None`, no `score` and no `verdict` key, per-task progress records whose `harness_output` is pinned, **no traces, no curve and no recordings**. Net assertion count moved 60 -> 53 in one file and 48 -> 51 in the other; no `skip`, no `xfail`, and no production override was added. The commit touched test files only.
- **A real platform bug, found by the same pass (`c42cb81`).** Docker 29 answers a removal of an already-gone network with `Error response from daemon: network NAME not found` where older daemons said `No such network`. Teardown after crash-reaping therefore reported a failure for a network it had correctly removed, which broke idempotent stop. `remove_network` is now reused during service teardown and both daemon replies are accepted, while errors for an active endpoint, a missing plugin or a *different* network are still reported.
- **A cross-worker interference, recorded rather than hidden.** The Docker cleanup (t6) was removing leaked platform-owned resources while this triage was running its own container tests, so resources the triage had inventoried disappeared mid-run. The triage's report states this as an unattributed daemon change instead of quietly re-running until it passed. Concurrency between two workers that both touch the same daemon is a real hazard and the remedy is sequencing: the cleanup should have run before the triage, not beside it.
- Validation on the merged tree: `test_container.py` **26**, `test_container_state.py` **19**, `test_jericho_runtime_admission.py` **13**, `test_jericho_runtime_boundaries.py` **17**, `test_appworld_service_diagnosis.py` **6**, `test_services.py` **43**, `test_web_gateway.py` **43** -- **167 passed**, in the four-lane runner with `test_services`/`test_container`/`test_container_state`/`test_web_gateway` in the exclusive lane.
- Evidence: [per-test verdicts](../reports/t5-verdicts.md), [overview](../reports/t5-overview.md).
- Commits: `8ce1785`, `c42cb81`, `08de995`, `304fa5a`.

## Concurrency defects, a leaked-network fix, and a Docker cleanup receipt — 2026-10-14 — t3, t6

- Scope: test isolation and host resource lifecycle. No dataset, model, endpoint or pilot execution.
- **`test_unix_model_relay.py` (t3, `99bef5b`).** Root cause found and named: the server's listen backlog is `request_queue_size = 5` by default, while the budget tests start up to eight clients that synchronize only *after* connecting. If `accept` is descheduled, clients are stranded outside the barrier and the run fails for a scheduling reason. Fixed by reserving eight slots in the fixture, plus the client now tolerates the server closing after a header-only rejection: the `BrokenPipeError` from `HTTPConnection`'s separate body write is caught, and the response is then read and asserted as before, so a missing or malformed response still fails. Two new deterministic regressions (gating `get_request`; observing `shutdown_request`) pin it without depending on machine speed. Verified **51 passed** serial and **51 passed in each of two concurrent copies**.
- **`test_isolation.py` (t3, `438af4c`).** The autouse guard added earlier in the day had itself become the load-sensitive part: it stats the whole checkout around every test and did not exclude the caches a concurrent process legitimately writes. The guard now prunes generated directories before comparing, so it still fails a test that edits the checkout while no longer flagging a neighbour's bytecode. **16 passed**, and the file is green in the configuration that previously reported `1 failed, 13 passed, 2 errors`.
- **`test_candidate_apply.py` (t3, `e084c60`).** Fixture directories made per-test instead of shared. **32 passed.**
- **`eval/service/services.py` (t6, `4e67250`) — a real platform defect, not a test defect.** `service_env(...)` was evaluated *before* the cleanup boundary that covers container startup, so a configuration failure raised after the task network had already been created left that network behind on the daemon. The call now sits inside the same boundary, so `RuntimeError` and `KeyboardInterrupt` both release it. Pinned by a new test that asserts `released == acquired` for both exception types, over a monkeypatched docker that fails on any operation other than the two it expects. Measured effect on the suite: `test_services.py` went from 6 failures to 5.
- **Docker cleanup receipt (t6, `4e67250`).** Inventory, classification and removal recorded in [the receipt](../reports/docker-resource-cleanup-20261014.md) with machine-readable evidence beside it: **removed 5 orphaned test containers, 3 test networks and 7 test snapshot images; preserved 20 images, 10 containers, 4 networks and all 15 volumes.** Ownership was decided from the code that generates each name (`eval/service/services.py`, `eval/containers/container_state.py`, `eval/verification/verifier.py`, and the tests' own `oracle-test-<pid>` / `leak-test-<pid>` identifiers), not from the `hg-` prefix, and a shared Unix account was explicitly not treated as proof of ownership. The receipt states its own limits: this worktree has no `runs/`, so "unreferenced" is established only within the permitted checkout, and inaccessible external historical receipts were not globally searched. No prune, no force-removal, no volume deletion.
- Validation: `test_service_start_cleanup.py` **2 passed**, `test_candidate_apply.py` **32 passed**, `test_unix_model_relay.py` **51 passed**, `test_isolation.py` **16 passed**; `test_services.py` re-ran alone as a REAL failure with **5 failed, 32 passed**, which t5 is triaging.
- Commits: `99bef5b`, `438af4c`, `e084c60` (t3), `4e67250` (t6).

## `eval/` grouped by concern, and the data-split open questions closed — 2026-10-14 — e1, t1, t2, t4

- Scope: the structural refactor of `eval/` plus four documents. No dataset, model, endpoint or pilot execution.
- **`eval/` split (e1, merged as `b96941a`).** 32 flat modules moved into seven subpackages — `run/`, `containers/`, `admission/`, `service/`, `observe/`, `policy/`, `verification/` — with the 32 old top-level paths left as **module-identity shims** (`sys.modules[__name__] = _implementation`), not `import *` re-exports, so private names, patch targets and mutable state are shared and a `monkeypatch.setattr("eval.runner.X")` still reaches the implementation. Verified after merging: all 32 shims import and alias to a subpackage implementation, and `eval.trace.first_object`, `eval.metrics.mean`, `eval.diagnostic_policy.ENDPOINTS` all resolve through them.
- Conflict resolution, and the reason it was not mechanical: three of the four conflicting files were conflicts of *kind*, not of text. `eval/diagnostic_policy.py`, `eval/metrics.py` and `eval/trace.py` had become shims on one side while carrying this round's edits on the other (the single-endpoint `ENDPOINTS`, the declared aggregation denominator in `mean`, the shim expiry). Taking the shim and re-applying each edit to the new implementation is the only resolution that keeps both; a checkout of either side alone would have silently reverted one of them. `tests/quality/test_isolation.py` conflicted because both sides had rewritten the same tests: the synthetic-platform structure was kept and every path inside it moved to the canonical layout.
- **`docs/data-split-plan.md` (t4, `9fe6404`).** The external-consumer question in §7 is answered: exactly three imports of `data.<name>` exist outside the repository, all in frozen receipts under `HarnessGrad-evidence-archive/`, and the rule that receipts are preserved means they must not be edited and that a re-execution failing against a new layout is correct behaviour. **Stage D therefore needs no compatibility shims**, and the plan's shim work and its estimate are retracted. The plan gains the single-writer prerequisite as a Stage D gate.
- **`docs/tau-bench-vendoring.md` (t1, `17fba78`).** 210 files inventoried: 4 adapter assets, 33 vendored upstream files (every one with recorded provenance, matching the pinned archive byte-for-byte), 173 generated, **0 unclear**. Open items are listed rather than assumed closed: two databases are absent and their reproduction is unverified, and upstream licence packaging is not established. No test was added, because the condition for one — an unprovenanced vendored file — was not met.
- **`docs/registry-discovery-order.md` (t2, `905d985`).** Verdict: the published order **is observable**. The chain is `glob("*.py") → sorted(paths) → kind_of() filtering → published()`, and four consumers preserve that sequence (`datasets_with_downloads()`, `published_datasets()`, `classify_all()`, `scan_options()` → `/api/options`). No catalog-order dependency was found in task selection or in splits. The 28-name sequence is now pinned by `tests/quality/test_registry_discovery_order.py`, so a file move that changes what a user sees fails loudly. The worker reported a scope breach — an early `rg` filter re-included an excluded path in a search — and the diff was checked: no excluded file was read into a change and nothing under `eval/` or `data/agentdojo` was touched.
- **The human commits to `main` directly, and that is supported.** Three commits landed on `main` while this round was running that this session did not make — `7fb474f`, `5a3b6e8` (adding `docs/eval-split-design.md`) and `ee2ea6f` — because the operator was editing the same corpus. The rule this session follows, and which `AGENTS.md` should state plainly: the operator may commit to the integration checkout at any time; an agent merges **on top of** whatever it finds and never rewrites, rebases away, or moves the operator's commits. The one thing to watch is ordering rather than ownership — a full suite that starts before the operator's commit describes the tree as it was, so a result is only attributable if the HEAD is recorded next to it. This round's suite ran from `344d432` and its classification is quoted against that commit.
- Validation: the post-merge full suite ran **152 files in 1475 s** and classified **8 files failing alone** (appworld scorer 2, appworld service diagnosis 1, container 6, container_state 1, jericho admission 1, jericho boundaries 2, services 6, web_gateway 3 — all pre-existing docker/host conditions) and **5 failing only under 12-way concurrency** (identity_and_verdicts, isolation, split, stop_semantics, unified_budget). That is down from 12 real and 8 load-sensitive before the merge, and `test_dataset_controls`, `test_cli_harness`, `test_parallel_tasks`, `test_verifier` and `test_unix_model_relay` all pass. Focused verification of the merged work: 234 tests over ten files, then 113 over six.
- Commits: `b96941a` (eval split), `9fe6404`, `17fba78`, `905d985` (documents), `27a9306` (the three new documents re-included in `.gitignore`, which they had to be: `/docs/*` ignores them and each was only force-added).

## One GPU endpoint, one writer, and a bounded shim — 2026-10-14 — parent

- Scope: host operations and platform policy, not a dataset. Two servers of the same model (`qwen3.5-9b-local`) were running, on GPU0/`8001` and GPU1/`8002`. The GPU0 server was stopped (SIGTERM, verified: `8001` no longer listening, GPU0 at 10 MiB / 0 %) to release the card, and operations concentrate on `8002`.
- Why `8002` and not `8001`: `eval/unix_model_relay.py` hard-codes the agent's model route to `127.0.0.1:8002`, so `8002` is the endpoint a containerised harness actually reaches. Keeping the other would have required a production change. `eval/diagnostic_policy.py::ENDPOINTS` is now the single live entry — it is what a staged receipt's `endpoint` is validated against, so a retired server left in the list would let a receipt attest to a binding nothing can serve.
- Utilization, stated plainly: **both GPUs measured 0 % utilization while loaded.** No dataset has `production_authorized=true` (all 28 carry an open shared blocker), so there is no approved diagnostic or pilot to run. The endpoint is left loaded and idle and no work was invented for it; `AGENTS.md` now records that idle is the correct state in this situation.
- Working-copy topology: an external scan found that two full clones inside `Study/` (`HarnessGrad-appworld-controls-20261117`, `HarnessGrad-gaia-controls-20261117`) are stranded on pre-rewrite commits whose objects do not exist in `main`'s store, still carry the old layout, and had `origin` pointing at the main checkout for fetch **and push**. Their remotes were removed; the checkouts were deliberately **not** deleted or reset, because they hold receipts and evidence (`gaia-evidence/`, `gaia-evidence-all17/`, `GAIA_FINAL_LAUNCH_RECEIPT.json`, the appworld `deliverables/` and `runtime/`) that exist nowhere else and rule 5 preserves old receipts. 10 of 20 local branches also point at pre-rewrite commits; they are refs, not writers, and were left for an explicit decision.
- `eval/trace.py` now carries an expiry of **2026-11-14** and says what to do then. The previous shim batch was removed only after outliving its callers and had no deadline; a shim without one outlives its reason.
- Regression found by the post-merge suite, and fixed: the aggregation-declaration merge broke three files that its own focused set did not cover — `test_parallel_tasks` staged a minimal platform without `data/aggregation.py`, and `test_cli_harness` / `test_verifier` run the undeclared `verify_demo` fixture through the driver. The fail-closed accessor is correct and kept; the three `verify_*` fixtures are now declared and the guard's `FIXTURES` set matches. `POLICY_REFUSED` narrowed to `gaia`, the only declared control that runs through `--platform` and is therefore stopped by the hook.
- Validation: `test_aggregation_policies.py`, `test_parallel_tasks.py`, `test_cli_harness.py`, `test_verifier.py` — **81 passed**; `test_dataset_controls.py` — **25 passed, 1 skipped**; `test_diagnostic_policy.py`, `test_trace_reader.py`, `test_staged_receipt_audit_codex193.py`, `test_lifecycle_receipt_codex177.py` — **224 passed**. Full suite on the merged tree classified 12 files failing alone and 8 failing only under 12-way concurrency.
- Commits: `01d419b` (regression repair) and `a62e163` (endpoint retirement, shim expiry, working-copy rule).

## Explicit aggregation denominators — 2026-10-14 — s9

- Scope: Stage B part 2 only, isolated `/tmp/hg-s9`, base `80c3707`; fabricated scorer inputs and pinned upstream source only.
- Finding: **(c), undocumented platform helper contract mismatch**. MuSiQue's `aggregate` divides by provided results, but upstream requires equal row counts and aligned IDs. 2Wiki's `evaluate_predictions` divides by all gold rows, matching upstream's missing-prediction behavior. Neither helper is the driver's run aggregation path.
- Change: explicit per-adapter aggregation manifests and a fail-closed shared denominator accessor, read by both corpus helpers and recorded run rewards. All 28 published adapters declare the existing measured-task run mean; excluded/locked adapter sources remain untouched.
- Evidence: [s9 report](../reports/s9-aggregation-denominator-report.md); `tests/fixtures/aggregation_s9_before.json`; `tests/quality/test_aggregation_policies.py` inventories source with AST and proves declarations are live.
- Numeric preservation: full synthetic before/after captures identical, SHA-256 `d7ab601e446d0a4eb24fde6bffe97fbc026669c43b84b7407224106e0040ee55`; MuSiQue reward `0.48148148148148145`, omitted-item helper reward `1.0`; 2Wiki complete/missing-row Joint F1 `100.0`/`50.0` percent remain identical.
- Validation: only aggregation-policy (**41 passed**), MuSiQue official-scorer (**106 passed**) and 2Wiki structured (**43 passed**) files; external basetemps under `/mnt/20t/xubuqiang/.hg-pytest/s9/`. No benchmark pilot/model execution.
- Commit: carried by `Declare per-adapter aggregation denominators without changing rewards`; parent integration in this round merged it as the aggregation-policy commit with the journal conflict resolved by keeping both entries.

## SpreadsheetBench QA submission provisioning — 2026-10-14 — S3

- Scope: isolated `/tmp/hg-s3`; only the requested SpreadsheetBench oracle control and one new focused regression file. No model or GPU execution.
- Cause: `data/spreadsheetbench.py::_setup` materialized `qa/bin/qa` without the module it imports, `qa/prediction.py`, so the submission CLI exited 1 with `ModuleNotFoundError: No module named 'prediction'`. `control.py::solve` ran it with `capture_output=True`, so both streams were discarded and the control reported only `CalledProcessError`. The golden workbook was present and copied correctly, and provisioning reported 400 tasks with LibreOffice available, so nothing about the data or the scorer was wrong.
- Change: declare `qa/prediction.py` in the dataset's `SETUP`, and drop the output capture so a failed submission prints the CLI's real error instead of a bare exit status. The comparison, the reward rule and the platform verifier are unchanged.
- Validation: `python3 data/spreadsheetbench/control.py --oracle` reaches reward **1** with `"measured": true`; the new `tests/quality/test_spreadsheetbench_control_submit.py` passes **2/2**, including a deliberately failing CLI that must expose both stdout and stderr. Together with `tests/quality/test_spreadsheetbench_official_scorer.py`: **13 passed**. No whole-suite execution in the worker worktree.
- Commit: `8c323e6 Fix SpreadsheetBench QA submission provisioning and diagnostics`; parent diff review and the focused re-run on `main` passed.

## Refusal contract without a stale catalog count — 2026-10-14 — S5

- Scope: isolated `/tmp/hg-s5`; one test file.
- Finding: `tests/quality/test_split_source.py::test_no_refused_dataset_pretends_to_have_an_evaluation_set` ended with `assert len(refused) >= 6`. Measured on the current catalog: exactly **4** adapters set `REFUSED` (`api_bank`, `nestful`, `sotuqa`, `tau2_bench`), so the minimum was a stale snapshot of the catalog rather than a contract. The per-adapter assertions it guards — a refused adapter must not publish `OFFICIAL_EVAL` and must reject `official_split` — were untouched.
- Change: keep the per-adapter contract and a non-vacuity check (`assert refused`), and drop the count. The docstring now says the number of refusals moves as adapters gain scoring support, and that only the per-adapter contract is fixed.
- Validation: `python3 -m pytest -q tests/quality/test_split_source.py` — **12 passed** on `main` after the merge.
- Commit: `80c3707 test: pin refusal contract without a stale catalog minimum`.

## Reports relocation and link repair — ref-8 — 2026-10-14

- Scope: repository layout. Audit, evidence and review output that had accumulated in the repository root was moved into `reports/` so the root stays navigable.
- Change: 65 tracked audit/evidence files relocated, the 24 relative references they broke were repaired, and `reports/` plus `AGENTS.md` were added to the integrity checker's `NOT_PLATFORM` list with written reasons — they are written by humans and review sessions after a measurement and are never read by a run, so hashing them would fail a certification because someone added a report.
- Evidence: [reports move verification](../reports/reports-move-verification.md). `reports/` now holds 68 files.
- Commits: `ad57926 cleanup: move audit and evidence files into reports/` and `8c9bf28 docs: verify reports move and repair relative references`. These carry rewritten identities after the history rewrite; the content is on `main`.

## Architecture map and import-direction guard — ref-6, ref-7 — 2026-10-14

- Scope: documentation and a source-only guard. No runtime, model or GPU execution.
- Change (ref-6): `docs/architecture.md` records the verified structure of the repository — which layers exist, what each owns, and which way imports are allowed to point.
- Change (ref-7): `docs/import-direction.md` states the rule, and `tests/quality/test_import_direction.py` enforces it by parsing every source file's imports. The guard records **11** existing `data -> eval` edges as explicit, reviewed exceptions rather than hiding them; a new edge outside that list fails.
- Validation: the guard test passes on `main` as part of the focused suite.
- Commits: `3d78cde docs: add verified repository architecture map` and `bee9e3d test: guard architecture import directions` (rewritten identities).

## Removal of unused top-level runtime shims — ref-3 — 2026-10-14

- Scope: dead-code removal in `harnessgrad/`.
- Change: `harnessgrad/events.py`, `harnessgrad/validator.py` and `harnessgrad/compat.py` were re-export shims with no remaining importers; they were deleted rather than left as a second, silently stale definition of the same names. No caller, schema or behaviour changed.
- Commit: `4b99bf4 Remove unused top-level runtime re-export shims` (rewritten identity).

## Jericho standalone verifier temp directory — 2026-10-14 — S2

- Scope: isolated `/tmp/hg-s2`; only the explicitly requested `acorncourt` oracle and a new focused regression file. No model or GPU execution.
- Cause: the standalone `/tmp/jericho-control-*` layout makes the verifier's fallback work root (`workdir.parent.parent`) equal `/`. The final read-only root bind covers the sandbox's private `/tmp`. Under the check's UID 1026, `/tmp`, `/var/tmp`, and the task directory fail creation with `EROFS`; `/usr/tmp` is absent. About 124 GiB and 112 million inodes remain available. Python's tempfile probing reports the combined failures as `ENOENT`.
- Change: `data/jericho/control.py::run_check` supplies its own `.control` work root, matching the agent phase, and restores the caller's environment even on verifier exceptions. The check retains writable private `/tmp` and read-only task artifacts. Shared sandbox/verifier code and the scoring rule are unchanged.
- Validation: `python3 data/jericho/control.py --oracle --task-id acorncourt` changes from unmeasured reward `-1` to measured reward **1**, **30/30 points in 17 moves**. `python3 -m pytest -q tests/quality/test_jericho_control_tempdir.py` passes **4/4**, including real sandbox temp writes and exception restoration. No whole-suite execution.
- Evidence: [unique receipt](../reports/jericho-control-tempdir-s2-receipt.json) records same-user candidate probes, source/code hashes, selected-task coverage, limits, exact control results, and an additional identical-control invocation with observed cleanup.
- Commit: accompanying focused `fix: give Jericho control verifier a dedicated work root`; parent integration remains separate.

## Canonical trace reader — 2026-10-14 — ref2

- Scope: structural refactor in isolated `/tmp/hg-ref-2`; no model/H0 execution.
- Finding/change: `eval.trace` handled reply parsing and loop facts while `eval.tracing` handled metadata and task artifacts. `eval.tracing` now owns all existing reader implementations; `eval.trace` only re-exports compatibility names. Callers and source references point to the canonical module.
- Evidence: `tests/quality/test_trace_reader.py` checks canonical function identity, caller imports, adapter delegation and existing parsing/metadata rules. AST comparison against the base commit confirms all nine pre-existing function implementations are unchanged.
- Validation: `python -m pytest -q tests/quality/test_trace_reader.py tests/quality/test_harness_submit.py tests/quality/test_task_id_paths.py tests/quality/test_appworld_receipt_integration_codex169.py tests/quality/test_harness_parsing.py tests/quality/test_method_channel.py --basetemp=/tmp/hg-ref-2/.pytest-tmp-trace-reader` — **69 passed**. This includes every test file directly importing either module. `git diff --check` passed.
- Commit: accompanying focused trace-reader refactor; parent integration remains separate.
## Pytest workspace placement — 2026-10-14 — Ref 9

- Scope: developer experience and test configuration in isolated `/tmp/hg-ref-9`.
- Finding: an in-platform `--basetemp` places driver tests' harness work roots
  inside the platform, correctly triggering the existing workspace refusal.
- Change: moved all 59 existing basetemp path arguments across 50 tracked files
  to dedicated external `/tmp/harnessgrad-pytest-*` directories; added warnings
  in contributor/test guidance and a root pytest startup guard. Relative,
  absolute, normalized and symlinked explicit paths are checked before tests
  run or pytest clears the directory. The normal default is preserved.
- Historical command paths in reports, captured output and the HTML companion
  are normalized for safe reuse. Their recorded results and other historical
  claims are unchanged; these edits do not claim those suites were rerun.
- Evidence: [exact commands and output](../reports/pytest-basetemp-ref9-validation.txt).
  The eight-test core set contains the six affected driver tests and two trial
  controls. Before the fix, the internal basetemp reproduced **6 failed, 2 passed**.
  After the fix, that invocation exits **4** before collection with an actionable
  error; the external basetemp passes **8/8**. Both affected files plus guard
  regressions pass **34 tests**, with **1 skip** for an absent historical run
  artifact. Guard regressions also verify the normal default.
- Runtime boundary: `driver.py` and `eval/runner.py` are unchanged. Validation
  uses only mock/demo tests; no model, endpoint, GPU or production H0 execution.
- Commit: accompanying focused `fix: keep pytest workspaces outside the platform`.

## Ordinary-run receipt semantics — Task 237 — 2026-10-14

- Scope: docs/tests only in isolated `/tmp/hg-codex-237`, base `0930d99cc882c5a049c98f9123e9427470e7e818`; no execution, host inspection, admin change, benchmark, provider, model, GPU, Docker or scorer calls.
- Deliverables: [proposed semantics and explicitly illustrative receipt](task-237-ordinary-run-receipt.md), [closed documentation schema](task-237-ordinary-run-receipt.schema.json) and [authored contract tests](../tests/quality/test_ordinary_run_receipt_codex237.py). Existing runtime/admission code and schemas are unchanged.
- Semantics: quota `false` is a known coverage gap; `"unknown"` is missing evidence. Requested/effective host/task sandbox boundaries remain separate. Local measured zeros, invalid attempts and unmeasured attempts remain distinct; snapshot/cleanup failures withhold the aggregate. Metric identity, selection/trial coverage, provenance gaps and comparison limits are explicit.
- Authorization: ordinary results always carry non-production labels and false production/formal-evidence/publication flags. Existing `certified` metadata is not formal authorization. This proposal adds no driver mode, no ordinary receipt writer, no relaxed gate and no permission to disable isolation or run a refused dataset.
- Validation: tests authored but **not executed**, per the task instruction; no pass count, score, runtime receipt or cleanup claim. Static source/diff review and `git diff --check` only; the whitespace check passed. Parent review/integration and any future implementation remain separate.

## Fresh diagnostic dry-launch template — 2026-10-14 — Task 223

- Status: `planning`; no dataset/task selected; no run ID reserved; no model/H0 or endpoint execution.
- Scope: docs-only source review in `/tmp/hg-codex-223`, base `82459cfa6d16c323ca40f21db2daf597921aedb3`; driver staged policy, diagnostic schema, lifecycle/admission contracts and current run-metadata writer.
- Evidence: [unique dry template and checklist](task-223-dry-diagnostic-launch.md), including exact receipt/metadata fields, empty planning envelope, future coverage invariants and evidence bindings.
- Finding: the current driver still supplies unknown cleanup/snapshot and no lifecycle producer; metadata records a plan, not production completion. Trusted observation/integration and dataset gates remain pending. This document grants no launch or expansion authorization.
- Validation: static embedded-JSON/schema-key/link checks and `git diff --check`; no runtime imports, datasets, tests, backend or model calls. Validation details accompany the template.
- Commit: accompanying Task 223 docs-only change; no parent/main merge.

## Staged diagnostic receipt audit — 2026-10-14 — Codex 193

- Status: `preflight`; narrow correctness fixes verified, publication remains blocked by missing trusted observations.
- Scope: isolated `/tmp/hg-codex-193`, base `a58b4b181193a2e2b201c6353722725ad77b597c`; source and authored synthetic tests only; no model/H0, heldout reads, Docker/backend queries or GPU runs.
- Finding: explicit timeout/nonzero exits could appear measured in staged adaptation; fresh receipt directories could still delete old workspace evidence and reap stale resources; schema allowed passing summaries with null hashes that Python refused.
- Platform change: staged adapter checks explicit exit results; staged workspace identities reserve exclusively and refuse old evidence; fresh staged runs skip legacy reaping; schema requires hashes for all passing summaries.
- Evidence: [exact audit and retained gaps](../reports/staged-receipt-audit-codex193-report.md), `tests/quality/test_staged_receipt_audit_codex193.py`, [captured test result](../reports/staged-receipt-audit-codex193-test-result.txt).
- Failure persistence: plans survive post-write preparation failures and evaluation exceptions; returned outcomes produce a separate final receipt; exceptions do not guarantee a final failure receipt. Exclusive writes are not crash-atomic/fsynced.
- Remaining gates: driver has no lifecycle producer; backend admission/quiescence/snapshot/cleanup observations, provenance verification, selected-only/scorer closure, provisional progress publication integration and global ownership/concurrency remain unresolved.
- Validation: **479 passed**, no failures/skips, six focused synthetic suites; exact command in the report; `git diff --check` passed. Synthetic lifecycle success is not production authorization.
- Commit: carried by this worktree's scoped receipt-correctness change; no main merge.

## Shared lifecycle publication gate — 2026-10-14 — Codex 177

- Status: `preflight`; shared offline contract implemented, trusted backend observations pending
- Scope: isolated `/tmp/hg-codex-177`, base `e7acaa1`; code/schema and authored synthetic tests only; no dataset, model/H0, Docker or GPU execution
- Finding: staged receipts and curves could expose measured scores while cleanup/snapshot attestations were unknown; snapshot preflight and best-effort removal cannot prove lifecycle completion
- Evidence: [lifecycle review](../reports/lifecycle-codex177-report.md), `eval/lifecycle_receipt.py`, `tests/quality/test_lifecycle_receipt_codex177.py`, `reports/lifecycle-codex177-test-result.txt`
- Platform change: immutable `scope/admit/execute/quiesce/score/seal/cleanup` checkpoints, shared admission replay, snapshot-worker/completion evidence, failure-only cleanup path, scoped sealed-outcome publication gate, diagnostic v2 and staged curve refusal with unknown evidence
- Remaining gates: independent observer and quota enforcement, snapshot capacity reservation, scorer/artifact linkage and closure, complete cleanup/lease backend, legacy non-staged publication integration; synthetic passes confer no production authorization
- Validation: exact four-suite offline command in the review; **439 passed**, no failures/skips; `git diff --check` passed; production modules do not import synthetic lifecycle fixtures
- Commit: this commit, `fix: gate staged score publication on shared lifecycle receipts`; existing receipts preserved; no main merge

## Entry format

```markdown
## Dataset — YYYY-MM-DD

- Status: `preflight` | `pilot` | `complete` | `blocked` | `incomplete`
- Scope: exact pool, split, pilot size and trial protocol
- Finding: what the dataset exposed
- Evidence: files, tests, controls or run IDs
- Platform change: reusable capability added or corrected
- Remaining gates: unresolved decisions or runtime requirements
- Validation: exact commands and results
- Commit: commit or `uncommitted artifact`
```

Do not record a partial score as a complete result. Use `incomplete` when execution stopped, timed out before measurement, or crossed a platform-integrity boundary. Keep diagnostic numbers separate from archive effects.

## TriviaQA — offline scorer provenance — 2026-10-14

- Status: `blocked` upstream acquisition; docs/tests repair complete, no model/H0
- Scope: fabricated scorer inputs and inert integrity-test bytes only; no released train/validation/test or heldout reads, no network requests
- Finding: the inherited “official” reference was a second local transcription, with no independent scorer commit or source bytes. The Hub dataset revision does not pin the GitHub evaluator; adapter “verbatim” claims remain unverified.
- Evidence: `tests/fixtures/triviaqa_upstream/README.md`; `tests/quality/test_triviaqa_official_scorer.py`; `DOWNLOADS.md` TriviaQA provenance notice; fresh `reports/triviaqa-scorer-provenance-codex157-report.md`
- Platform change: test-only acquisition contract requiring original source/license bytes, a separate immutable commit, reviewed origin/linkage attestation, and SHA-256/Git blob pins. The regular suite skips the upstream differential when fixture is absent; `tools/check_triviaqa_provenance.py` is the explicit nonzero gate and never falls back to a local copy.
- Comparison limits: `rc.nocontext` supplies no documents; validation differs from test evaluation; current reward is alias-max EM only; row-position identity drops question/document grouping. Full upstream grouping, denominator and missing-prediction rules remain unverified. No upstream code or F1 was invented or added.
- Validation: after `mkdir -p .scratch/triviaqa-provenance`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/quality/test_triviaqa_official_scorer.py --basetemp=/tmp/harnessgrad-pytest-triviaqa-provenance-pytest` — exit 1, **28 passed / 1 failed**, solely the absent-fixture provenance gate; no skips/errors. Adding `-k 'not test_em_components_match_pinned_upstream_fixture'` and using `--basetemp=/tmp/harnessgrad-pytest-triviaqa-provenance-pytest-local` — exit 0, **28 passed / 1 deselected**, not upstream certification. `git diff --check` passed.
- Remaining gates: independently acquire and review the original fixture/license/commit linkage, resolve any measured EM drift, then separately verify full evaluator grouping and comparison identity. No production H0 authorization follows from these synthetic checks.
- Commit: carried by `test: fail closed on unacquired TriviaQA scorer provenance`; exact hash reported with delivery

## TriviaQA — upstream evaluator acquired, adapter correction pending new identity — 2026-10-14

- Status: `source provenance acquired`; current adapter correction is isolated and historical runs remain unchanged
- Finding: public GitHub commit `ca43b5820b107f3970cf4b7d67f7db7a98117b79` supplies the original evaluator, helpers, Apache-2.0 license and Git-object evidence. The acquired differential found a real normalization mismatch: upstream replaces punctuation and underscores with spaces, while the old adapter removed and joined them.
- Platform change: `data/triviaqa.py` now follows the pinned upstream normalization for new runs; the scorer identity must change. Existing curves remain under their original identity and are not rewritten.
- Validation: synthetic upstream differential and provenance tests are rerun after the correction; no TriviaQA payload or heldout rows were read.
- Remaining gates: independent parent review of source equivalence, Hub dataset revision-to-scorer mapping, grouping/denominator semantics and fresh diagnostic authorization. This correction alone does not authorize a pilot.

## TriviaQA — scorer correction review — 2026-10-14 — Codex 205

- Status: `preflight`; synthetic EM component review passed, production comparison remains gated
- Scope: isolated `/tmp/hg-codex-205`, base `65b0f2a`; public scorer/license/Git evidence and fabricated test inputs only; no TriviaQA payload/heldout, model/H0, endpoint or GPU execution
- Finding: acquired source/license hashes and commit/tree linkage pass; merged normalization correction matches upstream. A remaining 200-alias cap loses a fabricated match at alias 201. Scorer evidence had no new explicit identity; fixture/download docs still described the old acquisition failure.
- Evidence: [unique review](../reports/triviaqa-scorer-review-codex205-report.md), `tests/quality/test_triviaqa_scorer_review_codex205.py`, [focused result](../reports/triviaqa-scorer-review-codex205-test-result.txt)
- Platform change: preserve every alias for the max; new verifier evidence records `triviaqa-alias-max-em-upstream-normalization-all-aliases-v2` and the pinned upstream reference. Docstrings distinguish matching EM semantics from local extensions. Original acquired source, acquisition receipt, historical reports/results and identities remain unchanged.
- Remaining gates: Hub revision-to-loader/scorer mapping, grouping/denominator comparability, actual scorer/harness hashes and all runtime/diagnostic admission requirements; source hashes alone do not establish full evaluator equivalence
- Validation: three focused offline synthetic suites — **38 passed**, no failures/skips; original full evaluator/CLI, source/license/linkage, normalization edges, alias-201 matches and shared-verifier identity on hit/miss; `git diff --check` passed. Exact command and before/after failures in the unique review.
- Commit: accompanying `fix: preserve TriviaQA aliases and record corrected scorer identity` commit; exact hash delivered with review

## TriviaQA — Hub conversion metadata review — Codex 225 — 2026-10-14

- Scope: isolated `/tmp/hg-codex-225`, base `61e7f82245c76e7c833740216940d1fcaf3b76be`; public historical code, license, manifest and Git/API metadata only. No dataset/task/heldout rows, parquet or archive access; no loader/scorer/model/H0/endpoint execution or main-branch mutation.
- Finding: exact Hub revision linkage remains unverified. Four retained exact-revision Hub requests failed with network unreachable. GitHub history supplied historical loader `413205c1a7247a2ff81cf709117ce93624fa6fd3`, preserved with Apache-2.0 license, original file hashes and reconstructed commit/tree/blob linkage. The loader trims normalized aliases but omits HumanAnswers and domain/verified flags; `rc.nocontext` combines sources and removes document lists. Its association with the requested Hub export is not established.
- Evidence: [unique review](../reports/triviaqa-hub-linkage-codex225-report.md), [code/metadata fixture and exact request](../tests/fixtures/triviaqa_hub_codex225/README.md), `tests/fixtures/triviaqa_hub_codex225/acquisition.json`, `tools/check_triviaqa_hub_provenance_codex225.py`, `reports/triviaqa-hub-linkage-codex225-validation.txt`.
- Platform change: refine the existing external `hub-export-scorer-linkage` request to require immutable export-to-loader association, human-answer preservation/absence/redundancy and source/selection/key/denominator mapping. Production code, metric identity, shared blockers and historical receipts remain unchanged.
- Validation: offline historical source integrity and changed/missing-source controls pass; original-scorer byte integrity passes; registry checker passes (28 datasets, eight shared gates, 11 historical records, no authorization); existing focused registry tests **52 passed**, no skips. Exact output is retained in the unique validation artifact. These are metadata/integrity checks, not benchmark measurements or production authorization.
- Commit: accompanying task-225 source/metadata review commit; exact hash delivered with handoff.

## TriviaQA — current scorer identity and registry review — Codex 215 — 2026-10-14

- Status: `preflight`; original evaluator source gate reviewed, no further adapter EM mismatch reproduced
- Scope: isolated `/tmp/hg-codex-215`, base `82459cf`; reviewed `fcbed17`/`4fa8481`, code-only fixture, registry and journal; fabricated inputs only, no dataset payload/heldout, network, model, H0 or GPU execution
- Finding: source/license/Git linkage and existing source/differential tests pass. The remaining repository-solvable mismatch was the active registry's obsolete upstream-acquisition blocker and pending-identity evidence anchor, despite the acquired source and already merged v2 identity.
- Evidence: [unique review](../reports/triviaqa-review-codex215-report.md), `tests/quality/test_triviaqa_identity_codex215.py`, [focused results](../reports/triviaqa-review-codex215-test-result.txt)
- Platform change: retire `upstream-evaluator-acquisition` from the active TriviaQA blocker list and name the actual external gate `hub-export-scorer-linkage`; retain all shared gates. Added fresh-interpreter checks of the actual materialized scorer/check inputs for text/structured hit and miss, empty and absent answers. Production scorer/check code, v2 identity, upstream bytes, acquisition receipt and historical records are unchanged.
- Remaining gates: independently pinned Hub export-to-loader/scorer mapping, grouping/denominator comparability, actual scorer/harness hashes and all runtime/diagnostic admission requirements; no production readiness or diagnostic authorization follows
- Validation: baseline source/differential suites **38 passed**; six materialized-verifier cases **6 passed**; final combined source/identity/registry suite **93 passed**, no failures/skips. Exact commands are recorded in the unique review; fixture integrity tool and registry checker exit 0, registry retains `production_authorized=false`, and `git diff --check` passes.
- Commit: accompanying `docs: align TriviaQA blocker with reviewed scorer identity` commit; exact hash delivered with review

## GSM8K — scorer contract

- Status: `complete` history; scorer correction pending new-run validation
- Scope: published `train`/`test` split; old H0 records use the scorer identity recorded at their run time
- Finding: the inherited integer-only flexible extractor turns `3.5` into `5` and `18.0` into `0`, while the task contract accepts decimal forms
- Evidence: `data/gsm8k.py`; `tests/quality/test_gsm8k_official_scorer.py`; 18 focused tests passed after the decimal-aware change
- Platform change: scorer identity must be explicit in evidence; decimal-aware extraction is now the current adapter contract and is not silently substituted into old archive records
- Remaining gates: rerun any GSM8K comparison under the new scorer identity before comparing it with old curves
- Commit: `d10b387 platform: cap early pilots and parse GSM8K decimals`

## GSM8K — scorer provenance repair — 2026-10-14

- Status: `preflight`; source/test provenance repaired, production validation remains pending
- Scope: source, synthetic scorer/verifier tests and documentation only; no model, H0, released-split reads or archive changes
- Finding: the decimal correction changed both the adapter and the purported original reference. Historical upstream attribution lacked a revision; stale docstrings also claimed upstream float equality, while the adapter uses an exclusive `1e-6` tolerance.
- Evidence: immutable `tests/fixtures/gsm8k_original/integer_extractor.json`, pinned to repository commit `f7ab62143108e120914b5ead34ed339d0c785ee9` with fixture SHA-256 `45c73aeb817878b5ba65709f45766f21eb7899182df4eba9a8101e9169d8276b`; `tests/quality/test_gsm8k_official_scorer.py`; `tests/quality/test_gsm8k_dataset.py`
- Platform change: preserved `decimal-aware-extract` behavior and compatibility fields; restored an independent integer-only reference with honest provenance, corrected scorer labels/docstrings and stale evidence assertion, and made focused checks independent of provisioned benchmark data
- Metric protocol: [provenance documentation](gsm8k-scorer-provenance.md) distinguishes the implemented trial-mean from verifier-selected test@N. test@N remains unimplemented; old receipts retain their recorded identities.
- Remaining gates: any production comparison still requires a separate approved diagnostic and matching scorer/protocol provenance. Synthetic test success does not authorize H0.
- Validation: `python -m pytest -q tests/quality/test_gsm8k_official_scorer.py tests/quality/test_gsm8k_dataset.py --basetemp=/tmp/harnessgrad-pytest-codex156-gsm8k-tmp` — 58 passed; fixtures and subprocess table-reader stubs prevent released-split reads
- Commit: this commit, `fix: repair GSM8K scorer provenance`

## ALFWorld — embodied runtime

- Status: `complete` H0 archive
- Scope: 9 train-side pilot tasks, 3 trials, `jobs=1`
- Finding: task-level action limits, TextWorld assets and verifier state must be checked before measuring a curve
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/alfworld-oracle-control.log`; `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/alfworld-noop-control.log`; run `alfworld-h0-10pct-v4`
- Platform change: files sandbox, explicit action budget, structured task events and immutable artifact hashing became required evidence
- Remaining gates: do not rerun the completed generation without a new protocol
- Commit: archive record in `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/qa-h0-archive-v4/index.json`

## Bird MiniDev — SQL measurement

- Status: `complete` H0 archive for v5; v4 is `incomplete`
- Scope: v5 planned 34 train-side tasks × 3 trials, `jobs=1`; only 28/34 tasks were measured (90 verify phases). The historical archive label `complete` does not certify full measurement coverage.
- Finding: a SQL verifier can distinguish a wrong query from an environment that cannot open `database.sqlite`; measured-zero and unmeasured must remain separate
- Evidence: `bird-minidev-h0-10pct-v5`; v5 score `0.3214285714`; v4 stalled and remains incomplete
- Platform change: structured verifier evidence and `effect=null` incomplete records are mandatory
- Remaining gates: preserve SQL engine errors and schema errors in per-task evidence
- Commit: archive record in `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/qa-h0-archive-v4/index.json`

## DS1000 — host slice and timeout evidence

- Status: final curve pending archive review
- Scope: 61-task train-side pilot from the adapter's 926/1000 host slice, 3 trials
- Finding: host availability is not full benchmark coverage; one task timeout cannot be relabeled as an ordinary wrong answer
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/61/report.md`; run `ds1000-h0-10pct-v4`; score `0.2076502732`
- Platform change: archive records carry source-pool coverage and task-level timeout evidence
- Remaining gates: append only after verifying all sample IDs, trial coverage and timeout classification
- Commit: archive not yet appended

## ScienceWorld — platform integrity

- Status: `incomplete` despite 354/354 task-trials completing
- Scope: 118 train-side tasks, 3 trials
- Finding: a platform content mismatch invalidates the run-level integrity claim even when every task has a verifier score. The error message `harness modified the platform` does not establish who wrote the changed files; concurrent developer changes are an alternative cause.
- Evidence: final event note in `scienceworld-h0-10pct-v4/events.jsonl`; diagnostic mean `0.1380508475` is for human inspection only
- Platform change: sandbox/mount integrity must prevent writes before execution; end-of-run hashing alone is too late
- Remaining gates: apply and review the isolated integrity patch, then rerun a capped pilot before any full sample
- Commit: patch candidate in `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/81/patch.diff`; not merged

## ScienceWorld — prevention source review — 2026-10-14 — Codex 186

- Status: `preflight`; code-solvable `prevent-platform-writes` review closed, current registry status `runtime`
- Scope: isolated `/tmp/hg-codex-186`, base `d21d79d` after `34a472a`; source review, inert synthetic fixtures and registry/journal updates only
- Finding: prevention already exists in `eval/sandbox.py`, the default native `eval/runner.py` launch and `harnessgrad/methods.py` call path. Protected platform paths are hidden before execution; required candidate/method inputs are restored read-only; an unavailable sandbox refuses the call. Explicit unsandboxed execution provides detection only. `34a472a` corrects writer attribution without weakening fatal mismatch detection; it adds no prevention implementation.
- Evidence: [unique review](../reports/scienceworld-platform-writes-codex186-report.md), `tests/quality/test_scienceworld_platform_writes_codex186.py`, `tests/quality/test_scienceworld_integrity_codex181.py`, `tests/quality/test_dataset_blockers.py`
- Platform change: current machine-registry work status changes from `code-solvable` to `runtime`; no production source change. The external Codex 81 candidate remains an unverified historical citation and was not opened or applied.
- Remaining gates: trusted live enforcement, immutable platform provenance and every shared registry gate remain unresolved. Synthetic command construction cannot attest effective mounts or runtime lifecycle, and authorizes no model/H0 execution. Any future authorized run follows the staged AGENTS.md policy with a fresh ID.
- History: the V4 entry above, run `scienceworld-h0-10pct-v4`, 354/354 reported task-trials, diagnostic-only mean and pinned historical registry record remain unchanged; status `incomplete`, `effect=null`, writer unknown.
- Validation: **64 passed**, no failures/skips; registry valid (28 datasets, 8 shared blockers, 11 historical records, production unauthorized); exact offline command in the unique review. No real dataset/JVM/backend/model/H0/GPU execution or production source edits.
- Commit: accompanying `docs: close ScienceWorld prevention code review, retain runtime gate` commit; exact hash reported on delivery

## HotpotQA — structured evidence and time budget

- Status: `incomplete`, user-stopped
- Scope: 492 train-side tasks were mistakenly too large for the time budget; 94/1476 task-trials completed
- Finding: complex evidence tasks can spend 60 minutes on one task; malformed `predicted_evidence` is a schema failure, not a normal wrong answer
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/qa-h0-incomplete-index.json`; console timeout and schema-error lines
- Platform change: early capped pilots; separate timeout, invalid and measured-zero states; evidence schema validation
- Remaining gates: do not rerun the old full-size protocol; use the capped pilot default and a repaired scorer boundary
- Commit: incomplete record only

## MuSiQue — answer/support evaluation fidelity — 2026-10-13

- Status: `scorer_repaired`, synthetic validation complete; no model/H0
- Scope: MuSiQue-Ans dev adapter; structured answer plus public support citations; explicit legacy answer-only mode retained
- Finding: prior reward measured Answer F1 only. Default structured scoring now reports Answer F1, Answer EM, Support F1/EM and a labeled platform joint policy; missing support yields zero support, and trusted evidence is verifier-only
- Evidence: `data/musique.py`; `docs/musique-output-contract.md`; public pinned evaluator fixtures; combined scorer validation
- Platform change: structured QA evidence transport and redacted verifier gold support
- Validation: combined MuSiQue/2Wiki/Chess suites passed `209 tests`; platform train-side controls: MuSiQue `musique/dev/0` oracle=1.0/noop=0.0; 2Wiki `twowikimultihopqa/dev/3` oracle=1.0/noop=0.0
- Control sweep: Codex 113 measured 18/18 selected controls across the frozen 50-ID manifests: 3 oracle=1.0 and 3 noop=0.0 for each adapter, jobs=1, no model/H0, cleanup complete. Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/113/worktree/runs/no-model-controls-20261013/report.md`
- Pilot result: run `musique-pilot-h0-20261013` completed 50 selected train tasks × 3 trials, jobs=1, 150/150 measured trials, 0 invalid, score `0.12751114`, one task passed, wall-clock `1884.4s`; receipt `/mnt/20t/xubuqiang/Study/musique-pilot-20261013/runs/musique-pilot-h0-20261013/curve.jsonl`
- Remaining gates: released-data controls and model/H0 validation remain separate; platform joint reward is not an official single leaderboard column
- Commit: `4d41a4c fix: restore MuSiQue and 2Wiki evaluation fidelity`
## 2WikiMultihopQA — 2026-10-13 evaluation fidelity

- Status: `scorer_repaired`, synthetic validation complete; no model/H0
- Scope: this adapter's public output contract, trusted gold transport and official v1.1 scoring; fabricated fixtures only, no released dev/train/test, heldout payload, alias-table or mirror reads
- Pilot recovery: the original 50-task pilot had two malformed structured-output invalids. Generic transport repair commit `1f41891` passed 129 focused tests; rerunning `twowikimultihopqa/dev/1589` and `/2501` ×3 produced `invalid=0`, task scores `0.8` and `0.0`. Combined full 50-task score is `0.50383334`; receipt `/mnt/20t/xubuqiang/Study/twowiki-invalid-recovery-20261013/runs/twowiki-invalid-recovery-h0-20261013/curve.jsonl`
- Public contract: JSON in `answer.txt`, submitted directly or with `python3 qa/bin/qa submit @submission.json`: `{"schema_version":1,"answer":"...","supporting_facts":[["Title",0]],"evidence":[["subject","relation","object"]]}`. Context sentences display zero-based indices. Each channel can be omitted; omitted metrics and Joint are zero. Explicit empty sets retain upstream semantics. Plain text and `score_answer_only` remain explicitly labeled `legacy_answer_only`, with Ans F1 reward and no Sup/Evi/Joint claim. This adapter uses the existing text-file transport; shared `submit-json` remains the pair-only schema.
- Evidence: `data/twowikimultihopqa.py`; `tests/quality/test_twowikimultihopqa_structured.py`; updated legacy assertion in `tests/quality/test_twowikimultihopqa_official_scorer.py`
- Platform change: adapter-scoped `score_prediction`, validation and `evaluate_predictions`; trusted inline support/triples plus relevant subject/object aliases, with alias products expanded per scored row. Inputs remain immutable. Aggregate percentages sum in gold order, divide by the entire gold pool including missing predictions, then round once to two decimals. No shared scaffold or other adapter changed.
- Differential coverage: Counter-based duplicate answer tokens; support deduplication/title casing and sentence indices; triple order, punctuation/whitespace normalization, aliases/demonyms and duplicate triples; independently maximized answer precision/recall; multiplicative Joint precision/recall; each missing channel, absent prediction rows and ignored extra ids; explicit empty sets; malformed contracts; trusted-gold privacy; CLI-to-materialized-verifier full/partial/legacy/noop/error controls. Preserve upstream's pre-normalization support deduplication and evidence-alias recall-above-100% quirks without clipping.
- Validation: `python3 -m pytest -q tests/quality/test_twowikimultihopqa_structured.py tests/quality/test_twowikimultihopqa_official_scorer.py::test_legacy_answer_only_is_labeled_and_does_not_claim_joint --basetemp=/tmp/harnessgrad-pytest-twowiki-pytest` — 40 passed. Synthetic tests suppress shared QASpec pool construction before both parent and verifier-child imports, so no provisioned payload is accessed. `git diff --check` passed.
- Remaining gates/blockers: no implementation blocker. Fetching the pinned upstream source from GitHub failed with curl exit 35 (connection reset); differential tests therefore execute the existing verbatim file evaluator, whose unchanged region is pinned to pre-patch SHA-256 `e18ccdf4b87d16c30e03a62b1dc9d0906c0b0130ae5eace17885d2a9ea1b13c9`. A fresh independent source-file comparison and released-data controls were not performed; real-data/model/H0 validation is outside this task.
- Commit: this entry is carried by `fix: restore 2WikiMultihopQA structured evaluation fidelity`; exact hash reported with the delivery

## Public Qwen3.5-9B baseline comparison — 2026-10-13

- Status: `comparison_archived`, no new benchmark run
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/qwen-baseline/report.md`; sources and local receipt summary beside it
- Public result recovered: Qwen's reviewed Qwen3.5-9B card reports LiveCodeBench v6 `65.6`; the reviewed card has no MuSiQue, 2WikiMultihopQA, GAIA or AppWorld row
- Local results: MuSiQue capped train pilot `0.12751114` over 50 tasks ×3 measured trials; 2Wiki original curve `0.5081597292` has 48 scored tasks and mixed legacy Answer F1/structured Joint F1; GAIA has no aggregate curve; AppWorld has repeated single-task measured zeros; LCB is smoke-only and row/scorer incomparable
- Interpretation: no direct public-versus-local ranking is valid. Local QA/AppWorld caps, prompts, splits and scorer policies differ from public benchmark recipes; Qwen card values are publisher-reported and not independent reproductions
- Commit: evidence archive only


- Status: preflight-required, no H0
- Scope: 1055 pool tasks; 3 train-side authored references and 4 eval-side references
- Finding: an authored reference proves scorer reachability for one task, not full benchmark coverage
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/79/report.md`; inert manifest selects `livecodebench/740`
- Platform change: reference coverage, public-only authoring and covered-subset manifests are separate from official benchmark claims
- Remaining gates: train metadata attestation, public-only export, independent review and official test verification
- Commit: inert artifacts only

### LiveCodeBench `/740` executable smoke

- Status: `smoke_passed`, H0 not authorized
- Scope: public `abc360_a` statement, one local-model smoke, external-process scorer variant
- Finding: 7/7 synthetic relay/privacy gates passed; local model smoke measured reward 1.0 with 6/6 tests and one request. The candidate agent stayed network-none and verifier stayed network-none.
- Evidence: `/mnt/20t/xubuqiang/Study/lcb_candidate_evidence/launch.json`; candidate path isolated checkout; production endpoint calls during synthetic validation were zero
- Platform change: agent-only Unix relay with max 4 calls and max 512 requested tokens; candidate/scorer/verdict separation
- Remaining gates: mixed-pool row/index binding remains unverified; scorer path differs from official wrapped-function execution; no H0
- Commit: `e2f9613 fix: harden LCB740 identity and relay admission`
- Verification: 79 focused tests passed; production endpoint/model requests=0; synthetic approved-row fixtures never became real evidence

### LiveCodeBench `/740` trusted metadata validation — 2026-10-14

- Status: `validator_hardened`, external row attestation still blocked; no H0
- Evidence: `reports/LCB_GATE.md`; existing public statement and preserved prior inert selection/launch metadata
- Platform change: bounded UTF-8 metadata-only record, canonical independently supplied approval digest, strict JSON constants and custodian validation; pinned row/pool/split checks retained
- Verification: 80 focused identity tests passed; `git diff --check` passed; no network, mixed-pool/heldout payload reads, model calls or H0
- Remaining blocker: no externally custodied, independently approved record binding pinned pool row 740 to `abc360_a`; self-hashes and synthetic fixtures do not establish custody

### BFCL selected-only/privacy patch

- Status: `patch_integrated`, real controls blocked by unprovisioned release
- Scope: selected `simple/<index>` and `irrelevance/<index>` category loaders; no import-time mixed-pool read
- Finding: selected loader removes import-time mixed-pool reads; irrelevance empty/NONE semantics remain reward=1; trusted expected functions are redacted; generic noop expectation is category-aware
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/98/bfcl-selected-only-receipt.md`; isolated 2 synthetic tests passed/11 release-dependent skipped; main compatibility run `147 passed, 23 skipped`
- Platform change: `load_selected`, `setup_for`, `verify_for`, category-aware controls and BFCL-specific evidence redaction
- Remaining gates: local BFCL v1.3 release is unprovisioned, so selected reference identity and real oracle/noop controls remain unproven; no H0
- Commit: `c08c8a1 fix: make BFCL controls selected-only and redact gold`

### BFCL selected-index and failure-path privacy follow-up

- Status: source/privacy regression closure; production release gate remains unverified.
- Scope: `data/bfcl_v3.py`, shared QA controller/verifier, and `tests/quality/test_bfcl_selected.py`; fabricated JSONL/index fixtures and synthetic read guards only.
- Finding: category filtering still read every question and answer row; empty selection fell back to all categories; controls reloaded selected records and the platform path could load the full pool; scorer explanations and pre-import/unmeasured diagnostics could expose trusted gold.
- Change: canonical nonempty selection validation precedes metadata/payload access; a `selected-index.v1.json` declares tag/tarball identity, question identity and exact question/answer byte spans with SHA-256. This index is **not authenticated or independently custodied**; its hashes are corruption checks, not provenance/trust. Selected loading uses bounded unbuffered seeks/reads, preflights all selected spans, reuses file descriptors and detects ordinary changes during load; it has no scan/index-build/full-pool fallback. Controls reuse one selected record; verifier evidence redacts gold on measured and failure paths.
- Validation: focused selected/privacy/read-boundary suite **73 passed** after Codex 171 bounds review; earlier main suite 55 passed. All fixtures are synthetic; no release or external dataset path was read.
- Remaining gates: independent custodian approval of exact metadata-only index bytes and row/split binding; authenticated immutable release storage; pinned official AST/full-call evaluator source and complete argument/reference data. Current scorer remains function-name multiset diagnostic, not official BFCL Simple. No model/H0 or production controls authorized.

## AppWorld / GAIA / tau-bench — local state boundaries

- Status: preflight-required, no H0
- Scope: AppWorld reference-covered train subset; GAIA validation-only pool; tau-bench returned local pool
- Finding: service reset, database state, attachments, web access and evaluator secrecy cannot be inferred from adapter loadability
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/86/report.md`; `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/87/report.md`; inert manifests
- Platform change: one shared lifecycle for scope, admission, restore, readiness, execution, quiescence, scoring, sealing and cleanup
- Remaining gates: real local controls after shared runtime repair; no fallback simulator or hidden web access
- Commit: inert artifacts only

### GAIA V2 real-model pilot attempt

- Status: `incomplete`, infrastructure-stopped
- Scope: 17-task validation-only pilot, 3 trials, `jobs=1`, GPU1/8002, frozen source `92f6b10`
- Finding: the first smoke exposed UTF-8 subprocess decoding; after the isolated fix, smoke reached the model and verifier normally. The pilot then stopped on `gaia/49` after an API timeout; partial trials are evidence of a stopped run, not a complete curve.
- Evidence: `/mnt/20t/xubuqiang/Study/gaia-h0-launch-v2/runs/gaia-validation-pilot-h0-20261117-v2`; sealed receipt `/mnt/20t/xubuqiang/Study/gaia-h0-launch-v2-evidence/GAIA_H0_V2_RECEIPT.json` reports 9 completed trial traces, 45 calls, 47,511 input and 3,219 output tokens. Event envelopes contain 10 done events, including `gaia/53`; this count differs from the persisted trace/usage receipt and must not be silently reconciled as full coverage. Timed-out request usage is unknown.
- Platform change: subprocess output decoding must tolerate arbitrary bytes; a per-request output cap is needed because steps/context limits do not bound one generation. Preserve measured scorer zero separately from actor failure.
- Remaining gates: enforce a bounded model output/token policy before another GAIA pilot; reconcile event versus persisted trial coverage; do not resume this run ID
- Commit: isolated harness fix `92f6b10`; pilot is incomplete and sealed

### GAIA V3 real-model pilot attempt

- Status: `incomplete`, infrastructure-stopped
- Scope: same 17-task validation-only pilot, 3 trials, `jobs=1`, GPU1/8002, source `cde983ff` with output cap `2048`
- Finding: 11 trials completed normally; `gaia/49` third trial reached agent completion at 228.6s, then its snapshot container exited 137 before verification. No aggregate score is valid.
- Evidence: `/mnt/20t/xubuqiang/Study/gaia-h0-launch-v3/runs/gaia-validation-pilot-h0-20261117-v3/events.jsonl`; `gaia/16`, `gaia/32`, `gaia/45` completed 3/3; `gaia/49` completed 2/3; owned interrupted resource was removed
- Platform change: snapshot/container exit codes must become explicit infrastructure outcomes; a task reaching agent completion does not imply a scorable attempt
- Remaining gates: determine why snapshot exits 137 and add resource/snapshot admission before any retry; never resume this run ID
- Commit: source `cde983ff`; pilot incomplete

## AppWorld — scoped train controls

- Status: `controls_passed`, H0 not launched
- Scope: 90 declared train/reference-covered tasks; deterministic pilot selects 9; 18 no-model controls cover 9 oracle and 9 noop arms
- Finding: full-pool import was unsafe for selected-only execution; a pinned train manifest and single-task sanitized controller fixed the boundary. Actor sees no ground truth, services use network none, images are pinned and pull=never.
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-appworld-controls-20261117/deliverables/appworld-offline-v2-report.md`; receipt SHA-256 `f62b8a830c31a889bfe44346c4084055f867b292ce49fb775b7beed19d0900fb`; frozen commit `d600378`
- Platform change: selected-only manifest custody, fresh actor/verifier state, owned labels, and cleanup receipts are reusable adapter controls
- Remaining gates: real-model smoke and production launch record on a frozen checkout before 9x3 H0
- Commit: `d600378 adapter: scope AppWorld to pinned train manifest`

### AppWorld real-model smoke blocker

- Status: `incomplete`, infrastructure repaired; actor protocol still blocked
- Scope: fresh one-task smoke on `07b42fd_1`, one trial, jobs=1, GPU1/8002, bounded generation 2048
- Finding: the original actor never started because the runner mounted the dependency overlay twice and Docker rejected the launch with exit 125. A second client bug passed unsupported argparse `choices`; the service image also now has an explicit `/usr/local/bin/appworld-server` command. After repair, the actor ran 8 model calls, service initialize returned 200, three execute requests returned 200, and the API-call log existed. The model still made zero AppWorld API calls, so the measured smoke score was 0.0 across 5 checks; this is actor/task protocol behavior, not a missing-log infrastructure failure.
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/101/deliverables/receipt.md`; `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/101/evidence/real-smoke/result.json`; `/mnt/20t/xubuqiang/Study/appworld-smoke-final-v4/runs/appworld-smoke-final-20261117-v4/events.jsonl`; fixed patch commit `a9e78d8`
- Platform change: explicit service command/entrypoint contract, duplicate overlay prevention, AppWorld CLI dispatch fix, service log preservation and invalid diagnostic trace retention
- Verification: 107 focused tests passed; a broader registry/scorer command exceeded the 120s command cap and was terminated, so it is not counted as passed
- Remaining gates: make the task-facing harness reliably issue an AppWorld API action without method-specific tuning, rerun one measured smoke with a nonempty API log, then launch 9x3 only after review
- Commit: `a9e78d8 fix: make AppWorld service and runner diagnostics explicit`

### AppWorld runtime tool protocol repair

- Status: `protocol_repaired`, H0 not launched
- Scope: public `SETUP.runtime_prompt` on train task `07b42fd_1`; unchanged generic `base_harness/loop`; one live smoke on GPU1/8002
- Finding: the prompt now teaches the adapter-declared `./aw init/action` contract, persistent `apis` namespace, documentation discovery, and action persistence without embedding a task answer or verifier data. The model made 4 authoritative calls: 3 documentation reads and `GET /spotify/artists`.
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/104/receipt/appworld-actor-protocol/receipt.json`; bundle SHA-256 `2ca5b8d1bf4508a93934c5b4005b509d35f49d3cbe73dfcc7ffe35978a8b1100`; patch SHA-256 `955d892d023062f46a3b8535e5b808d2ae4a2b46a3e1f773b2daeb8c81b18803`
- Verification: 63 focused tests passed; service initialized and returned 200 for all four execute requests; actor had no recording mount; cleanup had no owned containers/networks; measured verifier score remained 0.0 because the model did not submit a completed answer and later produced parse failures
- Platform change: adapter-scoped public runtime prompt contract, validated and delivered through files, exec mount, and container-state paths; no base harness branch or task-specific answer logic
- Remaining gates: improve generic action-loop robustness for long API results and shell quoting, then rerun one task to a completed measured answer; do not launch 9x3 from this unsolved smoke
- Commit: `87c6fc9 fix: provide adapter runtime tool instructions`

### AppWorld generic loop robustness repair

- Status: `protocol_partially_verified`, H0 not launched
- Scope: unchanged generic loop actor, one train task `07b42fd_1`, GPU1/8002, 8 steps, 2048 output tokens, jobs=1
- Finding: the actor now selects an explicit shell and tells the model whether Bash or POSIX syntax is available; structured JSON/list output is compacted with complete-record previews and exact full output saved separately; parser retries discard failed long replies from active context and request short actions. The smoke completed all 8 commands with no shell or parse error and recorded 7 API calls, but remained in API documentation discovery and made no state-changing call or final submission.
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/105/receipt/loop-robustness/smoke-receipt.json`; tests `20 new robustness + 62 existing focused = 82 passed`; patch isolated commit `77c573fa91f57ee6f1fe54c2497436baecddff99`
- Platform change: generic shell dialect identity, lossless structured-output preview, persisted exact output, robust block parser and bounded parse-retry context
- Remaining gates: get one generic loop smoke to complete a real task-facing state change and measured answer; no method/task-specific hardcoding; no 9x3 yet
- Commit: `df8beec fix: harden generic loop shell output and parse recovery`

### AppWorld sixteen-step smoke

- Status: `measured_smoke`, H0 not launched
- Scope: declared AppWorld split `147 train / 585 eval`, selected train task `07b42fd_1`, one trial, jobs=1, GPU1/8002, `max_steps=16`, `max_output_tokens=2048`
- Finding: actor completed normally in 41s and produced 15 authoritative API calls; verifier returned `measured=true`, score `0.0`. The earlier smoke split file covered only a partial manifest and was rejected before execution; this smoke used the complete declared split.
- Evidence: `/mnt/20t/xubuqiang/Study/appworld-smoke-final-v6/runs/appworld-smoke-final-v6-20261117/events.jsonl`; progress record reports `complete=true`, `n_trials=1`, `trial_scores=[0.0]`; API log is 1507 bytes with 15 calls
- Platform change: complete split admission is now verified separately from selected task execution; no payload or heldout task content was needed to build the split metadata
- Remaining gates: a successful measured actor task remains required before 9x3; do not convert this measured zero into a full pilot
- Commit: runtime evidence only

### AppWorld thirty-two-step smoke

- Status: `measured_smoke`, H0 not launched
- Scope: declared split `147 train / 585 eval`, selected train task `07b42fd_1`, one trial, jobs=1, GPU1/8002, `max_steps=32`, `max_output_tokens=2048`
- Finding: actor completed normally in 57s and produced 26 authoritative API calls; verifier returned measured score `0.0`. The runtime remained healthy with no infrastructure invalidation, but the model still did not complete the task. Increasing the step ceiling did not close the task gate.
- Evidence: `/mnt/20t/xubuqiang/Study/appworld-smoke-final-v7/runs/appworld-smoke-final-v7-20261117/events.jsonl`; progress record reports `complete=true`, `n_trials=1`, `trial_scores=[0.0]`; API log is 2638 bytes with 26 calls
- Decision: do not keep increasing the budget or tune the method to this task. AppWorld has stable platform/scorer protocol but no successful measured task smoke, so 9x3 remains unauthorized
- Commit: runtime evidence only

## Jericho — runtime boundary repair

- Status: `controls_passed`, model H0 still blocked
- Scope: two selected train study games (`905`, `acorncourt`), local/platform oracle/noop controls remain 16/16; no heldout or model execution
- Finding: the prior runtime exposed reference-bearing `game_info.py` walkthroughs, ignored declared timeout limits, reused action logs, and did not enforce native network isolation. The repaired path projects only public Jericho code/native library, strips reference bindings/walkthroughs/docs/bytecode, uses explicit 300s agent/verifier bounds, fresh logs, and refuses live agents under `network=none` before staging
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/109/worktree/report.md`; merged commit `28eebef`; 59 focused boundary/admission tests passed, 7 unrelated production/data cases deselected
- Platform change: allowlisted agent runtime projection, runtime policy admission, explicit phase timeout minimum, no-egress sandbox and fresh log reset
- Remaining gates: production ROM controls must run from a work root outside the platform checkout; interactive model H0 remains blocked until that path is independently exercised
- Commit: `28eebef Repair Jericho agent runtime isolation and phase boundaries`

## BFCL v3 — scorer/privacy controls

- Status: `blocked`, no real controls
- Scope: 2 inert reference anchors (`simple/29`, `irrelevance/236`), 8 planned control arms
- Finding: importing the adapter reads mixed train/eval files; irrelevance correctly treats empty output as success, so generic noop=0 is invalid
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/89/manifest.inert.json`; 32 synthetic/privacy tests; scoped lazy-import patch hash `ed45acc026a036be46b2ab48d7dbe79504f68b2d7c135e942dde71b109e9bc56`
- Remaining gates: train-only source binding, category-aware controls, raw evidence redaction, finite reward/unmeasured classifier
- Commit: inert patch only

## Shared runner refusal gate — Codex 163

- Status: `fail_closed_refusal_added`; backend enforcement remains blocked.
- Scope: runner-mediated tasks declaring exec/container, network, CPU/memory/deadline, resource/filesystem, or artifact policies; unknown backend observations refuse before dispatch/cache reuse.
- Change: `eval.runner._refuse_unobserved_policies` returns invalid/unmeasured admission receipts with no score and prevents these declared-policy tasks from reaching a passing verdict without a trusted backend observer. No adapter/caller-provided observation can override the refusal.
- Validation: synthetic early-refusal, cache-preservation and undeclared legacy-files compatibility tests; combined parent suite **263 passed** across runner admission, error paths and trials/unmeasured behavior.
- Limits: undeclared legacy tasks and direct backend/verifier entrypoints remain outside the hook; driver image preflight can occur earlier; no resource/network/quota/cleanup observer is wired, so declared-policy exec/container tasks intentionally remain blocked. This is a refusal boundary, not production admission or a pilot authorization.
- Evidence: `reports/SHARED_ADMISSION_WIRING.md`, `tests/quality/test_shared_admission_wiring_codex163.py`
- Commit: `39883d8 refuse tasks without enforced runtime observations`



- Status: `admission_hardened`, benchmark execution blocked
- Scope: inherited six cached train images, jobs=1; synthetic local runtime controls only
- Finding: admission now rejects empty device observations, negative reservations, unsafe mount flags, runtime-envelope mismatches before start, image-ID mismatches, and ambiguous cleanup absence; leases quarantine on uncertainty and retain capacity
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/112/report.md`; final offline review tests `199 passed`, no real Docker/model/H0/heldout access; merged implementation commit `b3e5409`
- Platform change: manifest-bound resource ledger, exact image pin checks, fixed no-network/no-pull runtime, fail-closed cleanup and trusted artifact mount
- Remaining gates: each scorer still lacks verified offline dependency closure/trusted runtime/state export; benchmark disk/inode quotas are not enforced; no official benchmark execution
- Commit: `b3e5409 fix: harden cached pilot admission boundaries`

### Shared runner admission follow-up — Codex 158

- Status: `isolated_contract`, filesystem enforcement remains a runtime blocker.
- Finding: reservations and snapshot free-space preflight cannot prove byte/inode quota enforcement. Unbounded or incomplete snapshot/resource/cleanup facts must stay unmeasured.
- Platform change: reusable `eval.runner_admission` runtime/network/filesystem/snapshot/cleanup contracts with fresh binding checks, bounded receipts and fail-closed cleanup release; byte-only legacy snapshot admission explicitly reports that no quota is enforced.
- Evidence: `reports/runner-admission-codex-158-report.md`; synthetic observations only, subprocess/socket execution denied in new tests, existing persistent lease regressions retained.
- Remaining gates: real byte/inode enforcement and trusted complete observers, bounded snapshot worker/daemon resources and growth, atomic receipt-to-lease integration, official scorer/offline closure and artifact-only export. The new scorer-bundle validator checks local declared file closure only and is not called by driver/runner/verifier; it does not establish official origin, image ABI, runtime execution or H0 readiness. Passing synthetic receipts authorize no H0.
- Commit: accompanying `platform: add offline runner quota and cleanup admission contracts` commit.

## AgentDojo — selected-only split controls

- Status: `controls_passed`, production H0 not launched
- Scope: pinned runtime registry 949 pairs; 615 train / 334 eval across 97 user groups; selected 4 complete train groups, 35 pairs, 70 oracle/noop arms
- Finding: targeted `control_task(task_id)` now reads only `prepared/<id>/case.json`; `ENV`, `SETUP`, `VERIFY` use fixed metadata maps without importing the mixed prompt catalog. Explicit task IDs are required before any targeted control read. User-group split remains suite/user based with zero cross-side overlap.
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/97/evidence/summary.json`; 70 measured controls, 35 oracle=1, 35 noop=0, attacker_success=0; no mixed catalog/heldout payload opened
- Verification: 20 focused/official/bridge tests passed on main
- Platform change: selected-only adapter control hook and explicit-ID enforcement
- Remaining gates: full mixed-catalog-to-registry alignment is intentionally unattested because `cases.json` remains unopened; no model H0 or platform run_one claim
- Commit: `80bc61f fix: make AgentDojo controls selected-only`

## ChessBench Puzzles — strict replay and public stepwise contract — 2026-10-13

- Status: `complete` synthetic scorer/contract repair; interactive official accuracy remains unmeasured
- Scope: ChessBench Puzzles adapter only, pinned upstream revision `90ae0e6b121673fc3079aaeffa047580bb600c0a`; fabricated boards and reference lines only. No model/H0, release controls, heldout puzzle payload reads, or changes to other adapters.
- Finding: official puzzle accuracy requests one move per observed board, then updates the board with reference opponent responses. The inherited one-shot sequence contract cannot attest those observations. `python-chess` `Board.push()` does not enforce legality: an impossible exact-reference pawn move can receive upstream reward 1.0; strict replay returns 0.0 with `illegal_move` on that synthetic case.
- Evidence: [contract and boundary](chessbench-puzzles-evaluation.md); [strict replay/session tests](../tests/quality/test_chessbench_puzzles_strict_replay.py); [verbatim upstream synthetic differential tests](../tests/quality/test_chessbench_puzzles_official_scorer.py); materialized-verifier diagnostics and shared QA rematerialization checks use synthetic gold exclusively.
- Platform change: default reward is `ChessBench strict legal puzzle replay v1`; preserved upstream unchecked-push reward is diagnostic-only in `official.upstream`, with strict details in `official.strict`. Setup, solver and applied reference opponent moves are legality-checked; malformed/illegal/wrong/missing moves have explicit verdicts; exact and alternate legal early mates terminate immediately. The trusted `StepwisePuzzle` contract exposes only current FEN, solver-turn number, contract, status and verdict, accepts exactly one UCI answer, and applies private opponent updates before the next decision. Adapter import is lazy and verifier evidence redacts gold. The shared QA contract test now honors declared evidence redaction; no shared runner or other adapter implementation changed.
- Remaining gates: no blocker to this patch. A trusted runner transport must deliver successive public observations before actor decisions to claim interactive official puzzle accuracy; the current QA runner remains explicitly offline. Release-pool replay, source-archive drift checks and real controls are intentionally unvalidated under the no-heldout/no-model scope, rather than inferred from synthetic success.
- Validation: `python3 -m pytest -q tests/quality/test_chessbench_puzzles_strict_replay.py tests/quality/test_chessbench_puzzles_official_scorer.py::test_synthetic_upstream_diagnostic_matches_verbatim tests/quality/test_chessbench_puzzles_official_scorer.py::test_alternate_mate_and_nonmate_against_official_function --basetemp=/tmp/harnessgrad-pytest-codex108-chessbench-test-tmp` → **42 passed in 0.49s**. `git diff --cached --check` passed before the implementation commit. Owned temporary test files were removed after validation.
- Commit: `d8d44a6 fix: enforce ChessBench puzzle replay legality and define stepwise contract`
- Validation: platform train-side control `chessbench_puzzles/test/0` oracle=1.0/noop=0.0; strict replay passed 42 focused tests
- Pilot interruption: run `chess-pilot-h0-20261013` is incomplete; 19 task-trials completed, 0 failed envelopes, then events stopped during `chessbench_puzzles/test/1270` trial 2 at agent elapsed 70s. Model services remained healthy and no final task verdict/aggregate curve exists. Preserve this run; do not resume or overwrite its run ID until an independent termination audit identifies the cause
- Recovery result: `chess-pilot-h0-20261013-recovery-01` reached 149/150 task-trials with 0 failed envelopes, then its final `chessbench_puzzles/test/9967` trial remained active past 620s. The parent stopped the driver to protect GPU time; no terminal verdict/curve exists for that last trial. Preserve recovery as incomplete and do not synthesize a 150-trial score or resume the run ID. Future pilots use a smaller diagnostic budget before any 50×3 expansion
- Interruption audit: termination authority is undetermined; receipts show no timeout/failure/cleanup/snapshot closure, and the path was native bwrap/files rather than Docker snapshot. Preserve the original and recovery IDs, receipt hashes and incomplete statuses. Every future attempt must use a genuinely new unique run ID; never resume or overwrite any used run ID, including `chess-pilot-h0-20261013` and `chess-pilot-h0-20261013-recovery-01`. Launch only under a persistent host supervisor after source/H0/split identity checks and the current AGENTS.md gates. Audit: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/chess/interruption-audit.md`, SHA-256 `db357459d4160a5058b022ef5483227f8e01629e24cdf528017db5e7d418de4f`


### AppWorld reporting review — Codex 169

- Scope: isolated `/tmp/hg-codex-169`; code review and fabricated receipt/events only. No real AppWorld task payload/run receipt, smoke/H0, model or runtime execution.
- Finding: saved verdicts preserve scorer evidence for TGC and guarded same-trial SGC; current progress drops it and task events lack explicit trial IDs/evidence. Source Test-N/Test-C labels remain declared manifest facts. This metric report cannot certify diagnostic provenance, endpoint, budgets, cleanup or snapshots.
- Change: report schema 2 separates measured/invalid/present-unmeasured/missing cells, preserves task/per-trial nonmeasurement flags, adds `recorded_unmeasured_task_trials` while retaining aggregate nonmeasurement coverage, and explains input/trial/output limits in CLI help.
- Evidence: `reports/appworld-reporting-codex169-report.md`; unique integration tests use current writers and guarded reporting CLI with fabricated inputs exclusively. Live receipt/event measurement integration remains unsupported; no writer or runner format changed.
- Validation: focused reporting/integration suite **30 passed in 0.96s**; diff whitespace check passed. Owned test scratch was removed after validation.
- Commit: merged follow-up `a80f68f`; parent validation 45 passed

## AppWorld reporting receipt integration audit — Codex 169

- Status: saved-verdict reporting supported; progress/events not sufficient for measured TGC/SGC
- Scope: fabricated Console/Reporter/progress/verdict events and guarded report CLI only; no real AppWorld payload, run receipt, smoke, H0, model or service execution
- Finding: current `verdicts/round-N/<task>.json` retains scorer evidence and can produce measured TGC and same-trial SGC with Test-N/Test-C manifest labels. Progress records keep only generic scores/trial means; events lack scorer evidence and explicit trial IDs. They cannot reconstruct TGC or same-trial SGC.
- Evidence: `reports/appworld-reporting-codex169-report.md`, `tests/quality/test_appworld_receipt_integration_codex169.py`
- Validation: fabricated writer/CLI integration tests passed; parent combined suite 45 passed. No runner writer format was changed.
- Remaining gate: persist minimal trusted scorer evidence plus original trial IDs at the trusted writer; establish manifest/run/model/source/lifecycle identity before diagnostic use. Never infer TestTracker success from generic score or event `passed`.

## AgentDojo selected production route reassessment — Codex 164

- Status: `blocked`; no production diagnostic/H0
- Scope: selected-control metadata interfaces only; mixed catalog, prompts, gold/actions, heldout, runtime and external archive were not opened or executed
- Finding: `control_task` selection still routes through command-control and platform QA verifiers; neither offers a verifier-free, non-scoring selected admission receipt. Existing 70 selected oracle/noop controls are historical claims, not a fresh production `run_one` proof.
- Evidence: `agentdojo-reassessment-codex164-report.md`; metadata privacy regression `tests/quality/test_agentdojo_metadata_privacy.py`
- Validation: 3 metadata privacy tests passed. This proves the tested metadata path avoids guarded reads; it does not prove case materialization, trusted attack verifier, runtime, cleanup or measurement.
- Remaining gate: define and independently review a selected-only, non-scoring production admission interface, or provision a coherent trusted attack-evaluation runtime and run approved oracle/noop controls; then run the staged one-task diagnostic. Do not bypass attack scoring with a synthetic verifier.

## GAIA lifecycle wiring audit — Codex 165

- Status: `blocked`; compatibility library is not a lifecycle receipt or runner authorization
- Scope: source/runtime wiring analysis and synthetic tests only; no Docker, model/H0, heldout, or production lifecycle run
- Finding: `eval.gaia_snapshot_attestation` compares supplied frozen source/runtime identities but does not collect/verify historical receipts or enforce a coherent source lock through runner execution. Fresh cleanup/absence, trusted verifier, dependency closure, artifact export and quota/backend observations remain missing.
- Evidence: `GAIA_LIFECYCLE_WIRING.md`
- Required before diagnostic: metadata-only selected manifest, coherent source lock before adapter import, fresh verifier/dependency/image identity, bounded snapshot and artifact export, observed backend limits/network, and verified owned cleanup, all bound in an immutable lifecycle receipt.

## BFCL v1.3 checker blob retry — 2026-10-14 — Codex 227

- Status: partial official code acquisition; full-call scorer, archive custody and production route remain blocked.
- Scope: fixed v1.3 commit Git-blob API only; code/license/spec metadata. No task, answer, reference, archive, heldout or external dataset-root access; no H0/model.
- Finding: `ast_checker.py`, `type_mappings.py`, LICENSE and `pyproject.toml` were acquired and their Git blob SHA-1/byte counts verified. The checker itself is 24,916 bytes. Static imports still require missing `model_config.py`, Java type converter and JavaScript type converter; their pinned blob SHAs were absent from allowed path metadata, so requests were not guessed.
- Evidence: `reports/bfcl-blob-retry-codex227-report.md`, `tests/fixtures/bfcl_ast_source/retry-codex227/provenance.json`, and exact request/response receipts in that fixture. Candidate remains `status=blocked`, `measured=false`, `custodian_approved=false`, `production_authorized=false`.
- Remaining gate: obtain independently pinned helper path/blob identities and licenses; bind the complete source projection to v1.3/V3 and the declared archive/index through independent approval; then derive/test full-call semantics on fabricated inputs only. Current function-name metric remains diagnostic-only.

## BFCL official call scorer review — Codex 166

- Status: selected-read/privacy hardening complete; official Simple AST metric and index custody blocked
- Finding: current metric compares function-name multisets and drops argument/reference-value alternatives. The selected index and per-row hashes are not externally authenticated; hashes do not establish release identity or confidentiality.
- Evidence: `reports/bfcl-ast-contract-codex166-report.md`; bounded span hardening in `data/bfcl_v3.py`; `tests/quality/test_bfcl_selected.py`
- Validation: 73 selected-span/privacy tests passed. No official release payload, AST scorer, model/H0 or heldout was read/run.
- Remaining gate: obtain pinned code-only official evaluator source and trusted archive/index custodian approval. Then preserve complete selected call/reference info, implement the source-derived AST contract, keep name metric diagnostic-only, and run fresh release-bound controls.

## BFCL Simple AST source acquisition review — Codex 184 — 2026-10-14

- Status: `external`; official full-call AST semantics, independent source acquisition and release/index custody remain blocked. No production H0.
- Scope: local source/registry review and docs/tests only in `/tmp/hg-codex-184`; no external release/archive or heldout reads, download, evaluator execution, model/endpoint calls or production controls.
- Finding: `simple-ast-contract` was classified code-solvable despite its prerequisite of independently acquired official source. The adapter declares gorilla v1.3/archive SHA-256 but provides no locally verified parser/checker/dispatch symbol contract; its function-name multiset diagnostic discards complete reference arguments. Acceptable-value alternatives alone do not make full-call scoring impossible.
- Change: registry status is now `external`, with an exact code-only handoff requirement: independently verified archive/tag/immutable commit/member linkage, original parser/checker/dispatch/helpers/licenses, reviewed closure and a separately approved exact receipt pin. The new test-only gate refuses missing/unpinned/malformed acquisition and checks all declared metadata and inventory before projected source reads; it neither imports nor executes acquired code. Original AST rules and signatures remain unresolved until source review.
- Evidence: [source acquisition contract](../tests/fixtures/bfcl_ast_source/README.md), `tests/quality/test_bfcl_ast_source_contract.py`, `tests/quality/test_bfcl_selected.py`, and the BFCL-specific registry regression in `tests/quality/test_dataset_blockers.py`. No acquired fixture or completed provenance receipt is supplied; simulated approvals and inert bytes occur only in fabricated tests.
- Validation: **164 passed** across those three focused test modules, with plugin autoload/bytecode/cache disabled and scratch files confined to `.scratch/bfcl-codex184`. The initial test invocation failed during temporary-directory setup because its parent was absent; creating that local parent resolved it. The explicit source gate without an approved pin exits **2**, `status=blocked`, `measured=false`, `production_authorized=false`. Registry validation passes with 28 datasets, 8 shared blockers and 11 unchanged historical records.
- Retained boundaries: production adapter/scorer code is unchanged; function-name diagnostic, lazy import, exact selected spans and measured/unmeasured gold redaction regressions pass. Full-call schemas/references and answer syntax still require future source-derived integration. Source integrity cannot establish reviewer authenticity, semantic equivalence, third-party offline closure, index custody or pristine runtime/export/quota/cleanup; all remain independent gates.

## BFCL v1.3/V3 public code provenance — Codex 195 — 2026-10-14

- Status: incomplete code-only candidate acquired; full-call checker/helper/runtime and independent archive/member custody remain `external`. No H0/model run; main worktree and production code are unchanged.
- Evidence: Berkeley's site links to `ShishirPatil/gorilla`; the public lightweight `v1.3` tag points to `ea13468e4423454d0c213704fb87cf7cb3990433`; the official release explicitly labels V3. Seven original source/license/specification files (126,311 bytes) were acquired at that commit with matching Git blob identities and recorded SHA-256/URLs. Apache-2.0 source license is preserved. The declared compressed-archive digest remains unverified; no archive or benchmark task/answer/heldout/external dataset root was accessed.
- Finding: acquired runner uses binary checker validity divided by prediction count, with decoding/format failures in the denominator. Non-live Simple AST aggregates Python, Java and JavaScript category accuracies by arithmetic mean. Complete checker acceptance rules remain unresolved: API rate-limit HTTP 403 blocked checker/helpers; no substitute semantics were invented.
- Artifacts: [unique report](../reports/bfcl-source-provenance-codex195-report.md), [source review](../tests/fixtures/bfcl_ast_source/candidate-codex195/README.md), candidate provenance and exact code-only custodian request alongside unchanged original files. Candidate schema is deliberately inadmissible; no approved receipt pin was generated.
- Validation: 37 existing source-contract tests passed; static source/size/SHA-256/Git-blob/license/symbol audit passed; explicit gate remains blocked (exit 2); candidate schema refusal precedes any projected source read. No upstream evaluator code was imported or executed. Registry, adapter and scorer remain unchanged.

## BFCL custody operator packet — Codex 208 — 2026-10-14

- Status: documentation-only; official full-call source/runtime and archive/index custody remain blocked. No production authorization or new approval pin.
- Artifact: [operator packet](bfcl-codex208-operator-packet.md), linked from the source acquisition contract. It enumerates retained/missing original paths, unknown transitive discovery, approved receipt delivery and independent trusted-channel pin, license/offline runtime closure, separate exact-index/storage/split approval and ordered verification/stop conditions.
- Finding retained: the current source gate checks approved projection integrity only; the selected reader has no independent index-pin admission. Neither source acquisition nor passing synthetic controls closes the remaining runtime/export/quota/snapshot/cleanup and diagnostic-review gates.
- Validation: **165 passed** across source-contract, selected/privacy and registry regressions; unpinned source gate exits **2**, `measured=false`, `production_authorized=false`. Rechecked all seven retained size/SHA-256/Git blob identities (126,311 bytes) and local document links.
- Scope: `/tmp/hg-codex-208` only; no benchmark files, archives, external dataset roots, network fetch, package install, upstream evaluator execution or model/GPU run. Candidate bytes, provenance, adapter, scorer and registry are unchanged.

## BFCL packet/provenance review — Codex 217 — 2026-10-14

- Status: docs/test correction only; full-call source/runtime and independent archive/index custody remain blocked. No production authorization or approval pin.
- Findings: the Task 208 packet omitted exact receipt/index field names and reader bounds; metadata response bodies are not retained with the Task 195 candidate, so recorded upstream observations cannot be independently reverified offline from this handoff. Clarified those limits and the source gate's commit-shape/declared-edge scope.
- Evidence: [unique review report](../reports/bfcl-packet-review-codex217-report.md), [corrected operator packet](bfcl-codex208-operator-packet.md), and a source-contract regression confirming the retained candidate's blocked flags and refusal before projected-source access even with its integrity digest.
- Validation: **87 passed** across source-contract and registry tests only; unpinned source gate exited **2** with `measured=false`, `production_authorized=false`. Source-only registry validation passed with 28 datasets, 8 shared blockers and 11 historical records.
- Scope: `/tmp/hg-codex-217` only; no dataset payload/answers/heldout/archive/external dataset-root access, network, upstream execution, installation or model/GPU work. Candidate, production code, registry and earlier receipts are unchanged.

## TriviaQA adapter impact review — Codex 167

- Status: production scorer unchanged; upstream source provenance blocked
- Finding: provenance commits changed tests/docs only; adapter blob and scorer behavior are unchanged. Regular suite reports 28 passed / 1 skipped; explicit `tools/check_triviaqa_provenance.py` exits 2 until acquired source exists.
- Evidence: `TRIVIAQA_ADAPTER_IMPACT.md`; `tests/fixtures/triviaqa_upstream/README.md`
- Remaining gate: independently acquire and review original evaluator bytes/license/commit linkage. This does not certify grouping, F1 or official full evaluator behavior.

## Filesystem quota backend audit — Codex 168

- Status: `documented_blocker`; no production quota authorization.
- Scope: source only in `/tmp/hg-codex-168`, base `10e983fc5fcb006c5afdbce1ef851dad71e953f2`; no mounts, quota operations, Docker queries, dataset/model/H0 or benchmark execution.
- Finding: bwrap/files writable binds and bare tmpfs, Docker exec writable roots/scratch, and host/method workspaces lack a complete paired byte/inode enforcement backend. Inert-control bounded tmpfs is a separate capability; `statvfs`, disk usage, reservations and snapshot preflight cannot close the gap.
- Evidence: [backend audit and exact OS/backend requirements](filesystem-quota-backends.md), [task report](../reports/filesystem-quota-codex168-report.md), [source hashes](../reports/filesystem-quota-codex168-source-evidence.json), [synthetic results](../reports/filesystem-quota-codex168-test-result.txt).
- Validation: 252 existing synthetic runner/artifact tests passed; temporary files stayed in the worktree and were removed. Runtime source and tests are unchanged.
- Remaining work: OS project-quota provisioning or bounded scratch allocation, actual daemon/snapshotter support for paired hard limits, complete trusted observers, admission before staging/writes, snapshot/export bounds and verified cleanup. No capability detector was added without an implemented backend.

## Process rule

Before launching any new adapter, add or update its entry here and add the corresponding platform capability to `docs/platform-improvement-log.md`. The launch review must cite the entry, the exact manifest hash and the runtime gate receipt.


### GAIA frozen source / snapshot compatibility — Codex 151

- Scope: isolated `/tmp/hg-codex-151`, base `8fcdcb80b90f43ab1c76c1f572c5cf70a6504e11`; source/control inspection and synthetic offline regressions only. No dataset/heldout/model/H0 run artifact reads or runtime execution.
- Change: added complete Git-tree/runtime compatibility review with explicit refusal to authorize lifecycle or reuse receipts; repaired snapshot admission handling for negative sizes, missing/relative Docker roots and observation exceptions.
- Validation: 91 focused offline tests passed (88 new, three existing mocked snapshot regressions); runner failures preserve invalid/no-score semantics and attempt owned teardown.
- Evidence: `reports/GAIA_GATE.md` documents observed base metadata, compatibility inputs and remaining measured closure. No local GAIA lifecycle receipt was available; no lifecycle evidence was created.
- Gate: production lifecycle remains BLOCKED pending selected-only provenance, coherent frozen-source controls, trusted verifier/dependencies, artifact export, quota enforcement and verified owned cleanup. Current stdout/exit codes and best-effort removal are insufficient.

## Dataset blocker registry — Codex 178 — 2026-10-14

- Status: `isolated`, source/journal index validated; no execution authorization
- Scope: `/tmp/hg-codex-178`, reviewed base `e7acaa1126c4c63c8ddc338bd9a7f4988f43ffdf`; repository taxonomy, adapter declarations, journal and tracked source-audit documents only. No adapter imports, external receipt/task-payload reads, model/H0, heldout, network, Docker, or main edits.
- Finding: all 28 publishable declarations need coverage, including refused/unprovisioned adapters. Current blocker work and historical run outcomes are independent. Missing dataset-specific journal entries are evidence gaps, not passing gates.
- Evidence: [machine-readable registry](dataset-blockers.json), [format and review limits](dataset-blockers.md), `tools/check_dataset_blockers.py`, `tests/quality/test_dataset_blockers.py`, pinned `tests/fixtures/dataset_blockers/history-codex178.json`.
- Platform change: AST-only coverage validation against existing `CAPABILITY` and `EXERCISES`; eight reusable shared blockers plus dataset-specific families/statuses/evidence/actions. Task `demand x surface` remains separate from harness `exercises`.
- Historical preservation: 11 incomplete/partial/pending-review observations are independently pinned and must remain unchanged; effects remain null. Unknown exact run IDs remain null. External receipts/scores are journal citations, not newly verified facts. Both chess and GAIA interruptions remain separate records.
- Documentation conflicts: the platform log's historical 50-task sizing and the chess audit's already-used recovery-ID advice are explicitly indexed. Current planning follows AGENTS.md; no old receipt or historical paragraph was rewritten.
- Validation: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_dataset_blockers.py` reports valid, 28 datasets, 8 shared blockers, 11 historical records, production_authorized=false. `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/harnessgrad-pytest-blocker-registry-codex178-pytest-final tests/quality/test_dataset_blockers.py` — **45 passed**. Tests deny adapter imports, external file reads, sockets and subprocess execution.
- Remaining gates: this registry records unresolved requirements; it authenticates no external receipt and closes no runtime/scorer/measurement gate. Parent review/merge remains separate.
- Commit: accompanying focused docs/code/tests commit; exact hash reported with delivery.

## AgentDojo selected metadata privacy closure — Codex 180 — 2026-10-14

- Status: code-solvable selected `ENV`/`SETUP`/`VERIFY` metadata privacy/detection review closed; separate production-route admission remains `blocked`.
- Scope: isolated `/tmp/hg-codex-180`, base `e8dd6f62aff3acdc10e92bb8e1cff84075cec3b7`; adapter Python source and synthetic metadata controls only. No adapter/data edits, catalog or `cases.json` reads, prompt/gold/action payload reads, runtime/verifier execution, attacks, model/H0, network or main edits.
- Finding: fixed synthetic metadata keys and selected setup/input path identities require no catalog/task/reference hooks; invalid selections raise `KeyError` with no fallback. Fresh module-body execution uses an inert QA dependency stub under I/O/import guards; it does not validate real dependency imports or production admission.
- Detection: all 13 guarded file/JSON/catalog/task/reference seams are deliberately probed for each of the three metadata maps and stop before underlying reads. Valid/rejected selected lookups record zero guarded attempts; verifier `argv` stays opaque.
- Evidence: [unique focused report](../reports/agentdojo-metadata-privacy-codex180-report.md), `tests/quality/test_agentdojo_metadata_privacy.py`, and the source-only registry boundary regression in `tests/quality/test_dataset_blockers.py`.
- Registry: retired the completed `selected-metadata-review` action from the active list because the schema has no closed status. The separate `production-route-admission` runtime blocker retains Codex 164's production-route evidence and adds this limited metadata closure; global production authorization remains false.
- Validation: **109 passed** (63 metadata controls plus 46 registry regressions). `tools/check_dataset_blockers.py` reports valid, 28 datasets, 8 shared blockers, 11 historical records and `production_authorized=false`.
- Remaining boundary: no production `run_one` or H0 readiness claim, case materialization proof, trusted verifier/runtime receipt, cleanup observation or benchmark measurement. Historical controls remain unverified claims; no route was repaired or executed.
- Commit: focused tests/docs/report on the isolated worktree; parent review and integration remain separate.

## AgentDojo metadata-only provenance reconciliation — Codex 190 — 2026-10-14

- Status: `production-route-admission` remains blocked; no production authorization or registry/code change.
- Scope: isolated `/tmp/hg-codex-190`, base `a58b4b181193a2e2b201c6353722725ad77b597c`; checkout declarations and Git/source metadata only. No external dataset/receipt inspection, cases/prompts/prepared payloads/gold/actions/heldout/runtime binary reads, adapter import, runtime/scorer/network/model/H0, or main edits.
- Finding: inherited `_src/runtime/agent_runtime/prepared` presence claims agree with declared path roles but authenticate no release or selected rows. Adapter and generated `DOWNLOADS.md` agree on commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60` and expected archive SHA-256; package `0.1.35` and suite `v1.2.2` are separate axes. No independent exact-release/selected-group/runtime manifest is available in the checkout.
- Evidence: [unique report](../reports/agentdojo-provenance-codex190-report.md), [scoped metadata/hash record](../reports/agentdojo-provenance-codex190-metadata.json). Git identities and local declaration hashes are freshly computed; external presence, split counts and historical controls remain inherited, unverified claims.
- Remaining gate: authenticated metadata-only release/selected-group custody and protected artifact/dependency/runtime identities, plus independently reviewed selected-only non-scoring admission and fresh identity-bound runtime/lifecycle evidence. Codex 180 privacy closure does not supply either part.
- Validation: static pin reconciliation, scoped Git/hash recomputation, JSON consistency and diff whitespace review; no execution tests or production measurement.
- Integration: local documentation/metadata outputs only; parent review and main integration remain separate.

## Filesystem quota operator/backend checklist — Codex 191 — 2026-10-14

- Status: `documented_blocker`; documentation/schema only. Host provisioning, backend observers/allocators, runner integration and live enforcement remain external/runtime work; no production authorization.
- Scope: only `/tmp/hg-codex-191`, base `a58b4b181193a2e2b201c6353722725ad77b597c`; repository guidance, quota documentation and admission source contracts. No mounts/quota operations, live host configuration inspection, Docker/model/H0 execution or task-payload reads.
- Change: [operator/backend checklist](filesystem-quota-backends.md) assigns owners and gates for XFS/ext4 hard block+inode limits, paired tmpfs bounds, pre-staging workspace allocation, actual Docker driver/snapshotter storage, bounded snapshot/export and verified cleanup/quarantine. All implementation checkboxes remain open. Historical Codex 168 source findings and 252-test claim are preserved as historical evidence.
- Evidence contract: [Draft 2020-12 JSON Schema](filesystem-quota-evidence.schema.json) specifies closed, metadata-only run/source/policy/observer-bound records for provisioning, project/tmpfs scopes, writer inventories, Docker storage, snapshots and cleanup. Required trust/freshness/arithmetic/ownership checks and projection limits are documented separately; no semantic validator or runtime integration is implemented. Current runtime admission still refuses writable actor roots.
- Validation: installed `jsonschema.Draft202012Validator.check_schema` plus `FormatChecker` under `python -B`: **32 synthetic in-memory shapes/lexical controls accepted, 262 malformed shapes/lexical controls rejected**. All seven document links and 169 local schema references resolve; historical audit table and validation text match the base; no checkbox is checked. `git diff --check` passes. These are schema/document checks, not live observations or OS enforcement tests; no observation receipts were created.
- Commit: accompanying docs-only commit; parent review/integration and external provisioning remain separate.

## LiveCodeBench custody operator packet — Codex 207 — 2026-10-14

- Status: `BLOCKED_EXTERNAL_ROW_ATTESTATION`; task-198 request remains unsent. No external custody record, signature or independent approval is supplied.
- Scope: docs only in isolated `/tmp/hg-codex-207`, base `65b0f2a5bf95fdafd218ca54198843c27b9fffbe`; local instructions, source and documentation only. No network, pool/statement/test/solution/heldout payload reads, adapter import, model/H0 or main-branch changes.
- Deliverable: [operator packet](task-207-livecodebench-operator-packet.md) gives the exact 12-key target JSON template, separate authenticated custody/reviewer signature channels, offline OpenPGP commands, bounded metadata-only preflight, failure dispositions and the no-payload boundary. The template is not an issued receipt; no attestation or approval artifact was created.
- Validation: target keys, values and types match AST-read admission constants; original-ID train calculation matches. Shell syntax and embedded Python compilation pass; all three packet links resolve; `git diff --check` passes. Verification commands were not executed and no payload-reading tests were run.
- Limit: existing `identity(statement, ...)` cannot run in this scope. Preflight cannot authenticate provenance by itself or set `row_attested`; independent review and later separately authorized production admission remain required. Fresh pool verification stays false, and other execution gates are unchanged. Parent review/integration remains separate.

## 2WikiMultihopQA source-gate review — Codex 206 — 2026-10-14

- Status: independent evaluator source gate closed for the pinned code-only fixture; fresh dependency, Hub/data provenance, historical metric comparability and shared runtime gates remain blocked. No production authorization.
- Scope: only `/tmp/hg-codex-206`, base `65b0f2a5bf95fdafd218ca54198843c27b9fffbe`; reviewed merged source fixture commit `349d74f1d930bcb4c6664b1f6521571f118a619a`, exact evaluator code, provenance metadata, focused tests and current registry. No benchmark task/answer/alias/split/heldout payload or external benchmark receipt reads, adapter imports, production scorer edits, network, model/H0 or controls/pilots.
- Source finding: original v1.0 and v1.1 evaluator bytes, exact Apache-2.0 license/requirements, and GitHub commit/root-tree metadata bind to upstream commit `209e761834d1ce055856fc11072c0a5aab47601d` and root tree `545a956af257f0c79c68c39a358086de7cbf243b`. Fresh tests reconstruct tree/blob identities and check independent SHA-256 pins; the v1.1 transcription region matches without importing the adapter. The unsigned commit's observed origin still relies on the preserved GitHub HTTPS acquisition metadata; no new acquisition or archive revalidation was performed.
- Metric boundary: upstream `f1` is Answer F1; `joint_f1` is the harmonic mean of product precision/recall across answer/support/evidence. Both remain distinct. Synthetic v1.1 alias/evidence quirks are preserved, including possible values above 100; finite fabricated-input checks do not certify production wrapper or leaderboard equivalence.
- Registry change: retired stale `independent-evaluator-source` because the active-only schema has no closed status; added explicit `ujson-native-offline-closure` and `hub-data-provenance` external blockers. `recovery-comparability`, all eight shared blocker references, the original partial-measurement record and its null effect remain unchanged. This supersedes only the earlier journal's missing-source finding, not its historical fetch failure, metrics or receipts.
- Dependency boundary: unchanged programs execute with real installed `ujson==5.10.0`, without transitive Python runtime requirements. Published wheel/sdist hashes are metadata only; payload acquisition, installation-origin linkage, supported Python/native image identity, native loader/transitive closure and a fresh offline installation/import/synthetic run remain required. No dependency was installed or substituted.
- Data boundary: code provenance and its license do not bind the Hub/data revision, split/selected manifest, alias artifact identity/completeness, dataset rights or release-to-evaluator mapping. Metadata-only custodian evidence remains required; no payload access is authorized by this closure.
- Evidence: [unique task 206 review and test receipt](task-206-twowiki-provenance-review.md), `tests/quality/test_twowikimultihopqa_provenance_codex197.py`, `tests/fixtures/twowikimultihopqa_upstream_codex197/provenance.json`, and the machine-readable blocker registry.
- Validation: fresh provenance suite **38 passed in 0.24s**, registry suite **49 passed in 2.92s** (**87 total**, no failures/skips), with plugin autoload/bytecode/cache disabled and source/synthetic-only guards. Registry checker: valid, 28 datasets, 8 shared blockers, 11 historical records, `production_authorized=false`. In-memory base comparison confirms only 2Wiki active blockers changed; all historical/shared/recovery objects and the complete earlier journal are preserved. Existing fixture, tests and production code are unchanged; `git diff --check` passed.
- Cleanup: fresh task-owned `.scratch/twowikimultihopqa-codex206` and `.scratch/blocker-registry-codex206` were removed after preserving results and verified absent. This is local test-file cleanup, not a runtime/snapshot receipt.
- Integration: focused documentation/registry/journal commit; parent integration remains separate.

## 2WikiMultihopQA registry audit — Codex 216 — 2026-10-14

- Scope: isolated `/tmp/hg-codex-216`, base `82459cfa6d16c323ca40f21db2daf597921aedb3`; local source/docs and code-only synthetic tests. No adapter imports, benchmark payload/external receipt reads, network, dependency installation, model/H0 or pilots.
- Finding: the current registry already retires `independent-evaluator-source`; `ujson-native-offline-closure` and `hub-data-provenance` remain `external`, `recovery-comparability` remains `measurement`, all eight shared gates remain active and production authorization remains false. No registry edit was needed.
- Change: three source-only registry regressions protect those blocker states, the unchanged original 48-scored/two-invalid mixed Answer F1/Joint F1 pilot with null effect, and separate `demand=evidence`, `surface=information_seeking`, `exercises=[context]` axes. Registry, history baseline, taxonomy, checker, evaluator and provenance fixture/tests are byte-identical to the base; the earlier journal is an unchanged prefix.
- Validation: registry checker valid (28 datasets, 8 shared blockers, 11 historical records); combined registry/provenance suites **90 passed in 3.10s** (52 + 38), no failures/skips. Baseline suites passed 87 tests. An initial missing scratch-parent setup error was corrected and is recorded separately in the [task 216 audit receipt](task-216-twowiki-registry-audit.md). `git diff --check` passed.
- Cleanup: task-owned `.scratch/registry-provenance-codex216-baseline` and `.scratch/registry-provenance-codex216-final` removed and verified absent. Local test cleanup and source/synthetic success establish no deployment, benchmark or production readiness. Docs/tests-only commit; parent review/integration remains separate.
## GAIA operator-packet contract review — Codex 219 — 2026-10-14

- Status: BLOCKED; task-210 clarification only. Task-212 readiness matrix is unavailable in this checkout/visible history, its path/commit was requested, and reconciliation remains pending. Task-202 evidence is still pending. No execution approval or gate closure.
- Scope: only `/tmp/hg-codex-219`, base `82459cfa6d16c323ca40f21db2daf597921aedb3`; repository source/docs/Git metadata and authored synthetic tests. No benchmark task/answer/attachment/heldout or external receipt reads; no Docker, network, model, H0, benchmark control or official scorer execution.
- Finding: task 210 contains no direct authorization or contradictory execution instruction, but omits explicit dry-preflight input/exit boundaries, diagnostic-v2 serialization/replay, lifecycle scope/outcome/snapshot/cleanup binding, no-model null encoding and the distinction between structural publication and production authorization.
- Change: [task-210 packet](gaia-operator-packet-codex210.md) now states those contracts and final-candidate comparison requirements; [unique review](gaia-contract-review-codex219.md) records findings, missing input and limits. No implementation/schema/admission exception or reusable platform capability changed.
- Validation: focused authored preflight, compatibility/snapshot, lifecycle and diagnostic-policy regressions: **285 passed, 11 driver/eval-side tests deselected in 2.08s**, no skips; `git diff --check` passed. These are synthetic regression results, not dataset/runtime receipts.
- Integration: narrow documentation commit in the isolated worktree; parent review/integration and task-212 review remain separate. Documentation paths remain conservatively runtime-affecting under the existing compatibility contract; no historical receipt reuse.

## ujson wheel provenance and offline package install — Codex 226 — 2026-10-14


- Status: exact package acquisition/RECORD and fresh offline installation verified; `ujson-native-offline-closure` remains `external`. No supported-image, loader/transitive native closure, native import, bundled-component notice clearance or production authorization.
- Scope: only `/tmp/hg-codex-226`, base `61e7f82245c76e7c833740216940d1fcaf3b76be`; public official PyPI JSON/wheel and repository code/metadata only. No benchmark dataset payload, adapter import, scorer, model, endpoint, H0, pilot or sdist/build acquisition. Native extension was never loaded; no `ldd` or native loader execution.
- Artifact: recorded target CPython 3.12.4/Linux x86_64 with glibc >=2.17; exact `ujson-5.10.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl`, 53,686 bytes, SHA-256 `f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1`. Official PyPI JSON binds URL/hash; original response, acquisition time/headers, wheel and static ELF reports retained in `tests/fixtures/ujson_pypi_codex226`. HTTPS metadata remains the origin trust boundary; no independent publisher signature is claimed.
- Dependency correction: this published extension hash differs from the task-197 installed extension. Static readelf records five direct libraries (`libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1`, `libpthread.so.0`, `libc.so.6`), required GLIBC/GLIBCXX/CXXABI/GCC versions, no RPATH/RUNPATH and no bundled shared libraries. Old three-library observations cannot attest this artifact. No declared transitive Python runtime requirements.
- Notices: exact combined 5,975-byte license retained, including Electronic Arts/ESN, MODP_ASCII and Tcl-derived terms. Defined double_conversion symbols have no corresponding notice in the wheel license; authoritative bundled source/revision/license and required-notice review remain open. No notice text or clearance was invented.
- Installation: two fresh task-local venvs used local-wheel-only, exact-hash, binary-only, no-dependency/no-cache/no-version-check/no-bytecode installation. The final replay also set `PIP_CONFIG_FILE=/dev/null` because `--isolated` still permits global/site configuration. Pip 24.0 reports and original non-RECORD file identities are retained; all five files byte-match the wheel. This is package installation on the current glibc 2.35 host, without an OS network namespace or immutable image attestation.
- Change: [task-226 report and reproducible offline procedure](task-226-ujson-wheel-report.md), [focused package provenance tests](../tests/quality/test_ujson_pypi_codex226.py), [HTML evidence summary](../reports/ujson-wheel-codex226-overview.html), and a narrow ujson-blocker observation/evidence/next-action refresh. External status, all histories/taxonomy/shared gates/other datasets and production authorization remain unchanged; earlier receipts/journal entries are preserved.
- Validation: final **61 passed in 4.03s** (9 package + 52 registry), no failures/skips. Registry checker valid: 28 datasets, 8 shared blockers, 11 historical records, `production_authorized=false`. The initial run's new-test version ordering mistake and nonliteral evidence locator caused 23 failures/38 passes; both were corrected and initial output retained separately. [Final result](../reports/ujson-wheel-codex226-test-result.txt); original JSON/wheel/acquisition pins and actual ELF metadata are checked offline without importing package or dataset code.
- Remaining handoff: platform owner must bind this wheel to a supported immutable Python/native image, attest resolved loader/library paths/hashes and recursive symbol providers, complete bundled-component notices, and observe a fresh network-denied image-bound install/native import/fabricated JSON round trip. Any later scorer synthetic run needs its own wheel/image-bound receipt.
- Cleanup: task-owned extracted ELF, both venvs, local HTML settings and pytest temporary files removed after preserving evidence; see `tests/fixtures/ujson_pypi_codex226/local-cleanup.json`. This is local file cleanup only. Focused task commit is for parent diff review/integration; no main merge or runtime gate change.
- Diff review: authored source/docs pass the focused staged whitespace check; raw readelf reports and initial pytest output preserve tool-emitted trailing spaces. All new relative documentation links resolve. The task-197 fixture/tests and all production code remain byte-identical to the base.
## GAIA scorer full-revision discrepancy — Codex 228 — 2026-10-14

- Status: `BLOCKED_CANONICAL_FULL_REVISION_RELATIONSHIP_UNRESOLVED`; no pin correction recommended on current evidence, no production authorization.
- Scope: only `/tmp/hg-codex-228`, base `61e7f82245c76e7c833740216940d1fcaf3b76be`; repository metadata/code and anonymous canonical public Space metadata/scorer requests. No dataset questions/answers/attachments/private gold, adapter/scorer import, dependencies, Docker, model/H0, benchmark execution or main-branch changes.
- Finding: adapter pin `9f133d71362ecb0a1c7ff6b4dcfc2a6b9f8ffd1e` and candidate `9f133d71362e77b3539f1514f31b9c101a545fec` differ after a shared 12-character prefix. The expected scorer SHA-256 is `0d44c07f3046eec521697c22e3eaca8719cc81e422a8eaf32695c5f22bdac6e2`. Local Git traces the unchanged declaration to the original GAIA adapter commit and contains neither upstream object; it cannot authenticate their relationship. Task-200 mirror checksum/tree/blob observations remain inherited claims.
- Canonical evidence: both revision API lookups, candidate root-tree/scorer requests and Git refs advertisement failed with network-unreachable errors before HTTP; both IPv4-only API retries timed out, also without HTTP. No canonical absence, alias, ancestry or typo claim is established.
- Deliverables: [unique report](task-228-gaia-scorer-revision-report.md) and [decision/evidence index](task-228-gaia-scorer-revision-evidence/decision.json) preserve exact IDs, failed requests, historical Git provenance, limits and required canonical commit/tree/scorer evidence. Production source, pins, mutable acquisition URL and admission gates are unchanged.
- Validation: all 29 metadata/source-integrity, historical Git binding, evidence hash, report link and append-only journal checks passed; `git diff --check` passed. No scorer or benchmark tests were run. These checks provide no run, runtime-cleanup or lifecycle receipt; execution fields are null. Parent review/integration remains separate.
## AppWorld canonical public source review — Codex 229 — 2026-10-14

- Scope: only isolated `/tmp/hg-codex-229`, base `61e7f82245c76e7c833740216940d1fcaf3b76be`; local source/docs and allowlisted official GitHub public code/docs/metadata. No repository archive, protected bundle, task/split payload, external benchmark receipt, wheel or image access; no adapter import, official task/scorer/runtime, model or H0 execution.
- Source: official `v0.1.3.post1` annotated tag `efac79081936323733f68fd78260dab6981f195a` peels to `66ad8099e12188ece0d3fe45e661dbc01880813b`, root tree `bbe398b91767a9a068add36eb84bdf936eed372f`, matching the local Dockerfile's requested package version. Eight original public code/docs/license files, raw contents-API responses, release/tag/commit/tree metadata and SHA-256 acquisition receipts are preserved. Failed raw-host requests and a tag-object API rate limit remain recorded; successful source acquisition used exact-commit official GitHub API responses. Official GitHub `git ls-remote` supplies tag/peeled-ref linkage; the annotated tag object itself was not acquired/rehashed. HTTPS acquisition is the origin basis, not independent custody/signature evidence.
- Mapping: pinned evaluator defines task/scenario goal completion and percentage output; local TGC/SGC use fractions, selected measured coverage, fixed-three variants and guarded original trial alignment. `test_normal` maps to local Test-N and `test_challenge` to Test-C; source keys and source splits stay separate from the harness train/eval partition. Public code identifies data version/URL `0.1.0`, but neither authenticates the adapter's bundle checksum/counts nor proves deployed image/package/evaluator contents. README short metric keys differ from actual implementation long keys.
- License: original public Apache-2.0 license is preserved. Upstream README separately adds encrypted-public-redistribution requirements for protected task/app/API-specific bundles; this review acquires no protected artifact and makes no blanket data-license claim.
- Remaining gap: current checker/runner supplies no original numeric trial identity to saved verdicts; the writer correctly marks anonymous cells unaligned, so current production-source flow cannot establish aligned SGC. Actual source/package/image/evaluator binding, split/manifest custody, coverage, budgets, endpoint, lifecycle/snapshot and cleanup receipts remain absent. No scorer/writer/adapter/registry behavior changed, no gate retired and no production authorization.
- Evidence: [task-229 report](../reports/appworld-canonical-source-codex229-report.md), [local adapter audit](appworld-local-adapter-audit-codex229.md), and [public-source manifest](evidence/appworld-codex229/source-provenance.json).
- Validation: offline custody checker passes 32 pinned-file digests, four reconstructed Git trees and eight public code/docs blobs; 27 local report links resolve within the worktree. Parent source/diff review and whitespace check pass. No upstream program, benchmark or synthetic scoring code executed and no score was generated. Focused local commit is for separate parent review/integration.
## Quota readback authentication review — Codex 233 — 2026-10-14

- Status: documentation proposal complete; host provisioning, observer/verifier implementation, allocation/runner wiring and runtime enforcement remain blocked. No checklist completion or production authorization.
- Scope: only `/tmp/hg-codex-233`, base `61e7f82245c76e7c833740216940d1fcaf3b76be`; reviewed quota schema/backend requirements, task-222 administrator checklist and runner/lifecycle source contracts. No host inspection/changes, network, Docker, key/signature generation, quota/runtime receipts, enforcement probes, models/H0 or pilots.
- Findings: current IDs/hashes and lifecycle replay authenticate no origin; historical root maintenance evidence is distinct from fresh run-bound provisioning/scope observations. Runner documentation requests distinct worker bindings while nested lifecycle snapshot checks use the enclosing binding; an explicit reviewed integration decision remains required.
- Change: [unique task-233 review](task-233-quota-readback-authentication.md) specifies enrolled Ed25519 roles and exact signed bytes, external closed statement bodies, challenge/lease/allocation joins, independent host/final-namespace collection, durable consumption and cleanup release. It preserves existing closed schemas, reason codes and false authorization flags. Existing checklist/backend/runner docs link the proposal; the [local HTML companion](task-233-quota-readback-overview.html) summarizes it.
- Validation: 24 local links across the four reviewed Markdown documents resolve; schema field/phase comparison passed; quota schema and both runner/lifecycle implementation files are byte-identical to base. Local HTML render completed with four panels and zero writing warnings; no external asset references. `git diff --check` passed. No runtime tests or host queries were run for this docs-only change.
- Cleanup/integration: only task-owned local HTML-render state was temporary; no runtime resource cleanup is claimed. Parent diff review and integration remain separate; no merge or gate closure.

## Current blocker observation audit — Codex 240 — 2026-10-14

- Scope: only `/tmp/hg-codex-240`, reviewed merged HEAD `0930d99cc882c5a049c98f9123e9427470e7e818`; source/provenance reports, metadata and current registry. No dataset payload/external receipt, adapter import, network, host query, scorer/runtime, model, GPU or diagnostic execution.
- Findings: mark AgentDojo's directory inventory as inherited metadata rather than authenticated current custody; distinguish the missing connected quota backend from unknown host quota capability/enforcement. Add merged report anchors. Both machine blockers remain `runtime`.
- Guide corrections: BFCL's partial code/checker acquisition in tasks 195/227 and ujson's exact wheel/offline package installation in task 226 supersede two old acquisition statements. Complete source/custody, notice/image/native closure and runtime gates remain open; no external blocker is downgraded.
- Preservation: independent comparison permits only those two machine `observed`/`evidence` pairs to differ. Every blocker ID/family/status/action, shared reference, taxonomy/review field and all 11 historical records match reviewed HEAD; earlier journal content is unchanged. No production code, tests, provenance fixtures or historical reports/receipts are edited.
- Validation: checker valid, 28 datasets / eight shared blockers / 11 historical records, `production_authorized=false`; existing guarded registry suite **52 passed in 2.66s**, no skips. Baseline passed 52 tests after creating the initially omitted scratch parent; the first invocation's setup errors are recorded in the [unique task-240 audit](task-240-blocker-registry-audit.md). Diff whitespace and local-link checks pass. Test-file cleanup is local housekeeping, not a runtime cleanup receipt. Parent review/integration remains separate.

## Ordinary GPU entrypoints and sandbox audit — Task 242 — 2026-10-14

- Scope: isolated `/tmp/hg-codex-242`, base `0930d99cc882c5a049c98f9123e9427470e7e818`; docs, CLI help and mocked tests only. No model/H0, endpoint, GPU, Docker or host-quota execution.
- Finding: ordinary entrypoints have no universal strict filesystem-quota/backend-observer prerequisite. Existing staged-policy requirements and the Task-163 declared-policy refusal remain; the UI explicitly chooses general sampling. Sandbox failure still refuses, and `--no-sandbox` remains explicit, warned, recorded and non-comparable, retaining the exec container boundary.
- Change: clarify CLI help and README scope; make local demo sampling explicit; add six capture-only/pre-execution controls. Runtime execution, CLI defaults, schemas and admission behavior are unchanged; an AST comparison confirms the driver diff changes only parser description/help text.
- Evidence: [task-242 audit](task-242-gpu-entrypoint-audit.md), `tests/quality/test_gpu_entrypoint_contract_codex242.py`, [focused result](../reports/gpu-entrypoint-codex242-test-result.txt). Four focused pure/mocked suites: **156 passed**, no failures/skips; three shell entrypoints pass `bash -n`; `git diff --check` passes. Initial missing-scratch setup errors, the corrected six-test result and the earlier focused output are retained. Final verification binds both pytest and stdlib temporary paths inside the worktree.
- Limits: authored model/sandbox successes are not live observations, quota enforcement, dataset-gate closure or production/H0 authorization. Unknown lifecycle/cleanup/snapshot evidence and current production gates remain unchanged.

## Legacy adapter relocation — ref-1 — 2026-10-14

- Scope: only `/tmp/hg-ref-1`; structural relocation of all 20 `adapters/` files to `legacy/adapters/`, preserving the historical README and contract coverage. `legacy/README.md` marks the archive unmaintained and NOT a supported route; the former RRSI domain is historical too.
- References: update documentation, source citations, split-test loading, relative roots in shell scripts and the historical domain, and the integrity exclusion from `adapters` to `legacy`. The domain retains the sibling-checkout default when installed into RRSI, and uses the containing checkout in the archive. Production imports are guarded by a new source-only AST test; no platform execution behavior, model/H0, endpoint or GPU activity.
- Validation: requested adapter and dataset-blocker suites **55 passed, 9 skipped** (optional external checkouts/run artifacts absent). Both shell scripts pass `bash -n`; archived Python changes are path references and domain root resolution, with source-only checks for archive/installed roots and environment override. The first test invocation had a missing scratch parent and a whitespace-sensitive README assertion; both were corrected before the passing run.
- Additional checks: integrity/split checks **4 passed, 1 skipped, 1 failed**. The failure lists `AGENTS.md` and `reports/` as unclassified; comparison against the starting commit confirms both pre-exist unchanged. `legacy/` is classified, and the platform hash scope is unchanged. No unrelated classification changes were made.

## Eval concern packages — e1 — 2026-10-14

- Scope: only `/tmp/hg-e1`, starting at `9c928ed`. Extracted/printed the real AST graph before selecting seven packages: `run`, `containers`, `admission`, `service`, `observe`, `policy`, `verification`. All 32 implementations moved; all 243 outgoing implementation edges (50 internal eval edges) are preserved under canonical remapping.
- Compatibility: every old `eval.<module>` path is a documented identity-preserving shim; production importers, tests, current documentation, source links, config-edge permissions and the two live blocker-index pointers use canonical paths. The architecture map lists all shims. Four module CLIs and standalone stdio execution remain usable. Schema location, GAIA historical-manifest required paths, historical receipts/source hashes and measured harness/method artifact bytes are preserved.
- Behavior review: executable module ASTs, signatures, annotations, defaults and literals match after import/root-depth rewiring. The archived critic's path references cover old and moved files; no unrelated bug fixes, model runs or H0 pilots.
- Validation: **275 focused tests passed**. Requested full run: 147 files, exit 1; final classification is 15 persistent assertion-failure files, one skip-only file, eight contention-sensitive files and one corrected live-index reference regression. Fourteen persistent failure files also fail on untouched `9c928ed`; independent baseline attribution for the expensive AppWorld scorer file remains unverified. The final isolated trials retry passes 15/15.
- Registry-only run: four of five files pass; `test_dataset_controls.py` has the same two failures / 23 passes / one skip on current and untouched baseline, including serial retry. A pre-existing orphaned 16-job runner shared this checkout with the requested 12-job run, so initial failures and even some serial rechecks were contention-sensitive. The runner's final failure summaries retain first-pass counts; the audit uses actual serial results.
- Evidence: [e1 refactor audit](../reports/eval-package-refactor-e1.md); local command transcripts and per-file baseline comparisons in `.scratch/eval-refactor/`. Existing container/services/isolation, fixture/configuration and stale-assertion failures are reported without changing their behavior.


## Data namespace split — 2026-10-15 — ds

- Scope: `/tmp/hg-ds` only, based on `fdef36a`; Stages A → C → D in separate commits.
  Stage B (`ad25c7d`, `5cb804e`) was already present. No main-branch commit or merge.
- A (`b4e2e96`): moved QA, registry, command control and command oracle harness into
  `data/scaffolds/`, with documented temporary module/script/standalone-asset shims.
  Focused gate: **92 passed**; adapters unchanged.
- C (`2e50b52`): rewired all scaffold consumers, including generator templates,
  verifier package copies and the supported harnessgrad-domain bridge; deleted
  all A shims. Moved Stage B's aggregation helper into scaffolds with unchanged
  policy JSON/rules. Added cross-adapter import guards. Gate: **126 passed,
  9 skipped**; bridge follow-up: **3 passed, 9 skipped**.
- D (accompanying commit): moved 28 adapters and 14 reviewed asset directories to
  `data/datasets/`, plus two explicitly owned difficulty sidecars; no adapter shims.
  Updated discovery, imports, dynamic names, asset paths, schema, tools, tests and
  current docs. The ordered 28-name catalog and explicit control/aggregation
  declarations are preserved. Fixtures stay top-level.
- Review: tau-bench's 210-file inventory has no unclear entries. Its 206 pinned
  vendored/generated files retain byte identity and provenance. PinchBench's
  inventory stays untouched/unclassified at `data/pinchbench/inventory.json`.
  Historical evidence retains baseline bytes and paths; no frozen receipt ran.
- D validation: blocker checker reports **valid:true, 28 datasets**; the ten
  requested focused files report **214 passed, 10 skipped**; registry-only runner
  reports **all 5 files passed**. No whole-suite, model, pilot or endpoint work.
- Exact commands, outputs, scope and remaining uncertainty:
  [split report](../reports/data-split-stages.md).

## FEVER — source-only journal coverage — b1 — 2026-10-15

- Review: [FEVER source-only journal review](dataset-reviews/fever.md), with
  file/line citations for the strict-score transcription, pinned validation
  mirror, platform hash split and files/command verifier contract.
- Closed: `dataset-journal-gap` documentation coverage only. The retained
  `measurement` record now names the established source facts and next gate.
- Next: authenticate Hub conversion/evidence-group provenance and independently
  pin the upstream FEVER scorer; singleton conversion prevents inferring original
  strict-score comparability (`data/scaffolds/qa/evidence_scorers.py:157–165`).
  All eight shared gates and the review's named provenance/privacy,
  comparability and measurement gates remain open.
- Boundary: repository inspection only; no payloads, adapter/scorer execution,
  controls, models, network or production/H0 authorization.

## Physics Questions — source-only journal coverage — b1 — 2026-10-15

- Review: [Physics Questions source-only journal review](dataset-reviews/physicsquestions.md),
  with file/line citations for accepted-spelling exact matching, the pinned
  ReWOO CSV declaration, asserted 53-row pool and files/command verifier contract.
- Closed: `dataset-journal-gap` documentation coverage only; the retained
  `measurement` record carries next-gate evidence requirements.
- Next: authenticate ReWOO-to-BIG-bench task/target linkage and original metric
  source. The reference-only period stripping is the implemented rule, despite
  broader prompt wording (`data/datasets/physicsquestions.py:93–100,155–161`).
  All eight shared gates and the review's named provenance/privacy,
  comparability and measurement gates remain open.
- Boundary: repository inspection only; no payloads, adapter/scorer execution,
  controls, models, network or production/H0 authorization.

## Reasoning Gym — source-only journal coverage — b1 — 2026-10-15

- Review: [Reasoning Gym source-only journal review](dataset-reviews/reasoning_gym.md),
  with file/line citations for the library `score_answer` call, declared
  version/seed/family/count/digest pin, generated pool and verifier dependency.
- Closed: `dataset-journal-gap` documentation coverage only; the retained
  `measurement` record carries next-gate evidence requirements.
- Next: authenticate the package/generator and pool manifest, then establish
  offline dependencies in the actual verifier. The loader does not enforce the
  pool digest and `score()` does not enforce the installed version
  (`data/datasets/reasoning_gym.py:75–87,106–124`). All eight shared gates and the
  review's named provenance/privacy, comparability and measurement gates remain open.
- Boundary: repository inspection only; no payloads, generation, adapter/scorer
  execution, controls, models, network or production/H0 authorization.

### Journal coverage regression boundary — b1

The source-only coverage guard discovers every `journal-coverage` entry from the
registry and requires a tracked Markdown review reference with a live locator.
The three pre-existing omissions outside this change's scope—sportsunderstanding,
spreadsheetbench and strategyqa—are explicit strict expected failures. New gaps
fail normally; resolved gaps fail as unexpected passes until their exception is
removed (`tests/quality/test_dataset_journal_coverage.py`). These exceptions do
not close those datasets' journal gates.

Validation: `python3 tools/check_dataset_blockers.py` reports `valid:true`, 28
datasets, eight shared blockers, 11 preserved historical records and
`production_authorized:false`. Focused source-only tests
(`python3 -m pytest -q -rx tests/quality/test_dataset_journal_coverage.py tests/quality/test_dataset_blockers.py`)
report **55 passed, 3 xfailed**; the three expected failures are exactly the
out-of-scope omissions named above. No whole-suite or dataset-runtime tests ran.
## sportsunderstanding source-only review — 2026-10-15 — b2

The [cited source review](dataset-source-reviews-b2.md#sportsunderstanding-source-only-review)
records the local binary label matcher and its BIG-bench attribution, pinned
ReWOO CSV origin, imposed hash split and QA runtime contract
(`data/datasets/sportsunderstanding.py:63-95,147-191`;
`data/scaffolds/qa/base.py:290-312,314-386`). CLOSED: missing source-only journal
review. OPEN: independent scorer equivalence, installed/selected-only provenance,
metric comparability and measured coverage, plus every existing shared gate
(`docs/dataset-blockers.json:18-140`; `AGENTS.md:61-81`). No dataset, scorer,
control, model or network execution; no production/H0 authorization.

## spreadsheetbench source-only review — 2026-10-15 — b2

The [cited source review](dataset-source-reviews-b2.md#spreadsheetbench-source-only-review)
records the single-variant named-cell comparison, pinned verified_400 mirror,
hash/all-eval split options and Python/openpyxl/LibreOffice requirements
(`data/datasets/spreadsheetbench.py:20-48,74-87,278-287,352-372`). CLOSED: missing
source-only journal review and clarification of `8c323e6`'s submission repair;
its inherited local-control results remain history (`docs/adapter-integration-journal.md:77-83`).
OPEN: source/scorer/runtime custody, comparability, coverage and failure
classification, including the parse-failure return becoming measured zero
(`data/datasets/spreadsheetbench/verify/check.py:174-188,369-387`), and every
existing shared gate (`docs/dataset-blockers.json:18-140`; `AGENTS.md:61-81`).
No dataset, scorer, control, model or network execution; no production/H0 authorization.

## strategyqa source-only review — 2026-10-15 — b2

The [cited source review](dataset-source-reviews-b2.md#strategyqa-source-only-review)
records ReWOO normalized whole-string EM, pinned CSV origin, imposed hash split
and the QA runtime contract (`data/datasets/strategyqa.py:66-101,157-199`;
`data/scaffolds/qa/base.py:290-312,314-386`). CLOSED: missing source-only journal
review. OPEN: independent scorer/original-benchmark comparability,
installed/selected-only and split provenance, measured coverage and every
existing shared gate (`docs/dataset-blockers.json:18-140`; `AGENTS.md:61-81`).
No dataset, scorer, control, model or network execution; no production/H0 authorization.

## b2 source-review validation — 2026-10-15

Only `python3 tools/check_dataset_blockers.py` and
`python3 -m pytest -q tests/quality/test_dataset_blockers.py --basetemp=/tmp/harnessgrad-pytest-b2-journal`
were run for validation: the checker returned `valid: true`, 28 datasets,
8 shared blockers, 11 historical records and `production_authorized: false`;
the focused file passed **53 tests**, including the new review-pointer guard.
No adapter/scorer/control, dataset payload, model, network or whole-suite execution.
The original blocker IDs/families/statuses, shared requirements and historical
records are preserved; only the three requested missing substantive reviews
close. The three coverage-only entries above remain explicitly pending.
## Four-dataset measurement coverage review — 2026-10-15 — hg-b3

- Scope: only `/tmp/hg-b3`; ALFWorld `current-runtime-review`, Bird MiniDev
  `sql-coverage-reconciliation`, DS1000 `host-slice-archive-review`, HotpotQA
  `schema-timeout-measurement`. Original `observed`/`next_action` text is preserved
  verbatim in the [unique review](../reports/measurement-coverage-hg-b3-review.md),
  with file/line evidence and per-dataset closed/open gates.
- ALFWorld: retain journal-complete `alfworld-h0-10pct-v4`, 9 tasks x3, jobs=1;
  27 is nominal protocol scope, not an independently checked measured count.
  Historical identity review closes; `current-runtime-identity` remains runtime.
- Bird: preserve v4 incomplete and v5's complete label/partial-measurement record.
  Planned 34x3=102, reported 28/34 measured tasks and 90 verify phases do not
  supply actual trial/error allocation. SQL failure semantics are reviewed and
  synthetically checked; original metadata reconciliation remains measurement.
- DS1000: documented 926/1000 host availability is separate from the 61-task,
  183-planned-trial pilot. Selected IDs, measured trial coverage and timeout
  records are absent locally; archive acceptance stays pending, effect=null.
  A synthetic failing timeout result reproduces why measured=true alone is
  insufficient for classification. Configured 120/130-second deadlines are limits.
- HotpotQA: malformed schema is unmeasured/no reward; valid missing/partial support
  is measured joint EM zero. Synthetic expiration reproduces a timeout detail
  without an unmeasured marker falling back to zero in aggregation. Source review
  closes; `timeout-aggregation-admission` remains code-solvable. The user-stopped
  94/1476 protocol remains incomplete, with no inferred unique-task coverage.
- Preserved: all prior journal sections, receipts, pinned historical records,
  null effects/unknown run IDs, and all eight shared gates. External citations
  were not opened; no whole-suite, model, H0, endpoint or benchmark execution.
- Validation: **68 focused tests passed**, no failures/skips; checker valid for
  28 datasets, 8 shared blockers and 11 unchanged historical records, production
  unauthorized. Commands and results are recorded in the unique review; no
  whole-suite tests were run.
## Preserved lifecycle metadata review — 2026-10-15 — B8

- Scope: `/tmp/hg-b8` only, base `906607202fe6d7674695a410a72eb7379b869e75`;
  GAIA `frozen-lifecycle-receipt`, tau-bench `local-state-lifecycle`, ChessBench
  `interruption-closure` and `trusted-stepwise-transport` only. Original observed/
  next-action text and file/line evidence are in the [unique review](../reports/preserved-lifecycle-review-b8.md).
- Findings: GAIA source/runtime identity comparison is not receipt validation;
  policy refusal remains and no aggregate is valid. Tau-bench declares task-specific
  setup/late verifier inputs but imports the full gold pool, lacks both clean
  databases here and supplies no independent selected lifecycle evidence in the
  reviewed metadata. Chess's cited audit leaves termination authority/cleanup
  unresolved; its pure public session remains offline-only without trusted runner
  integration or measured interactive official execution.
- Disposition: metadata review recorded; all four blockers remain `runtime`.
  Both GAIA and both Chess IDs, incomplete statuses, null effects, evidence pointers
  and the pinned history fixture are unchanged. External receipt/audit bytes were
  not accessed or authenticated. No provisioning, adapter/payload read, backend,
  model/control/scorer or pilot execution; unknowns remain unmeasured.
- Validation: blocker checker valid (28 datasets, 8 shared blockers, 11 historical
  records, production authorization false); focused source-only registry tests
  **52 passed in 2.95s**. An initial in-tree basetemp was refused before collection,
  then corrected to the required external directory. Structural scope/history
  comparison and `git diff --check` passed. No whole-suite run or readiness claim.
## AppWorld protocol review and shared pilot-guidance closure — 2026-10-15 — B9

- Scope: registered `/tmp/hg-b9`, base `9066072`; repository protocol/source and planning-document review only. No external benchmark receipt, selected-task payload, model, endpoint, production service, official scorer or pilot execution; no method or budget change.
- AppWorld: public init/action, persistent service Python, API discovery, state-change and final-answer instructions exist without task-specific solution logic. Source review DONE; `successful-task-evidence` remains `measurement` with its original next action. Retain the 16/32-step measured zeros, 15/26 API calls and unresolved successful-task gate; external receipt bodies were not reverified. Missing: authentic successful measured actor-task evidence bound to actual actions/completion and official scoring.
- Shared documentation: `pilot-guidance-conflict` is retained as `done` for documentation only. Repair the current platform reuse rule and onboarding wording; explicitly supersede old journal sizing advice and C-001's original contract without rewriting historical paragraphs, receipts, scores or IDs. All dataset shared references and the other shared gates remain unchanged; no runtime or measurement pass follows.
- Evidence: [B9 review](../reports/b9-appworld-protocol-and-pilot-guidance-review.md), with file/line references, complete relevant sizing-document inventory and reasons pinned reports remain historical. The registry guide documents bounded `done` scope; the checker accepts it without dropping evidence or historical-preservation requirements.
- Validation: **68 focused tests passed in 6.77s** (`test_dataset_blockers.py`, `test_appworld_actor_protocol.py`); checker printed `valid:true`, 28 datasets, 8 retained shared records, 11 historical records, `production_authorized:false`; `git diff --check` passed. Protocol controls are synthetic, not benchmark measurements. No whole suite ran.
- Commit: accompanying `docs: close shared pilot guidance review and retain AppWorld gate` commit, for parent review; no main checkout write or merge.
## BFCL and TriviaQA public provenance acquisition — B5 — 2026-10-15

- Scope: registered detached worktree `/tmp/hg-b5`, base `9066072`; only
  `bfcl_v3` release-index-custody/simple-ast-contract and TriviaQA
  hub-export-scorer-linkage. Read their original observed/next_action verbatim;
  preserve those entries in the new bundle. Tasks 195/227/196/225 are reused
  unchanged. No payloads, archive GET, dataset-root access, upstream BFCL/loader
  execution, model/GPU/H0 or pilot work.
- BFCL: fresh upstream v1.3 tag/V3 release/commit/tree responses; signed commit
  bytes and 93 trees reconstruct to the prior immutable identities. Add 42
  original blob-verified Python files, including all three previously missing
  direct checker helpers and parser/dispatch dependencies. Twenty-three
  transitive handler bodies hit HTTP 403, with raw failure bodies retained.
  Archive HEAD supplies availability/name only, not archive/member custody.
- TriviaQA: direct Hub requests remain unsuccessful. Public hf-mirror.com
  metadata supplies exact export revision/config/splits/file identities,
  predecessor d63a76f loader bytes and conversion PR #8 parent/addition/deletion
  history. This predecessor differs from task 225; the PR is not a build/execution
  receipt. Mirror origin, actual converter execution and full scorer equivalence
  remain unauthenticated; HumanAnswers/verified/domain omissions are documented.
- Boundaries: all three blockers remain external. No independent review,
  custodian approval or separate approved source receipt pin is supplied; no
  archive digest/member/index binding is self-approved. All raw responses and
  error receipts have SHA-256 inventories. Only the three owned blocker
  observations/actions/evidence change; shared and historical records are intact.
- Validation: blocker checker valid (28 datasets/eight shared/11 historical,
  production_authorized=false); 99 focused tests pass, no skips. Offline checks
  cover every retained body/receipt/source hash, BFCL commit/tree/path/blob chain,
  mirror LFS pointer/directory identities without payload access, and refusal of
  unapproved BFCL source. Parent diff review and integration remain separate.
- Evidence: [B5 report](../reports/external-provenance-b5.md),
  [per-blocker review](../tests/fixtures/external_provenance_b5/README.md),
  [inventory](../tests/fixtures/external_provenance_b5/inventory.json) and
  [all evidence digests](../tests/fixtures/external_provenance_b5/SHA256SUMS).
