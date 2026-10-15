# Installed artifact custody — w-prov

This packet narrows four `dataset-journal-gap` records without closing any of
them. It preserves public HTTP responses, local installed bytes, repository
source snapshots and reproducible source/row/split inventories. These are
point-in-time host observations, not pristine-verifier or selected-only export
receipts. No diagnostic, pilot, model, GPU or endpoint execution is authorized.

## Runtime inputs and revision binding

| Dataset | Actual runtime data read | Installed bytes | SHA-256 |
| --- | --- | ---: | --- |
| physicsquestions | ReWOO `data/bigbench/physics_question.csv` | 17,953 | `7747cf185111aaa58493b5d804ba7b496cb152a6ae89a69a66a0c443adfd34aa` |
| strategyqa | ReWOO `data/bigbench/strategy_qa.csv` | 200,453 | `c1fd0c271bf98741b68ac1ea3d167c5ccf2ed46da66645d5fc0ed6222e45f055` |
| sportsunderstanding | ReWOO `data/bigbench/sports_understanding.csv` | 137,846 | `5cfc24702b7a809409f42634f0b958f0d61c4d5aec8d732fd89889281c63d45e` |
| reasoning_gym | `pool.jsonl` plus installed `reasoning_gym` scorer library | 3,315,981 (pool) | `c0ff4eaef318cd59afcc61472ebe206362fc0211c4b589ed0d53946a569bd177` |

`installed-receipt.json` records the full paths, capture time, sizes and hashes;
`installed/` preserves the bytes. `source-receipt.json` binds the adapters,
generator and scaffold snapshots to base commit
`0b470b6` (full ID in that receipt). `rewoo/` and `reasoning_gym/` retain public
acquisition packets and their independent verification scripts.

The three CSVs bind byte-for-byte to archive members at ReWOO commit
`9cd0283043ff4be0c9d614fda2789d143ca6ffd1`, then to that commit's Git tree and
contents responses. The inherited full archive in
`../hg_e1_review/rewoo-archive.body` has SHA-256
`7fe653d18faad40bf10ddcc7d85415782af975d80792bb26401393203b9ce136`.
It is reused rather than duplicated. This identifies the exact released export
bytes; it does not identify the historical conversion program or conversion
time that produced those CSVs.

The adapters use standard-library CSV reading and inline scorer functions.
They do **not** import an installed ReWOO evaluator or BIG-bench package, and
their declared `pyarrow` dependency is unused in this data path. The acquired
ReWOO evaluator and BIG-bench task/metric sources are comparison evidence,
not installed runtime dependencies. BIG-bench comparison data are bound to
`092b196c1f8f14a54bbc62f24759d43bde46dd3b`.

There is no Hugging Face Hub input/revision declared by these three adapters.
The already-authenticated E1 Hub revision/tree responses are for **FEVER**;
they cannot bind the ReWOO exports or the locally generated Reasoning Gym pool.
No unrelated Hub mirror is substituted. These artifacts use their actual
GitHub/PyPI lineage. Public TLS responses and matching Git/content hashes do not
create a missing publisher attestation or historical converter receipt.

## physicsquestions installed custody

All 53 installed CSV rows match the pinned ReWOO member. E1 already established
ordered question/accepted-answer-list equality with all 53 nonblank examples of
the pinned BIG-bench task (54 examples including its blank first entry).
The installed file, row-to-task mapping and declared train/eval split now have
preserved bytes and independently reproducible hashes.

Open: a run-specific selected manifest and selected-only runtime binding;
matched BIG-bench response-processing/metric protocol (local asymmetric
whitespace/reference-period normalization differs); scorer dependency/offline
closure, pristine verifier execution and all remaining shared gates. No
historical converter revision or production measurement is inferred.

## strategyqa installed custody

All 2,290 installed rows match the pinned ReWOO member. Exact evaluator source
at that same revision is acquired and byte-bound to the archive/tree. The
adapter computes local normalized whole-answer EM; F1 and judge accuracy are
excluded. The reference evaluator is not imported at runtime.

Open: original-benchmark metric/split comparability beyond this vendored table,
run-specific selection/export binding, deterministic offline dependencies and
pristine verifier/runtime evidence. Acquiring evaluator identity is not an
execution-equivalence receipt.

## sportsunderstanding installed custody

All 1,000 installed rows match the pinned ReWOO member and the acquired
BIG-bench sports task provides an independently pinned comparison source.
BIG-bench `measure_multiple_choice_grade` selects the candidate with maximal
`log_prob` and reads that candidate's `target_scores`; this differs from the
adapter's generated-text word-label matching and dual-label rejection.
The preserved upstream source does not establish metric equivalence.

Open: matched metric/protocol comparability, run-specific selection/export
binding, offline scorer closure and pristine verifier/runtime evidence.

## reasoning_gym installed custody

