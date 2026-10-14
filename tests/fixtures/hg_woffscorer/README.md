# Bounded official scorer execution — w-offscorer

All paths in component reports are relative to this directory unless stated otherwise.
These fixtures score authored synthetic inputs only. They are not task trials, model
outputs, benchmark accuracy estimates, production isolation observations or pilot
admission. Historical runs and frozen archives are outside this packet and untouched.

The complete report is `reports/w-offscorer-equivalence.md`. Raw official and actual
local return values, per-input comparison files, source identities and exact commands
are retained in the `fever/`, `bigbench/`, `numeric_boolean/` and `public_qa/` subdirectories.
Complete upstream module/evaluator execution and selected unchanged upstream function
execution are explicitly distinguished. Different output channels, gold projections,
rounding/scaling, auxiliary metrics and upstream exceptions remain visible.

`offline_exec.py` installs a kernel seccomp filter denying socket APIs and io_uring_setup
before any scorer imports. IPv4, IPv6 and UNIX socket creation are actively probed and
must fail with EPERM; there is no weaker fallback. Each scorer invocation records the
actual Python and libseccomp paths/digests, CPU/fd limits and `production_runtime_observation:
false`. The outer command adds a wall timeout. No endpoint or model is involved.

Its supplemental Python audit hook blocks Python-level external dataset file reads;
it cannot intercept native extension opens such as PyArrow. Affected corrected local
imports temporarily refuse QASpec row construction or parquet row loading, restore
those fixture-only changes immediately, assert empty adapter record caches, and call
the original scorer functions. Initial import attempts that did not establish payload
exclusion are retained and disclosed in their component reports; they did not execute
benchmark tasks. This mechanism is not a production filesystem or verifier gate.

`local-source-pins.json` freshly hashes unchanged adapter/scaffold bytes at the recorded
baseline. Acquired official source copies are also hashed and their acquisition/Git blob
or archive identities checked by component verifiers. Those local pins do not provide
portable dependency payloads or complete image/ABI closure.

`SHA256SUMS` covers every file below this directory except itself and regenerable Python
bytecode. Nested manifests are included. To refresh after an intentional evidence edit:

```sh
python3 tests/fixtures/hg_woffscorer/refresh_manifest.py
```

Final integrity/scope and source-only registry checks are documented with their exact
commands and raw results in `reports/w-offscorer-validation.txt`. No shared blocker or
dataset blocker is closed by these controls.
