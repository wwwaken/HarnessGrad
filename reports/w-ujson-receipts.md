# w-ujson: image-bound offline runtime receipts

**Runtime checks pass; `twowikimultihopqa / ujson-native-offline-closure` remains external.** The unmet clause is authenticated original wheel source/build custody. This work runs fabricated controls only, without a benchmark, model, GPU or endpoint call. Production scoring code is unchanged.

## Pinned distribution and recomputed identities

- Base: `python@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b`. Raw pull: `tests/fixtures/hg_wujson/base-pull.stdout.txt`; inspect: `tests/fixtures/hg_wujson/base-inspect.stdout.txt`. The floating discovery tag was resolved before construction or runtime checks.
- The original OCI index bytes in `tests/fixtures/hg_wujson/base-manifest-proxy.stdout.txt` recompute to `sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b`. Its Linux/amd64 child is `sha256:edd0b3ec946cc68bd20e39480bd03929016d0fb6254cbf870cd3bc55ea25116d`; those raw bytes and their recomputed identity are in `tests/fixtures/hg_wujson/base-amd64-manifest.stdout.txt`. Dockerfile pins the index and architecture.
- Built local distribution: `hg-wujson-closure@sha256:1f5686c525d48af356933060335d6876455bf371229e8e66c3a4a7fca5014e45`. Build context `tests/fixtures/hg_wujson/deployment-v6/`, Dockerfile and `INPUTS.sha256`; build command `tests/fixtures/hg_wujson/deployment-v6-build.command.json`, raw log `tests/fixtures/hg_wujson/deployment-v6-build.stderr.txt`, image inspect `tests/fixtures/hg_wujson/deployment-v6-inspect.stdout.txt`. The image remains locally available for parent review. This is a new distribution, not a rollout to existing platform services.
- Exact wheel SHA-256, recomputed from the wheel used: `f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1`. Bytes: `53686`; original task-226 wheel and every copied distribution wheel match. Paths: `tests/fixtures/hg_wujson/wheel.sha256`, `tests/fixtures/hg_wujson/deployment-v6/ujson-5.10.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl`, `tests/fixtures/hg_wujson/runtime-v9/native-import.json`.
- Runtime: `3.12.15 (main, Oct  6 2026, 04:39:41) [GCC 12.2.0]`; pip `25.0.1`; glibc `2.36`. Raw native output `tests/fixtures/hg_wujson/runtime-v9/native-import.json`; glibc command/output `tests/fixtures/hg_wujson/runtime-v9/providers/glibc.command.json` and `.stdout.txt`. This tests CPython 3.12.15, not the older host 3.12.4 or all manylinux baselines.

The recipe installs the exact wheel in `/opt/ujson-runtime`, and copies **both complete notices** into `/usr/local/share/licenses/hg-wujson/`. The offline run reads and hashes these files directly from the read-only image, with only the receipt directory mounted. Both the fresh and deployed native-import receipts verify the notice bytes. Their source files are unchanged B6 originals.

- `/usr/local/share/licenses/hg-wujson/ujson-LICENSE.txt`: `36866344f0a486541bd9800f1a407a056c0c214a82c658f059694daf3dc394d2` (image readback in `tests/fixtures/hg_wujson/runtime-v9/native-import.json` and `deployed-native-import.json`).
- `/usr/local/share/licenses/hg-wujson/double-conversion-LICENSE`: `4af93c12062c58058378de2397dc1c92bbff9ddfb1d583a01c84127557ce97ca` (image readback in `tests/fixtures/hg_wujson/runtime-v9/native-import.json` and `deployed-native-import.json`).

The image also carries the unchanged evaluators, their Apache license and custody/source observations. The Docker build uses `--network=none` and `RUN --network=none`; its installer report is copied to `tests/fixtures/hg_wujson/runtime-v9-build-install-report.json`. No source build or package index access occurs.

## Exact network-denied commands and raw output

