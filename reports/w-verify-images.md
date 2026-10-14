# Adversarial image custody verification - w-verify

No image count or digest arithmetic was refuted. Configuration was re-derived from current adapter AST assignments and the actual external Terminal-Bench task TOMLs, before reading the old image inventory. All 94 references then received fresh, read-only `docker image inspect` calls. Capture: `2026-10-14T22:23:26Z`. No container, pull, model, endpoint, registry mutation, or adapter mutation was used.

Reproduction command, run at the repository root:

```sh
python tests/fixtures/hg_wverify/images/verify_images.py > tests/fixtures/hg_wverify/images/verify.stdout.txt 2> tests/fixtures/hg_wverify/images/verify.stderr.txt
```

The script, individual command argv/exit codes/stdout/stderr, source hashes, independently enumerated references, and results are under `tests/fixtures/hg_wverify/images/`. The seven relevant image/task-selection environment overrides were all unset. The Terminal-Bench configured root is `/mnt/20t/xubuqiang/datasets/terminal-bench`; all 89 task manifests were parsed directly with `tomllib`.

| Claim checked | Verdict | Exact command | Raw result |
| --- | --- | --- | --- |
| 94 configured references | REPRODUCED | Reproduction command above, AST/default extraction and TOML enumeration | `reference_count=94`, `unique_reference_count=94`; GAIA=1, Tau-bench=1, AppWorld=3, Terminal-Bench=89 |
| 91 locally present, all 91 with RepoDigests | REPRODUCED | Each `docker image inspect --format '{"Id":{{json .Id}},"RepoDigests":{{json .RepoDigests}},"RepoTags":{{json .RepoTags}},"Size":{{json .Size}}}' REFERENCE`; exact 94 argument vectors in `inspect-*.command.json` | `present_count=91`, `present_with_repo_digests=91`, `missing_count=3` |
| Terminal-Bench has 89 movable tags and 3 absent images | REPRODUCED | Reproduction command above; direct task TOMLs plus exact 89 inspect commands | `terminal_bench_tags=89`, `terminal_bench_present=86`, `terminal_bench_missing=3` |
| GAIA and Tau-bench configured by movable tag | REPRODUCED | Reproduction command above; AST extraction from `data/datasets/{gaia,tau_bench}.py` | `harnessgrad/gaia:20261008`, `harnessgrad/tau-bench:20261006`; both `pin=movable-tag` |
| AppWorld's three roles digest-pinned | REPRODUCED | Reproduction command above; AST extraction from `data/datasets/appworld.py` | `appworld_digest_pins=3`; IMAGE=`d3a04ec8…abbd8eb`, SERVICE_IMAGE=`db09e34e…23aca4`, VERIFIER_IMAGE=`f3cb916b…3e97ca`; full configured refs in `configured-references.json` |
| All 91 present references' RepoDigests independently hash to the preserved raw local manifest bytes | REPRODUCED | Reproduction command above; SHA-256 over `raw_utf8.encode('utf-8')`, ignoring the old `computed_digest`/`matches` fields | `root_digest_hash_matches=91` of 91; all 91 fresh image IDs also match the bound root/config identity. All 101 archived index/child/attestation blobs independently hash correctly: `preserved_manifest_hash_matches=101` of 101 |
| Direct fresh reread of the live daemon's manifest bytes | NOT CHECKABLE HERE | `ls -ld /var/lib/containerd/io.containerd.content.v1.content/blobs/sha256 /var/lib/docker/containerd/daemon/io.containerd.content.v1.content/blobs/sha256`; `sudo -n ctr --address /run/containerd/containerd.sock --namespace moby images list` | Both paths: `权限不够` (permission denied), exit=2; sudo: `需要密码` (password required), exit=1 |

The three absent references produced these exact fresh stderr lines:

```text
Error response from daemon: No such image: alexgshaw/mteb-leaderboard:20251031
Error response from daemon: No such image: alexgshaw/pytorch-model-recovery:20251031
Error response from daemon: No such image: alexgshaw/reshard-c4-data:20251031
```

For a separate native hash cross-check, the exact command was:

```sh
sha256sum tests/fixtures/hg_wverify/images/preserved-raw-manifests/*.json > tests/fixtures/hg_wverify/images/sha256sum-raw-manifests.stdout.txt
```

It rehashes the unmodified UTF-8 byte strings decoded from the old capture, saved individually by the audit script. Three representative raw digest outputs are:

```text
9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13  tests/fixtures/hg_wverify/images/preserved-raw-manifests/9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13.json
beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23  tests/fixtures/hg_wverify/images/preserved-raw-manifests/beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23.json
d3a04ec8e295710347e978d8e58c663161d829e7dfa544da4d82d0d67abbd8eb  tests/fixtures/hg_wverify/images/preserved-raw-manifests/d3a04ec8e295710347e978d8e58c663161d829e7dfa544da4d82d0d67abbd8eb.json
```

These are GAIA, Tau-bench, and AppWorld actor respectively; each matches its fresh RepoDigest. The other AppWorld roles and all 86 present Terminal-Bench references also match. The byte capture's source SHA-256 is recorded in `manifest-rehash.json`, and all input adapter/task-file hashes are recorded. This verifies preserved-byte digest arithmetic and current local image binding; it cannot authenticate the original capture process or establish publisher provenance, layer-byte integrity, or complete ABI closure. Those stronger properties are not inferred from matching hashes.

Reproduced: 94/91/3 counts, 89 Terminal-Bench tags, GAIA/Tau tags, three AppWorld pins, and all 91 RepoDigest roots across 101 preserved manifest hashes. Refuted: none. Not checkable here: fresh direct live-store manifest reread and original capture authenticity.
