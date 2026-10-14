#!/bin/sh
set -eux
python -I -B /opt/hg-wujson/network.py > /receipts/network-denial.json
case "$1" in
    published-runtime) wheel_dir=/opt/hg-wujson ;;
    rebuilt-runtime) wheel_dir=/packet/build/wheels ;;
    *) exit 2 ;;
esac
set -- "$wheel_dir"/*.whl
wheel=$1
python -I -B - "$wheel" <<'PY' > /receipts/requirements.txt
import hashlib
from pathlib import Path
import sys
print('ujson==5.10.0 --hash=sha256:' + hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
python -I -B -m venv /tmp/fresh-ujson
/tmp/fresh-ujson/bin/python -I -B -m pip --isolated --disable-pip-version-check --no-cache-dir install --no-index --find-links="$wheel_dir" --require-hashes --only-binary=:all: --no-deps --no-compile --report=/receipts/pip-install-report.json -r /receipts/requirements.txt > /receipts/pip-install.stdout.txt 2> /receipts/pip-install.stderr.txt
mkdir -p /tmp/fresh-ujson/share/licenses/hg-wujson2
cp /opt/hg-wujson/notices/ujson-LICENSE.txt /opt/hg-wujson/notices/double-conversion-LICENSE /tmp/fresh-ujson/share/licenses/hg-wujson2/
/tmp/fresh-ujson/bin/python -I -B /packet/scripts/runtime.py "$wheel" > /receipts/native-import.json
LD_BIND_NOW=1 LD_DEBUG=libs,versions,bindings /tmp/fresh-ujson/bin/python -I -B /packet/scripts/runtime.py "$wheel" > /receipts/loader-import.stdout.txt 2> /receipts/loader-debug.stderr.txt
/tmp/fresh-ujson/bin/python -I -B /opt/hg-wujson/synthetic.py > /receipts/synthetic-evaluator.json
/tmp/fresh-ujson/bin/python -I -B /opt/hg-wujson/providers.py > /receipts/providers-summary.json