The installed pool matches its declared digest and its 1,780 rows match the
declared family-major order: 89 families, each with indices 0–19. Questions
match their embedded entry question after stripping and references are
nonempty. This is structural eligibility, not proof of the reference=1,
empty=0 behavioral family rule. The adapter still does not enforce the pool
digest or installed package version on its runtime read/scoring path.

See `reasoning_gym/README.md` for preserved PyPI distribution bytes, exact
GitHub revision binding, installed-member comparison and the separately scoped
generation check. PyPI's wheel is 6,985,897 bytes, SHA-256
`7f17a3eddb13c015d7d4a755ed576a061df889faf9468bcc2cca334ebe9e0435`;
the sdist is 6,789,585 bytes, SHA-256
`932247c760dd23e09fb14d013d29ec4c8804e62846bd50473f6915dc854adad2`.
All 200 package/data members match both distributions and the Git tree at
`21e6d2a9a581b3e11aafe711abfd37402f8482d5` (`v0.1.25`). Of 205 installed
wheel members, 204 match; only pip's rewritten RECORD differs. No independent seed-specific pool release
or run-specific selected manifest was authenticated from the acquired public
sources. A local reproduction cannot authenticate
an absent upstream pool release or independently prove the historical run's
selection.

Open: behavioral family eligibility, deterministic transitive dependency
closure without scoring extras, run-specific selection/export binding and
actual pristine scorer/runtime evidence. No general offline-family or scored
coverage claim follows from the package/pool hashes.

The completed CPU-only regeneration at the declared seed did **not** reproduce
the pool: observed generated SHA-256
`d00b2b1cb8134ee37c7b76fce5547cb3e2c44a247dfa07beaa984385532cffd1`,
3,315,958 bytes, versus the pinned installed 3,315,981 bytes. The 84 mismatching rows
belong to `isomorphic_strings`, `knight_swap`, `polynomial_multiplication`,
`ransom_note`, `time_intervals` and `word_ladder`. No family, seed or generated
value was changed to seek a match. Earlier constrained failures, exact scripts,
stdout/stderr and the completed attempt's dependency/cleanup receipt are all
preserved. The generated digest is an observed command result, not a newly
published upstream pool pin. Missing generation environment/order pins remain
to be identified; package identity plus seed alone is insufficient evidence of
byte reproducibility in this observation.
Static source inspection identifies set/frozenset iteration, SymPy term ordering
and `date.today()` as additional inputs to affected generators. Their presence
does not prove the exact cause of every differing row or recover the original
process's date/hash randomization/dependency state. The complete new pool was
held in memory; its digest/count and mismatch coordinates are preserved as
observed process output, without installing a replacement pool.

## Eligibility, split and selection limits

`manifests/<dataset>.json` preserves every source-derived task ID, parsed-row
hash, declared side and ordered structural eligible inventory. Row hashes use
UTF-8 canonical JSON as specified in each manifest; they are not raw CSV-line
hashes. `declared_split.split_sha256` uses the exact JSON serialization in
`data/scaffolds/registry.py::split_hash`. The source hash accompanies it because
an ID-only split hash does not bind row content.

| Dataset | Loaded/structurally eligible | Declared hash train | Declared hash eval |
| --- | ---: | ---: | ---: |
| physicsquestions | 53 | 37 | 16 |
| strategyqa | 2,290 | 1,520 | 770 |
| sportsunderstanding | 1,000 | 663 | 337 |
| reasoning_gym | 1,780 | 1,216 | 564 |

All four have `official_eval=None`: the platform imposes a hash division, while
official mode considers the whole adapter pool evaluation material. That does
not authenticate an original benchmark's heldout split or completeness.
The word “eligible” here describes only successful static loader/gold shape
checks. It does not mean all admission gates passed or Reasoning Gym's
behavioral rule was executed.

No run ID, side-specific selection request or selected manifest was supplied.
`selected_manifest`, run ID and trial coverage fields remain **null**; no new
selection or diagnostic receipt is invented. The inventories let a future
review bind an independently supplied selected manifest to exact rows. Such a
review must still record its side, source/split/manifest hashes, endpoint,
limits, cleanup and snapshot evidence before any separately authorized run.

## Reproduction

Run from the repository root with `PYTHONDONTWRITEBYTECODE=1`:

```sh
python3 tests/fixtures/hg_wprov/verify.py
python3 tests/fixtures/hg_wprov/build_custody.py --check
python3 tests/fixtures/hg_wprov/rewoo/verify.py
python3 tests/fixtures/hg_wprov/reasoning_gym/verify.py
python3 tools/check_dataset_blockers.py
```

These verification commands use preserved evidence and never fetch responses,
import adapters/scorers, generate tasks or run a benchmark. Acquisition and the
separate bounded generation check are documented in their subpackets. The
root `SHA256SUMS` covers every packet file except itself and Python caches;
inherited E1 artifacts are checked by the ReWOO verifier. Exact validation
commands/output are in `reports/w-prov-validation.txt`.
