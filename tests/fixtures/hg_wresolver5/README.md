# w-resolver5 compact evidence packet

Read reports/w-resolver5-payloads.md and reports/w-resolver5-validation.txt.
The primary packet contains DS1000 import/declaration derivation, exact URL/name/size/SHA-256 artifact metadata, original raw command output, real network-denied install/refusal/cleanup receipts, scripts, coverage arithmetic and unchanged registry projection. The sibling hg_wresolver5_tb packet supplies three explicit bootstrap-only reconstructions.

All payloads, saved index bodies, redundant partial downloads and bulk import-site lists stay outside the repository. artifacts.json identifies the actual candidate directory and every digest. refetch.py re-fetches exact URLs into a new external directory, checking sizes/hashes; --filename selects an explicit bounded subset. Its successful smoke check covers flatbuffers only, while the Terminal-Bench refetch script verified its entire set.

acquire.stdout.txt and attempts/acquire-executed-initial.py preserve an incomplete redundant refetch, terminated with SIGTERM/exit143. attempts/acquisition-correction.json discloses two invalid unflushed-index digest captures. finalize.py independently audits the complete initial discovery artifacts and corrects closed-file index hashes with raw sha256sum. Partial redundant transfers never enter the resolved candidate set. The active acquire.py flushes before hashing. No unobtainability conclusion is made.

source.py reads only code_context import metadata from all released DS1000 rows; context_literals.py audits parseable import-containing strings. No prompts, gold/reference code, test bodies, task execution or scores are exported. The original complete temporary pip report is reduced to graph fields and a digest/size receipt, then removed with the disposable workdir; no full-report retention is claimed.

Read-only verification: python3 tests/fixtures/hg_wresolver5/validate.py and python3 tests/fixtures/hg_wresolver5_tb/validate.py. Acquisition/probe generators refuse existing captures; never rerun in place. SHA256SUMS seals this primary packet. No shared/dataset blocker or production gate closes.
