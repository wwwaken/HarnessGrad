#!/usr/bin/env bash
set -euo pipefail
packet=tests/fixtures/hg_woffscorer3/gaia_tau
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 "$packet/prepare.py" > "$packet/preparation.json"
timeout 150s python3 "$packet/offline_exec.py" "$packet/import_probe.py" > "$packet/tau-full-import.json" 2> "$packet/tau-full-import.offline.txt"
for dataset in gaia tau; do
  for mode in official local; do
    timeout 150s python3 "$packet/offline_exec.py" "$packet/run.py" "$dataset" "$mode" > "$packet/$dataset-$mode.json" 2> "$packet/$dataset-$mode.offline.txt"
  done
done
python3 "$packet/compare.py" > "$packet/comparison.json"
