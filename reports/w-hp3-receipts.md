# Jericho and ALFWorld sealed native closure receipts - w-hp3

The next tractable routes are Jericho's Frotz replay and ALFWorld's synchronous TextWorld `.tw-pddl` replay. Both now use the existing BIRD sealed-memfd/private-root mechanism, with independent literal admission pins and closure identity in verdicts. Bounded pinned native userland coverage advances from **1/7 to 3/7**. This is a mechanism/control result, not production dataset coverage, a pristine conversion, or permission for a diagnostic/pilot. No shared or dataset blocker closes.

## Concrete closures and measured loads

All paths below the evidence packet are relative to `tests/fixtures/hg_whp3/`. `facts.json` is derived from the retained raw commands; every digest in each manifest was independently recomputed with `/usr/bin/sha256sum`, with stdout, stderr, argv and status preserved in the capture's `commands/` and `invocations.json`. The final manifests also have byte-identical capture copies. Older unsuccessful captures remain separate.

| Route | Manifest SHA-256 | Admitted destinations / ELF / unique payload digests / bytes | Actual check ELF destinations, including interpreter/loader |
| --- | --- | --- | --- |
| Jericho | `dfd1979e4c42c582ab7680438fd24002a9c329e258bec92096287bdd9243cff7` | 1,292 / 193 / 1,261 / 1,354,615,752 | 57 across 2 launches |
| ALFWorld | `8bf87ee279e407b7a5eda8b2dc5ee85ad297d04bbc29ddf496338a4adeebd6dc` | 2,581 / 198 / 2,481 / 1,403,419,949 | 78 across 3 launches |

The independently configured pins are in `data/runtimes/__init__.py:4` and `:9`; manifests are `data/runtimes/alfworld-native.json` and `data/runtimes/jericho-native.json`. The respective final captures are `alfworld-locale-capture/` and `jericho-final-capture/`. `final-manifest-hashes.stdout.txt` also confirms BIRD's unchanged manifest digest `bc6f725f5ed371060e8f28f53fe69e339d65f18d97dae2ecc7000d3a4e07fb08`.

| Shared identity | Freshly observed value |
| --- | --- |
| Interpreter | `/mnt/8t/xubuqiang/anaconda3/bin/python3.12`; CPython 3.12.4; SOABI `cpython-312-x86_64-linux-gnu` |
| Interpreter SHA-256 | `0eb25a387ef43f21492b659f4865eae5bdaf8da30d6357097b2d9bb24873ebfb` |
| libc | `/lib/x86_64-linux-gnu/libc.so.6`; `b2cf6c33b74d2f22543b7a469a75b538911e690f769d0b238843a49465b83793` |
| Loader | `/lib64/ld-linux-x86-64.so.2`; `41daf7836f7fce21a40ca63a00c5caf21b05a35a76ccc075d86f1716212cdf01` |
| Package versions | Jericho 3.3.1; NumPy 1.26.4; mkl-service 2.4.0; ALFWorld 0.4.2; TextWorld 1.7.0; fast-downward-textworld 20.6.4 |
| Host envelope | Kernel `6.8.0-136-generic`, `x86_64`; full interpreter build and CPU/limits in `versions.stdout.txt` and `resource-envelope.stdout.txt` |

The closure includes the interpreter and child alias, stdlib source/extensions, selected package/resource supersets, recursively resolved ELF providers, MKL/OpenMP/TBB dispatch providers, and trusted scorer/helpers under `/scorer`. The ALFWorld closure additionally contains the configured C.UTF-8 locale files needed by this readline build. No ambient host directory supplies missing dependencies.

The complete per-file inventories are [jericho-closure-files.md](../tests/fixtures/hg_whp3/jericho-closure-files.md) and [alfworld-closure-files.md](../tests/fixtures/hg_whp3/alfworld-closure-files.md). Each destination has a freshly recomputed digest, source, scoring entry, and raw independent hash citation. These inventories are conservative admitted supersets: they do not assert that every package or provider executes.

Every actual check ELF has its digest, entry file/line and trace line in [jericho-actual-native.md](../tests/fixtures/hg_whp3/jericho-actual-native.md) and [alfworld-actual-native.md](../tests/fixtures/hg_whp3/alfworld-actual-native.md). Python entry citations identify the importer/ctypes load; transitive providers cite the loaded parent's numbered `readelf` DT_NEEDED/PT_INTERP record. `source-sites.json` and `source/` preserve source preimages, numbered lines and independent hashes. The actual trace is `bound-replay-final.strace.txt`; machine-readable subsets are `*-scorer-loads.json`.

