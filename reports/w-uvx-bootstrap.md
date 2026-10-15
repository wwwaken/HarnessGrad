# Terminal-Bench uvx bootstrap custody — w-uvx

**One task's tooling bootstrap can be pinned and ran offline. `scorer-offline-closure` stays OPEN; S1, S3, S4 and S6 remain PARTIAL.** This is the fresh `openssl-selfsigned-cert` bootstrap surface in its cached image, not all 89 task bootstraps, a benchmark scoring run, or a production scorer closure. No task tests, reference solution, model, GPU or endpoint call ran.

## Source scope and bootstrap commands

The actual external checkout is `/mnt/20t/xubuqiang/datasets/terminal-bench`, commit `2fd12b88aafdd04a52c298e3940bcb189f9766d6`. All **89 task sources** are locally present; **369/369** files match the recomputed SHA-256 values in `tests/fixtures/hg_wimg/capture/terminal-bench-source-surface.json`. Source presence does not imply image presence. Fresh image inspection here covers only OpenSSL.

There are **337 verifier bootstrap command blocks**: **82** tasks invoke `uvx`, **one** (`mailman`) uses `uv venv -p 3.12`, `uv pip install` and `uv run`, and **six** use `pip install`: `build-cython-ext`, `fix-code-vulnerability`, `headless-terminal`, `hf-model-inference`, `kv-store-grpc`, `largest-eigenval`. Thus the six non-uv scripts also bootstrap tooling; “83 uv scripts” does not mean six scripts have no bootstrap. The appendix lists every test.sh apt/uv-installer/uv/uvx/pip command with external file:line and literal install requirements, including continuation lines. Build-time Dockerfile declarations are separately indexed, not conflated with verifier execution.

`tests/fixtures/hg_wuvx/source/bootstrap-lines.md` and `source/inventory.json` contain the full 459 source-match blocks across verifier scripts, Dockerfiles and other test sources. `source/tasks/` preserves all 89 test.sh/Dockerfile preimages; `source/source-checks.json` and `source/summary.json` preserve the hash comparison. Other-source matches are a conservative lexical inventory, including diagnostic strings, not all executable bootstrap lines. Additional real calls include `configure-git-webserver/tests/verify.sh:5-6`, `git-multibranch/tests/test_outputs.py:12-13`, `overfull-hbox/tests/test_outputs.py:18`, and task-artifact `pip`/`uv sync` subprocesses in `pypi-server`/`reshard-c4-data`. No other task was bootstrapped or resolved.

Additional test-body operations, read only (all paths relative to that same external checkout):

| File:line | Exact package operation / what it installs |
| --- | --- |
| `configure-git-webserver/tests/verify.sh:5` / `:6` | `apt-get update`; `DEBIAN_FRONTEND=noninteractive apt-get install -y expect` |
| `git-multibranch/tests/test_outputs.py:12` / `:13` | Generated shell: `apt-get update`; `DEBIAN_FRONTEND=noninteractive apt-get install -y curl expect git openssh-client` |
| `overfull-hbox/tests/test_outputs.py:18` | `os.system('apt install -y --reinstall texlive-latex-base')` |
| `pypi-server/tests/test_outputs.py:23` | `python -m pip uninstall -y vectorops` removes the task package |
| `pypi-server/tests/test_outputs.py:24-32`, executed at `:52` | `python -m pip install --index-url http://localhost:8080/simple vectorops==0.1.0` installs the task artifact from its local service |
| `reshard-c4-data/tests/test_outputs.py:96` | `subprocess.run(["uv", "sync"], ...)` resolves the runtime project's dependency declarations; the command has no literal package list |
| `reshard-c4-data/tests/test_outputs.py:107` / `:150` | `uv run` on the task's compression/decompression script; may synchronize the same runtime project |

These extra source files are copied into `source/other-tests/`; Python preimages use `.py.txt` to prevent pytest collection. Their dependency resolution was not executed; task-artifact packages and runtime project declarations must not be mistaken for the OpenSSL tooling closure.

For OpenSSL, `/mnt/20t/xubuqiang/datasets/terminal-bench/openssl-selfsigned-cert/tests/test.sh` contains:

| Line | Operation / requested inputs |
| --- | --- |
| 4 | `apt-get update`: mutable Debian package indexes |
| 5 | `apt-get install -y curl`: curl plus apt-selected dependencies/recommends; no version pins |
| 8 | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh`: uv/uvx 0.9.5 installer and platform archive; no source-declared byte hash |
| 10 | Source `$HOME/.local/bin/env` to expose the installed commands |
| 18–22 | `uvx -p 3.13 -w pytest==8.4.1 -w pytest-json-ctrf==0.3.5 pytest ...`: Python minor request, two direct pins, four unpinned transitives |

Its `environment/Dockerfile:2` declares floating `python:3.13-slim-bookworm`; `:5-7` apt-installs openssl at image build. Adapter `data/datasets/terminal_bench.py:234` invokes `bash /tests/test.sh`, with trusted tests staged at `:238`. No production file changed.

## Concrete fresh resolution and byte custody

Used the already cached image by local ID `sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12`, whose inspect also lists `alexgshaw/openssl-selfsigned-cert@sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12`. This image identity was freshly inspected, not recomputed from exported OCI layers in this packet. The original image tag remains unchanged in production.

Fresh successful collection ran the script's apt operations, saved the installer before executing it, sourced its env, and ran its exact Python/package selection flags with **`pytest --version` instead of task tests**. `uvx -vv` preserves the selected interpreter, resolver decisions and six wheel GET URLs. The online container had bridge networking and only the documented free egress proxy `http://172.17.0.1:17890`; it was bounded to 1 CPU, 1 GiB and 128 PIDs. No image pull or managed Python download occurred.

