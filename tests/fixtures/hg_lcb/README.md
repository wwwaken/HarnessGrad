# w-lcb metadata custody evidence

This directory preserves five public HTTP acquisitions, including failures and
an OpenAPI redirect, made through `HG_EGRESS_PROXY=http://172.17.0.1:17890`.
Each request's URL, UTC time, TLS validation flag, HTTP status, body length and
SHA-256 are in its `receipt.json`. `response.body` is the exact HTTP entity
returned to urllib; `response.headers` is the parsed header serialization, not
wire octets. Redirects are not automatically followed. The OpenAPI redirect's
public documentation target was separately reviewed and fetched.

`SHA256SUMS` covers every fixture file except itself. `review.json` is derived
review metadata, **not a catalog, custody attestation or approval**. Upstream
LFS digests in it are advertised digests from the inherited pinned Hub metadata;
no shard was fetched or hashed here. Its upstream row list is empty and its
upstream count/rank are null. Three local filename-inferred candidates are kept
separate. The conditional full split calculation uses the existing declared
ordinal namespace; it does not establish actual pool contents or ID ranks.

The task-207 template and historical selection/launch records are read as inert
metadata. No task-207 record, custody envelope, signature or approval is issued.
The operator withdrew independent approval gates; they are not prerequisites
of this review. Real source and local transformation custody are still missing.
No adapter is imported and no pool, statement, reference, test, shard, dataset
conversion, benchmark, container, model, GPU or endpoint is accessed/executed.

From the repository root, reproduce all findings offline:

```sh
python3 -B tests/fixtures/hg_lcb/verify.py
(cd tests/fixtures/hg_lcb && sha256sum -c SHA256SUMS)
python3 tools/check_dataset_blockers.py
```

The verifier rehashes inherited raw metadata/headers/receipts and source files,
checks the pinned builder's Git blob against the authoritative revision
metadata, matches all six advertised shard digests with adapter literals,
compares the task-207 targets, regenerates the conditional 1,055-ordinal split,
and reproduces the preserved three-candidate ranking. It performs no requests.

Acquisitions are deliberately non-overwriting. To repeat the public requests,
copy `acquire.py` into a fresh directory outside the repository and run that
copy with the canonical proxy; its outputs go alongside the copy. The current
OpenAPI documentation and viewer availability are observations at acquisition
time, **not pinned-release responses**. The viewer OpenAPI does not document a
`revision` parameter; including it in a request does not authenticate a revision.
Do not replace these preserved observations with later results.
