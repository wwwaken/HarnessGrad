# w-tbdep source and local inspection evidence

This directory contains source/inspection evidence only, not a benchmark receipt.
No task, scorer replay, world constructor, submitted solution, model, GPU or endpoint
request was executed. Do not run the preserved upstream tests to validate this report.

- `repository-inspection.json`: AST import/runtime declarations and hashes at the
  reviewed source baseline; collected by `inspect_repository.py` without imports.
- `native/`: host identity, ALFWorld/TextWorld, ScienceWorld/Py4J and openpyxl
  import-only module lists, active declared dependency metadata, copied installed
  source, JVM JAR inventory and local ELF/LibreOffice version observations.
  Collection: `python3 tests/fixtures/hg_wtbdep/native/inspect_native.py`.
- `python/`: DS-1000/LiveCodeBench copied executor sources, imports, package
  requirements and native-library observations; BIRD SQLite and Chess package
  evidence. DS-1000 rows retain only import statements, loader-call expressions
  and context hashes, not solutions or complete gold contexts. Exact command in
  `python/commands.txt`; embedded ldd argv/results in its JSON outputs.
- `runtime/`: raw Docker inspect/history for GAIA/tau-bench/AppWorld; read-only
  image archive projections of generic scorer source, package metadata, dpkg
  status and ELF NEEDED declarations. `inspection-commands.json` gives exact argv
  and return codes. AppWorld's protected task evaluators were not opened.
  Terminal-Bench includes all 89 public task image/base/test-source declarations,
  an import/bootstrap/process-call appendix and 86 successful image inspections;
  the raw stderr preserves all three missing-image errors. Preserved Python test
  files end in `.py.txt` so pytest cannot collect them.
- `scope/`: guarded imports for Jericho, Reasoning Gym and AgentDojo, with network
  operations denied; source, metadata and readelf observations. Exact commands in
  `scope/commands.txt`; pure-QA imports and registry coverage were inspected by AST.
- `evidence-locators.json`: cited path, line number and exact source line. Literal
  locators are checked against the referenced file; empty/structural lines alone
  are not treated as substantive evidence.

The root `SHA256SUMS` covers every fixture file except itself, including subordinate
manifests. Run `sha256sum --check --quiet SHA256SUMS` from this directory.
Raw upstream source/output preserves its original whitespace. Authored report,
journal and collection scripts are checked separately; raw copies are not normalized.

A recorded package version, image ID, ELF SONAME or successful import is an
observation, not an enforced dependency lock, runtime attestation or production gate.

`container-abi/` supplements the saved-image projections with static Python,
libpython, _hashlib/_ssl/_sqlite3 ELF dependencies and raw hashlib/ssl source.
Its `custody.json` records exact image-member hashes and the inspection command;
no image executable was run.
