# Jericho and ScienceWorld bounded upstream execution - w-offscorer2-worlds

**S4 gains bounded installed-upstream execution evidence for Jericho and ScienceWorld. The shared blocker remains open; no dataset blocker is closed.**

This packet lives under `tests/fixtures/hg_woffscorer2/worlds/`. It confirms the topology survey's native actor-workdir routes: Jericho's verifier rebuilds Frotz and replays action strings, and ScienceWorld's verifier rebuilds the JVM world and replays action strings. The official side imports each complete, unchanged installed upstream package and directly calls its runtime APIs. The local side imports the unchanged production `verify/check.py` and calls `main(argv)` on separate fresh worlds. It is not two local-verifier calls labelled official.

## Commands and offline boundary

Exact replay from the repository root:

```bash
bash -x tests/fixtures/hg_woffscorer2/worlds/commands.sh > tests/fixtures/hg_woffscorer2/worlds/commands-output.txt 2> tests/fixtures/hg_woffscorer2/worlds/commands-exact.txt
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer2/worlds/verify.py > tests/fixtures/hg_woffscorer2/worlds/verification.json
python3 tools/check_dataset_blockers.py
```

`commands-exact.txt` retains the actual expanded timeout/env/bwrap/interpreter/script invocations, including the fresh scratch root. Official and local raw returns are `jericho-official.json`, `jericho-local.json`, `scienceworld-official.json` and `scienceworld-local.json`; `comparison.json` retains per-input results and counts. Inputs are `inputs.json`; all SHA-256 values are freshly recomputed by `prepare.py` and checked by `verify.py`, not copied from historical manifests.

Jericho uses the existing `tests/fixtures/hg_wverify/scorers/offline_exec.py` kernel seccomp guard. It denies all sockets and io_uring_setup, closes inherited socket descriptors, probes IPv4/IPv6/UNIX denial, and keeps complete guard receipts in `jericho-*-offline.txt`. The selected ROM is copied before scoring so external dataset payload reads are unnecessary.

ScienceWorld requires Python/JVM loopback IPC. Its exact `bwrap --unshare-net` commands establish a fresh network namespace with only `lo`, no IPv4 routes, and no inherited socket descriptors; `namespace_exec.py` checks a different namespace from the parent and records external-connect ENETUNREACH. The JVM stays inside that namespace. This is offline execution with local IPC, **not socketless execution**. Full device/route observations are preserved in `scienceworld-*-offline.txt`. Root mounts are read-only, with private writable `/tmp` and a fresh external scratch root. No model, GPU, endpoint or task runner executes.

Each dataset/mode command has a wall timeout and CPU/file-descriptor limits recorded in receipts. Cases execute sequentially, one fresh world per case per side. `execution-scope.json` records counts and bounds. This is a controlled scorer packet, not a pilot, eligible-task census, benchmark accuracy measurement, or production-runtime custody observation. No released evaluation task is played: selected Jericho `acorncourt` is outside the declared hash-eval split; ScienceWorld variation zero is absent from the checked-in canonical `task-3-find-non-living-thing` test-fold entries. The ScienceWorld full world uses no simplifications and never generates a gold path.

## Installed upstream identity and provenance limits

The identity pins are installed distribution versions plus freshly hashed installed Python/native/JAR bytes and package METADATA/WHEEL/RECORD. `identities.json` preserves absolute paths, sizes and every digest, alongside byte-identical Python source copies under `official-source/`. This does **not** authenticate a public source commit, independently validate wheel acquisition, or infer an upstream Git revision; `upstream_git_revision` is null. Jericho's reference-bearing `game_info.py` is hashed but deliberately not copied wholesale. Complete package imports read the installed package metadata in a trusted fixture process; this is not a selected-only production filesystem-isolation claim.

| Component | Identity | Recomputed SHA-256 |
| --- | --- | --- |
| `jericho/jericho.py` | installed `jericho==3.3.1` | `94f2e745cfd96deffaa95f7ea24b6be34a6ef29a2bc5c4b2bce891c1315353f8` |
| `jericho/libfrotz.so` | installed `jericho==3.3.1` | `1ade244682f43e1695489b22288e894a1d8b497c9785a7190991d7626e3996e0` |
| `scienceworld/scienceworld.py` | installed `scienceworld==1.2.3` | `23a37a2e9ed8e43d8c5e27d8660ea344d38a544abcd8c7e6af40071c7832ce68` |
| `scienceworld/scienceworld.jar` | installed `scienceworld==1.2.3` | `f4e1fdce0cdabe1bab7128a7e78ea820210d9db3c28d7272bcbbc3f3a1c5f0d7` |
| JRE `java` | staged Temurin release bytes, see `identities.json` | `f5aed21d3a0b0f4b05d3a3f9fe71263916d5bc0d47b53aa52a3340b90f0b4805` |
| JRE `libjvm.so` | staged Temurin release bytes, see `identities.json` | `11e5d09f442e42bddc4619b6eed829eaf3952158a5f77c797a58d558fae21738` |
| JRE `release` | staged Temurin release bytes, see `identities.json` | `a23a26314d44357bfbcee8358e63ffc117c42e6b6580bb0d27ccfef2c5d53983` |
| study ROM `acorncourt.z5` | selected local BYU-PCCL suite bytes | `7b13c904bf7608fa0de902ce7ecd5fcd0e026f293fc67baa87b99a35a3190c9e` |

