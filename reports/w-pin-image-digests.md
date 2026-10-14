# GAIA / Tau default image pins - w-pin

`scorer-offline-closure` and `artifact-only-state-export` remain OPEN. S3 remains PARTIAL.
This change replaces only the two adapter image defaults; environment overrides retain their existing semantics.
Source baseline: `9dab533093d4b71eaddd93c676ff9cd35d61ad43`. Before capture: `2026-10-14T23:29:14.499864+00:00`; after capture: `2026-10-14T23:30:24.777472+00:00`.

## Recomputed references and local resolution

| Adapter | Previous default | New default, read from fresh local RepoDigests and independently rehashed |
| --- | --- | --- |
| `data/datasets/gaia.py:94` | `harnessgrad/gaia:20261008` | `harnessgrad/gaia@sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13` |
| `data/datasets/tau_bench.py:125` | `harnessgrad/tau-bench:20261006` | `harnessgrad/tau-bench@sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23` |

Both original tags and both pinned references resolved with real `docker image inspect` before and after the source edits: eight successful inspections, exit code 0, empty stderr, identical image IDs across each tag/pin pair and across phases. The complete raw outputs are below. Digests were obtained from the daemon, not copied from prior reports or fixtures.

Direct access to the root-owned containerd content directories was denied and `sudo -n true` required a password. Instead, a read-only local Docker export supplied the original OCI bytes:

```text
$ docker image save harnessgrad/gaia@sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13 harnessgrad/tau-bench@sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23
exit_code=0
stderr: ''
```

Python `tarfile.open(fileobj=process.stdout, mode="r|")` streamed that export without extracting files or preserving a full image archive. For each RepoDigest, the exact `blobs/sha256/<digest>` member was read and `hashlib.sha256(raw).hexdigest()` recomputed. Both root OCI indexes are 856 bytes; their hashes match their fresh RepoDigests and Docker descriptors. Each root's two child manifest blobs were also present and rehashed successfully (linux/amd64 runnable manifest and unknown/unknown attestation manifest). This verifies manifest identity, not publisher authentication, compressed-layer rehashing or complete runtime/ABI closure. No container was created or started.

## What this establishes, and what remains

The GAIA and Tau adapter defaults now select the already-local image by OCI index digest instead of a movable tag. Their corresponding `DEFAULT_ENV["image"]` declarations use that value. `HG_GAIA_IMAGE` and `HG_TAU_IMAGE` still win, including a deliberately supplied movable tag or empty string; an override is not made immutable by this default change. AppWorld's three already-pinned roles are untouched.

S3 is still PARTIAL. This does not establish complete dynamic imports/providers, native host dependencies, post-bootstrap `uvx` ABI, actor-snapshot integrity or offline resolver payloads. Full S3 would still require those transitive image/ABI and runtime dependencies to be identified, pinned, available offline and bound to the actual verifier/snapshot lifecycle, together with the remaining Terminal-Bench image pins and availability. It does not establish an offline scorer closure, scorer execution, a valid diagnostic, production authorization, or either shared blocker's closure. No scoring logic, gate, blocker registry, external manifest, historical report, frozen receipt or `runs/` content was changed. No benchmark task, model, GPU, endpoint, registry request, image pull/build or container start was used.

## Terminal-Bench assessment (read-only)

Freshly read the external `*/task.toml` files under `/mnt/20t/xubuqiang/datasets/terminal-bench`: **89 declarations, 89 movable tags**. Real local `docker image inspect --format '{{json .RepoDigests}}' <ref>` returned success with nonempty RepoDigests for **86**, and failed for the same three below. No Terminal-Bench declaration was changed.

Pinning would require a reviewed update to those external task manifests, or an explicit version-controlled task-to-digest mapping consumed by the adapter. Bind each mapping to the task checkout revision and manifest hash; derive each digest from the intended image's actual manifest bytes, verify local resolution and retain the original source reference/provenance. The 86 present images can be pinned separately after that review. The three absent images make a complete, locally verified 89-image pin set impossible from today's local store. They do not prevent pinning the other 86 or obtaining authenticated digests elsewhere, but all three images must be acquired with verified manifests/layers and then resolve locally before claiming full local availability. Do not invent digests or drop those tasks. Acquisition is outside this change.

Fresh absence receipts:

