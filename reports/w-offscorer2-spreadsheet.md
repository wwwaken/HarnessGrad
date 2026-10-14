# SpreadsheetBench bounded official execution - w-offscorer2

`spreadsheetbench` now has bounded **complete upstream module and official CLI execution** on authored workbook controls. This packet narrows only S4; `scorer-offline-closure` remains open and no dataset blocker is closed. It establishes no production H0 authorization or benchmark accuracy.

## Source identity and scope

Executed the unmodified `RUCKBReasoning/SpreadsheetBench` source `evaluation/evaluation.py` at revision `e2758ac01c6c52efc746bf0d53b2fd01dbc42dd2`. Its lossless bytes were decoded from the already-local GitHub contents response at `reports/w-spread2-evidence/official-source-response.json`; the response is preserved again in `source/official-source-response.json`. The source copy is `source/official-evaluation.py`, recomputed SHA-256 `4ae77cee8df01d1f34684fceab972810d696886533d33be2e89373de6b4d3de3`, and recomputed Git blob SHA-1 `d8109e9509f06fc67e9458fbbd4d494e086e48fc`. The API receipt's immutable URL and blob are checked by `prepare.py`. There is no new acquisition or network request, and no independent authenticity beyond that inherited source receipt is claimed.

The pinned `verified_400` mirror identity is separately recomputed: adapter-declared Hub revision `ab0b742b0fc95b946f212d80ac7771b5531272e4`, archive SHA-256 `10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949`, metadata SHA-256 `bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7`. The installed metadata is byte-identical to its archive member. These are mirror inventory identities, **not released-task scoring evidence**. No released instruction or workbook was scored. All paths and recomputed identities are in `source-identity.json`.

All fixture-relative paths in this report resolve under `tests/fixtures/hg_woffscorer2/spreadsheetbench/`. `SHA256SUMS` covers controlled input bytes, source copies, runners and raw outputs. `inputs.json` authors `19` input definitions and `inputs/<id>/` preserves actual golden/result XLSX bytes and task metadata. The full upstream module imports normally with unchanged imports; no AST selection or module substitute was needed. Runtime versions and module digests are retained in `official.json`: openpyxl 3.1.2, NumPy 1.26.4, tqdm 4.66.4.

The local source is unchanged `data/datasets/spreadsheetbench/verify/check.py`, SHA-256 `9ec684b333d4d4ca648c76fe6991085a8c4d046f9a620566a945bf0cbcb7bd19`; adapter `data/datasets/spreadsheetbench.py`, SHA-256 `8fdfad8f320bce041555ca3b4c8b769b79d07ad971af78f314852eb5f9799505`. Official and local `compare_workbooks` consume **the same on-disk files, instruction_type and answer_position**. A separate upstream CLI profile builds its required three workbook copies per authored row, using identical bytes, while the local `main` profile uses a fresh copy once per row. This is a caller-policy comparison, not a claim that the one-pair mirror and three-variant original release are equivalent.

## Exact commands and offline enforcement

From the repository root, the complete packet was generated with:

```sh
bash tests/fixtures/hg_woffscorer2/spreadsheetbench/commands.sh
```

The exact expanded commands from that script are:

```sh
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=
python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/prepare.py > tests/fixtures/hg_woffscorer2/spreadsheetbench/preparation.stdout.json
timeout 150s python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/offline_exec.py tests/fixtures/hg_woffscorer2/spreadsheetbench/execute.py official > tests/fixtures/hg_woffscorer2/spreadsheetbench/official.json 2> tests/fixtures/hg_woffscorer2/spreadsheetbench/official.offline.txt
timeout 150s python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/offline_exec.py tests/fixtures/hg_woffscorer2/spreadsheetbench/execute.py local > tests/fixtures/hg_woffscorer2/spreadsheetbench/local.json 2> tests/fixtures/hg_woffscorer2/spreadsheetbench/local.offline.txt
timeout 150s python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/offline_exec.py tests/fixtures/hg_woffscorer2/spreadsheetbench/execute.py official-cli > tests/fixtures/hg_woffscorer2/spreadsheetbench/official-cli.json 2> tests/fixtures/hg_woffscorer2/spreadsheetbench/official-cli.offline.txt
timeout 150s python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/offline_exec.py tests/fixtures/hg_woffscorer2/spreadsheetbench/execute.py local-main > tests/fixtures/hg_woffscorer2/spreadsheetbench/local-main.json 2> tests/fixtures/hg_woffscorer2/spreadsheetbench/local-main.offline.txt
bash tests/fixtures/hg_woffscorer2/spreadsheetbench/formula-netns-command.sh
python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/compare.py > tests/fixtures/hg_woffscorer2/spreadsheetbench/comparison.stdout.json
```

