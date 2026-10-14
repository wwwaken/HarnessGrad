# Task 205 — TriviaQA scorer review

Reviewed isolated worktree `/tmp/hg-codex-205` at base
`65b0f2a` (2026-10-14), including fixture acquisition commit
`88dbe05200d9da93c5a2c8dafc0187773e2a1375` and normalization correction
`fcbed17368e27d1f065ae334dee53f6b3973d91d`.

The original-source provenance checks pass, and the merged normalization matches
upstream on synthetic inputs. One remaining scoring mismatch was reproduced and
fixed: gold materialization silently discarded aliases after position 200.
New evidence now records an explicit corrected adapter identity.

## Source, license and commit linkage

- Original repository: `https://github.com/mandarjoshi90/triviaqa`.
- Immutable scorer-reference commit: `ca43b5820b107f3970cf4b7d67f7db7a98117b79`;
  distinct from Hub dataset revision `0f7faf33a3908546c6fd5b73a660e0f8ff173c2f`.
- Original `evaluation/triviaqa_evaluation.py`: 5,710 bytes; SHA-256
  `51785a3bc2e02a8f1ebf9db3aa18834c6a5daa5089ee5d435c99e0babf4be682`;
  Git blob `b67ffcda2fc1af0616a427dc3280aa4189aef7db`.
- Original Apache-2.0 `LICENSE`: 11,340 bytes; SHA-256
  `5cc548335f22310a53877044624711ac3e20e5ed1117617c1fd3fc462c54330e`;
  existing Kenton Lee copyright preserved. The retained README license-only patch
  states that Apache-2.0 applies to code and data; the pinned root has no NOTICE.
- The offline tests verify all five source/helper/license/requirements file pins,
  retained evidence hashes, reconstructed commit Git identity, and root/subtree
  membership linking those blobs to the commit. They reconstruct signed commit
  bytes from retained GitHub payload/signature metadata. This is an offline
  consistency/linkage review; no independent PGP verification or new human
  acquisition attestation is claimed. The original receipt's reviewer scope and
  acquisition-time `production_scorer_changed: false` remain historical facts.
- Unmodified evaluator/helpers/CLI execute on fabricated inputs with standard
  library dependencies only. Repository-wide TensorFlow/NLTK/etc. declarations
  are retained but are not evaluator dependencies and were not installed.

## Narrow correction and identity

The new regression constructs 201 aliases with the sole hit at index 200.
Before correction, upstream alias-max EM is 1 and the adapter reward is 0.
This occurs for normalized aliases, human answers, and a combination of both.
`_gold` now preserves the full accepted list. This proves the code mismatch;
whether any released row exceeds the former cap was not inspected or inferred.
Larger alias lists now produce correspondingly larger gold artifacts and scoring
work; any future resource limit must reject an unsupported row explicitly rather
than silently change its score.

New shared-verifier evidence records
`official.scorer_identity = triviaqa-alias-max-em-upstream-normalization-all-aliases-v2`
and `official.reference` containing upstream repository, commit, source path and
source SHA-256. Synthetic hit and miss tests read the evidence actually written
by `data.qa.verify.check`. Existing reward, metric and compatibility fields remain.
The reference hash identifies original upstream source, not the deployed adapter.

Adapter source-byte SHA-256 identities:

- Before the normalization merge (`fcbed17^`):
  `67fd8504afba1f0f27de37a1ea5a401f2ea3ea8545ce562c2d42680494e962c9`.
- Review base, normalized but still capped (`65b0f2a`):
  `7cd8e58517bf7842cc4aedda59aefd8115d33c098113897476b3feadac88dd39`.
- Corrected current adapter (`data/triviaqa.py`):
  `1c18737824cbda3bb3e90bbdea3805f5b83c2ddc53f239de29c8a447335f6dcd`.

Historical results, receipts, acquisition evidence and old reports are untouched;
the intermediate normalized/capped adapter is not retroactively given the new
identity. Updated fixture/download docs distinguish past failures from current
component checks. Adapter docstrings no longer claim byte-for-byte transcription;
the merged normalization change had also removed a journal section header, which
is restored without changing its historical GSM8K entry.

## Focused synthetic validation

Initial existing suites: **32 passed**. New task-205 regressions before the fix:
**1 passed, 5 failed** (three lost-alias matches and two absent-identity evidence
checks), retained in `triviaqa-scorer-review-codex205-before-test-result.txt`.
The separator/Unicode comparison already passed on the merged correction.
It covers 82 authored strings across ASCII punctuation, added quote characters,
Unicode punctuation that upstream preserves, and whitespace.

Final command, from this worktree:

```sh
env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/quality/test_triviaqa_official_scorer.py tests/quality/test_triviaqa_source_provenance_codex196.py tests/quality/test_triviaqa_scorer_review_codex205.py --basetemp=/tmp/harnessgrad-pytest-triviaqa-codex205-final > triviaqa-scorer-review-codex205-test-result.txt 2>&1
```

Exit 0: **38 passed**, no failures/skips. The new suite uses the shared private
adapter fixture, which suppresses pool construction and forbids parquet/row reads
before adapter import; network connections are forbidden. Source-only evaluator
execution uses a fresh isolated interpreter and fabricated temporary JSON files.
The provisioned dataset suite `test_triviaqa_dataset.py` was not run.

`PYTHONDONTWRITEBYTECODE=1 python3 tools/check_triviaqa_provenance.py` exits 0,
verifying 5,710 source bytes; it explicitly does not certify full evaluator
equivalence. `git diff --check` passes. Final focused output is retained in
`triviaqa-scorer-review-codex205-test-result.txt`.

## Remaining comparison limits

The adapter reports per-row alias-max EM (0/1), with local string coercion, Hub key
spellings, float rewards and empty-reduction behavior. It does not report F1 or
implement upstream question/document grouping, verified filtering, or full-domain
missing-prediction denominators. Hub export-to-loader/scorer linkage and full
aggregation equivalence remain unverified. A new diagnostic must pin actual
scorer/harness bytes, source/split/manifest/model identities and its metric scope.

No TriviaQA question, answer, document, parquet, archive or heldout payload was
opened; all scorer inputs were fabricated. No model/H0, endpoint, GPU, dataset
fetch, archive mutation or pilot was performed. These tests do not authorize a
production diagnostic. This report, scoped correction, tests and documentation
are delivered together in the accompanying commit; its hash is reported on delivery.
