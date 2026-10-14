# Independent verification of frozen w-net Terminal-Bench evidence

The reported numerical scorer result survives: six CTRF test records contain five passes and one failure; the preserved reward file is exactly `b'0\n'`; the trace contains 32 independently counted model reply records. The final diagnostic publication remains **unmeasured**, with no published score. There is no discrepancy in the merged report, which expressly distinguishes raw scorer measurement from publication.

Verification is read-only over `reports/w-net-evidence/run-artifacts.tar.gz`. The replay reads regular tar members into memory; it never extracts archive paths, runs a model, starts Docker objects, or executes the captured official verifier. Original and review artifacts were not modified. Original source paths named inside receipts are historical identities, not newly observed paths.

Exact replay command, from repository root (all table rows use this command):

```sh
python3 tests/fixtures/hg_wverify/net/rederive_net.py > tests/fixtures/hg_wverify/net/rederive-output.json
cat tests/fixtures/hg_wverify/net/rederive-output.json
```

| Claim checked | Verdict | Raw observation from replay |
|---|---|---|
| Frozen archive matches its identity and inventory | REPRODUCED | SHA-256 `6a7c6469ddca5557eea1ade2684848282ff18f6ceb4ae84a4e0463721b200897`; 105324 bytes; 218 ordinary-file members and 218 inventory entries; `inventory_mismatches=[]`. |
| Official CTRF tests=6, passed=5, failed=1 | REPRODUCED | Independently counted the six `results.tests` entries: `tests=6, passed=5, failed=1, skipped=0, pending=0, other=0`; all equal CTRF summary values. Failure: `test_outputs.py::test_python_verification_script`. |
| CTRF review copy has custody to preserved verifier output | REPRODUCED | Archive CTRF has 4020 bytes and SHA-256 `67dbb020f78873084b681fa47cbe1f6e5c96f887ae80fab729aa91bb385e88ef`; observer digest agrees; current review copy is byte-identical. |
| Raw verifier score is 0.0 | REPRODUCED | Archive reward bytes `b'0\n'`, parsed `0.0`; execution per-task score, verdict score, and progress score are also `0.0`. Reward SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` agrees with observer. Preserved official script hashes to `4770437ea96c3cc84684b4f99d55fb148fcac09f9ea1e8ef49de487716e6c334` and emits 0 when pytest fails. |
| Agent used 32 model calls | REPRODUCED | Counted 32 JSONL rows containing `reply`, with steps 0–31; final usage `calls=32, input_tokens=163009, output_tokens=8527, retries=0`; aggregate calls=32 and gateway connections=32. Environment-service calls=0 is a separate field. |
| Actual/declared scorer isolation is internally consistent with `snapshot-service` | REPRODUCED | Six execution/verdict/progress class fields equal `snapshot-service`. Actor ID `33b07aa5952a86161ef9d329a92a6e61026ae1df30c5abb5ab01ff6816fe58a3` differs from verifier ID `65a5383c36f88ae502ebee61c87906c10f4fdf9b2cd78c9b9afd267d43eb7cf3`. Verifier image equals observed snapshot `sha256:59c94f3462a248e5af5909b2249cba07e2e46574eee4fd362896d7c048eac779`, whose parent equals actor image `sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12`. Both roles have bridge plus the owned task network. |
| Receipt eligible=1, selected=1, expected trials=1 | REPRODUCED | Launch selection lists only `openssl-selfsigned-cert`; staged plan and final receipt select it; trials=1, jobs=1; split=null. |
| Receipt invalid=0, unmeasured=1, measured=0 | REPRODUCED | Counted one outcome: `status=unmeasured, score=null, reason=policy_enforcement_not_observed`. Independent outcome coverage agrees with stored task/trial coverage: invalid 0, unmeasured 1, measured 0. Raw execution `invalid={}`. |
| Publication is withheld despite a real raw scorer result | REPRODUCED | Final receipt `score=null`, enforcement `measured=false, comparable=false, policy_enforcement_observed=false, production_authorized=false`. Scorer isolation `comparable=true` describes the isolation classification; it is not a publication authorization. Snapshot/cleanup are `status=unknown`; lifecycle is null. These fields explain the distinction rather than contradicting it. |
| Live independently attested policy enforcement, trusted lifecycle completion, or comparable measured publication | NOT CHECKABLE HERE | No such attestation is present in the inspected evidence, and none is claimed in the report. Replaying the frozen files cannot establish live enforcement. |

Raw replay output is `tests/fixtures/hg_wverify/net/rederive-output.json`. `input-members.json` identifies every selected archive member and its copied bytes/hash. Selected originals are copied byte-for-byte into the same fixture directory. The parent supplies the combined SHA-256 manifest and registry validation.

The term “measured run” can truthfully refer to raw scorer execution here. It cannot describe a measured diagnostic publication: that count is exactly zero. The original report already states this limitation, so it is not refuted by its own receipt.

Reproduced: all checked Terminal-Bench numerical and internal consistency claims. Refuted: none. Not checkable: stronger live enforcement/lifecycle/publication attestation.