The successful launch is recorded in `tests/fixtures/hg_wujson/runtime-v9-create.command.json`; the exact command is:

```sh
docker create --name hg-wujson-20261014T211147Z --pull=never --platform=linux/amd64 --network=none --read-only --user 1026:1026 --cpus=1 --memory=512m --memory-swap=512m --pids-limit=128 --cap-drop=ALL --security-opt=no-new-privileges --tmpfs=/tmp:rw,exec,nosuid,nodev,size=128m --mount type=bind,src=/tmp/hg-ujson/tests/fixtures/hg_wujson/runtime-v9,dst=/receipts --entrypoint=/bin/sh sha256:1f5686c525d48af356933060335d6876455bf371229e8e66c3a4a7fca5014e45 /opt/hg-wujson/closure.sh
```

It was started with the command recorded in `tests/fixtures/hg_wujson/runtime-v9-start.command.json`:

```sh
docker start --attach hg-wujson-20261014T211147Z
```

The image-resident `/opt/hg-wujson/closure.sh` executed these exact commands (source `tests/fixtures/hg_wujson/deployment-v6/closure.sh`; complete shell trace `tests/fixtures/hg_wujson/runtime-v9-start.stderr.txt`):

```sh
#!/bin/sh
set -eux
python -I -B /opt/hg-wujson/network.py > /receipts/network-denial.json
python -I -B -m venv /tmp/fresh-ujson
PIP_CONFIG_FILE=/dev/null /tmp/fresh-ujson/bin/python -I -B -m pip \
  --isolated --disable-pip-version-check --no-cache-dir install \
  --no-index --find-links=/opt/hg-wujson --require-hashes --only-binary=:all: \
  --no-deps --no-compile --report=/receipts/pip-install-report.json \
  -r /opt/hg-wujson/requirements.txt > /receipts/pip-install.stdout.txt 2> /receipts/pip-install.stderr.txt
/tmp/fresh-ujson/bin/python -I -B /opt/hg-wujson/native.py > /receipts/native-import.json
LD_BIND_NOW=1 LD_DEBUG=libs,versions,bindings /tmp/fresh-ujson/bin/python -I -B \
  /opt/hg-wujson/native.py > /receipts/loader-import.stdout.txt 2> /receipts/loader-debug.stderr.txt
/tmp/fresh-ujson/bin/python -I -B /opt/hg-wujson/synthetic.py > /receipts/synthetic-evaluator.json
/tmp/fresh-ujson/bin/python -I -B /opt/hg-wujson/providers.py > /receipts/providers-summary.json
python -I -B /opt/hg-wujson/native.py > /receipts/deployed-native-import.json
```

Container inspect before/after: `tests/fixtures/hg_wujson/runtime-v9-inspect-before.stdout.txt`, `tests/fixtures/hg_wujson/runtime-v9-inspect-after.stdout.txt`. They bind the final image, `NetworkMode=none`, read-only root, recorded user, CPU/memory/PID settings and the sole receipt bind. The last inspect records `ExitCode=0`, `OOMKilled=false`. The `/tmp` tmpfs explicitly allows native-code execution; no network or other gate was relaxed. Limits are requested Docker settings, not measured consumption.

Actual network-denial probe output (`tests/fixtures/hg_wujson/runtime-v9/network-denial.json`; command in the shell trace):

```json
{
  "interfaces": [
    "lo"
  ],
  "ipv4_routes": "Iface\tDestination\tGateway \tFlags\tRefCnt\tUse\tMetric\tMask\t\tMTU\tWindow\tIRTT                                                       \n",
  "reserved_documentation_ip": "203.0.113.1",
  "connect_ex_errno": 101,
  "errno_name": "ENETUNREACH",
  "passed": true
}
```

Fresh offline pip stdout (`tests/fixtures/hg_wujson/runtime-v9/pip-install.stdout.txt`; stderr is empty; machine report `pip-install-report.json` in the same directory):

