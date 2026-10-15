# Journal-coverage next-action follow-up — w-jc2

All six dataset-journal-gap blockers remain measurement/open. Both shared
blockers are unchanged. No selection packet or run ID was supplied or created.
The prior report's **single next concrete action** guides the investigations;
the registry's complete next_action remains binding, including its downstream
runtime/shared clauses. A "blocking input" below names the next upstream
dependency, not a claim that every other closure clause is satisfied.

## FEVER

**What moved:** official `https://fever.ai/download/fever/shared_task_dev.jsonl`
was acquired with raw HTTP custody and compared to every installed row by
`original_id`. Original-body SHA-256 is
`e89865bfe1b4dd054e03dd57d7241a6fde24862905f31117cf0cd719f7c78df7`;
installed export SHA-256 remains
`5da0ccc0ccf77f974611de13f8aac6f78c6bba6293912835099eb6029baa85d9`.
All 15,935 installed rows match original claim, label and verifiable fields.
All 9,525 non-NEI rows' evidence equals a complete original evidence group,
both ordered and as a pair set after explicit page-NFC/line-int normalization.
The 6,410 NEI rows match original claims but contain retrieved evidence, not
original gold groups. Counts and raw recomputation are in
`tests/fixtures/hg_wjc2/fever/observations.json:10` and
`tests/fixtures/hg_wjc2/fever/audit.stdout.txt:1`;
per-row content hashes/original line/group indices are retained in
`tests/fixtures/hg_wjc2/fever/row-correspondence.jsonl.gz`.

Producer corroboration also advances: the collaborator's issue reply points to
the Hub dataset at
`tests/fixtures/hg_wjc2/fever/producer-issue5-comments.body:1`; the pinned
README describes gold-group extraction, Papelo NEI retrieval and merging at
`tests/fixtures/hg_wjc2/fever/producer-readme.lines.jsonl:36`. Fresh README/merge/NEI
bytes match their previously authenticated repository tree blobs. Their
recomputed SHA-256 values are respectively
`374052abccfd55c67e5d1a94f3c05b82de4426f2ce1c5e9efdd9c5daa7164a34`,
`960f0540bb4c1e1c80027c88f256906b3c5d2124d5629e1fea0fdd7f32e36cfd`,
and `cf9d2d241577666b8cd7a52d041d3b09863d24dce8c503e3ce98c36f471a69fd`
(raw audit output, with blob comparisons, is preserved in the FEVER packet).

**What did not move:** this is row correspondence, not preservation of every
original group. Of the represented 6,551 non-NEI original IDs, 42 IDs have
51 alternative original groups absent from this validation export. No claim
is made about other Hub splits. There are 1,400 multi-sentence export rows;
in 1,395 rows an export sentence alone satisfies no complete original group,
with 3,046 such singleton occurrences
(`tests/fixtures/hg_wjc2/fever/observations.json:20`). Actual installed examples
are in `tests/fixtures/hg_wjc2/fever/examples.json:3`.
`data/scaffolds/qa/evidence_scorers.py:161` still promotes flat sentences to
sufficient singleton groups; its recomputed SHA-256 is
`a962f23e0c0f704b31294902ddaae3facee0e7496dfc43041bf973a912043729`.
These structural counterexamples do not claim scorer execution or a task score.
The metric remains local binary label-plus-evidence strict scoring, first five
pairs, NEI-exempt. Original FEVER strict_score equivalence is unproved.

The inspected scripts/README and issue corroboration do not bind the exact
Hub-producing conversion revision, export ID assignment, added original_id,
line-string conversion or validation partition/filter. Both Hub history GET
failures remain preserved; this search does not prove global absence.

