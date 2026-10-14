# Adversarial verification of merged quantitative claims - w-verify

**No checked numerical claim was refuted.** All nine controlled scorer results, the image reference/presence counts, and the preserved Terminal-Bench scorer numbers reproduce. The Terminal-Bench publication remains **0 measured / 1 unmeasured / 0 invalid**, with `score=null`; its raw verifier reward is `0.0`.

Baseline: `99a29904996a38eb66783f70c231809a574203ea`, registered worktree `/tmp/hg-verify`, branch `wg-verify`. Independent subtasks used registered worktrees; their diffs were reviewed and their outputs checked before integration. No model, GPU, endpoint, pull, container execution, adapter change, registry change, or frozen-evidence modification occurred. The only existing file changed is the explicitly requested append to the integration journal.

Commands below run from the repository root. `C1` executes newly authored controls **before** loading old synthetic inputs for exact-count cross-checks. These results come from executing the scorer sources, not from trusting the old comparison outputs. The three primary local adapters are byte-identical to those in the original scorer worktree; official source hashes match the reported pins. The 2Wiki source also matches the independently opened local upstream tar archive.

```sh
# C1: independent GSM8K, Physics Questions and 2Wiki calls; raw outputs also in output.json
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 tests/fixtures/hg_wverify/scorers/offline_exec.py tests/fixtures/hg_wverify/scorers/check.py > tests/fixtures/hg_wverify/scorers/stdout.txt 2> tests/fixtures/hg_wverify/scorers/stderr.txt

# C2: remaining six datasets; expands to twelve bounded scorer invocations
bash tests/fixtures/hg_wverify/extra-scorers/commands.sh

# C2b: distinguish MuSiQue raw policy differences from rounding; check aggregate
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_wverify/extra-scorers/offline_exec.py tests/fixtures/hg_wverify/extra-scorers/musique_precision_and_aggregate.py > tests/fixtures/hg_wverify/extra-scorers/musique-precision-aggregate.stdout.json 2> tests/fixtures/hg_wverify/extra-scorers/musique-precision-aggregate.offline.txt

# C3: independently enumerate configuration, inspect 94 references, rehash preserved manifest bytes
python tests/fixtures/hg_wverify/images/verify_images.py > tests/fixtures/hg_wverify/images/verify.stdout.txt 2> tests/fixtures/hg_wverify/images/verify.stderr.txt

# C4: read preserved Terminal-Bench tar members in memory; no captured commands are executed
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_wverify/net/rederive_net.py > tests/fixtures/hg_wverify/net/rederive-output.json

# C5: separate native digest calculation over the saved raw OCI bytes
sha256sum tests/fixtures/hg_wverify/images/preserved-raw-manifests/*.json
```

Every table command key refers to the exact invocation above; C2's individual argument vectors, exit codes and output paths are additionally in `extra-scorers/execution-commands.json`. Raw output paths are relative to `tests/fixtures/hg_wverify/`.

