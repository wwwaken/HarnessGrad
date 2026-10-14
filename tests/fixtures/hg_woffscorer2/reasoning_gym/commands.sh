#!/usr/bin/env bash
# Run from the repository root. Authored scorer inputs only; no benchmark tasks.
set -euo pipefail
packet=tests/fixtures/hg_woffscorer2/reasoning_gym
for side in official local compare; do
  timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
    python3 "$packet/offline_exec.py" "$packet/run.py" "$side" \
    > "$packet/$side.json" 2> "$packet/$side-offline.txt"
done