```text
$ docker image inspect --format '{{json .RepoDigests}}' alexgshaw/mteb-leaderboard:20251031
exit_code=1
stdout: '\n'
stderr:
Error response from daemon: No such image: alexgshaw/mteb-leaderboard:20251031
```

```text
$ docker image inspect --format '{{json .RepoDigests}}' alexgshaw/pytorch-model-recovery:20251031
exit_code=1
stdout: '\n'
stderr:
Error response from daemon: No such image: alexgshaw/pytorch-model-recovery:20251031
```

```text
$ docker image inspect --format '{{json .RepoDigests}}' alexgshaw/reshard-c4-data:20251031
exit_code=1
stdout: '\n'
stderr:
Error response from daemon: No such image: alexgshaw/reshard-c4-data:20251031
```

## Focused regression and checker

`tests/quality/test_adapter_image_pins.py` imports each adapter in a fresh namespace and checks a complete `@sha256:<64 lowercase hex>` default plus propagation to `DEFAULT_ENV`. Separate cases check that a tag override and an empty override each still win for both adapters. No Docker or task execution occurs in these tests.

Observed fails-before / passes-after: **2 failed, 4 passed** on the original defaults; **6 passed** after changing only the defaults. The two failures were precisely the missing `@sha256:` assertions. `python3 tools/check_dataset_blockers.py` remained valid after each edit; existing evidence locators still appear verbatim. Full test and checker output: `reports/w-pin-validation.txt`.

## Exact root manifest bytes

The JSON code block body for each root is its exact UTF-8 preimage, with no trailing newline (the newline separating the closing brace from the Markdown fence is excluded). Rehash these bytes, not a reserialized JSON object.

### harnessgrad/gaia@sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13

Tar member: `blobs/sha256/9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13`; bytes: `856`; computed: `sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13`.

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.index.v1+json",
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "digest": "sha256:bf3403993730a8f636793da2f62243348858bb15a8eef3dbdb9193eb2c4f7b9a",
      "size": 1628,
      "platform": {
        "architecture": "amd64",
        "os": "linux"
      }
    },
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "digest": "sha256:85fb7737568f2ea265432c7c0ed6fe881add6b281aaa4687f063f709b29ced93",
      "size": 566,
      "annotations": {
        "vnd.docker.reference.digest": "sha256:bf3403993730a8f636793da2f62243348858bb15a8eef3dbdb9193eb2c4f7b9a",
        "vnd.docker.reference.type": "attestation-manifest"
      },
      "platform": {
        "architecture": "unknown",
        "os": "unknown"
      }
    }
  ]
}
```

Child manifest hashes recomputed from the same stream:

- `sha256:bf3403993730a8f636793da2f62243348858bb15a8eef3dbdb9193eb2c4f7b9a` (1628 bytes; `linux/amd64`).
- `sha256:85fb7737568f2ea265432c7c0ed6fe881add6b281aaa4687f063f709b29ced93` (566 bytes; `unknown/unknown`).

### harnessgrad/tau-bench@sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23

Tar member: `blobs/sha256/beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23`; bytes: `856`; computed: `sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23`.

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.index.v1+json",
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "digest": "sha256:7b339d58c882927ddd14bb3e690d8d6cd9344f80b334376851de037edc9185ff",
      "size": 2190,
      "platform": {
        "architecture": "amd64",
        "os": "linux"
      }
    },
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "digest": "sha256:c591c74c75b82dc7e23fb8f04b8be5bf7005846fbcef96d4fe2e8a91553b8d11",
      "size": 566,
      "annotations": {
        "vnd.docker.reference.digest": "sha256:7b339d58c882927ddd14bb3e690d8d6cd9344f80b334376851de037edc9185ff",
        "vnd.docker.reference.type": "attestation-manifest"
      },
      "platform": {
        "architecture": "unknown",
        "os": "unknown"
      }
    }
  ]
}
```

Child manifest hashes recomputed from the same stream:

- `sha256:7b339d58c882927ddd14bb3e690d8d6cd9344f80b334376851de037edc9185ff` (2190 bytes; `linux/amd64`).
- `sha256:c591c74c75b82dc7e23fb8f04b8be5bf7005846fbcef96d4fe2e8a91553b8d11` (566 bytes; `unknown/unknown`).

## Raw Docker inspect output before source changes