Jericho enters at `data/datasets/jericho.py:257` (Python/check argv), `:278` (pin), `data/datasets/jericho/verify/check.py:46` / `:48` (bound helper and trusted `jer_env`), `:122` (bound game load), and `data/datasets/jericho/lib/jer_env.py:38` (`FrotzEnv`). Installed `jericho/jericho.py:223` loads a temporary copy of `libfrotz.so` through ctypes; its digest is linked to the admitted package object, not inferred from its random temporary filename.

ALFWorld enters at `data/datasets/alfworld.py:347` (Python/check argv), `:365` (pin), `data/datasets/alfworld/verify/check.py:63` / `:65` (bound helper and trusted `gym_env`), `:169` (replay), and `data/datasets/alfworld/lib/gym_env.py:67` / `:76` (TextWorld and `asynchronous=False`). Installed `fast_downward/interface.py:107` loads the copied `libdownward.so` through ctypes. Inform7 compilation and Glulx tools in TextWorld's optional `thirdparty` tree are excluded from this synchronous `.tw-pddl` route.

Both actual checks execute their native engines in-process; neither trace shows a scorer child executable. A separate authored inherited-child control replays through the same libraries in a Python parent and child. [jericho-control-native.md](../tests/fixtures/hg_whp3/jericho-control-native.md) enumerates 59 parent / 57 child ELF destinations; [alfworld-control-native.md](../tests/fixtures/hg_whp3/alfworld-control-native.md) enumerates 78 / 78. Each has independent digests, entry citations and raw map references; `*-control-loads.json` retains the audit-time copied-library hashes. The extra Jericho parent subprocess imports belong to this control, not the check.

Collection-time `ldd` is evidence, not the final resolution authority. For example, standalone `ldd` for FastDownward selected system libstdc++; the actual sealed check mapped Conda's `/mnt/8t/xubuqiang/anaconda3/lib/libstdc++.so.6`, digest `4f045231ff3a95c2fbfde450575f0ef45d23e95be15193c8729b521fc363ece4`. The inventory links that actual provider to the loaded parent's DT_NEEDED at `alfworld-locale-capture/commands/0202.stdout.txt:36` and actual map at `bound-replay-final.strace.txt:21975`. Both captured candidate providers are sealed; actual mappings define the measured subset.

## Reuse, admission and refusal

There is one implementation in `eval/verification/native_runtime.py`. Hashing while copying, kernel seals (`:51`), read-only descriptor mounts (`:82`), empty root, explicit loader/cache policy, private temporary storage and descriptor cleanup are BIRD's existing mechanism. The changes add an explicit dataset allowlist, the selected dataset in the receipt, digest-bound package-path bootstrap, descriptor rewind for repeated execution, and executable permissions only on ELF payloads. Python/data mounts remain read-only. Omitting unnecessary permission arguments keeps the larger ALFWorld mount plan within bubblewrap's argument limit.

Python still runs with `-I -S -B`; only `/scorer` and the sealed package root are explicitly added. Helpers resolve beside trusted check code, not actor cwd. The inherited-child control explicitly bootstraps the same package paths; plain isolated Python children otherwise have stdlib defaults in the same closed namespace. Host PYTHONPATH/LD_PRELOAD/LD_LIBRARY_PATH, actor helper/package shadows, and loader caches cannot supply code. The control also checks that scorer code cannot be overwritten.

`eval/verification/verifier.py:474` retains sandbox admission, `:478` retains files/check/topology/output/isolation restrictions, `:487` admits the closure, and `:635` dispatches the existing check through it. Unsupported routes and manifest/payload/input mismatches remain refused with an unmeasured null score and no ambient retry. All scorer-input/WAL rules remain. Successful verdicts carry the admitted identity via the existing verdict preservation path. No gate, eligibility, pristine declaration, quota or production authorization changes.

`tools/build_bird_native_runtime.py` is extended with `--dataset`; default remains BIRD. It collects packages/resources and ELF/dlopen supersets using the same capture mechanism. It is a provisioning tool, never an automatic expected-pin update. Content-addressed archives remain at `/tmp/hg-hp3-store/<manifest-sha256>.tar.gz`; their exact paths, freshly computed archive hashes and commands are in `facts.json` and each final capture. They are retained local payloads, not publisher-authenticated distributions. Runtime still hashes manifest source snapshots and refuses absent/changed sources; archive restoration requires explicit provisioning.

ScienceWorld is deliberately outside this extension: `eval/verification/native_runtime.py:21` restricts the admitted datasets, and `:85` through `:101` constructs the Python interpreter/flags/bootstrap command. The files/check admission at `eval/verification/verifier.py:485` is also explicit. A JVM extension needs a separately captured Java launch/provider/classpath contract and measured Java-child lifecycle; these Python replay controls cannot establish it.