```text
Looking in links: /opt/hg-wujson
Processing /opt/hg-wujson/ujson-5.10.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (from -r /opt/hg-wujson/requirements.txt (line 1))
Installing collected packages: ujson
Successfully installed ujson-5.10.0
```

Native import, exact wheel-to-installed-member comparison and fabricated encode/decode output (`tests/fixtures/hg_wujson/runtime-v9/native-import.json`):

```json
{
  "python": "3.12.15 (main, Oct  6 2026, 04:39:41) [GCC 12.2.0]",
  "executable": "/tmp/fresh-ujson/bin/python",
  "platform": "Linux-6.8.0-136-generic-x86_64-with-glibc2.36",
  "machine": "x86_64",
  "glibc": [
    "glibc",
    "2.36"
  ],
  "pip": "25.0.1",
  "ujson": "5.10.0",
  "module": "/tmp/fresh-ujson/lib/python3.12/site-packages/ujson.cpython-312-x86_64-linux-gnu.so",
  "import_spec": "ModuleSpec(name='ujson', loader=<_frozen_importlib_external.ExtensionFileLoader object at 0x72f081cde750>, origin='/tmp/fresh-ujson/lib/python3.12/site-packages/ujson.cpython-312-x86_64-linux-gnu.so')",
  "wheel_sha256": "f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1",
  "installed_members": {
    "ujson.cpython-312-x86_64-linux-gnu.so": {
      "installed_path": "/tmp/fresh-ujson/lib/python3.12/site-packages/ujson.cpython-312-x86_64-linux-gnu.so",
      "sha256": "deb036e60d4b61104bad389783094ebb09a35dbdecd21aeea572968762c3be5c"
    },
    "ujson-5.10.0.dist-info/LICENSE.txt": {
      "installed_path": "/tmp/fresh-ujson/lib/python3.12/site-packages/ujson-5.10.0.dist-info/LICENSE.txt",
      "sha256": "36866344f0a486541bd9800f1a407a056c0c214a82c658f059694daf3dc394d2"
    },
    "ujson-5.10.0.dist-info/METADATA": {
      "installed_path": "/tmp/fresh-ujson/lib/python3.12/site-packages/ujson-5.10.0.dist-info/METADATA",
      "sha256": "b7a07b8cfb552e87ddf1ff235080d3c23ab1dd3fdba0e53775ba456e7ba09488"
    },
    "ujson-5.10.0.dist-info/top_level.txt": {
      "installed_path": "/tmp/fresh-ujson/lib/python3.12/site-packages/ujson-5.10.0.dist-info/top_level.txt",
      "sha256": "201318b952021d68bdc6798c376d9434c10561fd784dc702ee8f6e60f872720d"
    },
    "ujson-5.10.0.dist-info/WHEEL": {
      "installed_path": "/tmp/fresh-ujson/lib/python3.12/site-packages/ujson-5.10.0.dist-info/WHEEL",
      "sha256": "3afb6f9dba5c6b11dae5381781f0b8f04e8903bccbafbb2f32ca4f3fb564e68f"
    }
  },
  "notices": {
    "/usr/local/share/licenses/hg-wujson/ujson-LICENSE.txt": "36866344f0a486541bd9800f1a407a056c0c214a82c658f059694daf3dc394d2",
    "/usr/local/share/licenses/hg-wujson/double-conversion-LICENSE": "4af93c12062c58058378de2397dc1c92bbff9ddfb1d583a01c84127557ce97ca"
  },
  "synthetic_roundtrip": {
    "synthetic": [
      "fictional azure",
      0.125,
      1e+100,
      true,
      null,
      "\u96ea"
    ]
  },
  "passed": true
}
```

