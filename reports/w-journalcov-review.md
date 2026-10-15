# Six journal-coverage blockers: clause review — w-journalcov

All six dataset-journal-gap blockers remain measurement; both shared blockers remain open.
This review establishes current bytes, structural inventories and scorer/input source linkage.
It creates no selection, chosen run split/side, selected-only export or diagnostic authorization.

## Scope and starting obligations

Read first: docs/dataset-blockers.json, reports/w-clo-actor-closures.md,
reports/w-offscorer2-coverage.md and the w-prov packet/validation log. Discovery found
no reports/w-prov-*.md files in this checkout; tests/fixtures/hg_wprov/README.md is
the preserved substantive review. Exact starting records are retained in
`tests/fixtures/hg_wjournalcov/registry-before.json`; the six next_actions are unchanged.

The prompt's common wording is not verbatim for all six current blockers. Physics
Questions explicitly says no selection/run ID is supplied; Sports Understanding and
StrategyQA also require independently supplied selection/export; Reasoning Gym adds
unreproduced generation and behavioral eligibility. FEVER asks for actual export,
converter/original-group and selected custody, rather than an installed CSV.
SpreadsheetBench asks for authenticated gradability/coverage and workbook/scorer/runtime
custody under its range-zero policy, rather than the quoted generic manifest sentence.
Their own obligations, not a substituted common template, control this review.

## Recomputed byte and structural inventory

Every value below comes from `audit.py` command 5's preserved stdout and
`observations.json`; every source/data hash has independent sha256sum raw output
in the packet. Inventory JSON files bind ordered task IDs to canonical parsed-row
hashes; they contain no expected-answer exports. Installed file paths and sizes,
per-workbook hashes and archive equality are in those files. Source hashes below
bind today's code, rather than reusing historical source pins.

| Dataset | Source pool split | Loaded rows | Hash train / eval | Installed data SHA-256 |
| --- | --- | ---: | ---: | --- |
| fever | validation | 15,935 | 10,559 / 5,376 | `5da0ccc0ccf77f974611de13f8aac6f78c6bba6293912835099eb6029baa85d9` |
| physicsquestions | test | 53 | 37 / 16 | `7747cf185111aaa58493b5d804ba7b496cb152a6ae89a69a66a0c443adfd34aa` |
| reasoning_gym | eval | 1,780 | 1,216 / 564 | `c0ff4eaef318cd59afcc61472ebe206362fc0211c4b589ed0d53946a569bd177` |
| sportsunderstanding | test | 1,000 | 663 / 337 | `5cfc24702b7a809409f42634f0b958f0d61c4d5aec8d732fd89889281c63d45e` |
| spreadsheetbench | verified_400 | 400 | 291 / 109 | `bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7` |
| strategyqa | test | 2,290 | 1,520 / 770 | `c1fd0c271bf98741b68ac1ea3d167c5ccf2ed46da66645d5fc0ed6222e45f055` |

The table columns are dataset, source pool split, loaded rows, imposed train/eval
counts, and SHA-256 of actual installed data (SpreadsheetBench: dataset.json).
These are structural loader inventories, not fully admitted eligible populations.

All six use the deterministic ID hash division at their default source configuration.
The QA pool split name is part of each task ID; it does not choose train/eval.
The native SpreadsheetBench IDs are the metadata IDs without a dataset prefix.
Official-mode eval covers each adapter's whole inventory (`official_eval=None`);
that does not authenticate original heldout completeness or metric comparability.
SpreadsheetBench also implements HG_SPREADSHEETBENCH_SPLIT=none for all-eval.
No mode, override or side is chosen for a run here. Actual inspected environment
values are preserved in observations.json; the SpreadsheetBench inventory explicitly
uses the default installed path and default hash rule, rather than treating the
current environment as run authorization.

