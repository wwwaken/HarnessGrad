#!/usr/bin/env bash
set -eu
fixture=$(cd "$(dirname "$0")" && pwd)
repo=$(git -C "$fixture" rev-parse --show-toplevel)
scratch=$(mktemp -d /tmp/hg-woffscorer2-worlds-exec-XXXXXX)
mkdir "$scratch/tmp"
export HG_WOFFSCORER2_WORLD_SCRATCH="$scratch"
export HG_WOFFSCORER2_PARENT_NETNS
HG_WOFFSCORER2_PARENT_NETNS=$(readlink /proc/self/ns/net)
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=
python3 "$fixture/prepare.py"
timeout --kill-after=5s 150s python3 "$repo/tests/fixtures/hg_wverify/scorers/offline_exec.py" "$fixture/acquire_study_reference.py" > "$fixture/reference-selection-output.txt" 2> "$fixture/reference-selection-offline.txt"
python3 - "$fixture" "$scratch" "$repo" <<'PY'
import json, os, sys
from pathlib import Path
Path(sys.argv[1], "execution-scope.json").write_text(json.dumps({
    "scratch": sys.argv[2], "repo": sys.argv[3], "parent_netns": os.environ["HG_WOFFSCORER2_PARENT_NETNS"],
    "model": None, "endpoint": None, "jobs": 1, "controlled_input_count": {"jericho": 5, "scienceworld": 4},
    "maximum_actions_bound_each_case": 20, "maximum_wall_seconds_each_dataset_mode": 150,
    "production_runtime_observation": False, "eligible_benchmark_task_coverage": "not measured; study scorer controls only",
    "trials": "one fresh world per authored trace per independent side"}, indent=2) + "\n")
PY
for mode in official local; do
  timeout --kill-after=5s 150s env TMPDIR="$scratch/tmp" python3 "$repo/tests/fixtures/hg_wverify/scorers/offline_exec.py" "$fixture/execute.py" jericho "$mode" > "$fixture/jericho-$mode.json" 2> "$fixture/jericho-$mode-offline.txt"
done
for mode in official local; do
  timeout --kill-after=5s 150s bwrap --die-with-parent --unshare-net --ro-bind / / --tmpfs /tmp --ro-bind "$repo" "$repo" --bind "$scratch" "$scratch" --proc /proc --dev /dev --chdir "$scratch" --setenv TMPDIR "$scratch/tmp" --setenv PYTHONDONTWRITEBYTECODE 1 -- python3 "$fixture/namespace_exec.py" "$fixture/execute.py" scienceworld "$mode" > "$fixture/scienceworld-$mode.json" 2> "$fixture/scienceworld-$mode-offline.txt"
done
python3 "$fixture/compare.py"
python3 - "$fixture" "$scratch" <<'PY'
import json, shutil, sys
from pathlib import Path
shutil.rmtree(sys.argv[2])
Path(sys.argv[1], "cleanup.json").write_text(json.dumps({"scratch": sys.argv[2],
    "scratch_removed": not Path(sys.argv[2]).exists(), "no_runs_or_frozen_receipts_modified": True}, indent=2) + "\n")
PY
