# w-verifierfix: missing snapshot reward is unmeasured

FOUND: the snapshot reward-file-absent branch now returns `unmeasured` while preserving its previous `detail`. The reason also carries the bounded stdout/stderr and exit code, so those streams survive the runner's saved invalid record, which consumes the reason rather than the separate verdict detail. The docstring distinguishes missing from present-but-unparseable rewards. Sources: `eval/verification/verifier.py:278`, `eval/verification/verifier.py:344`, `eval/run/runner.py:1261`, `eval/observe/tracing.py:457`.

FOUND: the regression follows the mocked-transport idiom in `tests/quality/test_verifier.py:76`, drives the real `_verify_container_state` reward branch with `cp_out=False`, then feeds that actual verdict through the real runner `_evaluate` and progress writer. Runtime creation/identity/startup are doubles, not observed Docker objects; identifiers beginning `synthetic-` are authored test inputs. The two exit-code cases assert invalid outcomes, no per-task score/cache entry, and both streams in the saved record. Sources: `tests/quality/test_verifier_reward_absence_w_verifierfix.py:12`, `tests/quality/test_verifier_reward_absence_w_verifierfix.py:52`.

FOUND: before the fix, both exit codes 0 and 3 returned a verdict without `unmeasured`; actual aggregation published `{"synthetic-task": 0.0}` and `invalid: {}`. The final test file against baseline source loaded in memory reported `2 failed, 4 passed in 1.23s`; after the fix it reported `6 passed in 1.94s`. Exact commands, outputs, and the observed baseline commit are in `registry/w-verifierfix-validation.txt:183` and `registry/w-verifierfix-validation.txt:247`.

FOUND: all four requested modules passed before and after, with unchanged test sources. Before -> final after counts:

- `tests/quality/test_verifier.py`: 23 passed -> 23 passed.
- `tests/quality/test_container.py`: 10 passed, 16 skipped -> 10 passed, 16 skipped.
- `tests/quality/test_staged_receipt_audit_codex193.py`: 23 passed -> 23 passed.
- `tests/quality/test_stop_semantics.py`: 4 passed -> 4 passed.

Exact commands, durations, outputs, intentional Docker skip reason, and basetemp removal are recorded in `registry/w-verifierfix-validation.txt:65` and `registry/w-verifierfix-validation.txt:247`.

FOUND: the present-numeric controls (0, 0.5, 1 despite check exit 3) and present-but-unparseable control all passed before and after, unchanged between those runs. These are newly added controls established before the production fix, not claims about pre-existing snapshot parseability coverage. The malformed branch still returns its ordinary failed verdict without `score` or `unmeasured`; the numeric path preserves its score. Sources: `tests/quality/test_verifier_reward_absence_w_verifierfix.py:79`, `tests/quality/test_verifier_reward_absence_w_verifierfix.py:89`, `eval/verification/verifier.py:351`, and the preceding validation references.

ABSENT: tracked changes in this enumerated scope: `eval/service/services.py`, `AGENTS.md`, `registry/dataset-blockers.json`, `docs/adapter-integration-journal.md`, and the four requested test modules. The exact `git diff --exit-code HEAD -- ...` scope and empty output with exit 0 are recorded in `registry/w-verifierfix-validation.txt:277`. Only verifier production logic, the standalone regression, and these two requested evidence files are submitted; no registry proposal is needed.

FOUND: `python3 tools/check_dataset_blockers.py` returned exactly `{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}`. The registry contents are unchanged; this verifier-only production edit does not change the blocker's schema/content checks. Source: `registry/w-verifierfix-validation.txt:277`.

UNKNOWN / reviewer attack point: actual Docker `cp_out` behavior is unverified. The false-return seam can represent absent output or a transport/access failure; both now remain unmeasured. Sixteen Docker-dependent tests were intentionally skipped using a blocking Docker shim. No live dataset, model, GPU, network dependency closure, or production authorization is established. Sources: `registry/w-verifierfix-validation.txt:247`, `registry/w-verifierfix-validation.txt:320`.
