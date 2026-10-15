#!/usr/bin/env bash
set -euo pipefail
packet=tests/fixtures/hg_woffscorer3/code_chess
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 JAX_PLATFORMS=cpu
python3 "$packet/prepare.py" > "$packet/preparation.json"
timeout 150s python3 "$packet/offline_exec.py" "$packet/execute.py" chess-official > "$packet/chess-official.json" 2> "$packet/chess-official-offline.txt"
timeout 150s python3 "$packet/offline_exec.py" "$packet/execute.py" chess-local > "$packet/chess-local.json" 2> "$packet/chess-local-offline.txt"
timeout 150s python3 "$packet/offline_exec.py" "$packet/execute.py" lcb-official > "$packet/lcb-official-strict-probe.json" 2> "$packet/lcb-official-strict-probe-offline.txt"
export HG_WOFFSCORER3_PARENT_NETNS
HG_WOFFSCORER3_PARENT_NETNS=$(readlink /proc/self/ns/net)
timeout 150s bwrap --unshare-net --die-with-parent --ro-bind / / --bind /tmp /tmp --proc /proc --dev /dev python3 "$packet/namespace_exec.py" "$packet/execute.py" lcb-official > "$packet/lcb-official.json" 2> "$packet/lcb-official-offline.txt"
timeout 150s python3 "$packet/offline_exec.py" "$packet/execute.py" lcb-local > "$packet/lcb-local.json" 2> "$packet/lcb-local-offline.txt"
python3 "$packet/compare.py" > "$packet/comparison.json"