**Single next blocking input:** a producer-authenticated conversion receipt
for this exact valid.jsonl blob, identifying executable export revision/input
pins, ID/group mapping, split/filter/omission rules and NEI retrieval inputs,
including an account of the absent alternative groups. The independent mapping
here satisfies neither that producing-record clause nor complete-group metric
preservation. Independently authorized selection/export, chosen split/side,
pristine execution and shared evidence remain later clauses. Full findings and
file/line citations are in `tests/fixtures/hg_wjc2/fever/REVIEW.md`.

## Reasoning Gym

**What moved:** the original introduction commit's generator and adapter were
recovered, and the installed pool's nine time-only metadata rows all retain the
effective date `2026-10-08`. The per-row lines/dates and recomputed counts are in
`tests/fixtures/hg_wjc2/gym/observations.json:12`; this is a carried effective
date, not an authenticated process timestamp. The installed generator parses
time-only strings without an explicit default at
`reasoning_gym/arithmetic/time_intervals.py:104` (full installed path and lossless
source preimage in `tests/fixtures/hg_wjc2/gym/source-lines.txt:105`). Today's
dateutil parser fills unspecified fields with datetime.now at its line 637
(preserved at `tests/fixtures/hg_wjc2/gym/source-lines.txt:2795`). Fresh whole-file
SHA-256 values are respectively
`b42d9a9f992eead49d028f13e0ffd454b24676f92402e1a323cbabdd74d20100` and
`ee494377289c92c401fd7825fb7500981c33098a2bd40219aa4948713e9d1fff`;
raw independent digests are in the gym packet's `independent-digests.stdout.txt`.

The recovered original generator
`tests/fixtures/hg_wjc2/gym/original-prepare.py:39` declares package 0.1.25;
lines 44–45 retain seed 20261008 and per-family count 20. Its SHA-256 is
`0ac637564179a4008504707f5b92c0ce13e10013e30151fe4bfa09636f199ce9`.
The original adapter at
`tests/fixtures/hg_wjc2/gym/original-reasoning_gym.py:73` already pins this pool,
and its SHA-256 is
`65f8dffb19af3c32c124a0edcadd8d6df0f12716cbee7271ea25b9a59d68beab`.
The original-to-current generator diff changes paths/root-depth only. Commit
dates and pool filesystem timestamps corroborate the carried date but cannot
authenticate the process clock, environment or dependencies. Pool SHA-256 stays
`c0ff4eaef318cd59afcc61472ebe206362fc0211c4b589ed0d53946a569bd177`.

**What did not move:** the original generation environment record was not
recovered in the inspected dataset directory, current and introduction-commit
source/docs, scoped tracked history or preserved attempt command fields. This
does not assert absence from private producer records or the entire machine.
The earlier unequal regeneration remains preserved; no generation rerun,
all-family reference/empty scoring, changed seed/family/order or runtime
execution occurs. Current dependencies are not historical dependency pins.

**Single next blocking input:** the original pool producer's launch/environment
receipt bound to this exact digest: invocation, interpreter/build identity,
effective clock/timezone, original hash-order inputs and dependency artifact
lock. Launch-time PYTHONHASHSEED plus hash implementation is needed; if hashing
was randomized, its realized hash secret/order evidence is needed as well.
Today's environment or a newly chosen seed/date cannot supply it. The carried
date narrows this upstream request; selection, behavioral eligibility, pristine
runtime and shared clauses remain open. Full scoped investigation and raw
commands are in `tests/fixtures/hg_wjc2/gym/REVIEW.md`.

## Physics Questions

**What moved:** exact expected-input custody now extends from parsed CSV rows
through the actual adapter gold projection to the verifier's serialization for
every installed row. `tests/fixtures/hg_wjc2/physicsquestions-gold-bindings.json:432`
records 53 ordered task/row/gold-digest bindings, matching all prior row hashes and
default imposed sides (37 train / 16 eval). Its recomputed SHA-256 is
`ff75af88480d42b9fb2e6fc5c63611cafe6d94d60046a10d2f5222c95abce5b2`.
Installed CSV SHA-256 remains
`7747cf185111aaa58493b5d804ba7b496cb152a6ae89a69a66a0c443adfd34aa`;
adapter SHA-256 is
`452d134d58a1900355112edb8dcc9837c39830c953d2d064db3b409d54c001cf`.
Raw recomputation output is `tests/fixtures/hg_wjc2/parent-1.stdout.txt` and
`tests/fixtures/hg_wjc2/independent-sha256sum.stdout.txt`.

