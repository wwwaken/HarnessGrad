# Bounded pre/post-export scoring equivalence - w-e5

**E5 remains PARTIAL. E4/E5/E6 remain PARTIAL; artifact-only-state-export and every dataset blocker remain open.**

Actual `export_state` projections preserve scoring on **18/18 authored pairs across
9/24 implemented scorer routes (9/28 published datasets)**, exercising **5/12
explicitly enumerated scorer read/transform shapes**. Each dataset has a passing
and a failing pair. This is equivalence **under the contracts below**, using the
actual local scorer entrypoints on original and exported states. It is not
equivalence in general, a production pristine dataset certification, or a new
official-vs-local metric comparison. **Zero production pristine datasets are
certified by this packet.**

Baseline: `bf917b3b237e352ac46373fdba501d35004c7911`, registered `/tmp/hg-e5`,
branch `wg-e5`. Read `AGENTS.md`, `reports/w-reassess2-shared-closures.md`,
`reports/w-quiesce-receipts.md` and `reports/w-offscorer3-coverage.md` before
implementation. A read-only delegated source audit was checked against source;
the parent reviewed the entire change and executes the checks. Production code,
dataset gates, admission/refusal logic, existing receipts and `runs/` are untouched.

All packet-relative paths below are under `tests/fixtures/hg_we5/`.
`evidence/` is the final packet. `coverage.json` derives the denominators from
the source-only published declarations and an explicit, disjoint audited shape
partition. `source-audit.txt` preserves numbered source excerpts and freshly
computed file hashes. These shapes describe scorer dependencies; they do not
replace the separate demand x surface and exercises axes.

## What the pristine path actually transforms

| Enumerated transformation | Source | New paired evidence and limit |
| --- | --- | --- |
| P1: select explicit files, drop all other actor state | `eval/admission/artifact_admission.py:326-355` | Every pair keeps an unselected decoy in the source, excludes it from export, and the scorer open observations show it is not consumed. Optional files cannot be dropped merely because they are optional: incomplete-projection controls below demonstrate changed scores. |
| P2: copy exact bytes under the same relative names into a fresh separate root | `eval/admission/artifact_admission.py:344-385` | Every selected file is independently compared with the original bytes and actual receipt, before and after scoring. Nested workbook paths are included. No text/JSON/SQL/XLSX conversion is performed by this function. |
| P3: replace filesystem identity and metadata | `eval/admission/artifact_admission.py:349-372` | The original files are mode 0600 with deliberately old mtime; exports are actually mode 0640 with different inode and mtime. Direct local scoring agrees at the two distinct roots. Metadata is observed, not inferred from the flags. Directory creation sets 0750/current effective group. |
| P4: change scorer namespace, access and environment | `eval/verification/pristine.py:114-129` | **Not newly exercised here.** Production uses `/control-input` and `/control-scorer` read-only binds, a distinct scorer UID, workdir `/tmp`, sealed command and restricted environment. Host checks under the platform UID do not validate these effects. |

Thus **3/4 enumerated transformation groups** are exercised at the filesystem
export API plus local-scorer boundary; P4 remains uncovered here. This fraction
does not mean three quarters of production E5 is satisfied. The existing
w-quiesce control supplies its own earlier container-path pair at its unchanged
authored scope; it is not counted as another dataset here.

Representation constraints are refusal gates, rather than conversions:
`artifact_admission.py:183-205` permits regular, single-link, non-executable data
and refuses link traversal. Limits and canonical explicit paths are checked at
`:144-177`; selected copying is bounded, cleans failed fresh projections and
never reuses an old destination (`:355-402`). The export rechecker at `:405-446`
requires the exact path set, size, content digest, task/run/trial identity and
accounting. It cannot discover a missing semantic dependency from an otherwise
well-formed but incomplete contract.

Private inputs are a separate transformation. `data/scaffolds/qa/base.py:339-358`
serializes task gold with sorted keys and retained Unicode, hashes those exact
bytes, and supplies task/digest arguments. The real checker hashes and parses
one consumed buffer (`data/scaffolds/qa/verify/check.py:168-184`). The final
controls call each actual `_SPEC.verifier` on authored gold, retain the returned
spec and use its exact gold content and policy flags. Private gold is outside
both original and exported actor roots and is held identical for each pair.
This exercises the factory serialization/buffer-binding contract, not acquisition
provenance or actor-private-input safety under production custody.