## Controls, failures and practical limits

The first four new regressions fail on the original implementation (`pytest-before.stdout.txt`: **4 failed**). The final focused suite is **124 passed** (`pytest-targeted.*`), including 11 new closure tests plus existing BIRD/verifier/WAL/blocker/Jericho admission controls. A separate syscall-traced pass reports **4 passed, 7 deselected** (`trace-bound-final.*`). The exact argv and exit status are preserved for each invocation. No timeout was increased.

Jericho uses an authored unsupported Z-machine ROM: two actions replay through Frotz, max_score is zero and the existing measured-zero behavior is preserved. This proves native replay and binding, not positive scoring compatibility for a supported released game. ALFWorld uses an authored ready-to-done PDDL game: an invalid action remains a no-op, `finish` satisfies the goal, and an empty action log scores zero through the unchanged helper/check. Mutating each bound input is refused. The standalone PDDL probe and its relocation check are retained separately. Neither control uses benchmark questions, released task/reference data or model output.

Earlier failures are retained, including the optional static Inform tool `ldd` failure, oversized bubblewrap argv, the unsuccessful `/proc/self/fd` mount experiment, readline SIGSEGV, initial broad tracing timeout, and derivation locator/count errors. `readline-debug-native.stdout.txt` and `readline-disassembly.stdout.txt` trace the locale failure to `_rl_init_locale` calling `strlen(NULL)` after failed locale setup. A diagnostic changed the locale only to isolate the cause; the final closure instead seals the configured C.UTF-8 data and keeps the original locale. The final trace narrows observation to execve/mmap with seccomp acceleration under the unchanged bounds. Failed outputs are neither overwritten nor counted as passing.

These are serial, no-model authored controls, without benchmark eligible/selected/task/trial coverage, production metric, selected manifest or run ID. No endpoint was called or model server started. Tests use external `/tmp` basetemps and bounded subprocess timeouts. The inherited AS/CPU/file-size limits are unlimited; NOFILE is 1048576 (`resource-envelope.stdout.txt`). Capturing payload sizes does not establish quota enforcement. Kernel/vDSO, CPU features and the platform/bubblewrap pre-namespace launch trust remain outside the scorer file-closure claim; kernel/machine admission is unchanged. Native closure does not establish artifact-only export, private selected-only inputs, full provenance, pristine scoring or production cleanup. Repository `runs/` and frozen receipts are untouched. Final integrity/cleanup observations and commands are recorded in `reports/w-hp3-validation.txt`.

## Remaining work across the seven host surfaces

| Dataset | Native scope now | Remaining work |
| --- | --- | --- |
| bird_minidev | Pinned EX/stdlib-SQLite host route; unchanged | Shared/dataset gates, production evidence, resource/export/provenance and broader compatibility obligations remain. |
| jericho | Pinned synchronous Frotz host replay | Supported-game positive scoring compatibility remains unmeasured here; optional tokenizer/model paths, full resource/production/export/provenance obligations remain outside this control. |
| alfworld | Pinned synchronous TextWorld `.tw-pddl` host replay | Released-game compatibility remains unmeasured here; compilation/Glulx/async paths and production/resource/export/provenance obligations remain outside this control. |
| scienceworld | Unpinned | Seal exact JRE interpreter/loader/native providers, Python/Py4J/JAR/classpath, Java child resolution and lifecycle; the current Python command bootstrap does not itself launch a JVM. |
| ds1000 | Unpinned | Define candidate-visible scientific/native stacks and child executables, seal resolution, bind actual scorer execution and refuse unavailable providers. |
| spreadsheetbench | Unpinned | Seal LibreOffice binaries/children, modules/plugins/codecs, fonts/configuration and Python workbook stack; bind the actual scorer. |
| chessbench_puzzles | Unpinned | Seal interpreter/stdlib/python-chess/trusted QA scorer and package resolution, then bind and trace the actual check. |

## Exact registry observation - w-hp3

Jericho and ALFWorld native closure 2026-10-15 - w-hp3: bounded pinned native userland coverage is 3/7, adding synchronous Jericho Frotz replay and ALFWorld TextWorld tw-pddl replay to BIRD through the same digest-verified sealed-memfd/private-root mechanism. Independent literal pins admit 1292/2581 file destinations, with 57/78 actual check ELF destinations including interpreter/loader on authored controls; separate inherited-child maps and copied-ctypes digests are retained. Manifest/payload/input mismatch still refuses without ambient fallback. This establishes neither released-game compatibility nor production execution, pristine/export/quota/provenance closure, JVM or remaining native surfaces. All shared/dataset blocker statuses, full next_actions, dataset/history records, gates and production_authorized=false remain unchanged.