| Dataset | Recomputed declared ID-split SHA-256 |
| --- | --- |
| fever | `5be7ed7984c321960d5098cbd111d1fdaf90eaec6c37efb61e2f8c679f5183f1` |
| physicsquestions | `820869d7fcf7eb40651fdf3e747609e3c57a72e1bb9d64a12deb948400528212` |
| reasoning_gym | `d3d860be5c2b3a26a25a0a9e0ee96c2b3dfd258685a1d682128bf13d2d81d195` |
| sportsunderstanding | `91207272facb1c63a51966f3e1815f3e0174d9857a2255f198dd85b68dfe232c` |
| spreadsheetbench | `7b315d59759ce97d9ee33a76c59b744d5d04003d61af744c75a1a521df382e7d` |
| strategyqa | `c4baab58c4101d28b981a771a4bb1ef198f020e64764905eda23a7379f396969` |

The split serialization is registry.split_hash's sorted ID lists serialized with
json.dumps(sort_keys=True); parsed-row hashes use canonical UTF-8 JSON with
ensure_ascii=False, sort_keys=True, separators=(',',':'), allow_nan=False. An ID
split digest does not bind content without the accompanying source/row digests.

## Current scorer and expected-data source linkage

| Dataset | Data → expected projection → scorer |
| --- | --- |
| fever | _rows `data/datasets/fever.py:46` → gold projection `data/datasets/fever.py:58` → scorer `data/datasets/fever.py:27` |
| physicsquestions | data read `data/datasets/physicsquestions.py:120` → gold projection `data/datasets/physicsquestions.py:135` → scorer `data/datasets/physicsquestions.py:103` |
| reasoning_gym | data read `data/datasets/reasoning_gym.py:80` → gold projection `data/datasets/reasoning_gym.py:94` → scorer `data/datasets/reasoning_gym.py:106` |
| sportsunderstanding | data read `data/datasets/sportsunderstanding.py:101` → gold projection `data/datasets/sportsunderstanding.py:112` → scorer `data/datasets/sportsunderstanding.py:80` |
| spreadsheetbench | metadata/pair read `data/datasets/spreadsheetbench.py:107` → deterministic workbook choice `data/datasets/spreadsheetbench.py:151` → expected-input binding `data/datasets/spreadsheetbench.py:224` |
| strategyqa | data read `data/datasets/strategyqa.py:107` → gold projection `data/datasets/strategyqa.py:118` → scorer `data/datasets/strategyqa.py:89` |

The five QA routes then share `data/scaffolds/qa/base.py:215`
(row position → task ID), `data/scaffolds/qa/base.py:290`
(split semantics), and `data/scaffolds/qa/base.py:339`
(exact serialized gold digest and task-scoped verifier specification). The checker
reads one byte buffer, hashes it and parses those same bytes at
`data/scaffolds/qa/verify/check.py:171`;
its structured/legacy dispatch is at
`data/scaffolds/qa/verify/check.py:254`.
SpreadsheetBench binds task.json plus golden.xlsx in its verifier specification;
`data/datasets/spreadsheetbench/verify/check.py:309`
passes bound private inputs into `data/datasets/spreadsheetbench/verify/check.py:315`
and `data/datasets/spreadsheetbench/verify/check.py:383`
consumes those inputs. This is current source linkage and an existing consistency
mechanism under trusted specs; it does not authenticate a missing independent run
selection or establish a live selected-only filesystem boundary.

| Current source file | Fresh whole-file SHA-256 |
| --- | --- |
| `data/datasets/fever.py` | `7c0cd67c7d82d9c71f2bde4c52e564f279930f6fc7f62aae4cdda5b7c27afcd0` |
| `data/datasets/physicsquestions.py` | `452d134d58a1900355112edb8dcc9837c39830c953d2d064db3b409d54c001cf` |
| `data/datasets/reasoning_gym.py` | `fcf4be2daa187dc4d74395530bbbdaa308e317bc0173b346f7de0bb889ac7f33` |
| `data/datasets/reasoning_gym/prepare.py` | `0b70953e525e8c4c3f2320f6617b8da7b604fa7f1adc1e3604464cc42db5bde3` |
| `data/datasets/sportsunderstanding.py` | `e44f856dda4c2761737ffe9d0b0b3fca59e149c1ec12e7451be33872df5d86ad` |
| `data/datasets/spreadsheetbench.py` | `1ed36abf71ff84f489d9be1cd9b231180d18e45c60ea514c9b4baf34add2ab9e` |
| `data/datasets/spreadsheetbench/verify/check.py` | `e7131a2649a89d818a73b6b83e1b66892e41b93c53a7fee8330749146ad3ee46` |
| `data/datasets/strategyqa.py` | `eaad45dfb944241fad84eb575882560ffcf7243de40c9d34fd0766a40c16a50a` |
| `data/scaffolds/qa/base.py` | `3c2242e4ed82d76eb7732a6c077122f3d74fb4387860caa3b53a9d8a049a8d8a` |
| `data/scaffolds/qa/evidence_scorers.py` | `a962f23e0c0f704b31294902ddaae3facee0e7496dfc43041bf973a912043729` |
| `data/scaffolds/qa/read.py` | `b28b1150ddf307a1cf037e3e0cb280117d13157687551329b27c24e0526bb383` |
| `data/scaffolds/qa/verify/check.py` | `7625d8070cac767c5a878623f98469cb7f4bb0b528a86980d7334b5fdbbbbe7e` |
| `data/scaffolds/registry.py` | `973e6adcfaf3b965d697f02a00d7ce80b54c0b2e8df7f49ac65007ae802339b1` |
| `data/scaffolds/scorer_input.py` | `3d567c5a7dcf19c011425979cf845c6352c468960ae406ec639a8d6e27c0dfee` |