```text
$ docker image inspect harnessgrad/gaia:20261008
exit_code=0
stdout:
[
    {
        "Id": "sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13",
        "RepoTags": [
            "harnessgrad/gaia:20261008"
        ],
        "RepoDigests": [
            "harnessgrad/gaia@sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13"
        ],
        "Comment": "buildkit.dockerfile.v0",
        "Created": "2026-10-08T21:59:12.767450604+08:00",
        "Config": {
            "Env": [
                "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "LANG=C.UTF-8",
                "GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305",
                "PYTHON_VERSION=3.12.15",
                "PYTHON_SHA256=c2c4321961fab0fb999d66e0cecf521c2ab3994c7992873ea99e306c1094fd5a",
                "DEBIAN_FRONTEND=noninteractive",
                "PIP_DISABLE_PIP_VERSION_CHECK=1"
            ],
            "Cmd": [
                "python3"
            ],
            "WorkingDir": "/app"
        },
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 102621041,
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:15f1c8eb1ab18eae260c7fb6296434cbe1ff0e1e30fd814ae92a80dd54005e62",
                "sha256:e1fa2746ad6d51e7de9171dfcbb1fe93d01d51c5d8d3623e0c3b223076dc5d23",
                "sha256:b361fa3b97940ee89a1aab8fde1027e47ab2c2e700ca2f8d5988ad2c64386e5c",
                "sha256:dca2a125b4903477bcb42084172cfc98865299810620ffd617bf6e12dd83d89f",
                "sha256:ce0aea0bb80840e885b496191b5a7f5bf8c47ef265a2a01944f5ff1e0394c7ea",
                "sha256:ef669068f556d4d8bec4ab498c087a070329fcba7af75be93d6135ddac5b1ee2",
                "sha256:baa574446e792062c14c684b58198c1256c586b262cfb270aae9e99efad17ccd"
            ]
        },
        "Metadata": {
            "LastTagTime": "2026-10-08T13:59:28.1064438Z"
        },
        "Descriptor": {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "digest": "sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13",
            "size": 856
        },
        "Identity": {
            "Build": [
                {
                    "Ref": "ypkrdfde81bvin6o2q5i7o8zm",
                    "CreatedAt": "2026-10-08T21:59:30.92628798+08:00"
                }
            ]
        }
    }
]
stderr: ''
```

```text
$ docker image inspect harnessgrad/gaia@sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13
exit_code=0
stdout:
[
    {
        "Id": "sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13",
        "RepoTags": [
            "harnessgrad/gaia:20261008"
        ],
        "RepoDigests": [
            "harnessgrad/gaia@sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13"
        ],
        "Comment": "buildkit.dockerfile.v0",
        "Created": "2026-10-08T21:59:12.767450604+08:00",
        "Config": {
            "Env": [
                "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "LANG=C.UTF-8",
                "GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305",
                "PYTHON_VERSION=3.12.15",
                "PYTHON_SHA256=c2c4321961fab0fb999d66e0cecf521c2ab3994c7992873ea99e306c1094fd5a",
                "DEBIAN_FRONTEND=noninteractive",
                "PIP_DISABLE_PIP_VERSION_CHECK=1"
            ],
            "Cmd": [
                "python3"
            ],
            "WorkingDir": "/app"
        },
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 102621041,
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:15f1c8eb1ab18eae260c7fb6296434cbe1ff0e1e30fd814ae92a80dd54005e62",
                "sha256:e1fa2746ad6d51e7de9171dfcbb1fe93d01d51c5d8d3623e0c3b223076dc5d23",
                "sha256:b361fa3b97940ee89a1aab8fde1027e47ab2c2e700ca2f8d5988ad2c64386e5c",
                "sha256:dca2a125b4903477bcb42084172cfc98865299810620ffd617bf6e12dd83d89f",
                "sha256:ce0aea0bb80840e885b496191b5a7f5bf8c47ef265a2a01944f5ff1e0394c7ea",
                "sha256:ef669068f556d4d8bec4ab498c087a070329fcba7af75be93d6135ddac5b1ee2",
                "sha256:baa574446e792062c14c684b58198c1256c586b262cfb270aae9e99efad17ccd"
            ]
        },
        "Metadata": {
            "LastTagTime": "2026-10-08T13:59:28.1064438Z"
        },
        "Descriptor": {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "digest": "sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13",
            "size": 856
        },
        "Identity": {
            "Build": [
                {
                    "Ref": "ypkrdfde81bvin6o2q5i7o8zm",
                    "CreatedAt": "2026-10-08T21:59:30.92628798+08:00"
                }
            ]
        }
    }
]
stderr: ''
```

