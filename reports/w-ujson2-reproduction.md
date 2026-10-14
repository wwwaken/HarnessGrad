# w-ujson2: source build does not reproduce task-226 wheel

**Build succeeded; wheel did not reproduce; blocker remains external.** The six file-member names agree and three members match byte for byte. The extension, WHEEL and RECORD differ. Embedded double-conversion implementation is observable, but the producer's exact vendored-versus-external-static build choice and source revision remain unauthenticated.

## Exact source and build recipe

All new evidence is under `tests/fixtures/hg_wujson2/` (paths below are relative to that directory unless stated otherwise). Every executed command has its actual argv, return code and original stdout/stderr preserved. `SHA256SUMS` covers the entire packet except itself.

Source acquisition used:

```sh
curl --fail --location --retry 2 --connect-timeout 15 --max-time 120 \
  --dump-header tests/fixtures/hg_wujson2/acquired/source.headers.txt \
  --output tests/fixtures/hg_wujson2/acquired/ultrajson-59875e089937c8b05c2f4b474530e3a9ec706a56.tar.gz \
  https://codeload.github.com/ultrajson/ultrajson/tar.gz/59875e089937c8b05c2f4b474530e3a9ec706a56
```

`commands/source-acquire.*` retains the command/output and `acquired/source.headers.txt` the HTTP headers. `scripts/verify_source.py` checks all **102 blobs** against the already preserved B6 Git tree and reconstructs root tree `f68f465c6b5d55dc9520b51c5bc666ddeb0dd2b5`. All match. Source archive SHA-256: `e58790a348faf2a15240e5c13b1b62f3d4c4a27ce1cd643362aacae24c290e8f`. Full blob checks: `source-verification.json`; raw command/output: `commands/source-verify.*`. The preserved GitHub commit response asserts signature verification; this work does not independently reverify that signature or assert that it authenticates the wheel.

Build inputs were acquired online before execution: `setuptools==69.5.1`, `wheel==0.43.0`, `setuptools-scm==8.1.0`, `packaging==24.0`. Exact download command, resolved PyPI URLs and output: `commands/build-deps-acquire.*`; wheel bytes: `acquired/`; computed hash requirements: `build-requirements.txt` and `commands/prepare.*`. Only wheel **0.43.0** is identified by the published WHEEL generator. The other versions are explicit compatible reconstruction choices, not recovered original versions.

The build uses the same immutable base as w-ujson:

- `python@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b`, `--platform=linux/amd64`;
- resolved child `sha256:edd0b3ec946cc68bd20e39480bd03929016d0fb6254cbf870cd3bc55ea25116d`;
- CPython **3.12.15**, GCC/G++ **12.2.0**, binutils **2.40**, glibc **2.36**. Raw inventory: `commands/toolchain-probe.*`, `build/environment.json`, and build output.

Actual orchestration from the repository root:

```sh
python3 tests/fixtures/hg_wujson2/scripts/container.py build
python3 tests/fixtures/hg_wujson2/scripts/container.py comparison
python3 tests/fixtures/hg_wujson2/scripts/container.py published-runtime
python3 tests/fixtures/hg_wujson2/scripts/container.py rebuilt-runtime
```

`scripts/container.py` records each exact Docker create/start/inspect/remove command under `commands/<stage>-*.command.json` and the matching raw streams. Each stage uses `--pull=never --network=none --read-only --cpus=2 --memory=1g --memory-swap=1g --pids-limit=128 --cap-drop=ALL --security-opt=no-new-privileges`, the host UID/GID, a 512 MiB executable `/tmp` tmpfs, read-only packet/prior-input mounts, and its sole writable receipt mount. These are requested resource limits. Before/after inspections bind image, architecture, mounts and network settings; all four containers exited 0 without OOM and were removed. Empty cleanup listings are preserved. The preflight tool inventory used a separate network-denied `docker run --rm`.

The exact in-container recipe is `scripts/build.sh`; its complete trace and compiler/linker output are `commands/build-start.{stderr,stdout}.txt`. Essential build commands/settings were:

