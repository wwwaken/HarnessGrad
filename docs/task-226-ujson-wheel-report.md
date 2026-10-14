# Task 226: exact ujson wheel and offline package provenance

**Artifact acquisition and fresh offline package installation verified. Native
runtime and supported-image closure remain blocked.** No benchmark dataset,
adapter, model, endpoint, H0, pilot or official scorer was used. All task writes
are inside `/tmp/hg-codex-226`; the base is
`61e7f82245c76e7c833740216940d1fcaf3b76be`.

## Exact target and artifact

The code-only task-197 provenance receipt records **CPython 3.12.4, Linux,
x86_64**. For this target using **glibc >= 2.17**, the exact selected wheel is:

```text
ujson-5.10.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
bytes: 53686
sha256: f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1
```

Official release metadata:
<https://pypi.org/pypi/ujson/5.10.0/json>

Exact wheel URL from that response:
<https://files.pythonhosted.org/packages/04/81/668707e5f2177791869b624be4c06fb2473bf97ee33296b18d1cf3092af7/ujson-5.10.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl>

The retained original JSON response has SHA-256
`a3c95fe11a39ff2db660e12cee42ff27ad0411d205320d1350fbc2924a7ab6a2`.
It lists this artifact as an unyanked `bdist_wheel`, uploaded
`2024-05-14T02:01:07.618187Z`. Acquisition on 2026-10-14 verified the URL,
filename, byte length and SHA-256 before inspection. HTTPS PyPI metadata supplies
the origin evidence; the hashes are byte identities, not an independent
publisher signature. No sdist or build dependency was downloaded.

The wheel declares `Root-Is-Purelib: false` and two equivalent platform tags:
`cp312-cp312-manylinux_2_17_x86_64` and
`cp312-cp312-manylinux2014_x86_64`. `Requires-Python: >=3.8` describes the
release, while this particular artifact requires the **cp312 ABI**. It does not
provide a CPython 3.8/3.11/3.13, PyPy, musl/Alpine or ARM artifact. The manylinux
tag is a compatibility declaration; an immutable supported-image receipt was
not supplied. The current installation host reports glibc 2.35, which does not
establish minimum-baseline or supported-image execution.

## License and notices

The exact wheel's `ujson-5.10.0.dist-info/LICENSE.txt` is retained verbatim in the
[fixture](../tests/fixtures/ujson_pypi_codex226/LICENSE.txt): 5,975 bytes, SHA-256
`36866344f0a486541bd9800f1a407a056c0c214a82c658f059694daf3dc394d2`.
The project uses BSD-3-Clause terms. The combined file includes:

- Electronic Arts / ESN copyright, redistribution conditions and disclaimer.
- MODP_ASCII / Nick Galbreath BSD terms and attribution.
- Tcl-derived numeric-decoder copyright and permission/disclaimer terms.

Retain the **entire** combined license file with redistributed binaries and
their documentation/materials; retaining only the project SPDX label would
lose embedded notices. There is no separate `NOTICE` member in this wheel.
PyPI's current `info.license` is null; that is not evidence of absent licensing.

**Notice completeness remains unverified:** ELF exports include defined
`double_conversion` functions, and the embedded package description says the
default build uses a bundled copy. The wheel's combined license has no
double-conversion/V8 notice. These observations require a source/license review;
they do not identify the precise bundled revision or independently prove all
applicable terms. Before redistributing an image, obtain authoritative
code-only source/revision and license evidence for the bundled component and
carry any required notices. This task neither downloaded an sdist nor invented
a missing notice or declared redistribution clearance.

## Python and native dependency metadata

PyPI JSON has `requires_dist: null`; wheel METADATA has no `Requires-Dist`.
There are **no declared transitive Python runtime packages**. This says nothing
about system libraries or the Python/installer runtime.

Static GNU `readelf` 2.38 inspection of the verified wheel's extension records:

| ELF property | Observed value |
|---|---|
| Member | `ujson.cpython-312-x86_64-linux-gnu.so` |
| Identity | ELF64, little endian, DYN, AMD x86-64 |
| Member bytes / SHA-256 | 105,936 / `deb036e60d4b61104bad389783094ebb09a35dbdecd21aeea572968762c3be5c` |
| Direct DT_NEEDED | `libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1`, `libpthread.so.0`, `libc.so.6` |
| Version needs from libc | `GLIBC_2.2.5`, `GLIBC_2.14` |
| Version needs from libstdc++ | `CXXABI_1.3`, `GLIBCXX_3.4` |
| Version needs from libgcc_s | `GCC_3.0` |
| RPATH / RUNPATH | Neither present |
| Bundled shared libraries | None; `ujson.libs/` is empty |

No version-need entries are declared directly for libm/libpthread. CPython API
symbols are undefined ELF imports resolved by the target Python process; there
is no direct `libpython` dependency. The maximum observed libc symbol version
does not lower the declared manylinux glibc floor from 2.17 to 2.14. Dependency
names, version requirements and wheel tags cannot prove loader search paths,
actual provider files, transitive libraries, CPU baseline or runtime success.

The old task-197 **installed** module hash was
`41ef15691cb490d5c38cde5f7e588d9d348cb92008888a0dcb2770ae84ea87db`,
with three observed direct libraries. It differs from this published wheel.
In particular, the old observation omitted this artifact's `libm.so.6` and
`libpthread.so.0`. The old module and old synthetic passes cannot attest the
new artifact's loader closure. Historical receipts were preserved.

## Reproducible offline installation procedure

The fixture includes the exact original wheel under `artifacts/`, acquisition
metadata, the original PyPI response, package hash lock, copied license, static
ELF reports, pip installation report and installed-file receipt. Its offline
tests verify the independent origin/artifact pins, archive RECORD hashes and
sizes, original member identities, tags/notices and actual ELF requirements.