The actual ScienceWorld JAR manifest is preserved verbatim in `identities.json`, including implementation/specification version. Its scoring code is the local installed JAR, not a fixture substitute. Local check/library hashes are in that same identity file and remain unchanged.

## Per-input measured results

Jericho upstream calls are `FrotzEnv(rom, seed=4)`, `reset()`, `get_max_score()`, `get_score()` and `step(action)`. Its maximum is a native return. The empty trace score is read by actual `get_score()`, not supplied by the verifier's empty-log initialization. ScienceWorld upstream calls are `ScienceWorldEnv('', None, envStepLimit=8)`, `load(..., generateGoldPath=False)`, `server.getScore()` and `step(action)`. ScienceWorld's 100-point scale is the unchanged upstream wrapper's `int(round(100 * getScore()))` unit convention, not an independently queried maximum. Empty traces read actual JVM `getScore()`; nonempty traces retain complete upstream `info` values and observations. Fractions are transparent unit conversions of those actual returns, compared to local reward.

The four authored Jericho traces are kept distinct from the positive, reference-derived study control. `acquire_study_reference.py` calls upstream `get_walkthrough()` only for selected non-heldout `acorncourt`; its exact returned actions and seed are `reference-selection.json`, and raw kernel-offline acquisition output is retained. This is a labelled study oracle control, not an authored trace or an accuracy measurement.

| Dataset/input | Official score | Scale/maximum | Official fraction | Local score/reward | Agreement |
| --- | ---: | ---: | ---: | --- | --- |
| `jericho/j-empty` | 0 | 30 | 0.0 | 0 / 0.0 | True |
| `jericho/j-look` | 0 | 30 | 0.0 | 0 / 0.0 | True |
| `jericho/j-impossible-command` | 0 | 30 | 0.0 | 0 / 0.0 | True |
| `jericho/j-get-ball` | 0 | 30 | 0.0 | 0 / 0.0 | True |
| `jericho/j-study-reference-full` | 30 | 30 | 1.0 | 30 / 1.0 | True |
| `scienceworld/s-empty` | 0 | 100 | 0.0 | 0 / 0.0 | True |
| `scienceworld/s-look` | 0 | 100 | 0.0 | 0 / 0.0 | True |
| `scienceworld/s-impossible-command` | 0 | 100 | 0.0 | 0 / 0.0 | True |
| `scienceworld/s-focus` | 0 | 100 | 0.0 | 0 / 0.0 | True |

`jericho`: **5 measured input comparisons, 5 agreements, 0 divergences, 0 unmeasured** in the final packet.

`scienceworld`: **4 measured input comparisons, 4 agreements, 0 divergences, 0 unmeasured** in the final packet.

Jericho's study positive control reaches the actual native maximum; raw per-step awards remain preserved. ScienceWorld controls all return zero and establish only fresh-world zero-score/invalid-action replay, not successful-task or positive-score execution. Neither sample establishes general scorer equivalence or coverage of other games/tasks.

## Preserved failures and corrected fixture mistakes

`preserved-first-attempt/` keeps the original inputs, scripts, identity, expanded commands and raw outputs. All four direct upstream ScienceWorld cases raised `FileNotFoundError: [Errno 2] No such file or directory: 'java'`: the fixture set JAVA_HOME but py4j's launch path also needed PATH to contain the JRE bin directory. The unchanged local helper already sets both, so its four first-attempt calls measured zero. Four ignored upstream destructor `AttributeError`s about absent `_gateway` are preserved in the same stderr. These are import/launch failures, not scores. The fixture-only PATH correction produced the later genuine JVM results; no production source changed.

The first-attempt fixture also assigned zero to empty official traces rather than querying upstream state. That was a fixture error and its apparent empty-trace agreement is not used as official evidence. Later execution reads native/JVM state explicitly; `preserved-second-attempt/` retains that corrected initial packet before the labelled study-positive control was added. Historical outputs are never smoothed into final scores.

## Cleanup and remaining scope

Official ScienceWorld child processes are closed and awaited; per-case termination/return-code observations are in `scienceworld-official-offline.txt`. The unchanged local verifier closes its world; local `child_cleanup` records and post-execution selected-child `/proc` observations are in `scienceworld-local.json` and `verification.json`. `cleanup.json` records removal of the final fresh scratch root. This bounded fixture cleanup evidence does not establish production snapshot ownership or trusted lifecycle closure.

Covered here: installed upstream Jericho and ScienceWorld scoring-runtime execution on the exact listed traces. This packet alone supplies no new execution evidence for ALFWorld, AppWorld, BFCL, BIRD, ChessBench, DS1000, GAIA, LiveCodeBench, Reasoning Gym, SpreadsheetBench, Tau-Bench or Terminal-Bench. Parent integration may incorporate separate packets. S1, S3, S4 and S6 remain partial, and no blocker or gate is closed.