Numbered source preimages are preserved in source-lines.txt; every cited file/line
can be checked against its corresponding fresh file digest. Production source is unchanged.

## fever

**Satisfied clauses:** the exact scorer source revision remains acquired (E1 integrity
passes; no named release is invented). Current installed validation bytes have
SHA-256 `5da0ccc0ccf77f974611de13f8aac6f78c6bba6293912835099eb6029baa85d9` and recomputed Git blob SHA-1
`ae61c5b6cb11eafcc7d6c33069c68dd5c848f91f`. The latter and byte size match
valid.jsonl in the previously authenticated Hub revision/tree
`a6b8d891d393e97a4efac791afffb2d7de5e57c6`.
This newly binds actual installed export bytes to that preserved public metadata,
superseding the earlier metadata-only/installed-linkage gap at this exact scope.
Every current row/task digest and default division is inventoried; raw rows have
IDs and list-valued evidence, which alone proves no original ID/group correspondence.

**Unsatisfied clauses:** the producing conversion revision and original FEVER
ID/complete evidence-group correspondence are still absent. The local flat branch
at `data/scaffolds/qa/evidence_scorers.py:161`
turns sentence triples into sufficient singleton groups. Thus the implemented
metric is binary label-plus-evidence strict scoring, first five pairs, NEI-exempt,
under the local gold projection; equivalence to original complete-group FEVER
strict_score is unproved. A byte-identical Hub export does not resolve that semantic
gap. Independently supplied selected manifest, fresh run ID, split mode/side,
selected-only export, actual pristine verifier execution and shared evidence remain
absent. Historical authored scorer controls are not installed-task coverage.

**Single next concrete action:** obtain the Hub export producer's conversion and
original-ID/evidence-group correspondence record for the now-bound valid.jsonl
blob; verify it without changing the installed export or assuming singleton equivalence.

## physicsquestions

**Satisfied clauses:** fresh ReWOO subpacket verification retains exact installed
CSV/member/revision custody and ordered pinned BIG-bench input/accepted-target
linkage. Current bytes, all row/task IDs and imposed split reproduce the preserved
w-prov inventory exactly. Scorer/input wiring is cited above. This review reports
the actual metric separately: local accepted-spelling exact match strips prediction
whitespace and strips reference whitespace/trailing periods; it is not a verified
full BIG-bench response-processing/aggregation result. BLEU is unmeasured and no
numeric tolerance is introduced. Existing source acquisition does not infer a
historical converter or new runtime execution.

**Unsatisfied clauses:** no independently supplied manifest, fresh run ID, chosen
split mode/side or selected-only export exists in this assignment. Therefore exact
selected-row/export custody cannot be established from the full inventory. Pristine
verifier execution, scorer-offline-closure and all remaining shared admission evidence
are unsatisfied; bounded historical function controls do not satisfy them. Invalid
and unmeasured trial coverage is null/unknown, not zero or ordinary wrong answers.
The official-scorer-identity proof obligation remains withdrawn.