```sh
export SETUPTOOLS_SCM_PRETEND_VERSION=5.10.0
export SOURCE_DATE_EPOCH=1715651320
export PYTHONHASHSEED=0 TZ=UTC LC_ALL=C.UTF-8
unset UJSON_BUILD_DC_LIBS UJSON_BUILD_DC_INCLUDES UJSON_BUILD_NO_STRIP
python -I -B -m venv /tmp/builder
/tmp/builder/bin/python -I -B -m pip --isolated --disable-pip-version-check --no-cache-dir install \
  --no-index --find-links=/packet/acquired --require-hashes --only-binary=:all: --no-deps \
  --report=/receipts/build-deps-install-report.json -r /packet/build-requirements.txt
mkdir /tmp/source
tar -xzf /packet/acquired/ultrajson-59875e089937c8b05c2f4b474530e3a9ec706a56.tar.gz \
  -C /tmp/source --strip-components=1
cd /tmp/source
/tmp/builder/bin/python -B setup.py bdist_wheel --dist-dir=/receipts/wheels
```

The archive has no Git history; the explicit version supplies the known package version, not source authentication. The SCM file-finder warning is preserved. `SOURCE_DATE_EPOCH` was deliberately taken from the published ZIP timestamp to remove that avoidable difference; matching timestamps are therefore not independent evidence. Default setup compiles all eight vendored double-conversion `.cc` files and `lib/dconv_wrapper.cc`, adds `-D_GNU_SOURCE`, and links `-lstdc++ -lm -Wl,--strip-all`; every invocation is in the raw build log. Python sysconfig supplies the remaining flags. No external double-conversion library was supplied to this build.

The output truthfully carries `cp312-cp312-linux_x86_64`. The original manylinux tags imply a repaired/distribution-specific artifact; the pinned source workflow names cibuildwheel 2.18.0, but supplies no authenticated actual image digest or build invocation for this wheel. This work neither runs auditwheel repair nor relabels a glibc-2.36 build as manylinux2014.

## Wheel and member comparison

Both wheel digests were recomputed from their bytes. The task-226 original and the existing deployment copy match the published digest; commands/output are in `commands/prepare.*` and `comparison/published-sha256.*`.

| Item | Published | Rebuilt | Agreement |
| --- | --- | --- | --- |
| Wheel bytes | 53,686 | 52,693 | Different |
| Wheel SHA-256 | `f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1` | `63a3456428e7a40f7270eafff1226f875bb3c3a2ce1770fa7058ce4dbcdcd378` | Different |
| Non-directory member names | Six | Same six | Exact set match |
| `LICENSE.txt` | 5,975 bytes | 5,975 bytes | Byte-identical |
| `METADATA` | 9,349 bytes | 9,349 bytes | Byte-identical |
| `top_level.txt` | 6 bytes | 6 bytes | Byte-identical |
| `WHEEL` | 152 bytes, two manylinux tags | 105 bytes, Linux tag | Generator and cp312 ABI match; platform tags differ |
| `RECORD` | 487 bytes | 480 bytes | Hash/size entries, ordering and CRLF/LF differ; both validate internally |
| `ujson.cpython-312-x86_64-linux-gnu.so` | 105,936 bytes | 97,664 bytes | Same extension name/ABI; bytes differ |
| Extension SHA-256 | `deb036e60d4b61104bad389783094ebb09a35dbdecd21aeea572968762c3be5c` | `aa732f589e3e14643271db8d59acf146eba237827d94b3e082be492dd09b7122` | Different |
| ELF `.text` | 60,853 bytes | 58,665 bytes | Different bytes |
| ELF `.rodata` | 7,200 bytes | 6,648 bytes | Different bytes |
| ELF `.comment` compiler | GCC 10.2.1, Red Hat 10.2.1-11 | GCC 12.2.0, Debian | Different |

The original also has two explicit directory entries, `ujson.libs/` (empty) and `ujson-5.10.0.dist-info/`, absent from the local ZIP. ZIP order differs; timestamps match by construction. Full member lists, sizes, hashes, ZIP attributes and per-row RECORD checks are in `comparison/comparison.json` and `comparison/{published,rebuilt}-members.json`. Every extracted member is retained under `comparison/{published,rebuilt}/`. Raw `cmp` returns 1; raw metadata/RECORD diffs, `readelf`, `nm`, disassembly and extracted section bytes are preserved alongside their exact subcommands. There are 68 common defined dynamic symbols; the published binary additionally defines `_ZdlPvm`, `_fini`, `_init`. Symbol presence is not byte or behavior equivalence.