`prepare.py` verifies already-local mirror inventory before scoring; it does not run a scorer. The four initial scorer invocations run through an unchanged copy of the prior `hg_woffscorer/offline_exec.py` guard (recomputed digest in source identity), which denies IPv4/IPv6/UNIX socket syscalls and io_uring at the kernel, closes inherited socket descriptors, and actively verifies denial. Its 120 CPU-second / 256-FD limits and interpreter/libseccomp digests are in all four `*.offline.txt` receipts; each outer command has a 150-second wall bound. Receipts record no attempted external dataset payload reads and `production_runtime_observation:false`. This fixture custody is not production filesystem/ABI/runtime closure. No model, GPU, endpoint, benchmark runner, historical run ID or frozen receipt is used.

The full upstream CLI child actually executed this exact command (also preserved in `official-cli.json`):

```sh
/mnt/8t/xubuqiang/anaconda3/bin/python3 /tmp/hg-offscorer2-spread/tests/fixtures/hg_woffscorer2/spreadsheetbench/source/official-evaluation.py --dataset controlled --setting control --model no-model-executed
```

Its recorded working directory was `/tmp/hg-woffscorer2-spread-cli-valyalw4/evaluation`. The fixture built only authored `../data/controlled/` files and retained exact raw CLI JSON in `official-cli-metrics.raw.json`, as well as the child stdout/stderr and exit status in `official-cli.json`. The temporary tree was removed on normal exit.

## Per-input results

Direct boolean outcomes: **15 numeric comparisons; 15 agreements, 0 numeric divergences; 4 nonnumeric inputs**. Official comparator exceptions: **2**. Local comparator exceptions: **3**. Exception/return differences are findings, not filled-in zeros.

Full upstream CLI exited **0**, executing **57 synthetic workbook-copy evaluations** (19 authored controls, three identical copies each). Caller-profile numeric outcomes agree **16/16**, with **0 numeric divergences** and **3 local unmeasured controls**. This does not combine the function-level and caller-policy counts.

| Authored input | Official comparator | Local comparator | Direct outcome | Official CLI three copies | Local full check |
| --- | --- | --- | --- | --- | --- |
| `exact-number` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `numeric-string` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `rounding-same` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `rounding-different` | 0 | 0 | agree | `[0, 0, 0]` | 0.0 |
| `wrong-text` | 0 | 0 | agree | `[0, 0, 0]` | 0.0 |
| `blank-empty` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `case-sensitive` | 0 | 0 | agree | `[0, 0, 0]` | 0.0 |
| `datetime-serial` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `time-minute` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `style-ignored` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `first-sheet-default` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `multi-range-wrong` | 0 | 0 | agree | `[0, 0, 0]` | 0.0 |
| `missing-result-sheet` | 0 | 0 | agree | `[0, 0, 0]` | 0.0 |
| `invalid-gold-sheet` | KeyError | KeyError | nonnumeric boundary | `[0, 0, 0]` | unmeasured (exit 3; no reward) |
| `malformed-column-only-range` | ValueError | 0 | nonnumeric boundary | `[0, 0, 0]` | 0.0 |
| `reversed-empty-range` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `missing-artifact` | 0 | FileNotFoundError | nonnumeric boundary | `[0, 0, 0]` | 0.0 |
| `corrupt-artifact` | 0 | RuntimeError | nonnumeric boundary | `[0, 0, 0]` | unmeasured (exit 3; no reward) |
| `uncached-formula` | 0 | 0 | agree | `[0, 0, 0]` | unmeasured (exit 3; no reward) |

Raw tuple returns, printed output, exception messages and tracebacks are preserved in `official.json` / `local.json`; raw local evidence and its actual main arguments are in `local-main.json`. `comparison.json` contains joined per-input outcomes and machine-derived counts.

## Measured findings and remaining limits

