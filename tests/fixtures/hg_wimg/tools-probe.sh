#!/bin/sh
# Read-only supplement: identify installed programs without executing task tools.
set +e
printf '%s\n' '=== libc and loader ==='
getconf GNU_LIBC_VERSION
ldd --version
for p in /lib64/ld-* /lib/ld-* /lib/*/ld-* /usr/lib/*/ld-*; do
    test -f "$p" || continue
    readlink -f "$p"
    sha256sum "$p"
done
printf '%s\n' '=== requested tools ==='
for name in "$@"; do
    printf '\nTOOL %s\n' "$name"
    path=$(command -v "$name")
    if test -z "$path" || ! test -f "$path"; then
        printf '%s\n' 'ABSENT_AS_FILE_ON_PATH'
        continue
    fi
    printf 'PATH %s\n' "$path"
    readlink -f "$path"
    sha256sum "$path"
    if command -v readelf >/dev/null 2>&1; then
        readelf -l -d -V -W "$path"
    fi
    ldd "$path"
    # Hash actual ldd-resolved providers, not host SONAME guesses.
    ldd "$path" 2>/dev/null | while read -r a b c rest; do
        case "$a" in /*) test -f "$a" && sha256sum "$a";; esac
        case "$c" in /*) test -f "$c" && sha256sum "$c";; esac
    done
done
printf '%s\n' '=== available package inventory ==='
if command -v dpkg-query >/dev/null 2>&1; then
    dpkg-query -W '-f=${Package}\t${Version}\t${Architecture}\n'
fi
if command -v apk >/dev/null 2>&1; then
    apk info -v
fi
exit 0
