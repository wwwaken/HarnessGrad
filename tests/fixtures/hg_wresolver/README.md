# w-resolver evidence packet

Read `reports/w-resolver-payloads.md` from the repository root. This packet never
imports a benchmark adapter, constructs a world, runs a scorer, collects a test
from a dataset or calls a model.

Collection commands, in execution order:

```sh
python3 tests/fixtures/hg_wresolver/assemble.py
unshare -Urn python3 tests/fixtures/hg_wresolver/probe.py
python3 tests/fixtures/hg_wresolver/tb_capture.py
python3 tests/fixtures/hg_wresolver/tb_capture.py tb2
python3 tests/fixtures/hg_wresolver/tb_capture.py tb3
python3 tests/fixtures/hg_wresolver/inventory.py
unshare -Urn python3 tests/fixtures/hg_wresolver/supplement.py
```

The initial native collector and first two containers failed before their resolver
invocations. All raw failures are preserved and explained in the report. Inventory
is a deterministic source read/derivation; its initial input-shape errors and the
corrected raw output are retained. The final interpreter and image identity come
from the actual runtime receipts, never from requested minor versions.

Do not rerun collectors into this evidence packet. `assemble.py`, `probe.py`,
`supplement.py` and each named container capture refuse an existing result.
For independent replay use a new packet directory and fresh scratch/container
names. Container capture requires only the existing cached image; it never pulls.

`payloads/` contains the three exact wheels for the two complete Python metadata
profiles. `profiles/*/resolved.lock` pins the actual pip selections. A fresh venv
can install those locks using `--no-index --find-links payloads --require-hashes`,
with dependency processing enabled. Native host/OS ABI and production adoption
are outside this payload guarantee.

The other 33-wheel-corpus candidates are retained outside git at the location in
`inputs.json`. Their metadata and recomputed hashes are committed. This is not a
portable archive for the failed profiles. Terminal-Bench's six wheels and uv archive
are already committed in `tests/fixtures/hg_wuvx/artifacts`; this packet reuses and
rehashes them, rather than editing or duplicating the prior evidence.

`registry-before.json` records registry content solely for an additive-only update
check. It is not a replacement registry or an authorization. `SHA256SUMS` binds all
packet files except itself. `validate.py` is a read-only evidence check by default;
`--seal` writes citation records and the packet's checksum manifest after collection.