- `malformed-column-only-range`: upstream direct `compare_workbooks` raises `ValueError: invalid literal for int() with base 10: ''`; local direct comparator returns false with its explicit official-equivalent-range-zero message. The actual upstream CLI catches the exception and emits `[0,0,0]`; local main produces measured zero. This is a caller-level compatibility result, not evidence that any cells were compared.
- `invalid-gold-sheet`: both direct comparators raise `KeyError: 'Worksheet Other does not exist.'`; upstream CLI swallows it into `[0,0,0]`, while local main records `measured:false`, exit 3 and no reward. This classification difference remains explicit.
- `missing-artifact`: official direct returns false (`File not exist`); local direct raises `FileNotFoundError`. The actual full callers both record zero for the absent authored result artifact.
- `corrupt-artifact`: official direct returns false (`File is not a zip file`); local direct raises `RuntimeError`. Official CLI produces `[0,0,0]`, while the local full check fails formula detection, records `measured:false`, exit 3 and no reward. This is not a numeric agreement.
- `uncached-formula`: both direct data-only comparators see `None` and return false. Upstream CLI also emits `[0,0,0]`; it does not recalculate workbooks. Local main attempts the documented installed LibreOffice path and fails under this strict no-socket profile: `LibreOffice exited 1: Warning: failed to launch javaldx - java may not function correctly` followed by `ERROR 4 forking process`. Its raw evidence has `recalculated:false`, `measured:false`, exit 3 and no reward. This initial profile does not establish production failure; the local-IPC retry below resolves the bounded offline conversion question. Upstream `evaluation/open_spreadsheet.py` was not available in this packet and was **not executed**. Official formula-recalculation workflow evidence remains uncovered.
- `reversed-empty-range`: both complete comparators and full callers accept the reversed range despite different authored A1 values, because it enumerates no cells. This observed vacuous pass is reported, not presented as semantic correctness.
- Compared return **booleans** agree for numeric controls. Diagnostic message strings differ (upstream often returns an empty string; local retains a mismatch reason); the comparison does not claim message-byte equality. Style changes are ignored by both scorers, matching the commented-out upstream fill/font checks. The actual data-only workbook read and the authored rounding, numeric-string, datetime, time, sheet and multi-range paths all ran.

## Separate formula retry with offline local IPC

The exact same authored `uncached-formula` input was copied fresh and passed through unchanged local `main` under a fresh **network namespace**, allowing LibreOffice's local UNIX IPC. This bounded retry is separate from, and does not overwrite, the strict deny-all-sockets failure above. Exact command:

```sh
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=
export HG_WOFFSCORER2_HOST_NETNS
HG_WOFFSCORER2_HOST_NETNS=$(readlink /proc/self/ns/net)
timeout 150s bwrap --unshare-net --die-with-parent --ro-bind / / --bind /tmp /tmp --proc /proc --dev /dev python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/formula_netns_guard.py > tests/fixtures/hg_woffscorer2/spreadsheetbench/local-formula-netns.json 2> tests/fixtures/hg_woffscorer2/spreadsheetbench/local-formula-netns.offline.txt
```

`formula-netns-command.sh` retains this command. The receipt records distinct host/scorer network namespaces, only loopback in `/proc/net/dev`, no IPv4 routes, IPv6 routes on loopback only, bwrap/interpreter hashes and the same CPU/FD limits. No network interface connects it to the host network. A dataset-payload-read audit found no attempted external payload read. This is a different isolation profile from denying all socket syscalls; local IPC is allowed. It remains a controlled fixture, not production runtime custody.

Measured result: **1 numeric workflow comparison; 0 agreements, 1 divergence**. Actual official data-only comparator/CLI result is **0** on the uncached `=1+2` workbook; local full check now returns **1**, exit **0**, `recalculated:true`, `measured:true`. Its actual LibreOffice subprocess argv is captured by a read-only Python audit observer in `local-formula-netns.json`; the converted workbook bytes are retained in `formula-recalculated.xlsx` with a recomputed digest in that output. The original common input workbook is unchanged. This comparison measures **recalculation workflow policy**, not divergence in `compare_cell_value` or a successful upstream `open_spreadsheet.py` execution. `comparison.json:formula_netns_profile` retains the separate counts.

Coverage supplied by this fragment is **SpreadsheetBench only**, bounded to its exact official evaluation module/CLI controls. It does not establish original three-variant dataset release provenance, complete transitive dependencies, the complete upstream formula-opening workflow, platform-selected gold export or trusted actor runtime isolation. Other datasets are outside this fragment. S1, S3, S4 and S6 remain partial; neither the shared blocker nor a dataset blocker is closed.

Validation: `reports/w-offscorer2-spreadsheet-validation.txt` retains fixture validation, SHA-256 verification and blocker-checker output. The upstream source preserves its original trailing whitespace to remain byte-identical; diff whitespace validation excludes only that copied upstream file.
