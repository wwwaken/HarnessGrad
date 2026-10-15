# w-mkl evidence packet

See `reports/w-mkl-payloads.md` for source witnesses, checked indexes, exact scope and coverage. `SHA256SUMS` covers this fixture's artifacts, raw HTTP bodies/headers, commands, failures and network-denied receipts.

The 14 exact Conda packages in `artifacts/` are installed; the PyPI 2.4.2 service wheel is an inspected alternative only. `quarantine/` retains two incomplete downloads, excluded from installation. The earlier Python wheelhouse remains a separate prerequisite, identified and freshly rehashed in `reused-artifacts.json`; this is an extension packet, not a standalone Python/runtime bundle.

`acquire.py` and `supplement.py` preserve initial acquisition failures. `accept_retry.py` and `accept_support_retry.py` accept the complete digest-verified API retries. Every HTTP acquisition's exact command is in `index/*.receipt.json`. Never overwrite these historical receipts when repeating acquisition: use a new packet directory.

`offline.py` reproduces the corrected fresh-prefix install/import procedure under `unshare -Urn` (base Python and Conda required). The recorded install attempt's initial probe mistakes are preserved; `retry_imports.py` corrected only observation code and re-imported the same fresh installed prefixes. `offline-summary.json` is the original attempt; **`final-summary.json` is authoritative for final imports**. All imported MKL libraries are required to originate inside their installed prefix. DS-1000 import exit 1 is expected for the preserved non-MKL failures; it is not a score.

Run `python3 tests/fixtures/hg_wmkl/validate.py` then `sha256sum --check tests/fixtures/hg_wmkl/SHA256SUMS` from the repository root. Validation recomputes new and reused artifacts, parses published Conda metadata, checks final imports/source hashes/provider origins/network denial and regenerates the manifest. No scorer/task/model operation is performed.
