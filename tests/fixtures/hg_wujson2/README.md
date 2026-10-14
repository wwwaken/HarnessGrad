# w-ujson2 source reproduction evidence

One network-denied source build, a wheel/ELF comparison, and two fresh network-denied
runtime replays. `assessment.json` records a non-reproducing build and an open blocker.

- `scripts/record.py`: exact executed argv, UTC times, return code, unmodified output.
  `commands/` contains host/container lifecycle commands and attached shell traces.
- `acquired/`: immutable-commit source archive and four pinned build-tool wheels.
  These inputs were acquired online, separately from network-denied build/replay.
- `source-verification.json`: all 102 archive blobs checked against the existing
  B6 source tree, plus reconstructed root tree. This authenticates source identity
  against that preserved observation, not the published wheel's original build.
- `build/`: build environment, numbered source excerpts, dependency install report
  and locally built wheel. Complete compiler/linker output is in
  `commands/build-start.stdout.txt`; shell trace and warnings are in its stderr.
- `comparison/`: inventories, RECORD validation, full extracted members, metadata
  diffs, raw ELF/symbol/disassembly output and extracted `.text`/`.rodata` bytes.
  Native subcommands have their own argv, return code, stdout and stderr.
- `published-runtime/`, `rebuilt-runtime/`: denied-network probes, hash-checked
  installation, native/member/notice identity checks, eager loader output,
  recursive providers (including observed host vDSO), and fabricated evaluator
  controls. The original unchanged provider/synthetic scripts, evaluators and
  notices are mounted read-only from `../hg_wujson/deployment-v6/`.
- `SHA256SUMS`: every file in this packet except the manifest itself, paths relative
  to the repository root. Verification output is in `reports/w-ujson2-validation.txt`.

The build intentionally retains its truthful `linux_x86_64` tag. No unaudited
manylinux retagging or binary substitution was performed. Matching ZIP timestamps
were explicitly selected from original ZIP metadata and do not authenticate a build.
The source archive has no Git history, so version 5.10.0 is explicitly supplied via
`SETUPTOOLS_SCM_PRETEND_VERSION`; the preserved SCM warning is not hidden.

From the repository root, the actual orchestration was:

```sh
python3 tests/fixtures/hg_wujson2/scripts/container.py build
python3 tests/fixtures/hg_wujson2/scripts/container.py comparison
python3 tests/fixtures/hg_wujson2/scripts/container.py published-runtime
python3 tests/fixtures/hg_wujson2/scripts/container.py rebuilt-runtime
```

These receipts are immutable evidence. For another execution, copy the recipe to a
new packet and change all output directories/names. The launcher rejects existing
receipt directories instead of resuming them. Each executed container was removed;
exact cleanup commands and empty container-list results remain in `commands/`.