Independent eager binding/import uses `LD_BIND_NOW=1 LD_DEBUG=libs,versions,bindings`. Full raw loader trace: `tests/fixtures/hg_wujson/runtime-v9/loader-debug.stderr.txt`; import stdout: `loader-import.stdout.txt` in that directory. It records actual paths, version checks and CPython symbol bindings during import, rather than a standalone `ldd -r` process that lacks Python.

## Recursive loader and symbol providers

Collector: `tests/fixtures/hg_wujson/deployment-v6/providers.py`, executed by the shell above. Each ordinary ELF is inspected with the exact command `readelf -h -l -d -V --dyn-syms -W <path>` and `ldd -v <path>`. The exact argv, return code, stdout and stderr are retained per file under `tests/fixtures/hg_wujson/runtime-v9/providers/<basename>.{readelf,ldd}.{command.json,stdout.txt,stderr.txt}`. The queue begins at the installed ujson extension and interpreter and follows every resolved recursive path. Raw loader configuration/cache, package inventory, process maps and tool versions are in that directory.

Provider files and SHA-256 values, read inside the container (`tests/fixtures/hg_wujson/runtime-v9/providers/files.json`):

- `/tmp/fresh-ujson/lib/python3.12/site-packages/ujson.cpython-312-x86_64-linux-gnu.so` — `deb036e60d4b61104bad389783094ebb09a35dbdecd21aeea572968762c3be5c`.
- `/usr/local/bin/python3.12` — `837a48d7afd08447fb43e28b282026fadb59368620072e57e01f66d12977e5ce`.
- `/usr/lib/x86_64-linux-gnu/libc.so.6` — `6b4a45352fd0c540a9c7c718f35ce8c8e46a4e482f9d3885a910c32d1a0e1421`.
- `/usr/lib/x86_64-linux-gnu/libgcc_s.so.1` — `2bd1552c47799ef67e701e81d4383061fd76059868e446e63560f0dd0d5ec14e`.
- `/usr/lib/x86_64-linux-gnu/libm.so.6` — `7f2ca87f652f56b094462474b076749e90e689d0ecb9cb63c7679820b271b4e7`.
- `/usr/lib/x86_64-linux-gnu/libpthread.so.0` — `b93a680da8a05b939b235c1533572e7a2f6d3d8808bf70209997edc64ea5fedc`.
- `/usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.30` — `e7848e32af4932840ba775169041759a2a8dd5a008af360e5c55bce506eebcf4`.
- `/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2` — `02bcda52c1a5dfc236f94d9e5255b4a0e26347d8a372a5223b650e31f291ce3c`.
- `/usr/local/lib/libpython3.12.so.1.0` — `4fcaa74a5a5c1170cb44972003b13abecade13c4cc7060dd41c9e5f5bf16e21c`.
- `[vdso]` — `d18eed0add042baaacb1881305db5a2c1146bc9cb9d801e1ebd98a4c27680607`.

The interpreter requests `/lib64/ld-linux-x86-64.so.2`, resolved to `/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2`. Its exact ELF and identity are in the files above and `tests/fixtures/hg_wujson/runtime-v9/providers/ld-linux-x86-64.so.2.readelf.stdout.txt`.

Provider package identities (`tests/fixtures/hg_wujson/runtime-v9/providers/package-versions.stdout.txt`, with exact `dpkg-query` command alongside):

```text
binutils	2.40-2	amd64
libc6	2.36-9+deb12u14	amd64
libgcc-s1	12.2.0-14+deb12u1	amd64
libstdc++6	12.2.0-14+deb12u1	amd64
```

The glibc/loader/libm/libpthread provider belongs to libc6, libstdc++ to libstdc++6, and libgcc_s to libgcc-s1. Original `dpkg-query -S` output and `/lib` fallback output retain merged-/usr path behavior. The image-built Python executable/libpython and wheel extension are not falsely assigned a Debian package. Python build recipe source/revision, source digest and build environment observations are recorded in the original OCI index annotations and base inspect; these remain image-publisher metadata.

