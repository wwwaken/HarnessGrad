#!/usr/bin/env bash
# Keep the two local HarnessGrad Qwen endpoints alive without duplicating healthy servers.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVE="$ROOT/tools/serve_local_model.sh"
STATE="${HARNESSGRAD_MODEL_STATE:-/tmp/harnessgrad-local-models}"
INTERVAL="${HARNESSGRAD_MODEL_CHECK_INTERVAL:-30}"
mkdir -p "$STATE"

is_healthy() {
  local port="$1"
  curl -fsS --max-time 3 "http://127.0.0.1:${port}/v1/models" >/dev/null 2>&1
}

start_one() {
  local gpu="$1" model="$2" port="$3" name="$4"
  local log="$STATE/${port}.log"
  if is_healthy "$port"; then
    return 0
  fi
  # The serve script performs its own readiness wait and uses the pinned vLLM environment.
  # Run it detached so a slow model load does not block supervision of the other GPU.
  CUDA_VISIBLE_DEVICES="$gpu" HARNESSGRAD_VLLM_LOG="$log" \
    nohup "$SERVE" --model "$model" --port "$port" --tp 1 \
      --max-len 16384 --name "$name" >>"$log" 2>&1 < /dev/null &
  echo "$!" > "$STATE/${port}.launcher.pid"
}

while :; do
  start_one 0 /mnt/20t/qzs/PLMs/Qwen3.5-9B 8001 qwen3.5-9b-local
  start_one 1 /mnt/20t/qzs/PLMs/Qwen3.5-9B 8002 qwen3.5-9b-local
  sleep "$INTERVAL"
done
