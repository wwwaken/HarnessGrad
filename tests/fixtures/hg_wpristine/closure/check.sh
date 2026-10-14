#!/control-scorer/sh
# Diagnostic control only: exact answer for the authored task 19 + 23.
set -eu
IFS= read -r expected < /control-scorer/expected.txt
IFS= read -r actual < /control-input/answer.txt
printf 'control_kind=synthetic-diagnostic\nexpected=%s\nactual=%s\n' "$expected" "$actual"
# Kernel observations from inside the actual scorer, not launch declarations.
for resource in cpu.max memory.max pids.max memory.current pids.current; do
    if IFS= read -r value < "/sys/fs/cgroup/$resource"; then
        printf 'cgroup.%s=%s\n' "$resource" "$value"
    else
        printf 'cgroup.%s=unknown\n' "$resource"
    fi
done
while IFS= read -r mount; do
    case "$mount" in
        *' /tmp '*|*' /control-output '*|*' /control-input '*|*' /control-scorer '*)
            printf 'mountinfo=%s\n' "$mount" ;;
    esac
done < /proc/self/mountinfo
if [ "$actual" = "$expected" ]; then
    printf 'completed_check=pass\n'
    exit 0
fi
printf 'completed_check=fail\n'
exit 1
