#!/bin/sh
set -eux
python -I -B /opt/hg-wujson/network.py > /receipts/network-denial.json
. /packet/build-env.sh
unset UJSON_BUILD_DC_LIBS UJSON_BUILD_DC_INCLUDES UJSON_BUILD_NO_STRIP
python -I -B -m venv /tmp/builder
/tmp/builder/bin/python -I -B -m pip --isolated --disable-pip-version-check --no-cache-dir install --no-index --find-links=/packet/acquired --require-hashes --only-binary=:all: --no-deps --report=/receipts/build-deps-install-report.json -r /packet/build-requirements.txt
/tmp/builder/bin/python -I -B -m pip list
python -I -B /packet/scripts/environment.py > /receipts/environment.json
gcc --version
g++ --version
ld --version
ldd --version
mkdir /tmp/source
tar -xzf /packet/acquired/ultrajson-59875e089937c8b05c2f4b474530e3a9ec706a56.tar.gz -C /tmp/source --strip-components=1
cd /tmp/source
sha256sum setup.py pyproject.toml setup.cfg LICENSE.txt deps/double-conversion/LICENSE
for source in setup.py pyproject.toml setup.cfg .github/workflows/deploy.yml lib/dconv_wrapper.cc deps/double-conversion/double-conversion/string-to-double.cc; do
    echo "FILE: $source"
    nl -ba "$source"
done > /receipts/source-lines.txt
/tmp/builder/bin/python -B setup.py bdist_wheel --dist-dir=/receipts/wheels
sha256sum /receipts/wheels/*.whl