| Claim checked | Verdict | Command | Raw numbers observed / evidence |
| --- | --- | --- | --- |
| GSM8K 10/16 extraction/comparison divergences | REPRODUCED | C1 | Cross-check: `inputs=16, agree=6, diverge=10`. Own inputs: `10/4/6`. `scorers/output.json`, `scorers/stdout.txt`. |
| Physics Questions 4/12 normalization divergences | REPRODUCED | C1 | Cross-check: `inputs=12, agree=8, diverge=4`. Own inputs: `8/4/4`. Official unchanged `exact_str_match_fn` AST execution; full module import is outside this check. |
| StrategyQA 7 raw-contract differences; Boolean projection agrees 4/4 | REPRODUCED | C2 | `12 inputs, 5 agreements, 7 differences`; explicit Boolean-to-text projection `4/4`. Boolean and text contracts remain distinct. |
| Sports Understanding 5 paired-channel differences | REPRODUCED | C2 | `12 inputs, 7 agreements, 5 differences`; candidate ranking and generated text are separate channels. |
| FEVER one flat-gold conjunction difference and three full-API exceptions | REPRODUCED | C2 | Strict predicate `16/17 agree`, one difference; full singleton API raises `3 ZeroDivisionError`s. Exceptions remain errors. |
| HotpotQA one empty-support boundary difference | REPRODUCED | C2 | `13 numeric inputs, 12 agree, 1 differs`; empty-support boundary. |
| MuSiQue common metrics agree; four reward-policy differences | REPRODUCED | C2, C2b | `12/12` common-metric comparisons agree; `4` local reward vs unrounded official answer-F1 component policy differences. Literal rounded-column vs unrounded-reward comparison gives `5`: the additional row is `0.667` vs `0.6666666666666666`, a rounding difference. `extra-scorers/musique-precision-aggregate.stdout.json` retains both definitions. |
| MuSiQue aggregate common metrics agree | REPRODUCED | C2b | Official and local aggregate both `{answer_f1:0.889, answer_em:0.833, support_f1:0.789}` on the original controls. |
| TriviaQA one upstream exception | REPRODUCED | C2 | `10/10` numeric inputs agree; `1 ValueError` remains nonnumeric. |
| 2Wiki agrees on all comparisons | REPRODUCED | C1 | `13/13` inputs agree on all `16` published metric cells each (`208/208`); all `16` aggregate metrics agree. Own inputs `8/8`, plus aggregate agreement. |
| 94 configured image references | REPRODUCED | C3 | `reference_count=94, unique_reference_count=94`; direct source/TOML enumeration: GAIA `1`, Tau-bench `1`, AppWorld `3`, Terminal-Bench `89`. `images/configured-references.json`. |
| 91 local images present with RepoDigests | REPRODUCED | C3 | Fresh inspect: `present_count=91, present_with_repo_digests=91, missing_count=3`; Terminal-Bench `86` present. `images/current-inspections.json`. |
| All 91 RepoDigests recompute from preserved local OCI manifest bytes | REPRODUCED | C3, C5 | `101/101` preserved index/manifest blobs hash correctly; `91/91` current RepoDigest roots and image identities bind to those bytes. Parent separately rehashed all `101` blobs and freshly inspected GAIA, Tau-bench and AppWorld actor. `images/manifest-rehash.json`, `images/manifest-fresh-inspect-bindings.json`, `images/parent-review.json`. |
| Fresh reread of live manifest-store bytes | NOT CHECKABLE HERE | C3: `ls -ld /var/lib/containerd/io.containerd.content.v1.content/blobs/sha256 /var/lib/docker/containerd/daemon/io.containerd.content.v1.content/blobs/sha256`; `sudo -n ctr --address /run/containerd/containerd.sock --namespace moby images list` | `ls` exit `2`, `权限不够` (permission denied); `sudo` exit `1`, `需要密码` (password required). Arithmetic on preserved bytes is checkable; live-store reread is inaccessible. |
| GAIA / Tau-bench use movable tags | REPRODUCED | C3 | `harnessgrad/gaia:20261008`, `harnessgrad/tau-bench:20261006`; both configured without digest pins. |
| All 89 Terminal-Bench references are movable tags, 3 absent | REPRODUCED | C3 | `terminal_bench_tags=89, terminal_bench_present=86, terminal_bench_missing=3`; absent: `mteb-leaderboard`, `pytorch-model-recovery`, `reshard-c4-data`, all `alexgshaw/*:20251031`. Exact Docker errors are in the image component report. |
| AppWorld three roles are digest-pinned | REPRODUCED | C3 | `appworld_digest_pins=3`; actor, service and verifier configurations each use `@sha256:`. Full references in `images/configured-references.json`. |
| Terminal-Bench task and CTRF tests=6 / passed=5 / failed=1 | REPRODUCED | C4 | Task `openssl-selfsigned-cert`; independent test-record count `6/5/1`, matching summary; failed test `test_outputs.py::test_python_verification_script`. `net/ctrf.json`. |
| Terminal-Bench raw verifier score 0.0 | REPRODUCED | C4 | Preserved reward bytes exactly `b'0\n'`; execution, verdict and progress scores all `0.0`. Diagnostic publication score is separately `null`. |
| Terminal-Bench 32 model calls | REPRODUCED | C4 | Independently counted `32` reply records, steps `0..31`; trace usage `calls=32`, aggregate `calls=32`, gateway `connections=32`. `net/trace.jsonl`, `net/rederive-output.json`. |
| Receipt isolation and coverage are internally consistent | REPRODUCED | C4 | Six class fields equal `snapshot-service`; actor and verifier IDs differ; verifier image equals captured snapshot; snapshot parent equals actor image. Eligible `1`, selected `1`, expected trials `1`; invalid `0`, unmeasured `1`, measured `0`. Publication `score=null`, reason `policy_enforcement_not_observed`. |
| Preserved Terminal-Bench archive and artifact custody | REPRODUCED | C4 | Archive SHA-256 `6a7c6469ddca5557eea1ade2684848282ff18f6ceb4ae84a4e0463721b200897`; `218/218` inventory files match, zero mismatches. Archived CTRF equals preserved review copy and observer hash. |
| Live policy enforcement / trusted lifecycle attestation | NOT CHECKABLE HERE | C4 | Receipt says `measured=false`, `comparable=false`, `policy_enforcement_observed=false`; snapshot/cleanup `status=unknown`. File consistency cannot establish live enforcement. The merged report already disclaims a measured publication. |

Three full digest recomputations, from C5, also matching fresh inspect:

```text
GAIA           9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13
Tau-bench      beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23
AppWorld actor d3a04ec8e295710347e978d8e58c663161d829e7dfa544da4d82d0d67abbd8eb
```

Reproduction limitation: this checkout contains only `67` tracked files under the original scorer packet. In particular, its cited offline wrapper, BIG-bench metric source, public-QA executor and 2Wiki upstream source are absent. The original registered `/tmp/hg-offscorer` worktree retains them. They were read without modification; needed source bytes, hashes and controlled inputs were copied into this **new** verification packet. `checkout-availability.json` records the missing paths. The original replay command therefore is not self-contained in this checkout, even though its numerical claims can be re-derived using what remains on disk. No missing file was repaired in place.

Detailed commands and raw interpretations: [additional scorers](w-verify-extra-scorers.md), [image custody](w-verify-images.md), [Terminal-Bench receipt](w-verify-net.md). Combined fixture manifest: `tests/fixtures/hg_wverify/SHA256SUMS` (681 files). Registry and unchanged-file validation: [w-verify-validation.txt](w-verify-validation.txt), `valid=true`, 28 datasets, registry SHA-256 unchanged at `600366784b54215632ca3a71fa5e0991baa9a85b1d27676fc13040c848a84799`. Authored-file whitespace checks pass; full whitespace diagnostics retain warnings in byte-preserved upstream copies and raw diagnostic text (`diff-check-full.txt`).

- **Reproduced:** all nine reported scorer results; image counts/pins and preserved-byte digest arithmetic; Terminal-Bench `6/5/1`, raw `0.0`, `32` calls, and receipt consistency.
- **Refuted:** none of the checked numerical claims.
- **Not checkable here:** fresh privileged manifest-store reread, authenticity of the original manifest capture, and live enforcement/lifecycle attestation. The Terminal-Bench measured publication count is checkable and is **zero**.
