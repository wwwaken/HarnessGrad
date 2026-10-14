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
