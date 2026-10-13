# LiveCodeBench /740 remaining-gate review

Status: focused admission/relay repairs implemented; row attestation and official scorer verification remain blocked. No H0, model invocation, full benchmark, or main-checkout edits were performed. Work is confined to `/tmp/codex/110/worktree` at detached HEAD, based on `ba7a4f3`.

## Evidence and exact blockers

The existing public statement identifies AtCoder `abc360_a`, but explicitly calls its `livecodebench/740` row mapping unverified. Its persisted excerpt SHA-256 matches the prior launch receipt: `072b9614bc27ae5fb47d3a7fc90de200c15208722a145d6291985967cb50c14f`. This binds the excerpt bytes, not raw HTML or a dataset row.

The provided evidence is preserved unchanged in:

- `docs/evidence/lcb740/prior-launch.json`, SHA-256 `b2402fc26b4ea0c675c7880ffd72e5272793df084ee9471aebcb06022ed8e168`.
- `docs/evidence/lcb740/prior-selection.inert.json`, SHA-256 `538b3258b90f212c8319e76df08c0e9a445c42f3b72823f203a1971bba504741`.

Both are historical records, not trusted row attestations. The selection says `FILENAME_INFERRED_NOT_POOL_ATTESTED`, `pool_hash_freshly_verified: false`, and `runnable_task_count: 0`. The launch receipt says `launch_executed: false`; the journal's later smoke assertion has no accompanying measured verdict in the allowed local evidence.

| Gate | Result and exact missing evidence |
| --- | --- |
| Public statement identity | Excerpt hash verified against the existing receipt; public URL identifies `abc360_a`. |
| Row/index/release/pool/train attestation | **Blocked:** no independently approved, metadata-only custodian record binds row 740 to `abc360_a` in the pinned pool and original split. A filename, candidate-written record, or self-computed checksum cannot supply that trust. |
| Public-only train export | Only the standalone public statement is present. A provenance-attested train export bound to the trusted row is missing; hash agreement alone does not close this gate. |
| Independent reference review/public verification | No independent review attestation or approved public-test artifact/result is supplied. This task did not execute authored references or create correctness evidence. |
| Relay/request budget | Focused offline tests cover fixed routing, validation, attempted-call/output reservations, concurrent caps, failure accounting, and quiescence. This is per-relay-instance enforcement, not restart persistence or a kernel-security attestation. |
| Official scorer equivalence/verification | **Blocked:** no official executor verification receipt is supplied. The standalone scorer uses a fresh interpreter per case; the prior receipt explicitly disclaims upstream wrapped-function equivalence and lists resource-limit differences. Passing relay tests does not establish official pass@1. |
| Model/H0/full benchmark | Not run; outside this task. |

The required row record must use schema `harnessgrad.trusted-public-index-row.v1`, with exactly the declared fields plus a nonempty custodian: task `livecodebench/740`, integer row `740`, question `abc360_a`, side `train`, release `0fe84c3912ea0c4d4a78037083943e8f0c4dd505`, pool SHA-256 `bbf2bf826856156656568f568e4026f7702f90b5da22a880b733b755a69f4256`, original split SHA-256 `af97cfb379d5af4ae2437e6fda50d4a15199f0d001b0dda64625304a85c9f187`, the statement hash above, `source_scope: metadata_only`, and `binding: POOL_ROW_ATTESTED`. Its approval digest must arrive through independent operator/custodian custody. No such artifact was fabricated here.

Current real admission returns `row_attested: false`, `pool_freshly_verified_here: false`, and blocker: **“No independently approved index record binds row 740 to abc360_a in the pinned pool.”** Its canonical identity SHA-256 is `652c5411d65fd4f8424353478b37eaf7427328f5668a097e35aeb2ecf8b0ce5e`.

## Focused repairs

`tools/lcb740_identity.py` now rejects duplicate JSON keys and excessive parser nesting. Previously a conflicting earlier row field could be silently overwritten before admission. Exact field/type checks, independent digest input, and the unverified default remain enforced.

`tools/launch_lcb740_candidate.py` constructs identity through admission for both CLI and callable entrypoints. Previously the callable accepted a caller-supplied identity dictionary and checked only its statement hash, allowing a fabricated attestation claim into the receipt. It now accepts the original metadata bytes and independent approval digest instead.

`eval/unix_model_relay.py` rejects duplicate request/provider-response keys, excessive parser nesting, and non-object provider responses. It bounds temperature before floating-point conversion, so an oversized integer returns HTTP 400 instead of crashing the handler. Requests reserve calls and requested output tokens atomically before forwarding; failed/unknown attempts retain reservations, and provider overruns block later calls.

The supplied standalone sources, statement, and evidence are included with the repair for reproducibility. The production adapter, driver, imposed split, official scorer wrapper, and authored references were not edited.

## Validation

Focused tests use real AF_UNIX HTTP requests and an in-memory fake provider. TCP connection creation is forbidden by the fixture; no production endpoint is probed. Launcher tests reject invalid/caller-fabricated attestation before relay access. Approved row records are explicitly synthetic fixtures and are never persisted as real evidence.

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q \
  tests/quality/test_lcb740_identity.py \
  tests/quality/test_unix_model_relay.py \
  --basetemp=.scratch/lcb740/pytest -p no:cacheprovider
```

Final result: **79 passed in 25.01s**. `git diff --check` passed. Coverage includes statement tampering; missing approval; wrong row/question/release/pool/split/side and extra fields; duplicate keys; malformed input; fixed route/model; credential/header stripping; socket permissions; request size/framing; exact 4-call, 512-token-per-call, 2048-requested-output-token ceilings; concurrent call/token caps; retained failure reservations; unknown usage; provider overruns; and shutdown waiting for pending forwards.

Input tokens are unmeasured; the relay limits request bytes to 32768. Requested output reservations and reported completion tokens are separate, and unknown usage remains explicitly counted. These checks do not certify total prompt-plus-output cost, agent/verifier namespace behavior, or full scorer equivalence. The release-dependent official test suite was not collected because its adapter imports the mixed pool.

Review scope note: an initial broad repository text search matched unrelated checked-in data; no matched payload was used as task evidence. Subsequent inspection and all focused validation used only the selected public statement, supplied receipts, and implementation/test sources. No LiveCodeBench mixed pool, released case file, external evidence path, or heldout payload was opened by the focused validation.