- `uv --version` → **`uv 0.9.5`**; `uvx --version` → **`uvx 0.9.5`**.
- Selected existing **CPython 3.13.7**, `/usr/local/bin/python3.13`, GCC 12.2.0; executable SHA-256 `73b68fc2dac176af16098180a2c98a03ee9f1f1b02db25d42d44d782e79e2330`.
- Cache tag **`cpython-313`**, SOABI **`cpython-313-x86_64-linux-gnu`**, extension suffix `.cpython-313-x86_64-linux-gnu.so`, platform `linux-x86_64`; **glibc 2.36**, **OpenSSL 3.0.17 1 Jul 2025**. These are measurements, not values inferred from the `3.13` request.
- `raw/online-python.json` records selected distribution metadata, interpreter/extension/provider hashes and raw recursive ldd output (19 native objects in the Python inspection superset); `raw/offline-python.json` independently agrees on the interpreter/ABI and six distributions. These probes include SSL/SQLite/compression/ctypes inspection, not proof every library is used by pytest. Offline stdout also retains ldd for uv, uvx and curl. The fixed image supplies the base Python/shared-library bytes; this fixture does not export the entire image or rebuild it from apt/source pins.

All following values were recomputed from retained bytes; raw `sha256sum` output is `raw/artifact-sha256.txt`. All six wheels have tag **`py3-none-any`** (no wheel-specific native ABI). URLs, sizes, wheel METADATA/WHEEL contents and digest checks are in `artifacts/wheels.json`. Wheels were fetched again from the exact GET URLs observed in uv's log; their METADATA/WHEEL hashes match the online-installed files. No authenticated publisher provenance or recovery of historical wheel transport bytes is claimed.

| Wheel artifact | Recomputed SHA-256 |
| --- | --- |
| `pytest-8.4.1-py3-none-any.whl` | `539c70ba6fcead8e78eebbf1115e8b589e7565830d7d006a8723f19ac8a0afb7` |
| `pytest_json_ctrf-0.3.5-py3-none-any.whl` | `e82fd1d69be2f92385bc33540063e5ad7b17b36de67764c84f3ceb9815a895e9` |
| `pluggy-1.6.0-py3-none-any.whl` | `e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746` |
| `iniconfig-2.3.1-py3-none-any.whl` | `9121e2c1fdb355232495be3194c8dfe87ccc2d5dee45947b78e68f499790d7a7` |
| `packaging-26.3-py3-none-any.whl` | `d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c` |
| `pygments-2.21.0-py3-none-any.whl` | `2363c69b61c4a97c838da3b130dcd6468f4848992b21a82f2a63ec34377137d9` |

| Other artifact | Recomputed SHA-256 |
| --- | --- |
| `uv-install.sh` | `8402ab80d2ef54d7044a71ea4e4e1e8db3b20c87c7bffbc30bff59f1e80ebbd5` |
| `uv-x86_64-unknown-linux-gnu.tar.gz` | `2cf10babba653310606f8b49876cfb679928669e7ddaa1fb41fb00ce73e64f66` |
| Archive member `uv-x86_64-unknown-linux-gnu/uvx` | `421b1bb58429180a04ade98da066b5a5b6763e8ed74edef97359701c4cb42db8` |
| Archive member `uv-x86_64-unknown-linux-gnu/uv` | `d3dc3ca8e29337dd602a9a4df9e6edb15ebc52aed91461debeedb96939dc4ce0` |

The archive's uv/uvx member hashes also match the binaries installed by the fetched installer (raw online stdout). The installer reports “no checksums to verify”; our local SHA-256 pins establish retained-byte identity, not upstream release attestation.

The apt operation fetched **19 bounded .deb artifacts**, including curl **7.88.1-10+deb12u15**. Each actual package's version/architecture/dependencies, captured `dpkg-deb -f` argv/stdout, byte size and recomputed digest is in `raw/apt-artifacts.json`; the complete list and hashes follows. Capturing disables the disposable image's `docker-clean` apt hook so apt retains its downloads; it does not change requested packages. The first collection failed *after* apt installation because that hook had deleted the .debs. Its raw outputs and original script are preserved as `raw/attempt1-online.*`, `raw/attempt1-online-container-inspect.*`, `raw/attempt1-online-cleanup.*` and `scripts/attempt1-online.sh`. A fresh second container collected successfully; no failed attempt is reported as a passed bootstrap.