Current-route rematerialization is different from pristine export:
`eval/verification/verifier.py:564-566` calls `_materialize`; its implementation
at `eval/observe/tracing.py:322-336` writes inline text or uses `copy2`/`copytree`.
It is not the pristine selected-file projection. Explicit pristine opt-in is
required at `verifier.py:478-486`, and current reward-file command specs cannot
be switched to that route unchanged: the exit0/completion-marker sealed-command
protocol remains required. Source inspection still finds **0/28 dataset literal
pristine opt-ins**. No artificial dataset opt-in is added by these tests.

## The documented scoring contracts that were tested

`collect.py` makes authored source/private states in a fresh external temporary
directory. `worker.py` invokes actual unchanged local `check.main` entrypoints,
first on that original source and then on the result of production `export_state`.
Each projection has a fresh UUID-based export identity, a native v2 receipt and
an enforced execution binding. Its genuine receipt is checked before and after
scoring. No refused projection is passed to a scorer.

The projection contract derives from the existing sealed addition control's
declaration: its closure bytes are actually rehashed and verified. Only task,
authored specification digest and export allowlist/bounds change. **That control's
scorer/image declaration is used solely to validate export API inputs. The dataset
scorers do not execute that sealed control, image or production pristine runtime.**
There is no claim that this derived export fixture authenticates a dataset scorer
closure or is a dataset production admission contract.

| Scorer / exact bounded contract | Positive pre → post | Negative pre → post | What is represented and read |
| --- | --- | --- | --- |
| GSM8K, current decimal-aware-extract adapter metric | 1 → 1 | 0 → 0 | UTF-8 answer.txt; quote/whitespace handling followed by current numeric extraction; fixed authored gold. This metric is distinct from upstream exact match. |
| StrategyQA, current whole-answer normalized match | 1 → 1 | 0 → 0 | UTF-8 answer.txt, matching quote removal and whitespace normalization; yes versus no. |
| TriviaQA, alias maximum exact match | 1 → 1 | 0 → 0 | Quoted alias/underscore input, same accepted-alias array and canonical value; incorrect town remains incorrect. |
| FEVER, strict label plus evidence | 1 → 1 | 0 → 0 | Both answer.txt and prediction.json; structured label/evidence takes precedence over an intentionally wrong fallback. Empty predicted evidence fails the authored non-NEI claim. |
| HotpotQA, joint EM | 1 → 1 | 0 → 0 | Both files, structured answer and title/index pair; dropping the supporting pair fails. |
| MuSiQue, current answer_support platform joint F1 | 1 → 1 | 0 → 0 | Both files and exact factory score-mode; answer F1 times support F1 is the platform reward policy, not an official MuSiQue joint metric. Empty support fails. |
| 2WikiMultihopQA, structured Joint F1 | 1 → 1 | 0 → 0 | Its own JSON contract is encoded inside answer.txt; answer, support pair and relation triple are retained. Empty evidence triples change the negative case. Generic prediction.json is absent. |
| BIRD Mini-Dev, per-question EX | 1 → 1 | 0 → 0 | answer.sql plus the identical separate private closed SQLite DB and gold SQL. Row order/duplicates are handled by real set equality; an incomplete result set fails. |
| SpreadsheetBench, named-cell value comparison, formula-free subset | 1 → 1 | 0 → 0 | answer.txt names nested/result.xlsx; both selected paths must survive. Private golden workbook/task stay identical. Numeric rounding in the comparator accepts the authored 3.141 versus 3.14 case; changed selected-cell value fails. No formula recalculation runs. |

These rows are generated facts reconciled against `evidence/summary.json` and
per-case `comparison.json`, raw child stdout/stderr, native scorer evidence and
reward files. Each `inventories.json` records actual original/exported path,
inode, permissions, timestamps and file hashes. The exact source, export and
private bytes are retained beside them. The original source inventory is
unchanged across its scoring interval in these controlled cases; this is not a
writer exclusion claim.

Python open audit observations retained in every child result show actual
selected-file and private-input reads. The auditor checks that each selected
path was read and the unselected decoy was not. SQLite native I/O is not fully
visible to Python open auditing; its actual scorer results, copied DB bytes and
separate logical row observations provide the SQLite evidence. No syscall-level
proof of all filesystem reads or dependency completeness is claimed.

