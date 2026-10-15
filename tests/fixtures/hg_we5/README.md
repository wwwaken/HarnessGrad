# w-e5 authored projected-state controls

Read `reports/w-e5-equivalence.md` for the exact scope, source references, coverage
fractions and counterexamples. E4/E5/E6 remain PARTIAL; no blocker closes.

`collect.py` uses actual export/recheck functions and fresh child invocations of
unchanged local dataset scorer entrypoints. `evidence/` retains original/exported
bytes, separate private inputs, native export contracts/receipts and raw results.
It is not a production pristine runtime or official metric equivalence packet.

`commands.sh` refuses to reuse the evidence directory. To replay collection,
use `collect.py --output <new-directory>` under the same existing offline guard;
never overwrite this packet or resume an old ID. Scratch is external `/tmp` and
new export IDs are generated for each operation. No benchmark/model/endpoint is
used. Initial evidence is preserved in a verified ZIP plus its raw command logs.

Read-only validation from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_we5/verify.py
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/quality/test_we5_equivalence.py -q --basetemp=/tmp/harnessgrad-pytest-we5
python3 tools/check_dataset_blockers.py
```

`source_audit.py` preserves source excerpts and derives the explicit disjoint
denominators in `coverage.json`; it deliberately refuses to overwrite its source
excerpt file. `preserve_initial.py` is the one-time verified archival command,
not part of replay validation. `SHA256SUMS` excludes itself to avoid self-reference.