## Double-conversion finding

**Embedded double-conversion code is observable in the published wheel. The precise producer build selection is not.** `comparison/published-readelf.stdout.txt` contains 53 defined dynamic symbols in `double_conversion`, all with concrete section indexes, and none undefined. For example:

```text
91: 0000000000005a90   349 FUNC    GLOBAL DEFAULT   11 _ZN17double_conversion6Bignum11PlusCompareERKS0_S2_S2_
```

`comparison/published-nm-defined-demangled.stdout.txt` contains:

```text
0000000000007240 T double_conversion::DoubleToStringConverter::DoubleToAscii(double, double_conversion::DoubleToStringConverter::DtoaMode, int, char*, int, bool*, int*, int*)
0000000000009850 T double_conversion::StringToDoubleConverter::StringToDouble(char const*, int, int*) const
```

Its direct `DT_NEEDED` entries are `libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1`, `libpthread.so.0`, `libc.so.6`; there is no double-conversion DSO or bundled library member. A fresh `dladdr` query also locates the cited Bignum symbol in the installed ujson extension itself (`published-runtime/native-import.json`). The local build has the exact same set of 53 double-conversion symbol names. This rules out the interpretation that this wheel merely imports the implementation from a separately loaded double-conversion DSO.

However, an embedded implementation could have been compiled from vendored `.cc` sources **or linked from an external static archive**. Symbols, tags and RECORD do not record the original `UJSON_BUILD_DC_LIBS`, actual source revision, compiler inputs or build invocation. Source `setup.py` lines 9–22 selects bundled sources when that variable is empty; lines 24–30 selects stripping and lines 32–47 specify compilation/link inputs. Original source: `../hg_wujson/deployment-v6/custody/setup.py`; numbered copies and wrapper code: `build/source-lines.txt`. The local log proves the bundled selection for this local build only. Neither the source default nor matching exported names proves the producer made that selection or used exactly vendored tree `629e1ff9b56216eb1423941ad615573354a857e4`.

## Fresh network-denied runtime receipts

Build, comparison and both runtime stages first ran the existing network-denial probe: only loopback, no IPv4 route, reserved-IP connection returns `ENETUNREACH`. Raw `network-denial.json` and Docker `NetworkMode=none` inspections remain for every stage. Acquisitions were online; installation, native analysis, build and evaluator execution were denied networking.

Each runtime independently creates a fresh venv and installs its wheel using `--no-index --require-hashes --only-binary=:all: --no-deps --no-compile`, retaining the pip report and raw output. Every installed non-RECORD member is compared byte for byte to its own wheel. Both complete original notices are copied into the temporary venv and read back with hashes; the existing notice-carrying deployment image is unchanged. Native import, fabricated float/string roundtrip, `LD_BIND_NOW=1 LD_DEBUG=libs,versions,bindings`, and both complete unchanged upstream evaluators on one invented row pass.

The existing unchanged provider collector was replayed: published wheel **703** undefined symbols, **0** strong resolution failures, **28** optional weak unresolved; rebuilt wheel **699**, **0**, **25**, respectively. Exact recursive ELF/package/glibc/provider identities, loader traces and observed host-kernel vDSO bytes are retained separately in the two runtime directories. The image does not pin the host kernel. Provider queries establish available resolutions; the loader trace records actual native-import bindings. The two fabricated evaluator outputs each contain the expected 16 metrics; these are synthetic controls, not benchmark measurements.

## Non-reproduction and remaining custody gap

**The wheel did not reproduce.** A successful build from verified source and identical package metadata support compatibility with that source, but do not authenticate the original binary's actual inputs. Different compiler markers and differing code sections show that this is not merely a ZIP timestamp or tag mismatch. This single reconstruction does not prove that no other original-environment reconstruction could reproduce it; it also does not prove malicious or modified source.

**Double-conversion's embedded link form is established; the exact vendored-versus-external-static producer selection and source/build custody are not. The blocker did not close.** The prior PyPI provenance 404 remains the recorded result; it was not queried again. The registry retains `status=external`, preserves its next action and all gates, and sharpens `observed` with this result. No production scoring code, prior receipts or `runs/` were changed. No benchmark, model, GPU or endpoint was run; no H0 authorization follows.
