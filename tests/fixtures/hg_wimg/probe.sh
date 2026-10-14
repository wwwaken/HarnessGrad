#!/bin/sh
# No task entrypoint, image CMD or benchmark code is executed.
set +e
printf '%s\n' '=== image-local shell facts ==='
for name in sh bash python3 python pypy3 java node ruby R; do
    command -v "$name"
done
getconf GNU_LIBC_VERSION
ldd --version
printf '%s\n' '=== loader paths ==='
ls -l /lib64/ld-* /lib/ld-* /lib/*/ld-* /usr/lib/*/ld-*
printf '%s\n' '=== shell ABI ==='
ldd /bin/sh
ldd /bin/bash
printf '%s\n' '=== interpreter ==='
python3 --version
printf '%s\n' '=== bash ==='
bash --version
printf '%s\n' '=== network namespace ==='
cat /proc/net/route
ls /sys/class/net
printf '%s\n' '=== Python collector follows ==='
exec python3 -I -B /wimg/probe.py "$1"