**Single next concrete action:** obtain an independently authorized selection packet
with a fresh run ID, exact ordered task IDs, explicit split mode/side and selected-only
export, then check its row/content/split identities against this preserved inventory.

## reasoning_gym

**Satisfied clauses:** fresh distribution/source/installed-member verification
retains the authenticated distribution custody; installed pool bytes match the
adapter's declared digest, all family/index ordering and nonempty reference/question
structure. All current row/task/split identities reproduce the preserved inventory.
The source route calls the installed family's score_answer on its stored entry with
the declared seed/size; reward can be fractional, with correct defined as reward>=1.
Prior resolver evidence separately establishes bounded Python metadata reconstruction;
it does not establish the actual pristine scorer. No scoring extras are enabled here.

**Unsatisfied clauses:** original generation environment/date/hash-order metadata
and byte reproduction remain missing. The preserved regeneration failure is rechecked
by the old verifier, not rerun or replaced; package identity plus seed does not reproduce
the installed pool. Independent reference=1/empty=0 behavioral eligibility over the
admitted families remains unproved. The historical three-family authored controls do
not prove all-family eligibility on the installed pool. No independently authenticated
seed-specific pool release, selected manifest/export or chosen run split/side exists.
The reader does not enforce pool digest or installed version on the runtime read/score
path. Deterministic execution-selected dependencies without scoring extras in the
actual pristine verifier, metric/runtime custody and all shared evidence remain open.
The official-scorer-identity proof obligation stays withdrawn.

**Single next concrete action:** recover the original pool-generation environment
record (including process date, hash-order inputs and dependency pins) for this exact
pool, so byte reproduction can be attempted without changing seed/families/original bytes.

## sportsunderstanding

**Satisfied clauses:** fresh verification retains installed-to-ReWOO and pinned
BIG-bench row linkage; current row/task/split mappings match w-prov exactly. The
metric-reporting alternative in its next_action is satisfied explicitly here: report
local generated-text word-label reward with dual-label rejection separately from
BIG-bench candidate-log-probability argmax/target_scores multiple_choice_grade.
No equivalence is asserted. The runtime uses the inline adapter scorer.

**Unsatisfied clauses:** the independent run-specific manifest, fresh ID, selected-only
export and chosen split/side are absent. Full-pool structural custody cannot supply
them. Matched original metric/protocol equivalence remains unestablished (the reporting
alternative does not prove equivalence). Offline/pristine runtime, complete shared
admission evidence and explicit actual invalid/unmeasured task/trial coverage are
unestablished; coverage fields remain null.

**Single next concrete action:** obtain the independently authorized selection packet
(fresh run ID, ordered task IDs, split mode/side and selected-only export) for binding
to the exact source-row inventory, keeping the local metric name explicit.

## spreadsheetbench

**Satisfied clauses:** this review retains the official-range-zero compatibility
policy. Released parser rejection is an explicitly named official-equivalent measured
zero, distinct from a completed cell comparison; infrastructure failures remain
unmeasured, and absent artifacts/completed mismatches retain their current classification.
One-variant scoring remains separate from paper soft/hard aggregates. The existing
parser audit in reports/w-spread2-evidence/audit-output.txt identifies the affected
released range task, and this inventory retains it in the pool denominator.
Fresh metadata bytes and every init/golden member the default loader chooses match
members of the actual local archive, whose recomputed digest equals the adapter pin.
The packet records 800 workbook-member comparisons and full per-row/task/content
and split inventories. This advances complete local loader-pair extraction custody;
it is not independent upstream mirror authentication or gradability.

**Unsatisfied clauses:** independent complete workbook/mirror-to-original-release
provenance, authenticated row-level gradable eligibility, and actual eligible/selected/
task/trial/invalid/unmeasured coverage are unestablished. No selection, run ID or chosen
split/side is supplied; no selected-only metadata/golden export is built. Source wiring
and the pinned local archive do not prove official scorer execution. Prior w-offscorer2
reports bounded workbook controls and a separate formula-workflow divergence; its
SpreadsheetBench raw subpacket is absent here, so that report cannot be fully revalidated
from this checkout. Formula/LibreOffice execution-selected offline closure and actual
pristine/runtime/scorer evidence remain open, as do both named shared gates. A loadable
pair or a parsable range alone does not establish gradability. No synthetic/local control
is promoted to production or ordinary dataset-trial coverage.

