#!/usr/bin/env bash
set -euxo pipefail
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1
git rev-parse HEAD
git branch --show-current
python3 --version
timeout 180s python3 tests/fixtures/hg_woffscorer3/gaia_tau/offline_exec.py tests/fixtures/hg_we5/collect.py --output tests/fixtures/hg_we5/evidence
