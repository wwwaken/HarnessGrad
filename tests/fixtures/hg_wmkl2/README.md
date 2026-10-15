# w-mkl2 DS-1000 import evidence

Read `reports/w-mkl2-ds1000.md` for scope and findings. No scorer/task/model/GPU/endpoint execution is part of this packet.

- `source-audit.*`, `source/`, `context-flow-sites.json`, `host.json`: raw static import/exclusion evidence, source digests/numbered files and absent host package metadata.
- `offline/host-original-pair.*`, `offline/fresh-original-pair.*`: original exact-version failure, before repair; `reproduce.py` contains only metadata capture and `import gensim`.
- `acquire/`, `acquisition.json`, `existing-pins.constraints.txt`: public acquisition and pin retention. `selected-wheel-metadata.json`, `metadata/`, `offline/plan.json` show actual selected wheel metadata.
- `offline/network.json`, `offline/retry-network.json`: kernel namespace network denial. Local installs are in `offline/*install.*`; negative controls cannot import the three missing roots.
- Final success: `offline/retry-completed-imports.*`, `offline/exact-named-imports.*`, `offline/installed-distributions.*`, `result.json`. Exact import statements and selected scientific dependency checks run without constructing models or executing contexts.
- Earlier failures are intentionally retained: `offline-launch.*` (collector directory error), `offline-launch-retry.*` and initial module probe (incorrect skip set). `initial-additions.lock` records the first install; `additions.lock` plus `retry.py` supply the corrected dependencies. The final `offline.py` also contains the corrected selection for replay in a new prefix.
- `reused-and-downloaded-artifacts.json` and `EXTERNAL_SHA256SUMS`: all retained external/reused candidate bytes, including unused alternatives. The new wheels are external, not bundled into this commit; replays require the exact retained files. Base interpreter/stdlib/OS ABI also remain prerequisites.
- `coverage.json`: derived installation inventory; no broader completeness/readiness claim.
- `validate.py`, `review_scope.py`, `SHA256SUMS`: packet consistency, unchanged registry/dataset/gate scope and committed-fixture integrity. `reports/w-mkl2-validation.txt` preserves actual final check commands/output.

For a new independent install/import replay, run the acquisition scripts only if payloads must be obtained, then `unshare -Urn python3 tests/fixtures/hg_wmkl2/offline.py` with a *new evidence output directory*: do not overwrite this packet's historical raw files. No existing benchmark run is resumed. The installed prefix/cache and payloads are intentionally retained for review.