```text
$ docker image inspect harnessgrad/tau-bench:20261006
exit_code=0
stdout:
[
    {
        "Id": "sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23",
        "RepoTags": [
            "harnessgrad/tau-bench:20261006"
        ],
        "RepoDigests": [
            "harnessgrad/tau-bench@sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23"
        ],
        "Comment": "buildkit.dockerfile.v0",
        "Created": "2026-10-06T19:27:05.173276419+08:00",
        "Config": {
            "Env": [
                "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "LANG=C.UTF-8",
                "GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D",
                "PYTHON_VERSION=3.11.16",
                "PYTHON_SHA256=91bcdebfdde239a003ae93738a7fce0f9230fee5c4bc2b86f6e6e8c6f98aabe8",
                "PYTHONDONTWRITEBYTECODE=1"
            ],
            "Cmd": [
                "python3"
            ],
            "WorkingDir": "/app",
            "Labels": {
                "harnessgrad.dataset": "tau_bench",
                "harnessgrad.provenance": "data/tau_bench/PROVENANCE.json (upstream sierra-research/tau-bench @ 59a200c)",
                "org.opencontainers.image.description": "tau-bench retail+airline tools, data and policy behind the tau CLI",
                "org.opencontainers.image.title": "harnessgrad/tau-bench"
            }
        },
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 46091804,
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:6f94328331290cbd81edab450664d42da7b64c191416c9346cd5d28c84f76035",
                "sha256:275f0a9e4758b8a31c628ab748d8184bd103fb27ec8aeff6b588003a3056d082",
                "sha256:3d7dddf62be3a47f3c072a9dc069ac228beea659375d9fff022792deaaf08d61",
                "sha256:1a8800d1b976e9a254659bbce8213f99d55639c12cc4d2ebecafe95a163797c5",
                "sha256:c5409f19ff46d3a1503ac91777c7c0f63e7f11fefaa32c77cd60e32d2fdb6085",
                "sha256:268cae486cb9ef8213ce4e6d69d5c19d6fb92469c0d7bb1f67eaa69edd3aedb2",
                "sha256:3a1e24fe3664b4f4d9bdaa8538c273d00a2d9f8798d9a6dd25ae49cd18d7c414",
                "sha256:eddf15396b4c9d98be303b32faabaf9e2cee131270952052f1157921b73b83cd",
                "sha256:21330395d4b73e26be5f02f86630bc1207f4d3229b90f9fc48a354229b0a1b4a",
                "sha256:0b4bbb0a67c653a236b09ec73c629f38bc893020ace1e69f5a1c6489498b07ba"
            ]
        },
        "Metadata": {
            "LastTagTime": "2026-10-06T11:27:05.649061151Z"
        },
        "Descriptor": {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "digest": "sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23",
            "size": 856
        },
        "Identity": {
            "Build": [
                {
                    "Ref": "pjxso354t75zt9uoelvxhm5ce",
                    "CreatedAt": "2026-10-06T19:27:05.725897013+08:00"
                }
            ]
        }
    }
]
stderr: ''
```