Source linkage: `data/datasets/physicsquestions.py:120` reads rows,
`data/datasets/physicsquestions.py:135` projects accepted spellings, and
`data/datasets/physicsquestions.py:103` scores them. The source-extracted
projection helper was executed without importing the adapter or scoring.
`data/scaffolds/qa/base.py:339` serializes gold with ensure_ascii=False and
sort_keys=True; these exact UTF-8 bytes, including the default JSON spaces,
are what the new inventory hashes. `data/scaffolds/qa/verify/check.py:171`
reads the single buffer whose digest is checked before parsing at
`data/scaffolds/qa/verify/check.py:184`.

**What did not move:** no independently selected row set, selected-only export,
chosen run split/side or pristine verifier execution exists. The local metric
remains accepted-spelling exact match with prediction whitespace stripped and
reference whitespace/trailing periods stripped; BLEU and full BIG-bench
response-processing/aggregation remain unmeasured. Structural custody is not
behavioral eligibility or trial coverage.

**Single next blocking input:** the benchmark operator must independently supply
an authorized selection packet with a fresh run ID, exact ordered task IDs,
explicit split mode and side, and the selected-only export to authenticate.
The default inventory cannot make those decisions. Once supplied, compare its
row, gold, content and split identities against the retained bindings; shared
and actual-runtime requirements still apply before any diagnostic.

## Sports Understanding

**What moved:** all 1,000 installed rows now have exact serialized-gold hashes
linked to task IDs, prior parsed-row hashes and unchanged imposed sides
(663 train / 337 eval), recorded at
`tests/fixtures/hg_wjc2/sportsunderstanding-gold-bindings.json:8008`.
The binding-file SHA-256 is
`537dce7d6ac8144f22cd14010dfef6d86e0cc922b84483954b636085735f2812`.
CSV SHA-256 is
`5cfc24702b7a809409f42634f0b958f0d61c4d5aec8d732fd89889281c63d45e`;
adapter SHA-256 is
`e44f856dda4c2761737ffe9d0b0b3fca59e149c1ec12e7451be33872df5d86ad`.
The file and independent raw digests are preserved beside Physics Questions.
`data/datasets/sportsunderstanding.py:101` reads rows,
`data/datasets/sportsunderstanding.py:112` validates/projects the label, and
`data/datasets/sportsunderstanding.py:80` scores generated text. The common
serialization/checker linkage cited above applies exactly.

**What did not move:** no selection packet, actual selected-only export, chosen
run split/side or pristine scoring receipt is present. The metric is **local
generated-text word-label reward with dual-label rejection**, separately from
BIG-bench candidate-log-probability argmax/target_scores multiple_choice_grade.
The reporting alternative remains satisfied; metric equivalence is unproved.
Coverage, invalid trials and unmeasured trials remain unknown/null.

**Single next blocking input:** an independently authorized operator selection
packet containing fresh run ID, ordered task IDs, explicit split mode/side and
selected-only export. Then authenticate against the preserved row/gold bindings
while retaining this local metric name; runtime and shared gates remain open.

## StrategyQA