Equality means identical measured classification, numeric reward/reward-file
bytes, correctness, scorer exit code and full `official` metric/profile dictionary
where supplied. Root-dependent paths, inode/permission evidence and diagnostic
wording are not required to be equal. All **18 pairs** are measured locally:
**9 passing pairs and 9 failing pairs**, with no unmeasured pair substituted as
zero. The separately labelled refusals below have no reward file.

## Changes outside those contracts and their actual outcomes

1. **Selected bytes changed after export: 18/18 refused.** Each completed pair is
   followed by a same-length mutation of a selected exported file. The actual
   `verify_state_export` raises `state projection seal mismatch`; the saved
   `tamper-refusal.json` has different recomputed original/mutated digests and
   `scorer_called=false`. No gate is bypassed and no refused state gets a score.
2. **Private gold no longer matches its bound bytes: refused.**
   `evidence/gsm8k-positive/foreign-private/` retains the real checker exit 3,
   measured=false, `scorer input task/digest binding mismatch`, and no reward file.
3. **Workbook pointer leaves the work root: refused.**
   `evidence/spreadsheetbench-positive/outside-pointer/` retains exit 3,
   measured=false and the confinement error, with no reward file.
   These two post-pair mutation inputs are literal bytes in `collect.py` (the
   private replacement JSON and `../outside.xlsx\n` pointer). Their consumed
   digest/request and raw refusal are retained; separate copies of those changed
   input files were not saved. Full pre/post paired input bytes are retained.
4. **Incomplete semantic dependency declarations: not automatically refused.**
   Eight fresh projections omit prediction.json or the named workbook. All still
   pass their narrower structural export contract. **4/8 change score 1 → 0**;
   the four already-failing inputs remain zero. This does not certify the
   narrower contract: unchanged failed scores cannot establish preserved inputs.
   Every source/full/incomplete outcome is retained in its
   `incomplete-comparison.json`. An authoritative contract must preserve the
   scorer's dependencies; native byte integrity cannot infer them.

### SQLite: identical main bytes can represent different scorer-visible state

`evidence/sqlite-wal-dependency/` is a separate authored **private-DB projection
counterexample**, not a claim that production BIRD exports a live actor DB.
An actual SQLite WAL writer commits a second row after an explicit truncate
checkpoint and stays open but performs no writes during the copy. The real BIRD
checker consumes that database. Its gold selects both rows, while submitted SQL
selects only the original row: **pre-state EX=0**.

A genuine `export_state` contract selecting db.sqlite and gold.sql but omitting
the WAL/SHM sidecars passes the native export check. The actual main-file SHA-256
is identical before and after copy (both recorded as
`3be20c5b8ac441683ddbf2f2a8d20e18028949a492c901b20659453c84dc6eef`),
yet the exported database exposes only the original row: **post-state EX=1**.
This is a measured dependency loss, not broad equivalence. The core export
checker correctly validates its declared files and does not detect this
out-of-scorer-contract semantic loss.

After the actual last writer closes, SQLite checkpoints the committed contents
into the main file. A new fresh export with the same selected names yields
**EX=0**, agreeing with the original logical state for this authored query pair.
The raw open-WAL main/sidecar bytes are preserved in
`live-private-before-close/`, closed main bytes in `live-private-after-close/`,
and both exported variants beside them. `observations.json` retains exact row
sets, PRAGMA results, pre/post hashes, contracts and native receipts. This covers
the demonstrated orderly close/checkpoint case only; atomic live snapshotting,
multiple writers, locking, concurrent checkpoint/recovery and general SQLite
backup equivalence remain unvalidated.

The final collector's parent row probe opens the main-only WAL-mode DB and
creates new SHM/empty-WAL files after the scorer call; these are preserved in
`main-only/`. That archived post-probe tree is not an untouched exact-allowlist
projection. The validator reconciles its declared main/gold bytes and identifies
the added sidecars, and runs the full native receipt recheck on the checkpointed
tree. An initial overbroad attempt to recheck the whole post-probe main-only tree
is retained in `verification.final-unsealed.stderr.txt` as a genuine allowlist
refusal; it is not a scorer failure or an ordinary zero.

## Coverage fraction and remaining obligations

The denominator is **28 published source declarations**, including **4 refused
datasets**, leaving **24 implemented scorer routes**. Coverage is **9/24**
implemented routes, or **9/28** published datasets, with authored projected-state
pairs only. **15/24 implemented routes remain unpaired in this packet.**
The following **5/12 shape groups** have some paired evidence, with residual
branches explicitly retained; the remaining **7/12 groups** have none.

