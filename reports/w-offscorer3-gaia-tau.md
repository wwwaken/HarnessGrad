# GAIA and Tau-Bench bounded official execution - w-offscorer3

Both complete upstream scoring modules import and execute under kernel-enforced socket denial. No shared or dataset blocker closes. These are authored scorer controls, not benchmark accuracy, production verifier admission or H0 runs.

All component-relative paths resolve under `tests/fixtures/hg_woffscorer3/gaia_tau/`.

## Source custody and exact commands

GAIA executes the complete unchanged `gaia-benchmark/leaderboard` `scorer.py`, adapter-pinned revision `9f133d71362ecb0a1c7ff6b4dcfc2a6b9f8ffd1e`, fresh SHA-256 `0d44c07f3046eec521697c22e3eaca8719cc81e422a8eaf32695c5f22bdac6e2`. Tau-Bench executes complete unchanged `tau_bench.envs.base.Env` at locally checked-out Git commit `59a200c6d575d595120f1cb70fea53cef0632f6b`, `base.py` fresh SHA-256 `1ad0402073f0ac9ca6b527efa0706e2aa8836dd2e5c1d453ed414ecb768c6d21`. Its complete `types.py`, `user.py`, `tool.py` and two actual upstream retail tools are retained, with every copied member checked against that commit's Git object. `identities.json` records all recomputed hashes and local verifier pins. Neither identity asserts a new remote provenance attestation; GAIA reuses the adapter pin and Tau-Bench authenticates local Git-object equality only.

Exact executed commands, repository-root cwd:

```sh
bash -x tests/fixtures/hg_woffscorer3/gaia_tau/commands.sh > tests/fixtures/hg_woffscorer3/gaia_tau/commands.stdout.txt 2> tests/fixtures/hg_woffscorer3/gaia_tau/commands.exact.txt
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer3/gaia_tau/verify.py > tests/fixtures/hg_woffscorer3/gaia_tau/verification.json
```

The script records expanded commands in `commands.exact.txt`, including a separate full Tau-Bench import probe and each `timeout 150s python3 .../offline_exec.py .../run.py gaia|tau official|local` command. The unmodified prior guard denies socket syscalls and io_uring, closes inherited socket fds, actively tests IPv4/IPv6/UNIX EPERM and imposes CPU 120 s / FD 256 limits. `*.offline.txt` receipts include actual interpreter/libseccomp hashes and no external dataset-payload read attempts. Source staging occurs before the guard and copies only scoring code, never released task records. Native filesystem exclusion is not claimed by the Python audit hook. `production_runtime_observation` is false. No model, endpoint, GPU, task runner, benchmark run or frozen receipt is used.

`run.py` records actual loaded scorer/dependency paths and hashes, full raw returns, print/warning output, argv, evidence and errors in `gaia-official.json`, `gaia-local.json`, `tau-official.json`, `tau-local.json`. Both sides bind the same input-file digest. `comparison.json` is joined by input ID; `verify.py` independently recomputes it and checks cleanup, guard probes and source bytes. The first packet before adding the final Tau-Bench boundary control is preserved under `preserved-initial/`; it contains no failed scoring attempt. Normal case directories are temporary outside the repository and all were removed.

## GAIA comparison

Official calls `question_scorer(answer, gold)` directly. Local imports unchanged `data/datasets/gaia/verify/check.py` and calls its real `main()` with the same authored answer bytes written to a file and the same gold serialized in JSON. Local whitespace stripping and placeholder/missing-answer policy are part of the caller being compared. For the labelled missing-file control the common canonical prediction is empty string; only the local filesystem channel omits the file.

Measured GAIA: **23 inputs; 20 numeric comparisons; 20 agreements; 0 numeric divergences; 3 nonnumeric/classification boundaries**. No official or local Python call exception occurred.

| Authored input | Official return | Local reward | Comparison |
| --- | ---: | ---: | --- |
| `number-exact` | 1.0 | 1.0 | agree |
| `currency-comma` | 1.0 | 1.0 | agree |
| `percent-unscaled` | 1.0 | 1.0 | agree |
| `number-wrong` | 0.0 | 0.0 | agree |
| `number-invalid` | 0.0 | 0.0 | agree |
| `float-inf-invalid` | 1.0 | 1.0 | agree |
| `float-nan` | 0.0 | 0.0 | agree |
| `text-case-space` | 1.0 | 1.0 | agree |
| `text-wrong` | 0.0 | 0.0 | agree |
| `text-internal-newline` | 1.0 | 1.0 | agree |
| `list-separator` | 1.0 | 1.0 | agree |
| `list-order` | 0.0 | 0.0 | agree |
| `list-punctuation` | 0.0 | 0.0 | agree |
| `list-numeric` | 1.0 | 1.0 | agree |
| `list-length` | 0.0 | 0.0 | agree |
| `list-empty-item` | 1.0 | 1.0 | agree |
| `list-space` | 1.0 | 1.0 | agree |
| `blank-answer` | 0.0 | 0.0 | agree |
| `whitespace-answer` | 0.0 | 0.0 | agree |
| `empty-gold` | 1.0 | unmeasured | nonnumeric/classification |
| `placeholder-gold` | 1.0 | unmeasured | nonnumeric/classification |
| `punctuation-empty` | 1.0 | unmeasured | nonnumeric/classification |
| `missing-answer` | 0.0 | 0.0 | agree |