```text
$ docker image inspect harnessgrad/tau-bench@sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23
exit_code=0
stdout:
[
    {
        "Id": "sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23",
        "RepoTags": [
            "harnessgrad/tau-bench:20261006"
        ],
        "RepoDigests": [
            "harnessgrad/tau-bench@sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23"
        ],
        "Comment": "buildkit.dockerfile.v0",
        "Created": "2026-10-06T19:27:05.173276419+08:00",
        "Config": {
            "Env": [
                "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "LANG=C.UTF-8",
                "GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D",
                "PYTHON_VERSION=3.11.16",
                "PYTHON_SHA256=91bcdebfdde239a003ae93738a7fce0f9230fee5c4bc2b86f6e6e8c6f98aabe8",
                "PYTHONDONTWRITEBYTECODE=1"
            ],
            "Cmd": [
                "python3"
            ],
            "WorkingDir": "/app",
            "Labels": {
                "harnessgrad.dataset": "tau_bench",
                "harnessgrad.provenance": "data/tau_bench/PROVENANCE.json (upstream sierra-research/tau-bench @ 59a200c)",
                "org.opencontainers.image.description": "tau-bench retail+airline tools, data and policy behind the tau CLI",
                "org.opencontainers.image.title": "harnessgrad/tau-bench"
            }
        },
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 46091804,
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:6f94328331290cbd81edab450664d42da7b64c191416c9346cd5d28c84f76035",
                "sha256:275f0a9e4758b8a31c628ab748d8184bd103fb27ec8aeff6b588003a3056d082",
                "sha256:3d7dddf62be3a47f3c072a9dc069ac228beea659375d9fff022792deaaf08d61",
                "sha256:1a8800d1b976e9a254659bbce8213f99d55639c12cc4d2ebecafe95a163797c5",
                "sha256:c5409f19ff46d3a1503ac91777c7c0f63e7f11fefaa32c77cd60e32d2fdb6085",
                "sha256:268cae486cb9ef8213ce4e6d69d5c19d6fb92469c0d7bb1f67eaa69edd3aedb2",
                "sha256:3a1e24fe3664b4f4d9bdaa8538c273d00a2d9f8798d9a6dd25ae49cd18d7c414",
                "sha256:eddf15396b4c9d98be303b32faabaf9e2cee131270952052f1157921b73b83cd",
                "sha256:21330395d4b73e26be5f02f86630bc1207f4d3229b90f9fc48a354229b0a1b4a",
                "sha256:0b4bbb0a67c653a236b09ec73c629f38bc893020ace1e69f5a1c6489498b07ba"
            ]
        },
        "Metadata": {
            "LastTagTime": "2026-10-06T11:27:05.649061151Z"
        },
        "Descriptor": {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "digest": "sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23",
            "size": 856
        },
        "Identity": {
            "Build": [
                {
                    "Ref": "pjxso354t75zt9uoelvxhm5ce",
                    "CreatedAt": "2026-10-06T19:27:05.725897013+08:00"
                }
            ]
        }
    }
]
stderr: ''
```

## Raw Docker inspect output after source changes

```text
$ docker image inspect harnessgrad/gaia:20261008
exit_code=0
stdout:
[
    {
        "Id": "sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13",
        "RepoTags": [
            "harnessgrad/gaia:20261008"
        ],
        "RepoDigests": [
            "harnessgrad/gaia@sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13"
        ],
        "Comment": "buildkit.dockerfile.v0",
        "Created": "2026-10-08T21:59:12.767450604+08:00",
        "Config": {
            "Env": [
                "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "LANG=C.UTF-8",
                "GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305",
                "PYTHON_VERSION=3.12.15",
                "PYTHON_SHA256=c2c4321961fab0fb999d66e0cecf521c2ab3994c7992873ea99e306c1094fd5a",
                "DEBIAN_FRONTEND=noninteractive",
                "PIP_DISABLE_PIP_VERSION_CHECK=1"
            ],
            "Cmd": [
                "python3"
            ],
            "WorkingDir": "/app"
        },
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 102621041,
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:15f1c8eb1ab18eae260c7fb6296434cbe1ff0e1e30fd814ae92a80dd54005e62",
                "sha256:e1fa2746ad6d51e7de9171dfcbb1fe93d01d51c5d8d3623e0c3b223076dc5d23",
                "sha256:b361fa3b97940ee89a1aab8fde1027e47ab2c2e700ca2f8d5988ad2c64386e5c",
                "sha256:dca2a125b4903477bcb42084172cfc98865299810620ffd617bf6e12dd83d89f",
                "sha256:ce0aea0bb80840e885b496191b5a7f5bf8c47ef265a2a01944f5ff1e0394c7ea",
                "sha256:ef669068f556d4d8bec4ab498c087a070329fcba7af75be93d6135ddac5b1ee2",
                "sha256:baa574446e792062c14c684b58198c1256c586b262cfb270aae9e99efad17ccd"
            ]
        },
        "Metadata": {
            "LastTagTime": "2026-10-08T13:59:28.1064438Z"
        },
        "Descriptor": {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "digest": "sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13",
            "size": 856
        },
        "Identity": {
            "Build": [
                {
                    "Ref": "ypkrdfde81bvin6o2q5i7o8zm",
                    "CreatedAt": "2026-10-08T21:59:30.92628798+08:00"
                }
            ]
        }
    }
]
stderr: ''
```