**What moved:** every installed row now binds to the exact serialized gold,
with 2,290 task/row/gold-digest entries and unchanged imposed sides
(1,520 train / 770 eval), recorded at
`tests/fixtures/hg_wjc2/strategyqa-gold-bindings.json:18328`. Binding-file SHA-256:
`4409c4cb13f4ce8e29f8ab60d01afefdfad4f5104b5630b3e4f02048a21cc5ef`.
CSV SHA-256:
`c1fd0c271bf98741b68ac1ea3d167c5ccf2ed46da66645d5fc0ed6222e45f055`;
adapter SHA-256:
`eaad45dfb944241fad84eb575882560ffcf7243de40c9d34fd0766a40c16a50a`.
`data/datasets/strategyqa.py:107` reads the table,
`data/datasets/strategyqa.py:118` validates/projects its label, and
`data/datasets/strategyqa.py:89` scores whole-answer normalized EM. Raw outputs
are retained with the other input bindings; no answer values were exported.

**What did not move:** selection, chosen run split/side, selected-only export,
original-benchmark split/protocol comparability and pristine runtime evidence
remain absent. Acquired ReWOO evaluator custody does not establish a runtime
import or scoring execution. Reported identity stays **local normalized EM**;
F1 and judge accuracy remain excluded, and trial counts remain null.

**Single next blocking input:** the independently authorized operator packet
with fresh run ID, ordered task IDs, explicit split mode/side and selected-only
export. Its rows and expected-input hashes can then be compared with this exact
CSV inventory. The runtime/offline/shared clauses remain separately unsatisfied.

## SpreadsheetBench

**What moved:** the prior report's concrete mirror-mapping action is satisfied
for the actual **Verified 400 release**. Canonical upstream commit
`49b73a94775fb489063f60ca1865e3a650079a79` contains the independently downloaded
release archive, byte-identical to the installed mirror archive. Both are
14,958,255 bytes, SHA-256
`10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949`,
with recomputed Git blob SHA-1 `b6baaf0f23ef5adc1cd22078f4eeb3102b4a7c72`
matching the pinned canonical GitHub tree/API. Raw receipts, bytes' digests and
equality are preserved in `tests/fixtures/hg_wjc2/spread/summary.json:2` and
the spread packet's audit command output. The revision-pinned upstream README
explicitly announces Verified 400 and links this mirror at
`tests/fixtures/hg_wjc2/spread/responses/github-release-readme-pinned.decoded.md:11`;
its SHA-256 is
`ba96370b14fa897a61d7a68f3ada6399391d0a4f5d4a8bb9be2a1a38a4316143`.

Installed metadata SHA-256 is
`bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7`.
The metadata and all 800 default-loader init/golden members match **both** the
mirror and canonical release archive; per-member paths and recomputed digests
are in `tests/fixtures/hg_wjc2/spread/member-mapping.json:2`. The released
parser-rejected task `283-32` remains included, with the official parser-only
rejection independently rechecked. The existing official-range-zero policy
and one deterministic workbook pair per task are retained. Parser rejection
is a named measured zero under that policy; infrastructure failure is still
unmeasured. No scored cell comparison, full scorer or trial result is inferred.

**What did not move:** Verified 400 is not byte-equivalent to the historical
912-task release. The independently acquired historical archive has SHA-256
`25d430f671613505232e47b143ddfd5a2ead87ec67ff25982f7a7dfb130fad18`;
its Git blob/size match canonical historical source metadata. Compared with it,
226 metadata rows differ and 94 chosen workbooks have no byte-identical match
within the same original task; 706 chosen workbooks do match. These historical
comparisons are retained in `tests/fixtures/hg_wjc2/spread/summary.json:42` and
the member map. No hidden transformation history or original-paper protocol
equivalence is asserted. The successful mapping is independently authenticated
current upstream Verified 400 custody, including its exact changed bytes.

The upstream "expert annotated" description and authentic release membership
do not independently establish row-level gradable eligibility. No actual
eligible/selected/task/trial/invalid/unmeasured coverage, selection packet,
chosen run split/side, selected-only export or pristine official-scorer receipt
is created. Formula/LibreOffice offline closure and all shared evidence stay open.

