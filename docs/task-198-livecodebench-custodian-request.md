# Task 198 — custodian request and metadata-only verification protocol

Draft only. Nothing has been sent. The values below describe the claim to verify;
they are not an attestation or an independently approved record.

## Request to the LiveCodeBench maintainers and designated independent custodian

Subject: Metadata-only provenance request for pinned LiveCodeBench identity and HarnessGrad row 740

We need independent provenance for a proposed mapping of HarnessGrad task
`livecodebench/740` to LiveCodeBench question ID `abc360_a`. Please confirm or
correct it from your existing, trusted metadata catalog and provenance records.
Do not assume the proposed mapping is true.

Please return only metadata and provenance evidence. Do not return problem
statements, prompt templates, starter code, examples, public/private tests,
solutions, dataset shards, pool rows, or heldout payloads. If an adequate
metadata-only catalog or existing custody receipt is unavailable, report that
limitation; do not reconstruct it by downloading or inspecting payloads for this
request.

For the upstream maintainers:

1. Confirm the official repository identity
   `livecodebench/code_generation_lite` and dataset revision
   `0fe84c3912ea0c4d4a78037083943e8f0c4dd505`.
2. Supply the revision-pinned builder/manifest metadata for `release_v6`: exact
   configuration name, source shard set and ordered composition, split name,
   counts, published object digests, and loader/builder revision. Distinguish
   the dataset configuration from a Git branch, Git tag, or GitHub Release.
3. Confirm whether your catalog binds `abc360_a` to that release. Specify the
   index namespace, indexing base, ordering, filters and any duplicate handling
   if you publish an ordinal. An upstream ordinal alone is insufficient for our
   locally transformed pool.
4. Identify any public signed index/manifest, row inclusion proof, or
   custodian-issued metadata record for this claim. Provide its official URL,
   exact signed scope, authenticated issuer/key identity and verification method.
   If none is published, please say so within the scope you administer.

For the designated custodian of the frozen HarnessGrad pool:

1. Independently reconcile the upstream metadata with the transformation at
   HarnessGrad checkout `16e3151f644cc1a0052e2bf09fa887d381066006`.
   `data/livecodebench/prepare.py` reads six declared shards, rejects duplicate
   IDs, and emits rows in Python `sorted(question_id)` order. The adapter uses
   zero-based indices after excluding the pool header.
2. From an existing complete metadata-only ID catalog, verify that `abc360_a`
   has sorted rank 740. Confirm completeness, unique IDs, the precise shard
   union and provenance of the catalog. A filename, reference file, statement
   hash, or matching number of rows does not establish this rank.
3. Use existing independently held custody receipts to bind that catalog and
   transformation to the pool digest below. A sorted-ID claim without a binding
   to the frozen pool bytes is insufficient. Do not newly open/hash the pool
   payload or tests within this task's scope.
4. Separately reconcile the HarnessGrad split digest and original task ID.
   This `train` assignment is imposed by HarnessGrad; please do not represent it
   as an official LiveCodeBench training split.
5. Verify the persisted public-statement digest through existing trusted
   provenance metadata. The statement itself must not be returned or read for
   this task. If you cannot substantiate any requested field, return a mismatch
   or an explicit evidence gap instead of a positive attestation.

Only after independently substantiating every field, please issue a UTF-8 JSON
record with exactly the following fields. Do not create a record merely by
copying the requested values.

| Field | Requested, unverified target value |
| --- | --- |
| `schema` | `harnessgrad.trusted-public-index-row.v1` |
| `task_id` | `livecodebench/740` |
| `row_index` | integer `740` |
| `question_id` | `abc360_a` |
| `revision` | `0fe84c3912ea0c4d4a78037083943e8f0c4dd505` |
| `pool_sha256` | `bbf2bf826856156656568f568e4026f7702f90b5da22a880b733b755a69f4256` |
| `split_sha256` | `af97cfb379d5af4ae2437e6fda50d4a15199f0d001b0dda64625304a85c9f187` |
| `side` | `train` |
| `public_statement_sha256` | `072b9614bc27ae5fb47d3a7fc90de200c15208722a145d6291985967cb50c14f` |
| `source_scope` | `metadata_only` |
| `binding` | `POOL_ROW_ATTESTED` |
| `custodian` | Your actual authenticated custody identity |

The record must be 1–4096 bytes, without a UTF-8 BOM, duplicate keys, non-finite
numbers, or additional fields. The custodian string must have 1–256 printable
characters with no surrounding whitespace. Preserve the exact transmitted bytes.

Please supply a separate signed custody envelope binding the exact record's
SHA-256, issuer, issuance time, source revision, index namespace/base,
transformation and pool/split provenance receipts, and the evidence used for each
claim. Publish it through your official channel or provide an authenticated
custody channel and a signing key that the reviewer can verify independently.
Keep those extra fields outside the strict admission record. The upstream
maintainers may substantiate only upstream claims; a separate custodian must
substantiate the local transformation and split if upstream cannot do so.

Our independent reviewer must approve the exact-byte record digest separately.
A `custodian` label, an attached key, a self-hash, or an approval digest supplied
only by the same unauthenticated record does not establish trusted custody.

## Safe verification protocol

1. Keep the gate blocked while the request is pending. Preserve existing inert
   selections and launch receipts. This request grants no execution authority.
2. Authenticate the issuer through a previously trusted official channel and
   independently verify its signing key. Verify the custody envelope signature
   and its binding to the exact record bytes. Do not trust a key solely because
   it arrived with the record.
3. Have a reviewer independent of the producer and this agent assess the
   upstream catalog, completeness/ordering evidence, local pool custody and
   local split separately. Require provenance for every claim. Unavailable
   evidence leaves the corresponding claim blocked.
4. Check the index namespace explicitly: 740 means zero-based position among
   body records of the ID-sorted local pool. It would be body ordinal 741 and
   physical JSONL line 742 if there is exactly one header and one line per record.
   Do not confuse it with an upstream `test` split ordinal or subset position.
5. Confirm the original ID remains `livecodebench/740`. The local split rule
   assigns evaluation when `SHA256(task_id.encode()).digest()[0] % 3 == 0`,
   otherwise training. Bind the full declared split to its independently held
   receipt; a one-ID side calculation alone does not prove the full split hash.
6. The independent reviewer supplies the approved exact-byte digest through a
   separate trusted channel. Store the record, detached custody evidence and
   reviewer approval as distinct immutable receipts. Computing a digest for
   transport integrity must never manufacture approval.
7. Perform bounded, offline metadata admission with the current strict schema
   and pinned constants. Do not import `data.livecodebench`: its module-level
   initialization reads the mixed pool. Do not invoke the current
   `identity(statement, ...)` entry point in this task, since it requires
   statement bytes. A later, separately authorized admission can use the
   independently approved record under its own permitted scope.
8. Record `row_attested` only after authentication, independent approval and
   admission all succeed. Record `pool_freshly_verified_here=false` unless a
   separate permitted process actually verifies pool bytes. Do not substitute
   historical custody for a fresh local hash claim.
9. Leave official scorer, privacy, runtime, snapshot and other execution gates
   unchanged. This metadata verification produces no benchmark measurement,
   model call, endpoint binding, H0 authorization or main-branch merge.

Required dispositions are: pending evidence, authenticated evidence incomplete,
identity/provenance mismatch, or independently approved metadata binding. Missing
evidence is not a zero score. No synthetic positive record is produced by this
protocol.
