# GSM8K and MuSiQue scorer/protocol comparability closure

Source review: 2026-10-15, `/tmp/hg-b4`, base commit
`906607202fe6d7674695a410a72eb7379b869e75`. File/line references below refer to
that snapshot unless explicitly identified as this report. This closes the two
metric-identity documentation actions. It establishes no new benchmark result or
comparable measured receipt pair. Only repository source, fixtures and journal
text were inspected; external receipts and released dataset payloads were not
opened. Historical receipts, fixture bytes and journal entries remain unchanged.

## GSM8K: scorer-protocol-comparability

### Blocker text read before review (verbatim)

**observed**

> Decimal-aware scorer provenance was repaired synthetically; old integer-scorer history and trial-mean/test@N remain distinct.

**next_action**

> Document matching scorer/protocol identities for future comparisons and preserve old receipts unchanged.

### Established facts

- **Current scorer:** `data/datasets/gsm8k.py:85` defines
  `(-?[$]?(?:\d[\d,]*\.\d+|\d[\d,]*))`.
  `official_flexible` at line 116 takes the last match anywhere in the answer,
  then removes commas and dollar signs. Gold is the text after the final `####`
  in the released answer (`_gold`, line 104). `numeric_equal`, line 137, uses
  `abs(float(got) - float(want)) < 1e-6`; unparsable values fail. `score`, line 149,
  returns binary reward/correct from that comparison and records
  `official.filter="decimal-aware-extract"`. Reasoning is not graded separately.
  `official_strict` at line 129 extracts the last strict marker only for evidence;
  it does not select the rewarded answer. Legacy `official*` names do not certify
  official upstream scoring.
- **Transport and failures:** the shared verifier uses a valid `prediction.json`
  answer when present, otherwise an unwrapped/stripped `answer.txt`
  (`data/scaffolds/qa/verify/check.py:185`, `:233`). Thus comparisons must match the
  verifier/parser as well as the adapter. Missing/no-number answers are measured
  zeros with available trusted gold/scorer; missing gold, invalid structured
  artifacts and scorer failures are unmeasured (`check.py:157`, `:198`, `:243`).
- **Historical extraction differs:** the immutable repository reference
  `tests/fixtures/gsm8k_original/integer_extractor.json:2` is
  `original-integer-only-extract`, regex `(-?[$]?\d[\d,]*)`, last match, comma/dollar
  stripping, from repository commit
  `f7ab62143108e120914b5ead34ed339d0c785ee9`. Its fixture SHA-256 is
  `45c73aeb817878b5ba65709f45766f21eb7899182df4eba9a8101e9169d8276b`
  (`tests/fixtures/gsm8k_original/README.md:3`). It extracts `0` from `18.0`, `5`
  from `3.5`, and `25` from `-3.25`; the current extractor preserves the decimals
  (`tests/quality/test_gsm8k_official_scorer.py:69`). This pins an inherited
  repository extractor, not the entire scorer/protocol of any uninspected run.
  Its old upstream attribution remains unverified. The provenance document's
  separately pinned lm-evaluation-harness v0.4.8 comparison uses a different regex
  and normalized string exact match (`docs/gsm8k-scorer-provenance.md:29`). Neither
  the integer fixture nor the decimal adapter may be relabeled as that scorer.
- **Data/split identity:** `data/datasets/gsm8k.py:74`, `:198`, `:238` pin
  `openai/gsm8k@740312add88f781978c0658806c59bc2815b9866`, config `main`, with
  declared per-file SHA-256 values at lines 211–214. The published division is
  7,473 train/study and 1,319 test/eval rows. `declared` and `official` resolve to
  that division; `default` hashes the combined 8,792-row pool instead
  (`gsm8k.py:270`). Matching the published split alone does not match the scorer
  or inference protocol. A selected test subset is not the full-test result.