**Single next blocking input:** an independently supplied operator-authorized
selection/qualification packet: fresh run ID, ordered task IDs, explicit split
mode/side and selected-only export for these exact Verified 400 rows/workbooks.
It must establish actual row-level gradable eligibility and coverage with the
scorer/range policy and evidence for admitted/excluded rows, retaining `283-32`
in its released range-zero classification. An upstream release label or loadable
pair cannot supply that packet. Required actual scorer/runtime/shared clauses
remain unsatisfied before full next_action closure. Full provenance scope and raw
validation are in `tests/fixtures/hg_wjc2/spread/REVIEW.md`.

## Current source and selection boundary

`tests/fixtures/hg_wjc2/bind_inputs.py` checks the new projections against the
prior row inventory without importing adapters, executing scorers or making a
selected-only filesystem export. `tests/fixtures/hg_wjc2/source-links.json`
retains verbatim source anchors. Independent current source SHA-256 values:

| Source | SHA-256 |
| --- | --- |
| `data/scaffolds/qa/base.py` | `3c2242e4ed82d76eb7732a6c077122f3d74fb4387860caa3b53a9d8a049a8d8a` |
| `data/scaffolds/qa/verify/check.py` | `7625d8070cac767c5a878623f98469cb7f4bb0b528a86980d7334b5fdbbbbe7e` |
| `data/scaffolds/scorer_input.py` | `3d567c5a7dcf19c011425979cf845c6352c468960ae406ec639a8d6e27c0dfee` |
| `data/scaffolds/registry.py` | `973e6adcfaf3b965d697f02a00d7ce80b54c0b2e8df7f49ac65007ae802339b1` |

The task ID's source pool name does not select a run side. No inventory is a
run manifest. No run ID, selected tasks, expected/measured/invalid/unmeasured
trial denominator or eligibility count is inferred from this custody audit.
No shared blocker, gate, admission/refusal code, historical run or frozen
receipt is changed; no model endpoint, model or server operation occurs.

## Validation and review boundary

Focused registry/journal tests: **59 passed, 3 expected xfails**. The xfails
remain the pre-existing missing standalone journal-review references; none is
removed to manufacture closure. Exact argv/stdout/stderr/exit are preserved in
`tests/fixtures/hg_wjc2/focused-tests.*` and copied into
`reports/w-jc2-validation.txt` without rerunning unchanged tests.

The combined validation rederives FEVER correspondence, Reasoning Gym retained
date/source custody, SpreadsheetBench archive/member/parser custody and all
three new gold-binding inventories. It also replays the prior full inventory,
checks raw response wrappers, checks every fixture checksum and verbatim source
anchor, and enforces the six-observed-fields-only registry delta. Only this
packet's new observations are written; inherited receipts are never repaired.
Public transport failures and fixture-development/whitespace failures remain
in their raw subpackets. The parent registry-format assertion failed before
any write; its stderr and correction are retained at
`tests/fixtures/hg_wjc2/parent-format-probe.*`.

The inherited w-journalcov root audit reproduces its derived inventory files,
then refuses its final whole-registry comparison because its baseline predates
the parent Resolver/AppWorld merges. That actual exit-1/traceback is retained in
the validation log. The exact pre-existing delta is
`tests/fixtures/hg_wjc2/inherited-registry-baseline-delta.json:1`.
`replay_prior_inventory.py` independently compares every derived old inventory
file; `check_scope.py` separately enforces this task's correct starting-HEAD
registry baseline. No old validator/baseline or receipt is changed, and the old
root validator is not reported as passing. Final current checks and this
explicit legacy limitation are recorded together in the validation log.

The primary worker reviewed and cherry-picked the isolated provenance commits,
then replayed their custody evidence. Downloaded SpreadsheetBench archive
preimages remain at the external paths recorded in the spread summary; they
are required for replay and must be preserved. No runtime scoring closure,
model utilization, new eligible count or production authorization is claimed.
Commit is confined to `wg-jc2` for parent review; main is untouched.