| Captured Debian artifact | Recomputed SHA-256 |
| --- | --- |
| `curl_7.88.1-10+deb12u15_amd64.deb` | `0dd9b6bf7a0bd11af2d68a52ec44c2a223fa7c11f9104c36ce1047e1137d4a8f` |
| `krb5-locales_1.20.1-2+deb12u5_all.deb` | `7a904247cda4006e25a6a1bdcf10bc3f0fa10f5c7df69dd199c1e2fdf99327fa` |
| `libbrotli1_1.0.9-2+b6_amd64.deb` | `563b4caec1aa5e876bd3355b36e7a38e1484baf5a293b48d1e8bd22db786e4d7` |
| `libcurl4_7.88.1-10+deb12u15_amd64.deb` | `3042904de01f9c4fbdcf1452b8f81abedcf2b015f9b9deba109063322b5bd68b` |
| `libgssapi-krb5-2_1.20.1-2+deb12u5_amd64.deb` | `d8b87aea91b956b416c01a28c44ff6228315ae3b73de40acddac3dc5043607d2` |
| `libk5crypto3_1.20.1-2+deb12u5_amd64.deb` | `7b6e47d15c5c9cdcd456137533d8308aeba608a54cec73b28bd59bfc4b54cf06` |
| `libkeyutils1_1.6.3-2_amd64.deb` | `cfac89e6a7a54ff3c6a4f843310e25efeddaa771baeae470bd98bd588c373563` |
| `libkrb5-3_1.20.1-2+deb12u5_amd64.deb` | `c90801be09701af221b54dd502a59cb378b7284ff31e480738baca317d2f7653` |
| `libkrb5support0_1.20.1-2+deb12u5_amd64.deb` | `8b9c05f2d8d461a10d657b118f572af5bf8fd6c8f93dcef81e852c5ab0f428ab` |
| `libldap-2.5-0_2.5.13+dfsg-5_amd64.deb` | `4b6c30f6554149c594628d945edc6003f0eea8d0cc1341638c0e71375db147ed` |
| `libldap-common_2.5.13+dfsg-5_all.deb` | `72a6c113801a0f307f3a9ab9fe7a7f9559d9164af990494ed2c50617a0e20452` |
| `libnghttp2-14_1.52.0-1+deb12u3_amd64.deb` | `5a5736cee57e51c1baed869979e6ecdbc6495e939e33203d6cfe3b6e5a149e3f` |
| `libpsl5_0.21.2-1_amd64.deb` | `4f0d35610204e4e754b057748719744114621f2f6f4202d846c314860a981afb` |
| `librtmp1_2.4+20151223.gitfa8646d.1-2+b2_amd64.deb` | `e1f69020dc2c466e421ec6a58406b643be8b5c382abf0f8989011c1d3df91c87` |
| `libsasl2-2_2.1.28+dfsg-10_amd64.deb` | `11ee190ad39f8d7af441d2c8347388b9449434c73acc67b4b372445ac4152efa` |
| `libsasl2-modules-db_2.1.28+dfsg-10_amd64.deb` | `3ac4fd6cbe3b3b06e68d24b931bf3eb9385b42f15604a37ed25310e948ca0ee6` |
| `libsasl2-modules_2.1.28+dfsg-10_amd64.deb` | `b1966bea9832686a0fd5ddba9787dce5816ebe02218a4a8f7472a1628d73451b` |
| `libssh2-1_1.10.0-3+deb12u1_amd64.deb` | `fff72a194e493f88e100a2567e22472bb4ab828d429c2956965c6f2f134f1b3a` |
| `publicsuffix_20230209.2326-1_all.deb` | `791c92c681a3cefcc9721445dc8a301a1a3cb3eef40ac2c16a4d9dd9ad5a42d7` |

The previous real verifier execution is preserved unchanged in `reports/w-net-receipts.md` and `reports/w-net-evidence/`. It records `uv 0.9.5` and six installed packages, but its bounded output does **not** record the complete Python patch/ABI or all transitive wheel versions/digests. Those historical values cannot be recovered from that receipt. This packet establishes the **new, explicitly bounded bootstrap resolution** in the same cached base; it does not retroactively assert identical historical transitive packages or recreate the actor's old snapshot.

## Demonstrated offline recipe and limits

**Network-denied bootstrap demonstrated for one task only: openssl-selfsigned-cert.** `scripts/offline.py` launches a new container from the same cached immutable image ID, with `--pull=never --network=none --cpus=1 --memory=1g --pids-limit=128`, mounting this fixture read-only. No proxy or cache is inherited. The exact argv/UTC time/exit code and stdout/stderr of each operation are under `raw/*.command.json` and adjacent files.

1. Verify `artifacts/SHA256SUMS`; check empty initial caches. `/proc/net/route` has no external route; socket connections to both `172.17.0.1:17890` and `1.1.1.1:443` fail with errno 101, `Network is unreachable`. Saved Docker inspect confirms `HostConfig.NetworkMode="none"`, no address/gateway and exit 0.
2. `dpkg -i /packet/artifacts/apt/*.deb` installs the retained Debian closure without package indexes. Full `dpkg-query -W` output matches the successful online collection byte for byte; `curl --version` succeeds.
3. Extract the retained uv archive, verify both binary hashes and observe `uv 0.9.5` / `uvx 0.9.5`. Select `/usr/local/bin/python3.13` from the fixed base with `--no-python-downloads`; the recorded executable hash/patch/ABI agrees online and offline.
4. Create a new venv and install `artifacts/requirements.lock` using `uv pip install --offline --no-index --find-links /packet/artifacts/wheels --require-hashes`. The lock pins all six distributions and their wheel hashes.
5. Use a **second, absent cache directory** for `uvx --offline --no-index --find-links /packet/artifacts/wheels --no-python-downloads -p /usr/local/bin/python3.13 -w pytest==8.4.1 -w pytest-json-ctrf==0.3.5 pytest --version`. It builds a new tool environment from the finite wheel directory and prints `pytest 8.4.1`. `pytest --help` exposes `--ctrf=CTRF`; no tests are collected or executed. Offline Python metadata matches all six online versions. This isolates the uvx proof from the preceding hash-checked pip-install cache.

