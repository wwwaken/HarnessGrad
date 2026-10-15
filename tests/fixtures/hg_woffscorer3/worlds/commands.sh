#!/usr/bin/env bash
set -euo pipefail
F=$(cd -- "$(dirname -- "$0")" && pwd)
R=$(git -C "$F" rev-parse --show-toplevel)
cd "$R"
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 "$F/prepare_alfworld.py"
for side in official local; do
 timeout 150s python3 "$F/offline_exec.py" "$F/run_alfworld.py" "$side" > "$F/alfworld-$side.json" 2> "$F/alfworld-$side-offline.txt"
done
IMAGE=sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca
docker image inspect "$IMAGE" > "$F/appworld-image-inspect.json"
# Archive is preserved as common input; source preparation is reproducible separately:
# docker run --rm --network none --read-only --tmpfs /tmp:rw,nosuid,size=256m --cpus 1 --memory 1g --pids-limit 128 --ulimit cpu=120:120 --ulimit nofile=256:256 -e PYTHONDONTWRITEBYTECODE=1 -e CUDA_VISIBLE_DEVICES= -e HG_IMAGE="$IMAGE" --mount "type=bind,src=$F,dst=/output" --entrypoint python "$IMAGE" /output/prepare_appworld.py
names=()
cleanup() {
 for name in "${names[@]}"; do docker rm -f "$name" >/dev/null 2>&1 || true; done
}
trap cleanup EXIT
for side in official local; do
 name="hg-woffscorer3-worlds-${side}-$$";names+=("$name")
 timeout 150s docker run --rm --name "$name" --network none --read-only --tmpfs /tmp:rw,nosuid,size=256m --tmpfs /appworld:ro,size=1m --cpus 1 --memory 1g --pids-limit 128 --ulimit cpu=120:120 --ulimit nofile=256:256 -e PYTHONDONTWRITEBYTECODE=1 -e CUDA_VISIBLE_DEVICES= --mount "type=bind,src=$F,dst=/fixture,readonly" --entrypoint python "$IMAGE" /fixture/appworld_parent.py "$side" > "$F/appworld-$side.json" 2> "$F/appworld-$side-offline.txt"
 if docker inspect "$name" > "$F/appworld-$side-post-inspect.json" 2> "$F/appworld-$side-cleanup.txt"; then
  echo 'Unexpected remaining fixture container' >&2;exit 1
 fi
done
python3 "$F/compare.py" > "$F/comparison.stdout.json"