`tests/fixtures/hg_wujson/runtime-v9/providers/symbols.json` records every GLOBAL/WEAK undefined dynamic symbol in the recursive ELF set: **703 symbols, 661 strong, no strong resolution failures; 28 optional weak imports are explicitly unresolved**. The collector uses `dlsym`/`dlvsym` with the consumer and CPython global scopes, and `dladdr` to identify actual available providers. TLS symbols use a matching ELF definition plus `dlinfo(RTLD_DI_TLS_DATA)` and exact offset/address equality. This supplemental provider query is distinguished from actual relocation bindings in the `LD_DEBUG` trace.

The extension imports CPython APIs from `/usr/local/lib/libpython3.12.so.1.0`; C runtime imports from libc; C++ exception/operators from libstdc++; and `_Unwind_Resume` from libgcc_s. Version requirements and recursive providers are in the raw `readelf`/`ldd -v` outputs, including `GLIBC_2.2.5`, `GLIBC_2.14`, `CXXABI_1.3`, `GLIBCXX_3.4` and `GCC_3.0` for the wheel. libm/libpthread remain real direct dependencies even where they supply no directly imported wheel symbol.

**Kernel boundary:** a recursive CPython symbol resolves to the kernel vDSO. Its actual mapped bytes are preserved as `tests/fixtures/hg_wujson/runtime-v9/providers/vdso.so`, with ELF output `vdso.readelf.stdout.txt`, byte hash in `files.json`, process mapping and `kernel-version.txt`. The immutable container image does not pin the host kernel; this receipt is scoped to the observed host, not an untested kernel.

## Unchanged synthetic evaluator output

Both complete unchanged upstream scripts execute on the same one invented row, prediction and empty alias file; no dataset payload is mounted. Exact per-evaluator commands and source digests are in `tests/fixtures/hg_wujson/runtime-v9/synthetic-evaluator.json`; input files and original stdout/stderr are in `tests/fixtures/hg_wujson/runtime-v9/synthetic/`. Source bytes are compared to the preserved task-197 pins before execution. The result is a fabricated control, not a benchmark score. Raw result:

```json
{
  "scope": "fabricated one-row control; no benchmark or model",
  "metric_identity": "upstream Answer/Sup/Evi/Joint EM,F1,precision,recall percent",
  "results": [
    {
      "argv": [
        "/tmp/fresh-ujson/bin/python",
        "-I",
        "-B",
        "/opt/hg-wujson/evaluator/2wikimultihop_evaluate.py",
        "/receipts/synthetic/prediction.json",
        "/receipts/synthetic/gold.json"
      ],
      "returncode": 0,
      "source_sha256": "854b03c487608286d6381379eb32e46d9b845493527d1fe1951d0bf4ec923a40",
      "metrics": {
        "em": 100.0,
        "f1": 100.0,
        "prec": 100.0,
        "recall": 100.0,
        "sp_em": 100.0,
        "sp_f1": 100.0,
        "sp_prec": 100.0,
        "sp_recall": 100.0,
        "evi_em": 100.0,
        "evi_f1": 100.0,
        "evi_prec": 100.0,
        "evi_recall": 100.0,
        "joint_em": 100.0,
        "joint_f1": 100.0,
        "joint_prec": 100.0,
        "joint_recall": 100.0
      }
    },
    {
      "argv": [
        "/tmp/fresh-ujson/bin/python",
        "-I",
        "-B",
        "/opt/hg-wujson/evaluator/2wikimultihop_evaluate_v1.1.py",
        "/receipts/synthetic/prediction.json",
        "/receipts/synthetic/gold.json",
        "/receipts/synthetic/aliases.jsonl"
      ],
      "returncode": 0,
      "source_sha256": "7c09ee2ec98c7ecb57df79eb68dba22eb381ab58d50e730dfcefafb4dda31458",
      "metrics": {
        "em": 100.0,
        "f1": 100.0,
        "prec": 100.0,
        "recall": 100.0,
        "sp_em": 100.0,
        "sp_f1": 100.0,
        "sp_prec": 100.0,
        "sp_recall": 100.0,
        "evi_em": 100.0,
        "evi_f1": 100.0,
        "evi_prec": 100.0,
        "evi_recall": 100.0,
        "joint_em": 100.0,
        "joint_f1": 100.0,
        "joint_prec": 100.0,
        "joint_recall": 100.0
      }
    }
  ],
  "passed": true
}
```

