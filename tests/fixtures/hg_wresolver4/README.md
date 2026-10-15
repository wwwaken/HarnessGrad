# w-resolver4 evidence packet

Gaia and AppWorld extend w-resolver3 to **13/13 bounded profiles and 12/23 complete nonempty dataset Python metadata profiles**. No shared/dataset blocker or production gate is closed.

- `selection.json`, `source-audit.json`, `source/`, `source-audit.stdout.txt`: source-derived roots, exact citations/preimages, observed-version policy and bounds.
- `inputs-gaia.json`, `inputs-appworld.json`, `target-*.json`, `observed-gaia.json`: exact candidates, recomputed hashes, target tags and metadata.
- `index/`, `index-appworld/`, `metadata/`, `metadata-appworld/`: actual versioned index/HTTP bodies and wheel members. AppWorld wheel-only candidate discovery command/output is in `raw/`.
- `payloads/`, `retained-targets.json`: all bytes new to the committed corpus and explicit prior committed byte locations for the remaining candidates. Both complete graphs are available from that union; temporary acquisition copies are also retained and independently hashed.
- `profiles/`, `results-complete.json`, `raw/`: real dependency-aware network-denied pip resolves, hash locks/installations, checks and mandatory-wheel refusals. Network/runtime/venv/cleanup receipts are retained.
- `probe-appworld.stderr.txt`, `bootstrap-diagnostic*`, `raw/appworld-ensurepip-diagnostic.*`, `raw/appworld-tooling-packaging-check.*`: exact first bootstrap and auxiliary-tool failures. `probe-appworld-retry*` uses a distinct fresh symlink venv and capture labels; no old run is resumed. The first attempt pre-resolution runtime was overwritten by a new in-session label collision and is unavailable; `capture-recovery.json` discloses the loss and verbatim recovery of network/cleanup from retained original tool stdout. Successful retry receipts are complete and moved byte-identically to distinct labels.
- `appworld-wheel-source/`, `installer-audit.json`, `installer-audit.stdout.txt`: exact shipped installer/decrypt source and static bundled-application import audit. No AppWorld module/CLI, package-tests bundle or task payload is executed/read.
- `remainder-audit.json` and `.stdout.txt`: fresh embedded source preimages, exact citations, independent hashes and each remaining gap. Generator source is embedded in the JSON.
- `coverage.py`, `summary.json`, `dataset-coverage.json`: arithmetic from completed captures and explicit inherited evidence. No N/A empty solve is counted.
- `registry-before.json`, `observation.txt`: additive observation only; statuses/actions/references/history/gates unchanged.

Read the report at `reports/w-resolver4-payloads.md` and validation transcript at `reports/w-resolver4-validation.txt`.

Read-only verification: `python3 tests/fixtures/hg_wresolver4/validate.py`. Acquisition/probe scripts deliberately refuse existing evidence captures; do not rerun them in place. Packet sealing is SHA256SUMS; no run/receipt is edited, no existing run ID resumed, no task/scorer/container/model/GPU/endpoint executed.
