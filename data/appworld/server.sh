#!/bin/sh
set -eu
mkdir -p /recordings/appworld/experiments
rm -rf /appworld/experiments
ln -s /recordings/appworld/experiments /appworld/experiments
export APPWORLD_ROOT=/appworld
exec python -m appworld.cli serve environment --port 8000 --no-show-usage --root /appworld
