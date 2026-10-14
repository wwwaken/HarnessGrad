Added the [receipt design](/tmp/hg-codex-237/docs/task-237-ordinary-run-receipt.md), schema, and contract tests covering quota `false`/`unknown`, sandbox facts, invalid/unmeasured states, metric identity, and explicit non-production labeling.

The proposal supports ordinary use without quota administration and grants no production authorization. Runtime behavior is unchanged.

`git diff --check` passed. Tests and runs were not executed.