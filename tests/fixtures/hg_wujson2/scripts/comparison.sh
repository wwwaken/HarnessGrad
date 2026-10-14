#!/bin/sh
set -eux
python -I -B /opt/hg-wujson/network.py > /receipts/network-denial.json
python -I -B /packet/scripts/compare.py
