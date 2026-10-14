# Task 207 — LCB /740 operator packet

**Unsent instructions; no custody record, signature or approval is supplied.**
Gate: `BLOCKED_EXTERNAL_ROW_ATTESTATION`. This packet operationalizes the
[task-198 request](task-198-livecodebench-custodian-request.md); it grants no H0
authority. [LCB_GATE.md](../LCB_GATE.md) remains the admission contract.

## Exact requested metadata

This is a **target template, not evidence**. Only an authenticated custodian who
independently substantiates every claim may issue the record and replace the
custodian placeholder. If a target is wrong, report the discrepancy separately;
do not force a matching record. Never save this template as an issued receipt.

```json
{
  "schema": "harnessgrad.trusted-public-index-row.v1",
  "task_id": "livecodebench/740",
  "row_index": 740,
  "question_id": "abc360_a",
  "revision": "0fe84c3912ea0c4d4a78037083943e8f0c4dd505",
  "pool_sha256": "bbf2bf826856156656568f568e4026f7702f90b5da22a880b733b755a69f4256",
  "split_sha256": "af97cfb379d5af4ae2437e6fda50d4a15199f0d001b0dda64625304a85c9f187",
  "side": "train",
  "public_statement_sha256": "072b9614bc27ae5fb47d3a7fc90de200c15208722a145d6291985967cb50c14f",
  "source_scope": "metadata_only",
  "binding": "POOL_ROW_ATTESTED",
  "custodian": "<actual authenticated custodian identity>"
}
```

Exactly these 12 keys/types; 1–4096 UTF-8 bytes, no BOM, duplicate keys or
non-finite numbers. Custodian: 1–256 printable characters, trimmed. Preserve the
received bytes, including whitespace; never pretty-print before verification.

## Separate custody and approval channels

Upstream maintainers substantiate `livecodebench/code_generation_lite`, the pinned
revision, `release_v6` configuration,
six-shard composition/order, counts, digests and loader identity. The pool
custodian must additionally substantiate a complete, unique metadata-only ID
catalog, `sorted(question_id)` rank, and its existing custody linkage to the
frozen pool and imposed split at checkout
`16e3151f644cc1a0052e2bf09fa887d381066006`. Index 740 is zero-based among body
records; body ordinal 741 / JSONL line 742 requires exactly one header and one
line per record. `train` belongs to HarnessGrad, not an upstream training split.
Existing provenance must also substantiate the statement digest. Matching counts
or an upstream ordinal cannot establish the local row.

The custodian supplies `record.json` and a separately signed UTF-8 JSON custody
envelope containing `record_sha256` (the exact record-byte SHA-256), authenticated
issuer, issuance time, revision, namespace/base, transformation, catalog
completeness/ordering evidence, pool/split custody receipts and evidence for each
claim. Keep all envelope fields outside the strict record.

A reviewer **independent of the producer and this agent** authenticates the
custodian/key through an already trusted official or custody channel, verifies
the envelope and every claim, then supplies the approved digest through a
separate authenticated review channel. For the offline OpenPGP profile below,
the reviewer signs `approved_metadata_sha256.txt`: exactly 64 lowercase hex
characters, optionally followed by one LF. A different signature format requires
its independently reviewed offline verifier; do not skip signature verification.

Provision separate minimal custodian/reviewer keyrings from independently pinned
fingerprints, with only the authorized signing keys. A key included in the
delivery, custodian label, source-commit signature, self-hash or digest computed
by this agent cannot grant approval. Retain exact record/envelope bytes, detached
signatures, trusted key fingerprints, channel references and reviewer decision as
distinct immutable receipts in a fresh workspace-local directory. Do not reuse
or overwrite prior receipts. No channel contact is performed by this packet.

## Offline verification commands

Future operator use only, **after** receiving genuine receipts and completing the
independent review above. From `/tmp/hg-codex-207`, provision the named files and
an isolated `gnupg` directory under `.scratch/task-207-lcb-receipts`; keyrings must
come from the trusted channels, not the delivery. Commands use no key discovery,
network, adapter import or payload. Stop at the first nonzero exit.