- **Run protocol:** the runner averages trial rewards per task
  (`eval/run/runner.py:1061`), then recorded run rewards use
  `mean(scores, dataset=sampling.get("dataset"))` (`harnessgrad/records.py:199`).
  GSM8K declares `arithmetic_mean / measured_tasks`
  (`data/aggregation_policies.json:14`); `eval/run/metrics.py:29` reads that
  denominator through `data/scaffolds/aggregation.py:32`. This is a task macro
  mean of trial means, with equal task weight. It performs no candidate ranking,
  verifier selection or oracle any-success selection. The distinction from the
  paper's verifier-selected test@N is documented in
  `docs/gsm8k-scorer-provenance.md:55`; test@N is not implemented.

### Comparison rule

Direct comparisons of future platform results require the same
**decimal-aware-extract + exclusive numeric tolerance + artifact parser + task
macro mean of trial means** identity, pinned scorer/verifier/aggregation code and
policy hashes, and the common receipt conditions below. For a published-split
claim, also match config `main`, revision/file bytes and the full official test
manifest. For an internal subset experiment, match the selected manifest and
label the subset explicitly. A harness or model may differ when that is the
declared experimental variable; its identity must still be recorded and other
conditions controlled.

Old integer-extractor and new decimal-extractor curves are separate metric
series, even when integer examples agree. A future independently approved,
separately identified matched-scorer measurement could establish a comparable
series; it cannot alter old receipts. `--trials N` is trial-mean, never test@N or
pass@N. A test@N comparison would additionally need the same candidate generation,
verifier model, ranking/selection and sampling budget, and its own implementation
and metric identity.

### Residual limits

`docs/adapter-integration-journal.md:264` records old H0 history and pending
new-scorer validation; lines 274–281 report source/synthetic provenance repair,
not a new measured GSM8K result. This review authenticates no historical run's
full protocol and establishes no matched receipt pair. Upstream string EM,
historical integer extraction, test@N/pass@N, different splits/subsets, and partial
coverage cannot be presented as this same comparison. Production scorer/runtime
and lifecycle evidence remain behind the unchanged shared gates.

## MuSiQue: joint-policy-comparability

### Blocker text read before review (verbatim)

**observed**

> The journal reports 150/150 measured pilot trials, but platform joint reward is not an official single leaderboard column.

**next_action**

> Review metric/split/source/lifecycle metadata before comparison; keep the journal claim separate from newly verified evidence.

### Established facts

- **Current components and reward:** `data/datasets/musique.py:44` normalizes
  answers by lowercasing, removing punctuation/articles and collapsing whitespace.
  `_score`, line 88, independently maximizes token F1 and EM over the canonical
  answer and row aliases. Support scoring uses sets of paragraph indices, ignores
  descriptive titles and deduplicates indices; extra indices are false positives
  (`compute_support`, line 75; `_score`, line 104). Both-empty support has F1=1.
  Default `answer_support` reward is the unrounded per-item
  `answer_f1 * support_f1`; `correct` is `answer_em * support_em == 1`.
  These platform joint quantities are explicitly labeled in `official` evidence
  (`musique.py:106`). Official MuSiQue-Ans columns are **Answer F1, Answer EM,
  Support F1**, separately, not a single joint leaderboard column.
- **Source identity and evidence boundary:** the adapter pins the component
  transcription to StonyBrookNLP/musique commit
  `922ac98f19a201998dbdae6d7f2887a5258dbdeb`, archive SHA-256
  `c1cc3d121e3f623f9925857559030d48c136142ee2c9cdb52214bb6134c02272`
  (`musique.py:40`, `:215`). The driver calls adapter scoring, not upstream
  `evaluate_v1.0.py` (`data/scaffolds/qa/verify/check.py:233`). Pinned local metric
  classes and their hashes support synthetic component differential checks
  (`tests/quality/test_musique_official_scorer.py:22`, `:93`). The earlier source
  acquisition/alignment findings in `reports/s9-aggregation-denominator-report.md:62`
  remain prior report evidence; no canonical archive was reacquired here.
