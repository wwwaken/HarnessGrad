# Filesystem quota backend source audit — Codex 168

Worktree: `/tmp/hg-codex-168`; inspected base:
`10e983fc5fcb006c5afdbce1ef851dad71e953f2`.

**Finding:** no complete byte-and-inode enforcement backend is implemented and
connected for bwrap/files, Docker exec (including its writable container-state
root), or harness/method workspaces. No detector was implemented for these
unsupported modes. No claim is made about the host's currently installed quotas
or kernel capabilities; this audit inspected source only.

The existing cached inert Docker control requests a concrete bounded tmpfs
configuration with both `size` and `nr_inodes`, and artifact helpers can construct
and validate similar configurations. Those limited paths do not enforce quotas
on production task binds, exec upper layers or workspaces. Supplied admission
facts and mocked passes cannot establish kernel enforcement. `statvfs`,
`disk_usage`, reservation ledgers and snapshot preflight remain observations or
accounting, not quotas.

Added [the backend audit and OS implementation requirements](docs/filesystem-quota-backends.md)
and [source SHA-256 inventory](filesystem-quota-codex168-source-evidence.json).
The requirements identify XFS/ext4 project-quota provisioning, paired block/inode
hard limits, pre-staging scope allocation/inheritance, bounded tmpfs, actual
Docker driver/snapshotter integration, separate commit/export storage scopes,
trusted read-only kernel observations, fail-closed runner wiring and cleanup.
Updated the runner-contract documentation and platform/journal entries to link
this finding. Runtime source and existing tests are unchanged.

Validation command (synthetic contracts only):

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/quality/test_runner_admission.py tests/quality/test_terminal_artifact_admission.py --basetemp=/tmp/hg-codex-168/.quota-audit-test-tmp -p no:cacheprovider > filesystem-quota-codex168-test-result.txt 2>&1
```

Result: **252 passed in 0.35s**; [captured output](filesystem-quota-codex168-test-result.txt).
These existing tests deny real subprocess/socket execution and inject Docker
facts; they verify unsupported/missing quota fact refusals and small artifact
contracts. Owned synthetic test files were removed from this worktree afterwards.
No mounts, quota operations, daemon queries, model/H0, dataset payload reads or
benchmark execution occurred. No live enforcement receipt or score was produced.

Remaining blocker: implement and separately verify an OS/backend enforcement
service and complete trusted observer, then connect it before filesystem writes.
The current production runners do not use `runner_admission` as a launch gate.
Unsupported modes must remain blocked wherever quota admission is required.