Findings: empty gold, placeholder `?` and punctuation-versus-empty-gold are accepted by upstream's string normalization; local exits 3 with `measured:false` and no reward. These are refusal boundaries, not numeric disagreements or filled-in zeros. On `float-inf-invalid`, upstream maps invalid numeric text to infinity and consequently accepts it against authored gold `inf`; local agrees. `nan` does not equal itself, percentages are stripped without rescaling, list order/punctuation are significant, and list-length mismatch emits the preserved upstream warning. This describes actual controlled returns, not eligibility of those gold values in GAIA.

## Tau-Bench comparison

Official imports the complete unchanged Env and constructs it on a wholly authored retail database/task using actual upstream `ModifyUserAddress` and `TransferToHumanAgents`. It uses upstream `HumanUserSimulationEnv`; fixture stdin supplies the literal `continue` only when the labelled ground-truth-respond boundary requests it. No user simulator, Env method, tool body or dependency is stubbed. Authored current database and utterance `Action`s represent the identical recorded local database/log. A real upstream `step(transfer_to_human_agents)` triggers `calculate_reward`; the unfinished control instead executes an unknown nonterminal action. Local invokes unchanged `data/datasets/tau_bench/verify/check.py:main(argv)` with the committed upstream tool/hash library and the same authored database, gold actions, utterances and done state. No released retail/airline task or committed missing clean database is needed for these synthetic controls. Airline and released task breadth remain uncovered.

Measured Tau-Bench: **11 inputs; 10 numeric comparisons; 9 agreements; 1 numeric divergences; 1 nonnumeric/classification boundaries**. No official or local Python call exception occurred.

| Authored input | Official return | Local reward | Comparison |
| --- | ---: | ---: | --- |
| `address-correct` | 1.0 | 1.0 | agree |
| `address-wrong` | 0.0 | 0.0 | agree |
| `output-present` | 1.0 | 1.0 | agree |
| `output-missing` | 0.0 | 0.0 | agree |
| `output-case` | 1.0 | 1.0 | agree |
| `output-comma-asymmetric` | 0.0 | 0.0 | agree |
| `unfinished` | 0.0 | 0.0 | nonnumeric/classification |
| `unknown-ground-truth-tool` | 1.0 | 1.0 | agree |
| `ground-truth-tool-error-noop` | 1.0 | 1.0 | agree |
| `terminate-skip` | 1.0 | 1.0 | agree |
| `ground-truth-respond-output` | 1.0 | 0.0 | diverge |

Findings: `ground-truth-respond-output` is a measured divergence, **official 1 / local 0**. During `calculate_reward`, upstream replays the authored ground-truth respond action and appends it to `self.actions`; its output scan therefore sees the replay's own `secret` although the original agent said nothing. The local verifier records unknown ground-truth tool `respond` in `replay_errors` and correctly finds no agent utterance. This is a deliberate invalid/atypical task-schema boundary, not a claim about released task prevalence. `unfinished` has upstream intermediate reward 0 with `done:false` and `reward_info:null`, versus local recorded measured zero: no upstream terminal reward was computed, so it is excluded from numeric scoring agreements. Unknown/refused ground-truth tools leave the authored database unchanged and both scorers accept the matching no-op state; upstream appended actions/final replayed database and local `unknown ground-truth tool` / `Error: user not found` diagnostics are retained. Output comma removal applies to agent content only in both paths. The skip-termination control executes the real upstream exclusion.

S4 gains bounded complete-module GAIA and Tau-Bench execution only. Complete remote provenance, transitive dependency/image/ABI custody, private selected-input/export equivalence, trusted production resource/lifecycle isolation and valid live controls remain outside this packet. S1, S3, S4 and S6 stay PARTIAL; no dataset blocker closes.

Dependency finalization finding: the full Tau-Bench import probe and official process each exit successfully but retain ignored `BaseEventLoop.__del__` tracebacks ending in `AttributeError: '_UnixSelectorEventLoop' object has no attribute '_ssock'`. These arise after importing the real litellm/asyncio graph under socket denial; no cause beyond that observed context is asserted. They are not scorer-call exceptions and do not replace the returned scores. `dependency-diagnostics.json` records counted occurrences and raw stderr hashes. The first read-only validator assumed the guard footer was the last stderr line and failed on these finalizer messages; its failure is preserved in `validator-first-failure.txt`, and the validator now locates the actual JSON footer without discarding the surrounding stderr.