```sh
set -eu
receipt_dir="$PWD/.scratch/task-207-lcb-receipts"
gpgv --homedir "$receipt_dir/gnupg" --keyring "$receipt_dir/custodian-keyring.gpg" \
  "$receipt_dir/custody-envelope.json.asc" "$receipt_dir/custody-envelope.json"
gpgv --homedir "$receipt_dir/gnupg" --keyring "$receipt_dir/reviewer-keyring.gpg" \
  "$receipt_dir/approved_metadata_sha256.txt.asc" "$receipt_dir/approved_metadata_sha256.txt"
python3 -I -B - "$receipt_dir" <<'PY'
import hashlib, json, re, runpy, sys
from pathlib import Path

# Reviewed source has only stdlib imports/constants/functions; never call identity().
v = runpy.run_path("tools/lcb740_identity.py")
p = Path(sys.argv[1])
def bounded(name, limit):
    with (p / name).open("rb") as stream:
        data = stream.read(limit + 1)
    if not 0 < len(data) <= limit:
        raise ValueError("missing/oversized metadata: " + name)
    return data
def parse(data):
    return json.loads(data.decode("utf-8"), object_pairs_hook=v["_unique_object"],
                      parse_constant=v["_reject_constant"])

raw = bounded("record.json", v["MAX_INDEX_BYTES"])
approved = bounded("approved_metadata_sha256.txt", 65).removesuffix(b"\n")
if re.fullmatch(rb"[0-9a-f]{64}", approved) is None:
    raise ValueError("malformed independently approved digest")
digest = hashlib.sha256(raw).hexdigest()
envelope = parse(bounded("custody-envelope.json", 65536))
if (not isinstance(envelope, dict) or envelope.get("record_sha256") != digest
        or approved.decode("ascii") != digest):
    raise ValueError("signed envelope/reviewer/record digest mismatch")
r = parse(raw)
expected = dict(schema=v["INDEX_SCHEMA"], task_id=v["TASK_ID"], row_index=v["ROW_INDEX"],
    question_id=v["QUESTION_ID"], revision=v["REVISION"], pool_sha256=v["POOL_SHA256"],
    split_sha256=v["SPLIT_SHA256"], side="train", public_statement_sha256=v["STATEMENT_SHA256"],
    source_scope="metadata_only", binding="POOL_ROW_ATTESTED")
if not isinstance(r, dict) or set(r) != set(expected) | {"custodian"}:
    raise ValueError("metadata schema mismatch")
for key, value in expected.items():
    if type(r[key]) is not type(value) or r[key] != value:
        raise ValueError("metadata mismatch: " + key)
c = r["custodian"]
if (type(c) is not str or not 0 < len(c) <= v["MAX_CUSTODIAN_CHARS"]
        or c != c.strip() or not c.isprintable()):
    raise ValueError("invalid custodian identity")
if hashlib.sha256(v["TASK_ID"].encode()).digest()[0] % 3 == 0:
    raise ValueError("original ID does not select train")
print("metadata_preflight_passed; row_attested=not_evaluated; "
      "pool_freshly_verified_here=false; H0_authorized=false")
PY
```

This docs-only preflight checks signature/digest binding and strict metadata
shape; envelope provenance and signer authorization require the independent
review. It is not a new production admission interface. The existing
[`identity(statement, ...)`](../tools/lcb740_identity.py) requires statement
bytes and **must not run here**, even with a fabricated statement or monkeypatch.
Later, separately authorized admission must receive the genuine record and
independently approved digest as separate inputs. Only after authentication,
review and admission succeed may it record `row_attested=true`.

## Failure semantics and no-payload boundary

| Condition | Disposition |
| --- | --- |
| Record, trusted key, signature or independent approval absent | Pending evidence; gate blocked |
| Authenticated evidence lacks catalog completeness, rank or custody linkage | Authenticated evidence incomplete; gate blocked |
| Invalid signature, untrusted signer, digest/field/provenance discrepancy | Authentication or identity/provenance mismatch; reject and preserve receipts |
| Tool unavailable, command/parser/size failure or source contract changed | Verification incomplete/failed; stop, review offline; no approval inferred |
| Review and preflight succeed | Independently approved metadata binding; production admission still pending |

All failures are unmeasured, not zero scores. Success supplies no benchmark
metric or execution authority. Keep `pool_freshly_verified_here=false`: historical
custody is not a fresh local pool hash. Other privacy, scorer, runtime, snapshot,
quota and cleanup gates remain unchanged; no endpoint/model/GPU run is authorized.

Use only supplied metadata and existing trusted metadata-only receipts. No
network access; no pool, shards, statements/prompts, starter code, examples,
public/private tests, solutions or heldout reads/downloads/hashes. Do not import
`data.livecodebench`, launch the candidate, run payload-reading tests or repair
evidence gaps by reconstructing a catalog from payloads. Preserve inert selections
and old launch receipts. This task neither sends the request nor creates a
positive attestation, reviewer approval or synthetic substitute.
