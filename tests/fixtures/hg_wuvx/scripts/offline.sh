#!/bin/bash
set -euxo pipefail
cd /packet/artifacts
sha256sum -c SHA256SUMS
test -z "$(ls -A /root/.cache 2>/dev/null || true)"
test ! -e /root/wuvx-cache
cat /proc/net/route
python3 - <<'PY'
import socket,json
r=[]
for address in [('172.17.0.1',17890),('1.1.1.1',443)]:
 s=socket.socket();s.settimeout(1)
 try:s.connect(address);raise RuntimeError('Unexpected external connection')
 except OSError as e:r.append({'address':address,'error':str(e),'errno':e.errno})
 finally:s.close()
print(json.dumps(r))
PY
dpkg -i /packet/artifacts/apt/*.deb
dpkg-query -W > /tmp/offline-dpkg.txt
curl --version
tar -xzf /packet/artifacts/uv-x86_64-unknown-linux-gnu.tar.gz -C /tmp
cd /tmp
sha256sum -c /packet/artifacts/uv-binaries.sha256
export PATH=/tmp/uv-x86_64-unknown-linux-gnu:$PATH
export UV_CACHE_DIR=/tmp/wuvx-locked-cache
uv --version
uvx --version
uv venv --no-python-downloads -p /usr/local/bin/python3.13 /tmp/locked-venv
uv pip install --offline --no-index --find-links /packet/artifacts/wheels --require-hashes --python /tmp/locked-venv/bin/python -r /packet/artifacts/requirements.lock
export UV_CACHE_DIR=/tmp/wuvx-uvx-cache
test ! -e "$UV_CACHE_DIR"
uvx -vv --offline --no-index --find-links /packet/artifacts/wheels --no-python-downloads -p /usr/local/bin/python3.13 -w pytest==8.4.1 -w pytest-json-ctrf==0.3.5 pytest --version
uvx --offline --no-index --find-links /packet/artifacts/wheels --no-python-downloads -p /usr/local/bin/python3.13 -w pytest==8.4.1 -w pytest-json-ctrf==0.3.5 pytest --help > /tmp/offline-pytest-help.txt
grep -F -- '--ctrf' /tmp/offline-pytest-help.txt
find "$UV_CACHE_DIR" -name pyvenv.cfg -print > /tmp/offline-venv-paths.txt
mapfile -t cfgs < /tmp/offline-venv-paths.txt
test "${#cfgs[@]}" = 1
"$(dirname "${cfgs[0]}")/bin/python" /packet/scripts/probe.py > /tmp/offline-python.json
ldd /tmp/uv-x86_64-unknown-linux-gnu/uv
ldd /tmp/uv-x86_64-unknown-linux-gnu/uvx
ldd /usr/bin/curl
