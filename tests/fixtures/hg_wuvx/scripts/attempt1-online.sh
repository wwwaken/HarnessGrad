#!/bin/bash
set -euxo pipefail
export UV_CACHE_DIR=/root/wuvx-cache
printf 'Binary::apt-get::APT::Keep-Downloaded-Packages "true";\n' > /etc/apt/apt.conf.d/99wuvx-capture
apt-get update
apt-get install -y curl
cp /var/cache/apt/archives/*.deb /packet/artifacts/apt/
dpkg-query -W > /packet/raw/online-dpkg.txt
curl -LsSf --max-time 120 https://astral.sh/uv/0.9.5/install.sh -o /packet/artifacts/uv-install.sh
sh /packet/artifacts/uv-install.sh
source /root/.local/bin/env
uv --version
uvx --version
sha256sum /root/.local/bin/uv /root/.local/bin/uvx
uvx -vv -p 3.13 -w pytest==8.4.1 -w pytest-json-ctrf==0.3.5 pytest --version
find "$UV_CACHE_DIR" -name pyvenv.cfg -print > /packet/raw/venv-paths.txt
mapfile -t cfgs < /packet/raw/venv-paths.txt
test "${#cfgs[@]}" = 1
"$(dirname "${cfgs[0]}")/bin/python" /packet/scripts/probe.py > /packet/raw/online-python.json
find "$UV_CACHE_DIR" -maxdepth 4 -type f -name '*.http' -o -name '*.rkyv' > /packet/raw/cache-metadata-paths.txt
curl -LsSf --max-time 180 https://github.com/astral-sh/uv/releases/download/0.9.5/uv-x86_64-unknown-linux-gnu.tar.gz -o /packet/artifacts/uv-x86_64-unknown-linux-gnu.tar.gz
tar -tzf /packet/artifacts/uv-x86_64-unknown-linux-gnu.tar.gz
