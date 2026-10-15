# w-resolver3 evidence packet

Source-scoped extension of w-resolver2. Start with `source-audit.json`,
`selection.json`, `inputs.json`, `results-complete.json` and `summary.json`.
`gap-audit.json` and full `gap-source/` preimages explain every remaining
nontrivial profile gap, including Tau-Bench's corrected N/A classification.

`obtain.py` rehashes inherited wheels and acquires exact missing public wheels;
`artifacts.py` retains actual HTTP response bodies and facts. The initial
public-wheel-only acquisition assertion and its script/state/output are preserved
in `attempts/`. A separately checked retained local Fast Downward build supplied
the absent wheel. `acquisition-chain/` preserves its original build receipt,
stdout/stderr and exact sdist; no new build occurred.

`unshare -Urn python3 tests/fixtures/hg_wresolver3/probe.py` generated the first
fresh venv experiment. ALFWorld and GSM8K completed. HotpotQA completed its
positive checks before a negative-directory name collision raised FileExistsError;
the raw failure and cleanup remain intact. `probe-retry.py`, in a separate fresh
network namespace and fresh venvs, completes HotpotQA, TriviaQA and LiveCodeBench
with unique negative directories. Its raw labels have the `retry-` prefix. Each
experiment records real external connect refusal, pip argv/exits/stdout/stderr,
selected JSON reports, hash-required installation and pip check, required-wheel
removal refusal after installation, and fresh-environment cleanup.

All subprocesses use the prior 180-second limit. Acquisition limits and exact
target tags are in `selection.json` and `target.json`. No model/server/endpoint,
container, task, scorer, source build, or production runtime ran. No runs/ or
frozen receipt is modified. The previous six bounded successes are carried
forward explicitly, not rerun. No successful empty graph is added to a numerator.

`payloads/` retains the ten wheel candidates new to the prior corpus. The entire
87-wheel graph remains externally retained at the path in `inputs.json`; this
directory alone is not a portable complete-profile archive. `coverage.py` derives
coverage from the real final receipts. `validate.py --seal` writes SHA256SUMS
after collection; `validate.py` checks byte custody, source excerpts, independent
extras-aware closure against pip's choices, all process results/refusals,
cleanup, exact coverage arithmetic and the additive registry-only boundary.

The report is `reports/w-resolver3-payloads.md`; validation output is
`reports/w-resolver3-validation.txt`. These are metadata reconstruction results,
not native/import/scorer/image/runtime closure or production authorization.