```text
$ docker image inspect harnessgrad/gaia@sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13
exit_code=0
stdout:
[
    {
        "Id": "sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13",
        "RepoTags": [
            "harnessgrad/gaia:20261008"
        ],
        "RepoDigests": [
            "harnessgrad/gaia@sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13"
        ],
        "Comment": "buildkit.dockerfile.v0",
        "Created": "2026-10-08T21:59:12.767450604+08:00",
        "Config": {
            "Env": [
                "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "LANG=C.UTF-8",
                "GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305",
                "PYTHON_VERSION=3.12.15",
                "PYTHON_SHA256=c2c4321961fab0fb999d66e0cecf521c2ab3994c7992873ea99e306c1094fd5a",
                "DEBIAN_FRONTEND=noninteractive",
                "PIP_DISABLE_PIP_VERSION_CHECK=1"
            ],
            "Cmd": [
                "python3"
            ],
            "WorkingDir": "/app"
        },
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 102621041,
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:15f1c8eb1ab18eae260c7fb6296434cbe1ff0e1e30fd814ae92a80dd54005e62",
                "sha256:e1fa2746ad6d51e7de9171dfcbb1fe93d01d51c5d8d3623e0c3b223076dc5d23",
                "sha256:b361fa3b97940ee89a1aab8fde1027e47ab2c2e700ca2f8d5988ad2c64386e5c",
                "sha256:dca2a125b4903477bcb42084172cfc98865299810620ffd617bf6e12dd83d89f",
                "sha256:ce0aea0bb80840e885b496191b5a7f5bf8c47ef265a2a01944f5ff1e0394c7ea",
                "sha256:ef669068f556d4d8bec4ab498c087a070329fcba7af75be93d6135ddac5b1ee2",
                "sha256:baa574446e792062c14c684b58198c1256c586b262cfb270aae9e99efad17ccd"
            ]
        },
        "Metadata": {
            "LastTagTime": "2026-10-08T13:59:28.1064438Z"
        },
        "Descriptor": {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "digest": "sha256:9cc27f813e596542d3f3447de10fc1166b27d66e282f271b2e057ee8ca0e0e13",
            "size": 856
        },
        "Identity": {
            "Build": [
                {
                    "Ref": "ypkrdfde81bvin6o2q5i7o8zm",
                    "CreatedAt": "2026-10-08T21:59:30.92628798+08:00"
                }
            ]
        }
    }
]
stderr: ''
```

```text
$ docker image inspect harnessgrad/tau-bench:20261006
exit_code=0
stdout:
[
    {
        "Id": "sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23",
        "RepoTags": [
            "harnessgrad/tau-bench:20261006"
        ],
        "RepoDigests": [
            "harnessgrad/tau-bench@sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23"
        ],
        "Comment": "buildkit.dockerfile.v0",
        "Created": "2026-10-06T19:27:05.173276419+08:00",
        "Config": {
            "Env": [
                "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "LANG=C.UTF-8",
                "GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D",
                "PYTHON_VERSION=3.11.16",
                "PYTHON_SHA256=91bcdebfdde239a003ae93738a7fce0f9230fee5c4bc2b86f6e6e8c6f98aabe8",
                "PYTHONDONTWRITEBYTECODE=1"
            ],
            "Cmd": [
                "python3"
            ],
            "WorkingDir": "/app",
            "Labels": {
                "harnessgrad.dataset": "tau_bench",
                "harnessgrad.provenance": "data/tau_bench/PROVENANCE.json (upstream sierra-research/tau-bench @ 59a200c)",
                "org.opencontainers.image.description": "tau-bench retail+airline tools, data and policy behind the tau CLI",
                "org.opencontainers.image.title": "harnessgrad/tau-bench"
            }
        },
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 46091804,
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:6f94328331290cbd81edab450664d42da7b64c191416c9346cd5d28c84f76035",
                "sha256:275f0a9e4758b8a31c628ab748d8184bd103fb27ec8aeff6b588003a3056d082",
                "sha256:3d7dddf62be3a47f3c072a9dc069ac228beea659375d9fff022792deaaf08d61",
                "sha256:1a8800d1b976e9a254659bbce8213f99d55639c12cc4d2ebecafe95a163797c5",
                "sha256:c5409f19ff46d3a1503ac91777c7c0f63e7f11fefaa32c77cd60e32d2fdb6085",
                "sha256:268cae486cb9ef8213ce4e6d69d5c19d6fb92469c0d7bb1f67eaa69edd3aedb2",
                "sha256:3a1e24fe3664b4f4d9bdaa8538c273d00a2d9f8798d9a6dd25ae49cd18d7c414",
                "sha256:eddf15396b4c9d98be303b32faabaf9e2cee131270952052f1157921b73b83cd",
                "sha256:21330395d4b73e26be5f02f86630bc1207f4d3229b90f9fc48a354229b0a1b4a",
                "sha256:0b4bbb0a67c653a236b09ec73c629f38bc893020ace1e69f5a1c6489498b07ba"
            ]
        },
        "Metadata": {
            "LastTagTime": "2026-10-06T11:27:05.649061151Z"
        },
        "Descriptor": {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "digest": "sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23",
            "size": 856
        },
        "Identity": {
            "Build": [
                {
                    "Ref": "pjxso354t75zt9uoelvxhm5ce",
                    "CreatedAt": "2026-10-06T19:27:05.725897013+08:00"
                }
            ]
        }
    }
]
stderr: ''
```

