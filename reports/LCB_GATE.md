# LCB /740 trusted row attestation gate

Status: **BLOCKED_EXTERNAL_ROW_ATTESTATION**. Strict metadata validation is
implemented; real row attestation is not established.

The exact blocker is: **No independently approved index record binds row 740 to
abc360_a in the pinned pool.** No externally custodied record or independent
approval digest was supplied or found in the reviewed local public evidence.
Neither a self-computed record hash nor its `custodian` label establishes custody.

## Observed local evidence

- `data/livecodebench/abc360_a.public.md` matches the pinned public statement
  SHA-256 `072b9614bc27ae5fb47d3a7fc90de200c15208722a145d6291985967cb50c14f`.
  This identifies the persisted statement excerpt, not its mixed-pool row.
- `docs/evidence/lcb740/prior-selection.inert.json` explicitly records
  `FILENAME_INFERRED_NOT_POOL_ATTESTED`, `metadata_attestation_required=true`,
  and `pool_hash_freshly_verified=false`.
- `docs/evidence/lcb740/prior-launch.json` explicitly records an unverified,
  filename-derived row binding and `H0_authorized=false`.
- `DOWNLOADS.md` pins the release revision and shard digests. These declarations
  do not supply independently approved row/index attestation.

Calling `tools.lcb740_identity.identity` with only the existing public statement
still yields `row_attested=false`, `pool_freshly_verified_here=false`, and
`binding=FILENAME_INFERRED_NOT_POOL_ATTESTED`. Its unchanged identity receipt hash
is `652c5411d65fd4f8424353478b37eaf7427328f5668a097e35aeb2ecf8b0ce5e`.

## Required external evidence

A trusted custodian must supply a metadata-only JSON record with exactly these
fields and values, plus their actual custodian identity:

- `schema`: `harnessgrad.trusted-public-index-row.v1`
- `task_id`: `livecodebench/740`
- `row_index`: integer `740`
- `question_id`: `abc360_a`
- `revision`: `0fe84c3912ea0c4d4a78037083943e8f0c4dd505`
- `pool_sha256`: `bbf2bf826856156656568f568e4026f7702f90b5da22a880b733b755a69f4256`
- `split_sha256`: `af97cfb379d5af4ae2437e6fda50d4a15199f0d001b0dda64625304a85c9f187`
- `side`: `train`
- `public_statement_sha256`: `072b9614bc27ae5fb47d3a7fc90de200c15208722a145d6291985967cb50c14f`
- `source_scope`: `metadata_only`
- `binding`: `POOL_ROW_ATTESTED`
- `custodian`: 1–256 printable characters, without surrounding whitespace

The operator must independently approve the SHA-256 of the record's exact bytes
through trusted custody and supply it separately as `approved_metadata_sha256`.
The validator checks this supplied trust anchor; it cannot authenticate its
origin. Approval must not be taken from inside the record or manufactured by
hashing a locally invented record. Synthetic fixtures are not production evidence.

The record must be 1–4096 bytes of UTF-8 JSON without a BOM, duplicate keys,
non-finite constants, missing fields, or extra fields. Approval is exactly 64
lowercase hexadecimal characters. Pinned field values and their types must match;
the original task ID determines the train side, without subset reindexing.

## Validation and execution scope

Changes are confined to strict admission in `tools/lcb740_identity.py`, focused
tests, this gate report, and the integration journal. No external record or
approval was fabricated. Existing evidence receipts are preserved.

Focused validation: **80 passed** using the following command after creating the
workspace-local `.scratch` parent:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q -p no:cacheprovider tests/quality/test_lcb740_identity.py --basetemp=.scratch/lcb740-gate-validation
```

Tests use the public statement and explicitly synthetic metadata. They verify
exact-byte approval before parsing, strict schema/types/encoding/size/custodian
validation, unchanged unattested receipts, and rejection before relay access.
`git diff --check` passes. No network, mixed-pool/heldout payload reads, model calls,
or H0 execution occurred. Benchmark task/trial coverage and metrics are not
measured; no endpoint was bound. Workspace-local test scratch directories were
removed after validation. Passing these tests does not authorize H0 or establish
official scorer equivalence.