| Scorer read / transformation group | Datasets and bounded coverage | Remaining scope / reason |
| --- | --- | --- |
| Scalar QA | **3/8**: gsm8k, strategyqa, triviaqa covered; sportsunderstanding, physicsquestions, reasoning_gym, bfcl_v3, chessbench_puzzles unpaired | Shared reader does not certify each scorer's profiles/private inputs. BFCL names-only and Chess strict sequence metrics must not be conflated with upstream metrics; Reasoning Gym reconstructs generator/task context. |
| Pair-evidence structured QA | **3/3**: fever, hotpotqa, musique | Full schema breadth, long evidence lists, alternate gold groups/aliases, modes, malformed/missing artifacts and acquisition/custody remain bounded. |
| Triple-evidence JSON in answer.txt | **1/1**: twowikimultihopqa | Own JSON schema, aliases/entity products, partial channels and aggregation breadth remain. `data/datasets/twowikimultihopqa.py:422-496`; it is not the generic pair-only prediction schema. |
| GAIA answer normalization | **0/1**: gaia | Own file/placeholder policy and pinned normalizer need an actual state pair (`gaia/verify/check.py:81-99`); older official/local comparisons are not such a pair. |
| SQL plus private SQLite | **1/1**: bird_minidev | Query execution and set equality `bird_minidev/verify/check.py:99-133`; mutable DB/sidecars and general DB closure remain, as the WAL counterexample demonstrates. |
| Workbook pointer plus XLSX | **1/1**: spreadsheetbench, formula-free subset | Path rebasing/normalization `spreadsheetbench/verify/check.py:328-375`; formulas cause real recalculation and replacement via `shutil.move` at `:237-250`. This write does not automatically work on pristine read-only inputs. Formula caches, external links, formatting/locale and recalculation equivalence are untested. |
| Source-program reconstruction | **0/2**: ds1000, livecodebench | DS builds a wrapper from context and candidate (`ds1000/verify/check.py:26-56`); LCB parses private tests and starts a worker (`livecodebench/verify/check.py:150-170`). Candidate-only projection does not prove runtime/data/child equivalence. |
| Ordered native action replay | **0/3**: alfworld, scienceworld, jericho | JSONL/action extraction and fresh environment replay have native state/seed/budget semantics: respective checks `:147-175`, `:140-175`, `:98-135`. No native worlds are started here. |
| Service recording replay | **0/1**: appworld | URL query removal, method normalization, call replay, world evaluation (`appworld/verify/check.py:35-56`) need paired state/recording semantics beyond existing predicate comparisons. No service/container is started. |
| JSON DB hash plus dialogue gates | **0/1**: tau_bench | Upstream `consistent_hash(to_hashable(...))` (`tau_bench/verify/check.py:115-117`), expected database construction and done/output gates (`:184-197`, `:284-309`) are distinct; ordinary JSON string equality is not a substitute. |
| Single-action replay | **0/1**: agentdojo | action.json is passed to trusted bridge (`agentdojo/verify/check.py:21-30`); injection/runtime and utility reconstruction are unpaired. |
| Arbitrary task snapshot | **0/1**: terminal_bench | Whole task snapshot and trusted test insertion (`data/datasets/terminal_bench.py:231-245`); arbitrary filesystem/volume/mode semantics cannot be inferred as a selected-file allowlist. |
| Refused, outside the implemented-route denominator | **0/4**: api_bank, nestful, sotuqa, tau2_bench | Source load refusals remain at respective modules `:170`, `:52`, `:158`, `:151`; no execution or eligibility change. |

Source references in the table use `data/datasets/` as the prefix unless a full
repository-relative path is shown. The partition is an explicit audit aid, not
an exhaustive count of every possible transformation. Neither a covered shape
nor a count of paired datasets certifies its untested branches. P4 production
namespace/UID/read-only behavior, source/writer custody (E4), execution-selected
official metric/profile breadth (E5) and live lifecycle/cleanup across applicable
routes (E6) remain open. Existing official component comparisons stay at their
published bounded scope; no new upstream equivalence is inferred here.

## Commands, custody, validation and preserved attempts

The exact final collection command was:

