# E3 BFCL source acquisition candidate

This is unapproved code/metadata evidence, with no tasks or model results.
The inventory is deliberately not an admissible source-gate receipt. It grants
no official scorer, model, H0 or runtime authorization.

The [line-cited review](../../../docs/e3-bfcl-simple-source-review.md) records the
starting requirement, tasks 195/227/B5, newly acquired bodies, the Simple graph,
remaining custody/review/runtime work and honest `external` disposition.

- `starting-blocker.json`: exact blocker before this review.
- `responses/`: 24 raw public GitHub blob JSON bodies and request/response receipts.
- `files/`: 23 original handler bodies and ten original empty initializers.
- `inventory.json`: all 83 unique old/new original paths, sizes, SHA-256, Git
  blob IDs, local paths, prior tree/inventory hashes and unapproved custody flags.
- `static-audit.json`: AST-only import names, source lines, function scopes,
  dynamic/evaluation calls and non-stdlib roots. This is not runtime closure.
- `SHA256SUMS`: all files in this new bundle except itself; an integrity record,
  never an independent approval pin.

Run the offline audit without importing any upstream code:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/e3_bfcl_source/verify.py
```

`acquire.py` records the acquisition procedure. Do not rerun it into this bundle:
it refuses existing response filenames. Preserve receipts and use a fresh output
directory for any later authorized acquisition. No archive GET occurred; original
archive member strings remain candidate declarations with verification false.
