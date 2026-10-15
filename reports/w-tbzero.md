# Is `terminal_bench`'s 0.0 a measured failure or "nobody tested this"?

Investigator: w-tbzero. Read: `INTERFACE.md` §2.2 and §2.5.7/§2.5.9 before concluding.

## 1. What the existing 10 runs actually contain

| run | per-task record | result |
| --- | --- | --- |
| `clean-1` (10-02 20:22), `41133` (10-01 17:07), `submit-1` (10-02 19:24) | `verdicts/round-*/*.json` | 65 verdicts, all `score=0.0` |
| `26452`, `26452c`, `48401`, `51682`, `54460`, `58172`, `90815` (09-29..09-30) | none | `curve.jsonl` says `score=0.0, n_scored=5 (or 1), n_invalid=0, measured_by_platform=true`; no verdict/trace of the check survives |

Of the 65 verdicts that do exist:

* **41** carry a real pytest summary — the check ran. E.g. `41133 round-0 chess-best-move`:
  `"reward 0 from /logs/verifier/reward.txt (exit 0) | ... FileNotFoundError: [Errno 2] No such file or directory: '/app/move.txt' ... FAILED ../tests/test_outputs.py::test_move_correct ... 1 failed in 0.08s"`.
* **8** show the check **failed to install its own test runner** and still scored 0.0 with no flag.
  E.g. `41133 round-3 build-pmars`:
  `"reward 0 from /logs/verifier/reward.txt (exit 0) | ... failed to download https://github.com/astral-sh/uv/releases/download/0.9.5/uv-x86_64-unknown-linux-gnu.tar.gz ... uv's release process is not working!"`.
  With no `uvx`, pytest never ran; `test.sh` writes `0` to `reward.txt` anyway and exits 0.
  `submit-1` has the same signature on `break-filter-js-from-html` in rounds 1-5.
* **15** are empty: `{"task_id": ..., "score": 0.0, "kind": null, "passed": null, "detail": null}`
  (`41133` rounds 2, 4, 5). `eval/run/runner.py:1417-1421` names this run by name: the round was
  entirely cache hits and the cached payload did not carry the verdict. The 0.0 is the cached
  round-0 measured value, not a fresh unmeasured trial.

All three curves report `n_invalid=0`, `verifier_kinds=["command"]`, `score 0.0`. The 7 older runs
predate both mechanisms needed to tell the two apart — `evidence_file`/ctrf and `HG_EGRESS_PROXY`
both first appear in the pre-rewrite history at `3633d6d` (2026-10-03 14:02), after every one of
the 10 runs.

## 2. What the check does when it cannot install pytest (code)

`data/datasets/terminal_bench.py:231-246` declares `argv ["bash","/tests/test.sh"]`,
`reward_file=/logs/verifier/reward.txt`, `evidence_file=/logs/verifier/ctrf.json`.
Every sampled `tests/test.sh` does
`curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh; source $HOME/.local/bin/env; uvx -p 3.13 -w pytest==8.4.1 pytest --ctrf /logs/verifier/ctrf.json ...`
and then writes 1/0 to `reward.txt`, exiting 0 either way (`docs/egress.md:5-18`).

On current `main` (`eval/verification/verifier.py:339-401`) a failed fetch means
`uvx: command not found`, so no `ctrf.json`; the verifier sets
`unmeasured = "the check wrote no /logs/verifier/ctrf.json: its tests did not run, so this task was not measured"`
and `eval/run/runner.py:1228-1237` turns that into an `invalid` task at stage `check`. It does
**not** fail closed into 0.

Residual gap (code reading only): if the **reward file itself** is absent, `verifier.py:341-345`
returns `{"kind":..., "passed": False, "detail": ...}` with no `score` and no `unmeasured`, and
`runner.py:1333` then defaults it to `0.0` (`float(v.get("score", 1.0 if v.get("passed") else 0.0))`).

## 3. The fresh probe

The instructed command (3 tasks, `--jobs 2`) cannot execute on current `main`: every `exec` task is
refused at admission — `! bn-fit-modify: invalid for dataset 'terminal_bench' at stage 'admission'
-- backend_observation_unavailable` (`runner.py:43-93`), and the driver prints `refusing to run:
none of the 3 tasks ... produced a scoreable result`. That is a refusal, recorded `invalid`, not a
zero.

A bound single-task diagnostic (`tb-zero-diag-cancel`, `cancel-async-tasks`,
`--sampling diagnostic --authorize-unobserved-diagnostic`) did execute. Harness worked (3 model
calls, wrote `/app/run.py`, submitted); result:
`"invalid": {"stage": "check", "detail": "the check wrote no /logs/verifier/ctrf.json: its tests
did not run, so this task was not measured"}`, `per_task = {}`, no curve.
Reproduced by hand in the task image with the proxy env: first attempt
`curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to releases.astral.sh:443` →
`uvx: command not found` → `reward.txt=0`, no `ctrf.json`; second attempt succeeded —
`ctrf.json` (17492 bytes), `6 failed in 2.12s`, `reward.txt=0`. The egress path to astral.sh is
intermittent, not absent.

## 4. Answer

Mixed, and the distinction is real. In the runs that kept records, 41/65 verdicts are **measured**
zeros (the check ran and failed), 8/65 are genuine "nobody tested this" recorded as a 0.0, and
15/65 are cache-hit artifacts carrying an earlier measured 0.0. The 7 runs with no per-task record
are untraceable: their 0.0s cannot be attributed to a check that ran. So the historical platform
**did** commit the bug this platform exists to prevent, and it was not rare.

## 5. Fix

Already on `main`, for the ctrf case: `evidence_file` declared by the dataset
(`terminal_bench.py:138,244`), `unmeasured` in the verifier (`verifier.py:375-400`), `unmeasured →
invalid` in the runner (`runner.py:1222-1237`), and proxy plumbing (`verifier.py:80-109` +
`HG_EGRESS_PROXY`). Remaining, small (~5 lines + a test): add `unmeasured` to the
reward-file-absent branch `verifier.py:341-345`; also keep the check's stdout on the invalid
record, which currently drops it. External, not a platform fix: `releases.astral.sh` is
intermittently unreachable even through the proxy.

## 6. Not determined

* Whether the 7 record-less runs' checks ran — nothing on disk says.
* Whether `docs/egress.md`'s 83/89 count is exactly reproducible (one task's `test.sh` sampled directly).
* Whether refusing every ordinary `exec` run at admission is intended policy or makes the dataset
  unmeasurable in practice outside a bound diagnostic.
