#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../.."
packet=tests/fixtures/hg_woffscorer3/bfcl
for side in import official local compare; do
  timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
    python3 "$packet/offline_exec.py" "$packet/run.py" "$side" \
    > "$packet/$side.json" 2> "$packet/$side-offline.txt"
done