For another acquisition, request the official version JSON above, select the
single exact filename, require `bdist_wheel`, `yanked=false`, expected size and
the SHA-256 above, and use **only that entry's HTTPS files.pythonhosted.org URL**.
Fetch into a fresh isolated task worktree, verify byte length and SHA-256 before
publishing the wheel to an offline wheelhouse, and retain the original JSON and
acquisition time/headers. Do not substitute an index-selected artifact, sdist,
different platform or locally installed module if a check fails.

For reproducibility, first identify an approved immutable Linux/x86_64 image
with CPython 3.12.4, glibc >=2.17, venv/ensurepip and a pinned pip version.
Record interpreter, pip and native-runtime identities. A venv inherits the host
Python and native libraries; it does not pin an OS image. The following procedure
was verified on the current host with pip 24.0, **without importing ujson**.
Run from `/tmp/hg-codex-226` in a fresh task directory:

```bash
set -eu
test ! -e .scratch/ujson-codex226-replay
mkdir -p .scratch/ujson-codex226-replay
TMPDIR="$PWD/.scratch/ujson-codex226-replay" python -B -m venv \
  .scratch/ujson-codex226-replay/venv
.scratch/ujson-codex226-replay/venv/bin/python -I -B - <<'PY'
import importlib.metadata, platform, sys
assert sys.implementation.name == 'cpython'
assert sys.version_info[:3] == (3, 12, 4)
assert platform.system() == 'Linux' and platform.machine() == 'x86_64'
family, version = platform.libc_ver()
assert family == 'glibc' and tuple(map(int, version.split('.'))) >= (2, 17)
assert importlib.metadata.version('pip') == '24.0'
PY
PIP_CONFIG_FILE=/dev/null TMPDIR="$PWD/.scratch/ujson-codex226-replay" \
  .scratch/ujson-codex226-replay/venv/bin/python -I -B -m pip \
  --isolated --disable-pip-version-check --no-cache-dir install \
  --no-index --find-links="$PWD/tests/fixtures/ujson_pypi_codex226/artifacts" \
  --require-hashes --only-binary=:all: --no-deps --no-compile \
  --report="$PWD/.scratch/ujson-codex226-replay/install-report.json" \
  -r tests/fixtures/ujson_pypi_codex226/requirements-codex226.txt
```

Stop on any failed command; never reuse a partial environment. The hash lock has
one exact version and one exact wheel digest. `--no-deps` is appropriate only
because the verified METADATA declares no Python dependencies. Binary-only
installation avoids source builds and build-backend execution. The checked
wheel contains no `.pth` or installer script. `PIP_CONFIG_FILE=/dev/null`
disables pip configuration files, including global and site files that
`--isolated` alone still permits. Together with Python `-I`, disabled
index/version/cache access and a fresh venv, this avoids ambient installer
configuration. These options are not an OS network sandbox; an approved
supported-image replay should also deny networking at the runtime boundary.

Preserve the pip report and compare the installed extension, METADATA, WHEEL,
top-level declaration and complete license to the original wheel. Installed
RECORD differs because pip adds installation records; validate the original
archive RECORD separately. The task-226 fresh venv passed these byte comparisons
for all five original non-RECORD files. No native extension was imported, no
`ldd` or dynamic loader was invoked, and the global Python installation was
unchanged. Temporary task directories are removed after evidence is retained.

## Precise remaining blocker

The platform/image owner must provide a supported immutable image manifest,
Python/interpreter identity and native loader receipt for **this wheel hash**.
That receipt must bind loader configuration and resolved paths/hashes/package
versions for all five DT_NEEDED libraries and their recursive dependencies,
including required symbol-version providers and CPython API resolution.
The bundled-component notice review above remains open as well.

Then repeat a fresh network-denied installation in that image, preserve the
artifact-to-installed-file mapping, and observe a native import plus a tiny
fabricated JSON encode/decode round trip. Any later unchanged-scorer synthetic
check needs its own receipt tied to this wheel/image identity. Installation
success alone is insufficient because wheel installation does not load its ELF.

The `ujson-native-offline-closure` registry blocker remains **external**;
supported-image, loader/transitive runtime, native import and production
authorization flags remain false. Dataset provenance and shared admission gates
are unchanged. This task supplies package evidence and a procedure, not a
benchmark or runtime-closure receipt.

## Focused verification

Run the source/package-only suite with GNU readelf available, plugin autoload
disabled, bytecode/cache disabled, and task-local temporary paths:

```bash
mkdir -p .scratch/ujson-codex226-tests
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  TMPDIR="$PWD/.scratch/ujson-codex226-tests" python -B -m pytest -q \
  -p no:cacheprovider --basetemp=.scratch/ujson-codex226-tests/pytest \
  tests/quality/test_ujson_pypi_codex226.py tests/quality/test_dataset_blockers.py
python -B tools/check_dataset_blockers.py
```

Final test counts and task-local cleanup are recorded in
[`ujson-wheel-codex226-test-result.txt`](../ujson-wheel-codex226-test-result.txt)
and the integration journal. The initial run had 23 failures and 38 passes:
one lexical-versus-version ordering comparison error in the new ELF test and
one nonliteral registry locator causing 22 cascading registry failures.
Both were corrected; the original failure output is preserved in
[`ujson-wheel-codex226-initial-test-result.txt`](../ujson-wheel-codex226-initial-test-result.txt).
Raw readelf reports and initial pytest output retain tool-emitted trailing
whitespace. Authored docs/code pass the focused staged whitespace check;
normalizing pinned evidence would alter the preserved bytes.
Parent diff review/integration remains separate.
