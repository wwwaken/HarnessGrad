#!/usr/bin/env bash
set -eu
p=tests/fixtures/hg_wverify/extra-scorers
for dataset in strategyqa sportsunderstanding fever hotpotqa triviaqa musique; do
  for panel in authored crosscheck; do
    timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 "$p/offline_exec.py" "$p/verify.py" "$dataset" "$panel" > "$p/$dataset-$panel.stdout.json" 2> "$p/$dataset-$panel.offline.txt"
  done
done
