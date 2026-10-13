# TriviaQA scorer provenance — Codex 157

Docs/tests repair complete in `/tmp/hg-codex-157`; upstream acquisition remains
blocked. No production scorer, model, H0, endpoint, released dataset or heldout
payload was used or changed. No network acquisition was attempted.

The previous test reference duplicated the adapter rather than verifying an
upstream source. It has been removed. The new mandatory test requires independently
acquired source/license bytes, a GitHub scorer commit separate from the Hub dataset
pin, reviewed acquisition evidence, and SHA-256/Git blob hashes. There is no fake
upstream implementation, installed placeholder receipt, F1 addition, skip or
local-reference fallback.

The [acquisition contract](tests/fixtures/triviaqa_upstream/README.md) records
`rc.nocontext`, validation, EM-only and row/question/document grouping comparison
boundaries. Exact full-evaluator grouping and denominator rules remain unverified.
Source-file identity and finite EM component checks cannot certify a complete
leaderboard evaluation.

Validation used the commands in that contract with workspace-local temporary
directories and disabled third-party pytest plugin autoload:

- Full suite: exit 1, **28 passed / 1 failed / 0 skipped / 0 errors**. The only
  failure is `test_em_components_match_pinned_upstream_fixture`, because acquired
  source and `provenance.json` are absent. This is the required fail-closed result.
- Contract/local subset: exit 0, **28 passed / 1 deselected**. This excludes the
  source gate and establishes no upstream equivalence.
- `git diff --check`: passed. Generated synthetic temporary files were removed.

The first test invocation lacked the parent directory for `--basetemp`; after
creating it, both final commands produced the results above. The documented
commands include that setup.

Remaining work requires original acquisition material and a separate review;
passing synthetic checks does not authorize model/H0 execution. The safe docs/tests
commit is titled `test: fail closed on unacquired TriviaQA scorer provenance`;
its exact hash is reported with delivery.