- **Explicit aggregation now:** `data/aggregation_policies.json:18` declares two
  scopes: `run_reward = arithmetic_mean / measured_tasks` and
  `corpus_metrics = ordered_macro_mean / provided_results`. The training driver
  and eval-side entrypoint pass the dataset name (`driver.py:1154`,
  `harnessgrad/loops/eval_side.py:154`); recorded scores and train scores call
  `mean(..., dataset=...)` (`harnessgrad/records.py:199`, `:312`), which consults
  the declaration (`eval/run/metrics.py:29`). The runner first averages trials per
  task (`eval/run/runner.py:1069`). The corpus helper `aggregate`,
  `musique.py:130`, instead divides ordered sums by provided results, rounds only
  official Answer F1/EM and Support F1 columns to three decimals, leaves joint
  reward unrounded, and rejects mixed modes. **Mean of per-item products is not
  product of corpus means.** The helper is not the driver's run-score path.
- **Completeness is separate from a denominator declaration:** `aggregate` has no
  gold inventory/ID alignment gate (`musique.py:135`). A supplied subset therefore
  yields a subset mean. The pinned upstream evaluator requires equal prediction
  and gold row counts and aligned IDs; this is documented with source lines in
  `reports/s9-aggregation-denominator-report.md:65`, `:93`. For official-column
  compatibility, supply the complete aligned ID sequence in gold order and match
  the upstream rounding; the helper alone cannot certify completeness. Repeated
  trials also require an explicit reduction/order/rounding protocol for each
  component. A scalar-only curve cannot reconstruct the three official columns;
  retain each trial's component evidence, not just the last trial's verdict
  (`eval/run/runner.py:1051`, `:1104`).
- **Legacy policy differs:** trusted `legacy_answer_only` produces Answer F1
  reward, Answer EM correctness, and `support_f1=None` (unmeasured), with no joint
  claim (`musique.py:96`). Mode is trusted verifier configuration
  (`musique.py:265`, `:271`), not prediction-controlled. Plain text under default
  scoring supplies empty evidence; it does not select legacy mode (`:125`).
  Structured artifact validation and precedence are defined in
  `docs/musique-output-contract.md:20` and `check.py:185`; malformed artifacts are
  unmeasured, not an incorrect-answer zero or fallback to valid text.
- **Data/split/source limits:** the pool is the 2,417 answerable MuSiQue-Ans v1.0
  dev rows from third-party `dgslibisey/MuSiQue`, revision
  `c8f4f8c9465fb69d31a8eae894c3fd509c4ca321`, data SHA-256
  `15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b`
  (`musique.py:36`, `:166`, `:208`). Canonical HF identity remains independently
  unestablished after mirror acquisition (`:13`, `:214`). Declared division is
  the platform hash train/eval partition; `--split official --side eval` selects
  the full **dev pool**, not the official hidden test set (`:242`). MuSiQue-Full
  sufficiency evaluation is outside this contract.

### Historical claim versus current evidence

`docs/adapter-integration-journal.md:346` reports that the prior reward was
Answer F1 only, followed by structured joint-policy repair. Line 355 claims
`musique-pilot-h0-20261013`, 50 selected **train** tasks × 3 trials, `jobs=1`,
150/150 measured trials, 0 invalid, score `0.12751114`, one task passed and wall
time `1884.4s`. Its external curve path is a citation only. No receipt, manifest,
model/harness hash, endpoint, budget or cleanup record was inspected here; no
missing field is inferred from today's code. The entry's own status and remaining
gates at lines 348 and 356 are preserved, including their tension with the pilot
claim. The score remains a journal-reported platform pilot value, not newly
verified evidence, an official column, or a current-policy rerun.

The later aggregation change declares previously implicit arithmetic without
changing the synthetic before/after numbers (`docs/adapter-integration-journal.md:67`;
`tests/fixtures/aggregation_s9_before.json`; `reports/s9-aggregation-denominator-report.md:131`).
For example, the existing full synthetic helper reward remains
`0.48148148148148145`, while the one-result subset remains `1.0`. This verifies
numeric preservation on those authored cases, not historical pilot equivalence
or permission to add a policy identity retroactively to its receipt.

### Comparison rule

Compare platform joint rewards only with **answer_support, per-item Answer F1 ×
Support F1, task macro mean of trial means, measured-task denominator** results
meeting the common receipt conditions below. Match answer/alias normalization,
paragraph-index evidence semantics, mode, transport, data bytes, split, selected
IDs, trial count, rounding/scale and aggregation declaration. Identify any intended
harness/model change separately. A full-dev official-column comparison requires
complete aligned gold IDs and separately aggregated Answer F1, Answer EM and
Support F1 from retained unrounded components, with the pinned upstream macro
order/rounding; a platform joint scalar is insufficient.

