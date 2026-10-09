#!/bin/sh
set -eu
mkdir -p /recordings/appworld/experiments
rm -rf /appworld/experiments
ln -s /recordings/appworld/experiments /appworld/experiments
export APPWORLD_ROOT=/appworld
exec python -m uvicorn appworld_service:app --host 0.0.0.0 --port 8000
