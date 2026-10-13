# QA structured submission recovery — 2026-10-13

Implemented in `/tmp/hg-codex-118`, detached from HarnessGrad main at
`25570054b06c509dbe434f5f7fbbfc32ef5a2bfb`. The main branch and its checkout were
not edited. Existing pilot artifacts were inspected read-only. No heldout data,
released QA rows, model backend, H0 execution, or pilot rerun was used for validation.

## Diagnosis

Source run:
`/mnt/20t/xubuqiang/Study/twowiki-pilot-20261013/runs/twowiki-pilot-h0-20261013`.
The invalid traces are under `progress/round-0/traces/`, rather than
`round0_traces/`. Only the two requested invalid trace payloads and their progress
records were inspected; matching event records provided the verifier errors.

- `twowikimultihopqa/dev/1589`: the first command action was truncated and rejected
  without execution. The next reply was a complete outer action with a prediction
  **object** in `answer`. The loop accepted it but used `str(action["answer"])`,
  emitting a Python dictionary representation with single-quoted property names.
  The adapter's existing JSON parser refused it at line 1, column 2, character 1.
  Evidence: `1589.invalid.jsonl`, lines 2–5; `events.jsonl`, record 200.
- `twowikimultihopqa/dev/2501`: the first command action was also truncated and
  rejected. The next reply was valid outer JSON containing a prediction **string**
  whose inner JSON lacked the final object delimiter. The loop checked only the
  outer action and submitted the malformed string. The verifier refused it at
  line 1, column 167, character 166. Evidence: `2501.invalid.jsonl`, lines 2–5;
  `events.jsonl`, record 270.

The shared `qa submit` path independently allowed malformed JSON through because
it checked only for a nonempty string before writing `answer.txt`. Neither failure
requires a dataset-specific parser repair or a change to the official scorer.

## Patch

`base_harness/loop/agent.py` serializes object-valued final answers with
`json.dumps`, preserving every supplied prediction field. A final string starting
with `{` must parse as complete JSON before submission. Malformed inner JSON and
unsupported final-answer types enter the existing bounded `PARSE_RETRIES` path.
The original failed reply remains in the trace; recovery feedback explains how to
provide a complete object. Truncated shell actions still never execute.

`data/qa/cli/qa` checks complete JSON syntax for object-looking `submit` input from
files, arguments, and stdin. It returns exit 2 before writing on failure and leaves
any existing answer intact. Valid legacy text and valid JSON submission bytes keep
their existing transport behavior, including the CLI's trailing newline.

The runtime changes are generic: no method, adapter name, task ID, expected answer,
supporting fact, or evidence triple is embedded in the recovery logic. `submit`
checks syntax only; the existing adapter validates its own schema. `submit-json`
continues to validate the shared pair-evidence schema. No prediction fields are
added, removed, inferred, or replaced using gold, and no malformed JSON is silently
completed or converted from Python literals.

The verifier, schema validators, official scorers, gold materialization, privacy
boundaries, and reward policies are unchanged. Schema errors and directly written
malformed JSON still produce an unmeasured verdict with no reward file. Recovery
requires a fresh valid reply and remains subject to the existing retry/step limits;
this patch makes no claim about the score a future pilot would achieve.

## Validation

The new `tests/quality/test_qa_submission_recovery.py` uses fabricated predictions,
materialized public CLI files, and scripted completions. It covers object
serialization, quoted/Unicode content, omitted channels, malformed Python repr,
truncated objects/strings, missing values, trailing commas/data, bounded retry
exhaustion, invalid final-answer types, all three CLI input paths, unchanged prior
submissions, legacy strings, adapter-specific contracts, and shared-schema rejection.

The existing synthetic 2Wiki suite now also checks object answers and truncated-inner
JSON recovery through the actual materialized CLI/verifier. It verifies unchanged
legacy and structured scores, missing-channel behavior, rejection of unknown fields,
missing schema versions and wrong types, and gold redaction on both measured and
unmeasured paths. Dataset loading is blocked before importing the adapter in both
the parent tests and verifier subprocesses.

Result: **164 passed in 8.22s**, exit 0, no skipped or expected-failure tests. Existing
loop parsing, command execution, retry, submission, and scorer differential tests
are included. `git diff --check` passed. The first pytest invocation encountered a
missing parent for the workspace-local temp directory; creating it resolved the
test setup error before the passing runs.

The exact test command and result are in `qa-submission-recovery-test-result.txt`.
