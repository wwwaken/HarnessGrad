#!/usr/bin/env python3
import pathlib,json,hashlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[1];repo=ROOT.parents[2]
wh=json.loads((ROOT/'artifacts/wheels.json').read_text());apt=json.loads((ROOT/'raw/apt-artifacts.json').read_text());inv=json.loads((ROOT/'source/inventory.json').read_text());summary=json.loads((ROOT/'source/summary.json').read_text())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
text='''# Terminal-Bench uvx bootstrap custody — w-uvx

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
| 8 | `curl -LsSf https://astral.sh/uv/0.9.5/install.sh \\| sh`: uv/uvx 0.9.5 installer and platform archive; no source-declared byte hash |
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
'''
for w in wh:text+=f"| `{pathlib.Path(w['path']).name}` | `{w['sha256']}` |\n"
text+='\n| Other artifact | Recomputed SHA-256 |\n| --- | --- |\n'
for f in ['uv-install.sh','uv-x86_64-unknown-linux-gnu.tar.gz']:text+=f'| `{f}` | `{h(ROOT/"artifacts"/f)}` |\n'
for x in json.loads((ROOT/'artifacts/uv-members.json').read_text()):text+=f"| Archive member `{x['path']}` | `{x['sha256']}` |\n"
text+='''
The archive's uv/uvx member hashes also match the binaries installed by the fetched installer (raw online stdout). The installer reports “no checksums to verify”; our local SHA-256 pins establish retained-byte identity, not upstream release attestation.

The apt operation fetched **19 bounded .deb artifacts**, including curl **7.88.1-10+deb12u15**. Each actual package's version/architecture/dependencies, captured `dpkg-deb -f` argv/stdout, byte size and recomputed digest is in `raw/apt-artifacts.json`; the complete list and hashes follows. Capturing disables the disposable image's `docker-clean` apt hook so apt retains its downloads; it does not change requested packages. The first collection failed *after* apt installation because that hook had deleted the .debs. Its raw outputs and original script are preserved as `raw/attempt1-online.*`, `raw/attempt1-online-container-inspect.*`, `raw/attempt1-online-cleanup.*` and `scripts/attempt1-online.sh`. A fresh second container collected successfully; no failed attempt is reported as a passed bootstrap.

| Captured Debian artifact | Recomputed SHA-256 |
| --- | --- |
'''
for a in apt:text+=f"| `{pathlib.Path(a['path']).name}` | `{a['sha256']}` |\n"
text+='''
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
'''
for r in inv:
 if r['phase']!='verifier-bootstrap':continue
 rel=str(pathlib.Path(r['path']).relative_to('/mnt/20t/xubuqiang/datasets/terminal-bench'));cmd=r['text'].replace('\\\n',' ').replace('\n',' ').replace('|','\\|')
 text+=f"| `{rel}:{r['line']}` | `{cmd}` |\n"
(repo/'reports/w-uvx-bootstrap.md').write_text(text)
print('report bytes',len(text.encode()),'bootstrap rows',sum(x['phase']=='verifier-bootstrap' for x in inv))
