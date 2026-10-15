# w-jvm local lifecycle packet

`collect.py` materializes the real platform checks and authors tiny bounded
inputs, runs them once per selected runtime under an external strace observer,
and retains `/proc`, cgroup, scratch and cleanup evidence. It makes no production
scorer/admission changes. Collector limits and assistance are explicitly scoped
in `reports/w-jvm-runtime-observations.md`.

Never point it at an existing packet or work root. For another authorized local
control use a new `--output reports/<unique-name>`; it refuses an existing output
directory and generates a fresh external `/tmp/w-jvm-*` work root. Do not reuse
these runtime IDs or write into `runs/`.

`entry.py` applies the control bounds, records namespace topology and executes the
unchanged materialized check with `runpy`. `audit_packet.py` only audits this
particular retained packet (including its fixed observed PID identities); it
does not execute scorers. Run the auditor from the repository root and then
`sha256sum -c reports/w-jvm-evidence/SHA256SUMS`.

The original launch failures, successful world executions, LibreOffice abort
and fresh four-runtime followup are all preserved. Earlier collector versions
are retained beside those receipts. The current collector includes the
metadata-only fix that retains CLI arguments in future execution records;
the historical exact commands are in the packet's `invocations.json`.