`scripts/summarize.py` checks these agreements and writes `resolution.json`; containers are explicitly removed, with successful cleanup commands saved. The collector timeout is 600 seconds per container command and wheel/uv downloads are separately bounded. The captured payload is exactly six wheels, 19 .debs, one installer and one uv archive; no other task's dependencies were downloaded.

**Pinnable now:** these exact bootstrap packages, uv/uvx binaries, selected interpreter/ABI under this cached image ID, and their finite offline installation payload. Pre-seeding a complete uv cache would be another approach; the demonstrated approach uses wheels plus a hash lock, so no opaque warm cache is required. Pinning only uv or only the two direct Python packages would not freeze Python selection, transitives or apt.

**Still unpinned in the upstream script:** apt indexes/versions, installer/archive byte identity, Python patch selection and wheel transitives/hashes. The unmodified online installer URL cannot fetch with the network denied; the original script is **not** claimed to run offline. The demonstrated frozen recipe intentionally replaces apt index fetching with local .debs, curl installation with the local archive, and floating package/Python discovery with finite inputs and an explicit base interpreter. Production adapter/scoring logic has not been modified to adopt this recipe. Portability requires preserving/provisioning the fixed base image separately; no complete image rebuild closure, actor-snapshot integrity, task-artifact dependency graph, other 88 task bootstraps or broader dataset offline closure has been established. No genuine unpinnable dependency was found in this one bootstrap; historical omitted resolution bytes remain unobtainable from the saved receipt.

## Registry boundary

Only `scorer-offline-closure.observed` is sharpened with this one-task result, plus an additive evidence reference. **S1, S3, S4 and S6 remain PARTIAL; no shared or dataset blocker closes.** All statuses, next_actions, dataset/history records, admission gates and `production_authorized=false` are preserved. S3 still needs the other task/runtime branches, complete image/base rebuild and execution-selected ABI/input custody, and actor-snapshot integrity at the appropriate scope. The official execution and lifecycle/live-control obligations remain separate. No runs/ or frozen receipt was changed or resumed. Validation commands/checker output: `reports/w-uvx-validation.txt`.

## Appendix: every local test.sh bootstrap invocation

Each row is a verbatim command block (continuations flattened only for table layout). Package arguments after `install`/`-w`, interpreter requests, indexes and Git URLs state what it installs. `apt-get update` refreshes indexes and installs no package; curl's uv installer installs uv/uvx 0.9.5. For a `uvx`/`uv run` row only the bootstrap flags are inventoried: the pytest tail shown is **not executed here**. External checkout root for every relative file below: `/mnt/20t/xubuqiang/datasets/terminal-bench/`. Full absolute paths and verbatim multiline preimages are in the source index.

