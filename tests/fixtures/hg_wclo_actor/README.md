# Actor-workdir scorer byte closures — w-clo-actor

These are **partial local byte closures**, not execution receipts, offline runtime
bundles, official-score certifications or pilot authorization. The source-established
scope is all 19 actor-workdir routes in `reports/w-shared-topology-survey.md`: 12 QA
commands and seven native commands. ChessBench's alternate controller is separate.

`datasets/<dataset>.json` is the entry record. It binds source entry points and exact
line locators, gold/source-data manifests, interpreter, guarded import observations,
installed distribution content manifests, and unresolved findings. All recorded file
digests were calculated from current bytes. Configured source declarations are
preserved separately; `matches_literal_adapter_digest` compares a **computed** data
digest to those declarations. No digest from an inherited report is adopted as a
current file hash.

- `gold/`: source/expected-data files, provenance revisions, independently hashed
  archives/shards and, where recorded, byte comparisons to archive members. No gold
  contents, hidden test contents, reference solutions or per-task materializations
  are copied here. Source-artifact counts are not eligible/selected trial counts.
- `imports/` and `import-commands.json`: fresh package-only imports with networking
  denied, GPU visibility disabled and no scorer/constructor/candidate invocation.
  `phase` distinguishes requested imports from modules already loaded by interpreter
  startup/inspection. The latter are not attributed to a metric. `packages` describes
  observed imports; default declared requirements are a separate superset.
- `packages.json` and `packages/`: actual installed versions, Requires-Dist metadata,
  and independently computed SHA-256s for all metadata-enumerated installed members
  except regenerable bytecode. RECORD is hashed as a file, never trusted as the source
  of member digests. Distribution manifests do not certify unlisted files or provide
  offline wheel payloads. No offline installer/runtime bundle was provisioned.
- `interpreter.json`, `interpreter-files.json`, `native-files.json`, `jre-files.json`:
  current host interpreter/stdlib, imported extensions, files named by prior ABI
  inspection, and the staged JRE. Native files are a bounded inventory, **not** a
  complete OS/ELF/dlopen/plugin closure or evidence of future runtime selection.
- `common-sources.json`, `installed-scorer-entry-points.json`: AST/source entry points;
  per-family candidates are not assertions that every family was executed.
- `prior-evidence.json`: recomputed identities for reviewed reports and existing
  ALFWorld observations; Terminal-Bench's snapshot-service evidence cannot establish
  an actor-workdir control. Missing prior fixture directories are explicit findings.
- `SHA256SUMS`: every file here except itself, including scripts and this README.

External file paths identify existing local bytes under `/mnt/...`; they are not
vendored or promised to exist on another host. Repository code paths identify bytes
in this worktree. Reproduction requires those matching source/data/runtime files,
the selected task's trusted gold serialization and submitted artifact, and matching
known isolation classes. Those execution bindings are not produced by inspection.

To collect again in a **fresh evidence directory/worktree**, without running a task:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B tests/fixtures/hg_wclo_actor/inspect_closures.py
PYTHONDONTWRITEBYTECODE=1 python3 -B tests/fixtures/hg_wclo_actor/finalize_records.py
PYTHONDONTWRITEBYTECODE=1 python3 -B tests/fixtures/hg_wclo_actor/check_closures.py --write-sums
PYTHONDONTWRITEBYTECODE=1 python3 -B tests/fixtures/hg_wclo_actor/check_closures.py --external-bytes
python3 tools/check_dataset_blockers.py
```

`inspect_closures.py --imports-only` refreshes package-import observations without
rehashing the large data/package inventory; then rerun finalization and validation.
Do not use either collection mode to overwrite a historical receipt. The final
validation commands/results for this work are in `reports/w-clo-actor-validation.txt`.