```text
$ docker image inspect harnessgrad/tau-bench@sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23
exit_code=0
stdout:
[
    {
        "Id": "sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23",
        "RepoTags": [
            "harnessgrad/tau-bench:20261006"
        ],
        "RepoDigests": [
            "harnessgrad/tau-bench@sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23"
        ],
        "Comment": "buildkit.dockerfile.v0",
        "Created": "2026-10-06T19:27:05.173276419+08:00",
        "Config": {
            "Env": [
                "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "LANG=C.UTF-8",
                "GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D",
                "PYTHON_VERSION=3.11.16",
                "PYTHON_SHA256=91bcdebfdde239a003ae93738a7fce0f9230fee5c4bc2b86f6e6e8c6f98aabe8",
                "PYTHONDONTWRITEBYTECODE=1"
            ],
            "Cmd": [
                "python3"
            ],
            "WorkingDir": "/app",
            "Labels": {
                "harnessgrad.dataset": "tau_bench",
                "harnessgrad.provenance": "data/tau_bench/PROVENANCE.json (upstream sierra-research/tau-bench @ 59a200c)",
                "org.opencontainers.image.description": "tau-bench retail+airline tools, data and policy behind the tau CLI",
                "org.opencontainers.image.title": "harnessgrad/tau-bench"
            }
        },
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 46091804,
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:6f94328331290cbd81edab450664d42da7b64c191416c9346cd5d28c84f76035",
                "sha256:275f0a9e4758b8a31c628ab748d8184bd103fb27ec8aeff6b588003a3056d082",
                "sha256:3d7dddf62be3a47f3c072a9dc069ac228beea659375d9fff022792deaaf08d61",
                "sha256:1a8800d1b976e9a254659bbce8213f99d55639c12cc4d2ebecafe95a163797c5",
                "sha256:c5409f19ff46d3a1503ac91777c7c0f63e7f11fefaa32c77cd60e32d2fdb6085",
                "sha256:268cae486cb9ef8213ce4e6d69d5c19d6fb92469c0d7bb1f67eaa69edd3aedb2",
                "sha256:3a1e24fe3664b4f4d9bdaa8538c273d00a2d9f8798d9a6dd25ae49cd18d7c414",
                "sha256:eddf15396b4c9d98be303b32faabaf9e2cee131270952052f1157921b73b83cd",
                "sha256:21330395d4b73e26be5f02f86630bc1207f4d3229b90f9fc48a354229b0a1b4a",
                "sha256:0b4bbb0a67c653a236b09ec73c629f38bc893020ace1e69f5a1c6489498b07ba"
            ]
        },
        "Metadata": {
            "LastTagTime": "2026-10-06T11:27:05.649061151Z"
        },
        "Descriptor": {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "digest": "sha256:beda1b01f43ca4912555b44ccdfe25b1fe384b42e77d87a5316302ccf493fb23",
            "size": 856
        },
        "Identity": {
            "Build": [
                {
                    "Ref": "pjxso354t75zt9uoelvxhm5ce",
                    "CreatedAt": "2026-10-06T19:27:05.725897013+08:00"
                }
            ]
        }
    }
]
stderr: ''
```
