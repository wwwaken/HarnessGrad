# Task 196 — original TriviaQA evaluator acquisition

**Original source acquired; adapter equivalence remains blocked.** Work stayed
in `/tmp/hg-codex-196`, detached base
`16e3151f644cc1a0052e2bf09fa887d381066006`.

## Deliverables

- `tests/fixtures/triviaqa_upstream/`: original evaluator, two imported helpers,
  Apache-2.0 license, repository requirements, provenance receipt, and offline
  commit/tree/GitHub metadata evidence.
- `tests/quality/test_triviaqa_source_provenance_codex196.py`: source identity,
  license/dependency checks, and unchanged full evaluator/CLI on synthetic inputs.
- Existing provenance test: corrected repository and acquisition-method support;
  missing source now fails rather than skips. No scorer implementation changed.

Original repository: <https://github.com/mandarjoshi90/triviaqa>.
The inherited `mandarjoshi/TriviaQA` URL returned HTTP 404.

Immutable commit: `ca43b5820b107f3970cf4b7d67f7db7a98117b79`.
Source: <https://github.com/mandarjoshi90/triviaqa/blob/ca43b5820b107f3970cf4b7d67f7db7a98117b79/evaluation/triviaqa_evaluation.py>.

Evaluator SHA-256:
`51785a3bc2e02a8f1ebf9db3aa18834c6a5daa5089ee5d435c99e0babf4be682`.
The receipt records raw-byte SHA-256 and Git blob identities for every acquired
file. Exact reconstructed commit/tree object hashes connect those files to the
commit pin; no independent PGP verification or human review is claimed.

## Findings

The original evaluator computes alias-max EM and token F1, scales their averages
to 0–100, counts missing predictions in the denominator, and ignores extra
predictions except in `pred_len`. Wikipedia groups by question ID. Web groups by
`QuestionId--Filename`; dictionary duplicate keys collapse. Verified evaluation
filters questions and, for Web, documents. The CLI has no no-context, validation,
or Hub config branch; it evaluates the supplied original-format file.

The full evaluator import closure needs standard-library modules and the two
acquired helpers, with no third-party dependencies. Repository-wide TensorFlow,
NLTK, tqdm, and Jinja2 requirements were recorded without installing them.
Original package initializer blobs are known empty from tree metadata, but their
fetch hit the API rate limit; Python 3 namespace packages execute the acquired
files unchanged. The original license and pinned commit's license-only README
patch explicitly establish Apache-2.0 coverage.

**Confirmed mismatch:** upstream normalizes `A-Team` to `team`; the local adapter
normalizes it to `ateam`. Upstream replaces punctuation/underscores with spaces
and handles extra quote characters. The differential gate therefore fails,
without changing production code or weakening the assertion.

The fixture README explains grouping/no-document/validation boundaries and gives
an exact code/metadata acquisition request for the loader/conversion provenance
of Hub revision `0f7faf33a3908546c6fd5b73a660e0f8ff173c2f`.
The Hub loader attempt failed on network access; the alternate historical GitHub
loader lookup hit the anonymous API rate limit. Its source pin and export mapping
remain unverified. These failures do not invalidate acquired original source.

## Validation and scope

With third-party pytest plugin autoload disabled, bytecode writes disabled, and
worktree-local basetemp paths:

- Source-only suite: exit 0; **3 passed**.
- Source plus existing differential/contract suite: exit 1; **31 passed,
  1 failed, 0 skipped**. The sole failure is the documented `A-Team` mismatch.
- `tools/check_triviaqa_provenance.py`: exit 0; 5,710 scorer bytes verified.
- Git whitespace/diff check passed for authored tests, receipt, README and report.
  The full staged check exits 2 only for two space-only signature continuation
  lines in `evidence/commit.git`. These are required original Git object bytes;
  removing them would break the immutable commit hash. They were preserved.

Only public source, license/requirements, and GitHub/Git metadata were fetched.
No questions, answers, documents, sample rows, dataset archives, parquet, heldout,
external dataset paths, GPU endpoints, model, or H0 were accessed. Production
adapter/main/model/H0 files and old reports/receipts remain unchanged. Synthetic
inputs are fabricated and produce no benchmark score or production admission.
Temporary acquisition/test files were removed; only the handoff artifacts remain.