### Residual limits

Legacy Answer F1, platform joint reward, official component columns, product of
corpus means, provided-result subset means and measured-task run means are
distinct quantities. Do not mix modes, relabel the 50-train-task/three-trial pilot
as full dev or hidden test, or compare it as the same protocol as a new staged
one-task/one-trial diagnostic. Canonical data-source custody, production official
scorer execution, coverage and lifecycle/cleanup are still unverified for any
proposed receipt pair; the shared gates remain active. MuSiQue-Full/hidden-test
claims and public-versus-local rankings are unsupported by this review.

## Common receipt conditions and control identity

A direct comparison needs explicit metric identity; source/data revision and byte
hashes; split and selected-manifest hashes; scorer, parser, aggregation policy and
harness hashes; model/provider and endpoint binding; generation settings and
resource/budget limits; trial count and reduction; eligible/selected/measured task
and trial coverage; invalid/unmeasured counts and causes; and trusted verifier,
snapshot and cleanup evidence (`AGENTS.md:75`). Record the intended experimental
variable and comparability exceptions. Missing identity or coverage evidence
prevents a direct ranking; do not manufacture matching metadata or convert a
failure into zero. The current runner excludes a task if a trial becomes
unmeasured, even after earlier measured trials (`eval/run/runner.py:980`, `:996`,
`:1047`); do not assume a partial task was averaged into the reported score.

The shared QA control resolves optional adapter `NOOP_EXPECTED` (constant or
record callable), default `0.0`, in **both** local and platform paths; oracle
expectation is `1.0` (`data/scaffolds/qa/base.py:141`;
`data/scaffolds/qa/control.py:108`, `:199`, `:261`). Neither GSM8K nor MuSiQue
declares an override in the reviewed adapter source, so both use the default
no-op expectation. This expectation is control configuration, not a new metric,
a fabricated measured control, or proof that a refused control scored zero. The
platform control rejects a missing score as unmeasured (`control.py:263`). Earlier
oracle/no-op journal claims stay historical; the adapter-declared mechanism does
not authenticate them or authorize H0.

The original metric-comparability blocker IDs are retired in the registry.
Separate `matched-scorer-protocol-receipts` (GSM8K) and
`matched-joint-policy-receipts` (MuSiQue) measurement-coverage gaps retain the
missing independent receipt review. The registry schema/checker and all shared
blockers, other datasets and historical records are unchanged.

Future runs still require all dataset gates, a fresh one-task/one-trial diagnostic,
and separate review before expansion (`AGENTS.md:59`). The old 50×3 pilot is not
new-run guidance. Never resume or overwrite any old run ID. No run is launched by
this closure.

## Focused validation

- `python3 tools/check_dataset_blockers.py` passed: `valid=true`, 28 datasets,
  8 shared blockers, 11 historical records, `production_authorized=false`.
- The following focused invocation passed **269 tests in 6.40s**:

  ```sh
  python3 -m pytest -q \
    tests/quality/test_dataset_blockers.py \
    tests/quality/test_gsm8k_official_scorer.py \
    tests/quality/test_gsm8k_dataset.py \
    tests/quality/test_musique_official_scorer.py \
    tests/quality/test_aggregation_policies.py \
    tests/quality/test_qa_control_expectations.py::test_noop_expected_declaration \
    --basetemp=/tmp/harnessgrad-pytest-b4-metric-comparability
  ```

  These check source-only registry invariants, immutable integer-extractor bytes,
  decimal/tolerance and synthetic verifier behavior, MuSiQue component/policy
  differentials, live declared denominators and synthetic numeric preservation,
  and adapter-declared no-op expectations in both control paths. The no-op test
  patches execution; it is not a released-data control receipt.
- `git diff --check` passed. Review confirmed only the two owned registry blocker
  entries changed; shared blockers, other dataset rows and all historical records
  remain identical to the base.

No whole test suite, model endpoint, released-data control, diagnostic or pilot
was run. No scorer/runtime implementation, historical receipt or journal text was
changed.
