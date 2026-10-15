# hg_wuvx — bounded OpenSSL verifier bootstrap payload

One fresh `openssl-selfsigned-cert` tooling resolution and network-denied replay; no task tests or scoring. See `reports/w-uvx-bootstrap.md` for exact scope and all raw-output paths.

- `source/`: 89 local verifier scripts and Dockerfiles, source comparison and invocation index.
- `artifacts/`: six resolved wheels, 19 apt .debs, uv 0.9.5 installer/archive, hash lock and artifact SHA256SUMS. Requires the separately cached image ID in the report.
- `raw/`: exact Docker/curl argv, output, exit/cleanup records, first-attempt failure, online/offline Python ABI and package inventories.
- `scripts/`: collectors and evidence checks; `collect.py` performs bounded network access, `offline.py` uses Docker network=none. These are evidence tooling, not production adapters.
- `SHA256SUMS`: all packet files except this manifest; `scripts/verify.py` checks bytes and scope invariants without executing a container or contacting the network.

The original online script remains unchanged and is not claimed to work offline. S1/S3/S4/S6 remain PARTIAL; no blocker closes.