```sh
bash -x tests/fixtures/hg_we5/commands.sh > tests/fixtures/hg_we5/commands.stdout.txt 2> tests/fixtures/hg_we5/commands.stderr.txt
```

The script records actual baseline/branch/Python identity and uses the existing
unmodified `hg_woffscorer3/gaia_tau/offline_exec.py` guard. The guard installs
kernel seccomp socket/io_uring denial, closes inherited sockets, probes AF_INET,
AF_INET6 and AF_UNIX denial, and enforces CPU 120 s / 256 FDs. The entire collector
has a 180-second wall bound; individual fresh scoring children have 30 seconds.
Children inherit the kernel filter. No model, GPU, endpoint, paid API, production
runner, benchmark scoring run, Docker or released task payload is used.
Only import-time QASpec row loading is suppressed; real scorer/parser/validator
functions are unchanged. This is not a full native-filesystem sandbox.

Source hashes and exact binary/text inputs are command-derived and preserved.
`evidence/source-pins.json` binds production/export/scorer sources and rehashed
existing control closure bytes. `execution-source-pins.json` records the reviewed
helper/guard bytes after final execution; it is not an independent pre-execution
attestation. Root `SHA256SUMS` seals the packet including scripts/raw outputs,
and `verify.py` recomputes it and reconciles bytes, original/export inventories,
actual scorer-file reads, task-bound consumed gold, raw returns, metrics and
counterexamples. No changed/refused output is promoted to an ordinary score.

The first complete packet is preserved byte-for-byte in
`preserved-initial-evidence.zip`; `preservation.json` verifies every archived
member. It used authored direct JSON serialization rather than the actual gold
factory and lacked raw open-WAL byte copies, so only the final packet supports
those additional claims. Its raw command logs remain separate. An initial ZIP
attempt encountered pre-1980 fixture timestamps; the incomplete archive remains
as `preserved-initial-partial.zip`. The verified retry clamps ZIP timestamp
metadata only; original observed timestamps remain in the inventories.

The first audit-test output `pytest-initial.txt` retains **19 passes / 3 failures**:
the corruptions were correctly refused by production `AdmissionError`, but the
test expected the wrong exception type. The test was corrected to require that
actual admission exception, with no production change; `pytest-corrected.txt`
records **22 passes**. These are fixture-test failures, not scorer failures.

Final commands/results are preserved in `reports/w-e5-validation.txt`.
Final verification rehashes **592 packet members**; **163 focused tests pass**,
including the complete retained packet, selected-content/allowlist corruption
controls, existing export/bundle admission and source-only registry checks.
The registry checker stays valid with **28 datasets, 2 shared blockers and 11
historical records**, production_authorized=false. The validation script also
compares the registry structurally against the recorded baseline and verifies
that only additive shared observed/evidence changes exist.
The raw staged whitespace findings are retained as reversible JSON in validation:
intentional answer whitespace, verbatim source excerpts and original command/test
outputs are preserved. The owned-change whitespace check excludes only those six
named raw files; all helper/test/report/registry/journal edits pass.
Registry changes are additive `observed` detail and verbatim evidence locators
on shared artifact-only-state-export only. Statuses, next_actions, dataset and
historical records and `production_authorized=false` remain unchanged.

## Exact registry observation - w-e5

Bounded pre/post-export scoring equivalence 2026-10-15 - w-e5: actual selected-file
exports preserve 18/18 authored passing/failing pairs across nine local scorer
routes, covering 9/24 implemented routes (9/28 published datasets) and some branches
of 5/12 enumerated scorer read/transform shapes. Three of four enumerated pristine
transformation groups are exercised only at the filesystem-export/local-scorer
boundary; production namespace/UID/read-only execution is not exercised. Eighteen
same-length selected-byte mutations are refused before scoring; bound private-gold
and outside-workbook-pointer changes are unmeasured with no reward. Incomplete
semantic contracts remain a real limitation: omitting structured predictions or
the named workbook changes four of eight control scores; copying an open SQLite
main file without its committed WAL changes actual BIRD EX from 0 to 1 despite
identical selected main bytes. A fresh export after orderly writer close/checkpoint
preserves EX=0 for the authored case only. These are conditional state-projection
controls, not general equivalence, official metric equivalence or production
pristine dataset certification. E4/E5/E6 remain PARTIAL; artifact-only-state-export
remains OPEN/code-solvable, all dataset blockers and full next_actions/history/gates
remain unchanged, and production_authorized remains false.