## Remaining source/build custody requirement

**The blocker stays external.** Runtime import, recursive provider resolution, notices in the distribution and the synthetic evaluator replay now exist for the exact wheel/image above. What remains unestablished is **authenticated linkage from that published wheel to its actual original source/build inputs**, including the actual vendored double-conversion source and bundled/external build selection.

The acquired immutable ujson commit `59875e089937c8b05c2f4b474530e3a9ec706a56`, reconstructed trees, default setup.py and licenses are preserved under `tests/fixtures/hg_wujson/deployment-v6/custody/`. They establish source/default-build observations, not the wheel producer's actual compiler/build environment/invocation or `UJSON_BUILD_DC_LIBS` value. This task's Docker build log binds the already-built binary to the new image; it cannot retroactively attest the original wheel build. A successful import does not supply that missing custody.

The fresh official PyPI Integrity provenance query is in `tests/fixtures/hg_wujson/pypi-build-attestation.command.json`, original HTTP headers in `pypi-build-attestation.headers.txt`, status output in `pypi-build-attestation.stdout.txt`, and original body in `pypi-build-attestation.body`. It returned:

```text
404
{"message":"No provenance available for ujson-5.10.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"}
```

This is a result for that endpoint, not proof that no build attestation could exist elsewhere. No source rebuild is substituted for the required exact task-226 wheel. The registry retains `status=external` and sharpens the remaining action; no H0 or production authorization follows. Shared gates and the separate Hub/data provenance blocker remain unchanged.

## Preserved failures, cleanup and verification

Every attempt has a fresh container name and receipt directory; no receipt was edited or resumed. `runtime-create` failed before creating a container because build `--iidfile` gave a config digest while this Docker store launches the inspected manifest digest. `runtime-v2` failed to write the receipt mount under the dropped-capability root user; v3 installed offline but native mmap was blocked by the default noexec tmpfs. The corrected launch uses the host UID/GID and explicitly executable tmpfs.

`runtime-v4` exposed the collector's missing global CPython lookup; v5 exposed TLS handling; v6 exposed a non-ELF locale mapping in the TLS search; v7 exposed eager opening of the special loader; v8 exposed the kernel vDSO being mistaken for a filesystem DSO. These are retained incomplete collector attempts, not passing runtime closure receipts. Each corrected collector is a separate immutable `deployment[-vN]` context/build/image. The successful complete evidence is **deployment-v6 / runtime-v9**. No production code changed.

The direct raw-manifest request timed out (`base-manifest.stderr.txt`); the canonical-proxy request succeeded, and original bytes recompute to the pin. All failed logs remain.

Every created container was removed after its inspect receipt. Exact remove commands/output and name-filtered absence checks are in `tests/fixtures/hg_wujson/runtime-v2` through `runtime-v9` `*-remove.*` and `*-cleanup-check.*` files. The final owned-name query is `tests/fixtures/hg_wujson/final-owned-container-check.command.json` with empty stdout. The new image distributions remain for review; historical runs, archives and platform images are untouched.

Complete fixture hashes: `tests/fixtures/hg_wujson/SHA256SUMS` (all files except itself). Verify with `cd tests/fixtures/hg_wujson && sha256sum -c SHA256SUMS`. Focused receipt/package/source/registry verification and the required blocker checker output are in `reports/w-ujson-validation.txt`.