**Single next concrete action:** obtain an independently authenticated mirror-to-original
release mapping for the exact metadata rows and init/golden members pinned here, retaining
the released parser-rejected task and single-variant identity.

## strategyqa

**Satisfied clauses:** fresh verification retains installed CSV/member/revision and
exact ReWOO evaluator identity; current ordered row/task/split digests match w-prov.
The source normalization and whole-answer exact-match identity are explicit. This
review reports local normalized EM only; F1 and judge accuracy remain excluded.
Acquired reference evaluator bytes do not imply a runtime evaluator-package import.

**Unsatisfied clauses:** independently supplied run-specific selected manifest,
fresh run ID, selected-only export and explicit split mode/side remain absent.
Original-benchmark metric/split comparability beyond the vendored table is unresolved;
authenticated ReWOO custody and historical authored controls do not settle it.
Execution-selected deterministic offline dependencies, actual pristine verifier/runtime
and all shared admission evidence remain open. Actual invalid/unmeasured trial counts
are unknown/null and no execution-equivalence receipt is inferred from source acquisition.

**Single next concrete action:** obtain an independently authorized selection packet
with fresh run ID, ordered task IDs, explicit split mode/side and selected-only export,
then bind it against these exact CSV rows while retaining local EM identity.

## Shared evidence, coverage and validation boundary

All six reference scorer-offline-closure and artifact-only-state-export. Neither
shared blocker is edited. Current task-bound expected-input mechanisms (w-tbi/w-tbi2)
advance consistency under trusted independently selected specs; they cannot create
an absent authorized selection or certify a selected-only privacy projection.
The later w-resolver2 metadata evidence narrows Python dependency obtainability for
Reasoning Gym/SpreadsheetBench; it does not certify execution-selected native/ABI/
LibreOffice resources or trusted runtime. Complete runtime custody, official provenance/
execution at the required scope, resources/budgets, artifact-only state export and
connected class-specific snapshot/lifecycle/cleanup/admission evidence remain unmet.
In particular, authoritative per-task export/private-input contracts, ownership,
quiescence/trial binding, scoring equivalence and live lifecycle/cleanup are still
required by artifact-only-state-export; source inventories certify none of them.
No complete shared closure is certified by this source audit.

For every dataset, run_id, selected_manifest, selected_only_export, chosen_split_mode,
chosen_side, selected_tasks, expected_trials, measured_trials, invalid_trials and
unmeasured_trials are null in observations.json. There are no benchmark trials here;
unknown historical/authorized-run denominators are not fabricated as measured zeros.
No endpoint/model binding, resource-limited trial, cleanup or diagnostic receipt is
invented for this inert read-only review. No endpoint is contacted or utilization claimed.
No runs/, frozen receipts, gates, admission/refusal code or main checkout is changed.

The four preserved row/split inventories, ReWOO and Reasoning Gym provenance subpackets,
and E1 integrity checks pass. The full inherited w-prov verifier fails because today's
qa/base.py differs from its old source snapshot; current source is independently rebound
here. The inherited w-offscorer2 verifier fails at missing bird_ds/SHA256SUMS; its
SpreadsheetBench subpacket is also absent. Both raw failures are retained in this packet,
not fixed by rewriting old receipts or claimed as successful validation. commands 0 and 4
retain two fixture-development failures before final audit capture (path typo, AST f-string);
command 5 is the successful final audit. No scorer failure is assigned a score.

Final reproducibility, checksum, registry-scope and focused-test output is in
reports/w-journalcov-validation.txt. Only these six observed fields gain
new qualified observations; statuses, next_actions, histories, shared records and
production_authorized=false remain unchanged. Commit is confined to this registered
worktree for parent review.

Focused registry/journal validation: 59 passed, 3 expected xfails. Full packet
reproduction, independent digests and the registry checker pass. An initial staged
whitespace check detected spaces introduced by the numbered-source wrapper on empty
source lines; the wrapper now uses lossless JSON-quoted lines without changing any
source byte/digest. Its raw failure is retained as JSON-encoded stdout in the
validation log, followed by the final full staged check.