| File:line | Bootstrap command / requested installs |
| --- | --- |
| `adaptive-rejection-sampler/tests/test.sh:4` | `apt-get update` |
| `adaptive-rejection-sampler/tests/test.sh:5` | `apt-get install -y curl` |
| `adaptive-rejection-sampler/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `adaptive-rejection-sampler/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w numpy==2.3.3    -w scipy==1.16.2    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `bn-fit-modify/tests/test.sh:4` | `apt-get update` |
| `bn-fit-modify/tests/test.sh:5` | `apt-get install -y curl` |
| `bn-fit-modify/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `bn-fit-modify/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pandas==2.3.2    -w scipy==1.16.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `break-filter-js-from-html/tests/test.sh:4` | `apt-get update` |
| `break-filter-js-from-html/tests/test.sh:5` | `apt-get install -y curl` |
| `break-filter-js-from-html/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `break-filter-js-from-html/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w selenium==4.35.0    -w beautifulsoup4==4.13.5    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `build-cython-ext/tests/test.sh:9` | `pip install pytest==8.4.1 pytest-json-ctrf==0.3.5` |
| `build-pmars/tests/test.sh:4` | `apt-get update` |
| `build-pmars/tests/test.sh:5` | `apt-get install -y curl` |
| `build-pmars/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `build-pmars/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `build-pov-ray/tests/test.sh:3` | `apt-get update` |
| `build-pov-ray/tests/test.sh:4` | `apt-get install -y curl imagemagick` |
| `build-pov-ray/tests/test.sh:7` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `build-pov-ray/tests/test.sh:16` | `uvx    -p 3.13    -w pytest==8.4.1    -w pillow==11.1.0    -w numpy==2.3.1    -w scikit-image==0.25.0    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `caffe-cifar-10/tests/test.sh:4` | `apt-get update` |
| `caffe-cifar-10/tests/test.sh:5` | `apt-get install -y curl` |
| `caffe-cifar-10/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `caffe-cifar-10/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `cancel-async-tasks/tests/test.sh:4` | `apt-get update` |
| `cancel-async-tasks/tests/test.sh:5` | `apt-get install -y curl` |
| `cancel-async-tasks/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `cancel-async-tasks/tests/test.sh:19` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `chess-best-move/tests/test.sh:4` | `apt-get update` |
| `chess-best-move/tests/test.sh:5` | `apt-get install -y curl` |
| `chess-best-move/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `chess-best-move/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `circuit-fibsqrt/tests/test.sh:4` | `apt-get update` |
| `circuit-fibsqrt/tests/test.sh:5` | `apt-get install -y curl` |
| `circuit-fibsqrt/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `circuit-fibsqrt/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `cobol-modernization/tests/test.sh:4` | `apt-get update` |
| `cobol-modernization/tests/test.sh:5` | `apt-get install -y curl` |
| `cobol-modernization/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `cobol-modernization/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `code-from-image/tests/test.sh:4` | `apt-get update` |
| `code-from-image/tests/test.sh:5` | `apt-get install -y curl` |
| `code-from-image/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `code-from-image/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `compile-compcert/tests/test.sh:4` | `apt-get update` |
| `compile-compcert/tests/test.sh:5` | `apt-get install -y curl binutils` |
| `compile-compcert/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `compile-compcert/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `configure-git-webserver/tests/test.sh:4` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `configure-git-webserver/tests/test.sh:14` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `constraints-scheduling/tests/test.sh:4` | `apt-get update` |
| `constraints-scheduling/tests/test.sh:5` | `apt-get install -y curl` |
| `constraints-scheduling/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `constraints-scheduling/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `count-dataset-tokens/tests/test.sh:4` | `apt-get update` |
| `count-dataset-tokens/tests/test.sh:5` | `apt-get install -y curl` |
| `count-dataset-tokens/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `count-dataset-tokens/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `crack-7z-hash/tests/test.sh:4` | `apt-get update` |
| `crack-7z-hash/tests/test.sh:5` | `apt-get install -y curl` |
| `crack-7z-hash/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `crack-7z-hash/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `custom-memory-heap-crash/tests/test.sh:6` | `apt-get update` |
| `custom-memory-heap-crash/tests/test.sh:7` | `apt-get install -y curl` |
| `custom-memory-heap-crash/tests/test.sh:10` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `custom-memory-heap-crash/tests/test.sh:20` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `db-wal-recovery/tests/test.sh:4` | `apt-get update` |
| `db-wal-recovery/tests/test.sh:5` | `apt-get install -y curl` |
| `db-wal-recovery/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `db-wal-recovery/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `distribution-search/tests/test.sh:4` | `apt-get update` |
| `distribution-search/tests/test.sh:5` | `apt-get install -y curl` |
| `distribution-search/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `distribution-search/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w numpy==2.3.0    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -v -rA` |
| `dna-assembly/tests/test.sh:4` | `apt-get update` |
| `dna-assembly/tests/test.sh:5` | `apt-get install -y curl primer3` |
| `dna-assembly/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `dna-assembly/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `dna-insert/tests/test.sh:3` | `apt-get update` |
| `dna-insert/tests/test.sh:4` | `apt-get install -y curl primer3` |
| `dna-insert/tests/test.sh:7` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `dna-insert/tests/test.sh:17` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `extract-elf/tests/test.sh:4` | `apt-get update` |
| `extract-elf/tests/test.sh:5` | `apt-get install -y curl gcc` |
| `extract-elf/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `extract-elf/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `extract-moves-from-video/tests/test.sh:4` | `apt-get update` |
| `extract-moves-from-video/tests/test.sh:5` | `apt-get install -y curl` |
| `extract-moves-from-video/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `extract-moves-from-video/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `feal-differential-cryptanalysis/tests/test.sh:4` | `apt-get update` |
| `feal-differential-cryptanalysis/tests/test.sh:5` | `apt-get install -y curl gcc` |
| `feal-differential-cryptanalysis/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `feal-differential-cryptanalysis/tests/test.sh:17` | `uvx    -p 3.13    -w pytest==8.4.1    -w setuptools==80.9.0    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -v -rA` |
| `feal-linear-cryptanalysis/tests/test.sh:4` | `apt-get update` |
| `feal-linear-cryptanalysis/tests/test.sh:5` | `apt-get install -y curl` |
| `feal-linear-cryptanalysis/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `feal-linear-cryptanalysis/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -v -rA` |
| `filter-js-from-html/tests/test.sh:4` | `apt-get update` |
| `filter-js-from-html/tests/test.sh:5` | `apt-get install -y curl` |
| `filter-js-from-html/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `filter-js-from-html/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w selenium==4.38.0    -w bs4==0.0.2    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `financial-document-processor/tests/test.sh:4` | `apt-get update` |
| `financial-document-processor/tests/test.sh:5` | `apt-get install -y curl` |
| `financial-document-processor/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `financial-document-processor/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pandas==2.3.2    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `fix-code-vulnerability/tests/test.sh:9` | `pip install pytest==8.4.1 pytest-json-ctrf==0.3.5` |
| `fix-git/tests/test.sh:4` | `apt-get update` |
| `fix-git/tests/test.sh:5` | `apt-get install -y curl` |
| `fix-git/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `fix-git/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `fix-ocaml-gc/tests/test.sh:4` | `apt-get update` |
| `fix-ocaml-gc/tests/test.sh:5` | `apt-get install -y curl` |
| `fix-ocaml-gc/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `fix-ocaml-gc/tests/test.sh:30` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `gcode-to-text/tests/test.sh:4` | `apt-get update` |
| `gcode-to-text/tests/test.sh:5` | `apt-get install -y curl` |
| `gcode-to-text/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `gcode-to-text/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `git-leak-recovery/tests/test.sh:4` | `apt-get update` |
| `git-leak-recovery/tests/test.sh:5` | `apt-get install -y curl` |
| `git-leak-recovery/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `git-leak-recovery/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `git-multibranch/tests/test.sh:4` | `apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y expect curl` |
| `git-multibranch/tests/test.sh:7` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `git-multibranch/tests/test.sh:17` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `gpt2-codegolf/tests/test.sh:4` | `apt-get update` |
| `gpt2-codegolf/tests/test.sh:5` | `apt-get install -y curl` |
| `gpt2-codegolf/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `gpt2-codegolf/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `headless-terminal/tests/test.sh:4` | `apt-get update` |
| `headless-terminal/tests/test.sh:5` | `apt-get install -y vim` |
| `headless-terminal/tests/test.sh:13` | `pip install pytest==8.4.1 requests==2.32.5 pytest-json-ctrf==0.3.5` |
| `hf-model-inference/tests/test.sh:4` | `pip install pytest==8.4.1 psutil==7.0.0 requests==2.32.4 pytest-json-ctrf==0.3.5` |
| `install-windows-3.11/tests/test.sh:4` | `apt-get update` |
| `install-windows-3.11/tests/test.sh:5` | `apt-get install -y curl` |
| `install-windows-3.11/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `install-windows-3.11/tests/test.sh:19` | `apt-get update -qq && apt-get install -y mtools socat vncsnapshot tesseract-ocr` |
| `install-windows-3.11/tests/test.sh:21` | `uvx    -p 3.13    -w pytest==8.4.1    -w opencv-python==4.11.0.86    -w numpy==2.3.1    -w pytesseract==0.3.13    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `kv-store-grpc/tests/test.sh:4` | `pip install pytest==8.4.2 requests==2.32.5 psutil==7.0.0 pytest-json-ctrf==0.3.5` |
| `large-scale-text-editing/tests/test.sh:4` | `apt-get update` |
| `large-scale-text-editing/tests/test.sh:5` | `apt-get install -y curl` |
| `large-scale-text-editing/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `large-scale-text-editing/tests/test.sh:27` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `largest-eigenval/tests/test.sh:9` | `pip install pytest==8.4.1 pytest-json-ctrf==0.3.5 --break-system-packages` |
| `llm-inference-batching-scheduler/tests/test.sh:6` | `apt-get update` |
| `llm-inference-batching-scheduler/tests/test.sh:7` | `apt-get install -y curl` |
| `llm-inference-batching-scheduler/tests/test.sh:10` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `llm-inference-batching-scheduler/tests/test.sh:20` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `log-summary-date-ranges/tests/test.sh:4` | `apt-get update` |
| `log-summary-date-ranges/tests/test.sh:5` | `apt-get install -y curl` |
| `log-summary-date-ranges/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `log-summary-date-ranges/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `mailman/tests/test.sh:9` | `apt-get update` |
| `mailman/tests/test.sh:10` | `apt-get install -y curl` |
| `mailman/tests/test.sh:13` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `mailman/tests/test.sh:23` | `uv venv -p 3.12 .tb` |
| `mailman/tests/test.sh:26` | `uv pip install pytest==8.4.1 mailman==3.3.8 pytest-json-ctrf==0.3.5` |
| `mailman/tests/test.sh:28` | `uv run pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `make-doom-for-mips/tests/test.sh:4` | `apt-get update` |
| `make-doom-for-mips/tests/test.sh:5` | `apt-get install -y curl python3-pillow` |
| `make-doom-for-mips/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `make-doom-for-mips/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w numpy==2.3.1    -w pillow==11.2.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `make-mips-interpreter/tests/test.sh:4` | `apt-get update` |
| `make-mips-interpreter/tests/test.sh:5` | `apt-get install -y curl python3-pillow` |
| `make-mips-interpreter/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `make-mips-interpreter/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w numpy==2.3.1    -w pillow==11.2.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `mcmc-sampling-stan/tests/test.sh:7` | `apt-get update` |
| `mcmc-sampling-stan/tests/test.sh:8` | `apt-get install -y curl` |
| `mcmc-sampling-stan/tests/test.sh:11` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `mcmc-sampling-stan/tests/test.sh:22` | `uvx    -p 3.13    -w pytest==8.3.4    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json test_outputs.py -rA` |
| `merge-diff-arc-agi-task/tests/test.sh:4` | `apt-get update` |
| `merge-diff-arc-agi-task/tests/test.sh:5` | `apt-get install -y curl git` |
| `merge-diff-arc-agi-task/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `merge-diff-arc-agi-task/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `model-extraction-relu-logits/tests/test.sh:4` | `apt-get update` |
| `model-extraction-relu-logits/tests/test.sh:5` | `apt-get install -y curl` |
| `model-extraction-relu-logits/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `model-extraction-relu-logits/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w numpy==2.3.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `modernize-scientific-stack/tests/test.sh:4` | `apt-get update` |
| `modernize-scientific-stack/tests/test.sh:5` | `apt-get install -y curl` |
| `modernize-scientific-stack/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `modernize-scientific-stack/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w numpy==2.3.4    -w pandas==2.3.3    -w matplotlib==3.10.7    -w scipy==1.16.3    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `mteb-leaderboard/tests/test.sh:4` | `apt-get update` |
| `mteb-leaderboard/tests/test.sh:5` | `apt-get install -y curl` |
| `mteb-leaderboard/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `mteb-leaderboard/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `mteb-retrieve/tests/test.sh:4` | `apt-get update` |
| `mteb-retrieve/tests/test.sh:5` | `apt-get install -y curl` |
| `mteb-retrieve/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `mteb-retrieve/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w mteb==1.36.8    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `multi-source-data-merger/tests/test.sh:4` | `apt-get update` |
| `multi-source-data-merger/tests/test.sh:5` | `apt-get install -y curl` |
| `multi-source-data-merger/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `multi-source-data-merger/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pandas==2.3.3    -w pyarrow==22.0.0    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `nginx-request-logging/tests/test.sh:4` | `apt-get update` |
| `nginx-request-logging/tests/test.sh:5` | `apt-get install -y curl` |
| `nginx-request-logging/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `nginx-request-logging/tests/test.sh:17` | `uvx    -p 3.13    -w pytest==8.4.1    -w requests==2.32.4    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -v -rA` |
| `openssl-selfsigned-cert/tests/test.sh:4` | `apt-get update` |
| `openssl-selfsigned-cert/tests/test.sh:5` | `apt-get install -y curl` |
| `openssl-selfsigned-cert/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `openssl-selfsigned-cert/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `overfull-hbox/tests/test.sh:9` | `apt-get update` |
| `overfull-hbox/tests/test.sh:10` | `apt-get install -y curl` |
| `overfull-hbox/tests/test.sh:13` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `overfull-hbox/tests/test.sh:23` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `password-recovery/tests/test.sh:4` | `apt-get update` |
| `password-recovery/tests/test.sh:5` | `apt-get install -y curl` |
| `password-recovery/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `password-recovery/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `path-tracing/tests/test.sh:4` | `apt-get update` |
| `path-tracing/tests/test.sh:5` | `apt-get install -y curl` |
| `path-tracing/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `path-tracing/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pillow==11.2.1    -w numpy==2.3.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `path-tracing-reverse/tests/test.sh:4` | `apt-get update` |
| `path-tracing-reverse/tests/test.sh:5` | `apt-get install -y curl` |
| `path-tracing-reverse/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `path-tracing-reverse/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pillow==11.2.1    -w numpy==2.3.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `polyglot-c-py/tests/test.sh:4` | `apt-get update` |
| `polyglot-c-py/tests/test.sh:5` | `apt-get install -y curl` |
| `polyglot-c-py/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `polyglot-c-py/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `polyglot-rust-c/tests/test.sh:4` | `apt-get update` |
| `polyglot-rust-c/tests/test.sh:5` | `apt-get install -y curl` |
| `polyglot-rust-c/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `polyglot-rust-c/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `portfolio-optimization/tests/test.sh:4` | `apt-get update` |
| `portfolio-optimization/tests/test.sh:5` | `apt-get install -y curl` |
| `portfolio-optimization/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `portfolio-optimization/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w numpy==2.3.2    -w setuptools==78.1.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `protein-assembly/tests/test.sh:4` | `apt-get update` |
| `protein-assembly/tests/test.sh:5` | `apt-get install -y curl` |
| `protein-assembly/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `protein-assembly/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w biopython==1.85    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `prove-plus-comm/tests/test.sh:4` | `apt-get update` |
| `prove-plus-comm/tests/test.sh:5` | `apt-get install -y curl` |
| `prove-plus-comm/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `prove-plus-comm/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `pypi-server/tests/test.sh:4` | `apt-get update` |
| `pypi-server/tests/test.sh:5` | `apt-get install -y curl` |
| `pypi-server/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `pypi-server/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pip==25.2    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `pytorch-model-cli/tests/test.sh:4` | `apt-get update` |
| `pytorch-model-cli/tests/test.sh:5` | `apt-get install -y curl ffmpeg libsm6 libxext6` |
| `pytorch-model-cli/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `pytorch-model-cli/tests/test.sh:17` | `uvx    --index https://download.pytorch.org/whl/cpu    --index-strategy unsafe-best-match    -p 3.13    -w torch==2.7.1    -w torchvision==0.22.1    -w numpy==2.3.1    -w opencv-python==4.11.0.86    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -v -rA` |
| `pytorch-model-recovery/tests/test.sh:4` | `apt-get update` |
| `pytorch-model-recovery/tests/test.sh:5` | `apt-get install -y curl` |
| `pytorch-model-recovery/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `pytorch-model-recovery/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w torch==2.7.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `qemu-alpine-ssh/tests/test.sh:4` | `apt-get update` |
| `qemu-alpine-ssh/tests/test.sh:5` | `apt-get install -y curl sshpass` |
| `qemu-alpine-ssh/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `qemu-alpine-ssh/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `qemu-startup/tests/test.sh:4` | `apt-get update` |
| `qemu-startup/tests/test.sh:5` | `apt-get install -y curl expect` |
| `qemu-startup/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `qemu-startup/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `query-optimize/tests/test.sh:4` | `apt-get update` |
| `query-optimize/tests/test.sh:5` | `apt-get install -y curl` |
| `query-optimize/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `query-optimize/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `raman-fitting/tests/test.sh:4` | `apt-get update` |
| `raman-fitting/tests/test.sh:5` | `apt-get install -y curl` |
| `raman-fitting/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `raman-fitting/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `regex-chess/tests/test.sh:4` | `apt-get update` |
| `regex-chess/tests/test.sh:5` | `apt-get install -y curl` |
| `regex-chess/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `regex-chess/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w chess==1.11.2    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `regex-log/tests/test.sh:4` | `apt-get update` |
| `regex-log/tests/test.sh:5` | `apt-get install -y curl` |
| `regex-log/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `regex-log/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `reshard-c4-data/tests/test.sh:9` | `uvx    -p 3.13    -w pytest==8.4.1    -w datasets==3.6.0    -w tqdm==4.67.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `rstan-to-pystan/tests/test.sh:4` | `apt-get update` |
| `rstan-to-pystan/tests/test.sh:5` | `apt-get install -y curl` |
| `rstan-to-pystan/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `rstan-to-pystan/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json test_outputs.py -rA` |
| `sam-cell-seg/tests/test.sh:4` | `apt-get update` |
| `sam-cell-seg/tests/test.sh:5` | `apt-get install -y curl git libgl1` |
| `sam-cell-seg/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `sam-cell-seg/tests/test.sh:29` | `uvx    --index https://download.pytorch.org/whl/cpu    --index-strategy unsafe-best-match    -p 3.11    -w torch==2.5.1    -w torchvision==0.20.1    -w pandas==2.3.2    -w timm==1.0.19    -w opencv-python==4.12.0.88    -w shapely==2.1.1    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    -w git+https://github.com/ChaoningZhang/MobileSAM.git@${COMMIT_HASH}    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `sanitize-git-repo/tests/test.sh:4` | `apt-get update` |
| `sanitize-git-repo/tests/test.sh:5` | `apt-get install -y curl` |
| `sanitize-git-repo/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `sanitize-git-repo/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w gitpython==3.1.44    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `schemelike-metacircular-eval/tests/test.sh:4` | `apt-get update` |
| `schemelike-metacircular-eval/tests/test.sh:5` | `apt-get install -y curl` |
| `schemelike-metacircular-eval/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `schemelike-metacircular-eval/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `sparql-university/tests/test.sh:4` | `apt-get update` |
| `sparql-university/tests/test.sh:5` | `apt-get install -y curl` |
| `sparql-university/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `sparql-university/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w rdflib==7.1.4    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `sqlite-db-truncate/tests/test.sh:4` | `apt-get update` |
| `sqlite-db-truncate/tests/test.sh:5` | `apt-get install -y curl` |
| `sqlite-db-truncate/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `sqlite-db-truncate/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `sqlite-with-gcov/tests/test.sh:4` | `apt-get update` |
| `sqlite-with-gcov/tests/test.sh:5` | `apt-get install -y curl` |
| `sqlite-with-gcov/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `sqlite-with-gcov/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `torch-pipeline-parallelism/tests/test.sh:4` | `apt-get update` |
| `torch-pipeline-parallelism/tests/test.sh:5` | `apt-get install -y curl` |
| `torch-pipeline-parallelism/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `torch-pipeline-parallelism/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w torch==2.7.0    -w transformers==4.55.0    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `torch-tensor-parallelism/tests/test.sh:4` | `apt-get update` |
| `torch-tensor-parallelism/tests/test.sh:5` | `apt-get install -y curl` |
| `torch-tensor-parallelism/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `torch-tensor-parallelism/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w torch==2.7.0    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `train-fasttext/tests/test.sh:4` | `apt-get update` |
| `train-fasttext/tests/test.sh:5` | `apt-get install -y curl` |
| `train-fasttext/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `train-fasttext/tests/test.sh:20` | `uvx    -p 3.11    -w pytest==8.4.1    -w scikit-learn==1.7.0    -w fasttext-wheel==0.9.2    -w numpy==1.24.0    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `tune-mjcf/tests/test.sh:4` | `apt-get update` |
| `tune-mjcf/tests/test.sh:5` | `apt-get install -y curl` |
| `tune-mjcf/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `tune-mjcf/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w mujoco==3.3.5    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `video-processing/tests/test.sh:4` | `apt-get update` |
| `video-processing/tests/test.sh:5` | `apt-get install -y curl` |
| `video-processing/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `video-processing/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w toml==0.10.2    -w opencv-contrib-python==4.11.0.86    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `vulnerable-secret/tests/test.sh:7` | `apt-get update` |
| `vulnerable-secret/tests/test.sh:8` | `apt-get install -y curl` |
| `vulnerable-secret/tests/test.sh:11` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `vulnerable-secret/tests/test.sh:21` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `winning-avg-corewars/tests/test.sh:4` | `apt-get update` |
| `winning-avg-corewars/tests/test.sh:5` | `apt-get install -y curl` |
| `winning-avg-corewars/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `winning-avg-corewars/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
| `write-compressor/tests/test.sh:4` | `apt-get update` |
| `write-compressor/tests/test.sh:5` | `apt-get install -y curl` |
| `write-compressor/tests/test.sh:8` | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \| sh` |
| `write-compressor/tests/test.sh:18` | `uvx    -p 3.13    -w pytest==8.4.1    -w pytest-json-ctrf==0.3.5    pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA` |
