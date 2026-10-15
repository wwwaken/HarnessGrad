# Native task-bound scorer inputs - w-tbi2

**19/19 surveyed actor-workdir dataset routes now have task-bound scorer inputs;
0/19 remain unbound. All seven different-task substitutions were refused.**
This extends w-tbi's 12 QA-command routes with the seven native routes confirmed
from its report and adapters: **alfworld, bird_minidev, ds1000, jericho,
livecodebench, scienceworld, spreadsheetbench**. ChessBench puzzles already uses
QASpec and belongs to the existing 12; its alternate in-process controller is not
new coverage. The denominator is the same historical 19, not all 28 registry entries.

Baseline `bf917b3`, registered worktree `/tmp/hg-tbi2`, branch `wg-tbi2`.
Read `reports/w-tbi-receipts.md`, its raw audits/test receipts and actual QA
implementation first. Baseline source lines, original local sources, recomputed
identities and real task pairs are preserved in
`reports/w-tbi2-evidence/baseline-audit.json`. Current complete source, numbered
lines and recomputed file hashes are in `current-source-audit.jsonl` in that same
directory; `audit.py` generates it. No gold values are invented or printed here.

## Binding and consumption

At baseline **all seven lack a selected-task consumed-input digest check**. Staging
and source inventories do not provide that check; task labels in Jericho and
Spreadsheet metadata were not independently compared. DS1000's context was only
actor setup, so verification could consume the actor's replacement tests.

`data/scaffolds/scorer_input.py:32` builds a selected-task binding from actual
inline UTF-8 bytes and local file bytes. `:17` computes SHA-256 of canonical JSON
mapping relative input paths to their SHA-256 digests (sorted keys, compact
separators). `:45` declares `scorer_input={task_id,path,sha256,files}` and trusted
argv pins; `:50` stages the helper. Source-hash reuse is keyed by filesystem
identity/size/mtime/ctime; the consuming check always recomputes its own hashes.

`data/scaffolds/scorer_input.py:62` copies the actual inputs to a private temporary
tree, hashing each stream while copying, and compares the entire inventory and
aggregate digest before scoring. The callback consumes those same private copies,
which remain alive until it returns, then are removed. A mismatch/missing input
exits 3, writes `measured=false` and actual/expected identity, and creates no reward.
The scoring callback is outside the validation exception handler, preserving the
route's existing scoring/error semantics. No metric predicate was changed.

`eval/verification/verifier.py:491` retains w-tbi's independently selected task
comparison before staging. `:512` retains its receipt check and additionally
compares the per-file inventory when declared. A foreign spec, missing selected
task, missing/foreign/unverified receipt or removed binding arguments yields
`score=null` and an unmeasured reason. QA source files are byte-identical to the
baseline; the QA receipt contract remains valid. Legacy by-hand calls without any
binding arguments remain explicitly unbound, and cannot satisfy a bound dispatch.
As before, low-level APIs bypassing `_verify` must enforce their own selected spec.

## Per-route delivery, use and mismatch

Paths in this table are repository paths; line numbers refer to current source.
All file deliveries are through a `files` environment and trusted `VERIFY.inputs`,
restaged by the existing verifier. Every row now has recomputed consumed-file
identity **and** selected-task binding; neither existed at baseline.

| Native route | Expected-input delivery and actual consumption | Binding added and real mismatch result |
| --- | --- | --- |
| alfworld | `data/datasets/alfworld.py:358` inline stripped `game.tw-pddl`; `data/datasets/alfworld/verify/check.py:170` passes its path to replay | Adapter `:364` pins stripped bytes. Replay gets the authenticated private PDDL. Selected `look_at_obj_in_light-AlarmClock-None-DeskLamp-308__trial_T20190908_222917_366542` versus `look_at_obj_in_light-AlarmClock-None-DeskLamp-308__trial_T20190908_222933_607649`: refused before replay, exit 3/no reward. |
| bird_minidev | `data/datasets/bird_minidev.py:265` inline `gold.sql`, `:266` DB file as `database.sqlite`; `data/datasets/bird_minidev/verify/check.py:110` reads SQL, `:116` opens SQLite | Adapter `:269` pins SQL **and DB**. Both reads use private copies; SQL normalization/EX unchanged. `bird_minidev/0` versus real task `/30`, chosen because it also uses a different database: SQL-only and DB-only substitutions each refused before connect/query, exit 3/no reward. |
| ds1000 | Formerly SETUP-only `context.json`; now `data/datasets/ds1000.py:202` trusted context plus `:206` four explicit CSV inputs. `data/datasets/ds1000/verify/check.py:46` parses private context; `:73` passes private CSV directory via `SEABORN_DATA` | Adapter `:212` pins context and all four expected CSVs. Restaging restores task tests. `ds1000/0` versus `/1` context refused before child process; four separate shared-CSV tamper controls also refused, exit 3/no reward. |
| jericho | `data/datasets/jericho.py:268` task/ROM/seed JSON, `:271` ROM file; `data/datasets/jericho/verify/check.py:123` passes private config/ROM into `load_game`; `data/datasets/jericho/lib/jer_env.py:56` parses that config | Adapter `:277` pins config **and ROM**. Library takes explicit overrides instead of reopening fixed workdir names; the seed comes from pinned config. `acorncourt` versus `advent`: config-only and ROM-only substitutions each refused before engine construction, exit 3/no reward. |
| livecodebench | `data/datasets/livecodebench.py:273` selected `tests.json` file; `data/datasets/livecodebench/verify/check.py:161` reads its private copy and forwards parsed text to unchanged executor branch | Adapter `:285` pins released test-file bytes. `livecodebench/0` versus `/1`: refused before executor/measurement branch, exit 3/no reward. |
| scienceworld | `data/datasets/scienceworld.py:329` task-name/variation/simplifications JSON, `:327` stages actual installed world JAR; `data/datasets/scienceworld/verify/check.py:168` passes private config/JAR to loader; `data/datasets/scienceworld/lib/scw_env.py:142` parses config, `:128` forwards explicit JAR as `serverPath` | Adapter `:339` pins config **and world JAR**. Package-default JAR fallback cannot replace the bound payload. `task-1-boil/21` versus `/22` config refused before JVM/world construction. A separate real JRE JAR substituted for the shared world JAR is also refused, exit 3/no reward. |
| spreadsheetbench | `data/datasets/spreadsheetbench.py:247` golden workbook file, `:248` task metadata JSON; `data/datasets/spreadsheetbench/verify/check.py:333` parses metadata and `:383` compares private golden workbook | Adapter `:257` pins metadata **and workbook**. `13-1` versus `17-35`: metadata-only and golden-only substitutions each refused before comparator/recalculation, exit 3/no reward. Official range/parser/rounding behavior unchanged. |

The two ScienceWorld tasks use the same world JAR, and DS1000 tasks share the CSVs.
Identical shared bytes cannot demonstrate different-task rejection. Those five
extra payload controls therefore substitute **different actual local files** and
are labeled shared-payload tampering, not different-task gold. The 15 separate
component substitutions comprise ten task-specific component swaps across all seven
routes plus these five shared-payload controls. Every digest/source/task ID comes
from commands/tests and is preserved in the raw artifacts, not transcribed guesses.
`outcomes.json` extracts selected pins, all 15 receipts and native dispatch outcomes
from the authoritative `tests-after.txt` output.

## Fails before / passes after

- Exact same 106 native controls on baseline: **99 failed, 7 passed**; final: **106 passed**.
- Three real-library path-forwarding controls: **3 failed before, 3 passed after**.
  Combined focused coverage: **102 failed/7 passed before -> 109 passed after**.
- All 15 direct component mismatches were accepted at the baseline spy boundary;
  all 15 are now refused with exit 3, `measured=false`, no boundary call/no reward.
  All seven foreign-task native dispatch cases return null/unmeasured.
- The 253-test regression set passed, including all **156 existing QA binding
  controls**, ordinary verification, registry, boundaries and DS1000 scratch cleanup.

Native tests use actual local adapter records. They invoke real checks, materialize
actual verifier inputs and consume actual verdict files; only process/scoring
boundaries are spies. No TextWorld/Jericho/JVM engine, SQL query, candidate program,
released scorer or workbook comparison runs. Empty-answer/sentinel branches are
plumbing controls, never benchmark scores. The three extra controls run actual
Jericho/ScienceWorld loader/factory functions and intercept only native constructors,
checking the selected config/seed/ROM/JAR despite foreign workdir config.

Independent replacement-after-authentication controls confirm reads from private
copies remain unchanged when original inputs are replaced. Defect controls cover
missing/foreign task/digest/files/unverified receipts, foreign specs, missing selected
task, removed binding flags and DS1000 trusted context rematerialization. Scoring
`ValueError` propagation is preserved. Final QA regression repeats follow the native
inventory-consumer change; exact outputs are in the validation receipt.

Raw artifacts under `reports/w-tbi2-evidence/`:
`tests-before.txt`, `tests-after.txt`, `engine-paths-before.txt`,
`engine-paths-after.txt`, `tests-regression.txt`, `tests-final-regression.txt`,
`baseline-audit.json`, `implementation-review.json`, `current-source-audit.jsonl`,
`outcomes.json`, `review-audit.json` and `audit.py`.
The initial 99-control baseline is retained as `tests-before-initial.txt`; final
before/after counts use only the identical final 106-control file. Preserved
`tests-after-exploratory.txt` records an early test-spy defect (98 passed/1 failed:
ScienceWorld's legacy spy did not handle explicit `server_path=None`); the spy was
corrected. `tests-after-exploratory-final.txt` preserves the worker's 106-pass check;
the parent reran the same final tests for the authoritative after receipt. Exact commands,
checker output and full final focused outputs are in `reports/w-tbi2-validation.txt`.

## Scope and registry observation

**19/19 bound, 0/19 unbound** applies to these surveyed command routes under trusted
selected spec/check custody. It does not authenticate upstream row provenance,
arbitrary caller-supplied specs, runtime/import/native dependencies or arbitrary
scorer JSON. A trusted caller consistently relabeling the wrong source row is still
outside this consistency check. Historical/cached receipts are not upgraded.
AppWorld, GAIA, tau-bench and Terminal-Bench snapshot/service routes are outside this
denominator, as are alternate controllers. Full runtime custody, pristine execution,
backend enforcement, lifecycle and broader official-execution evidence remain open.

No benchmark/pilot/model/GPU/endpoint/container/network call. All pytest basetemps
are outside the platform. `runs/` and frozen receipts are untouched; no existing
run ID was resumed. Additional disk use is bounded to local test scratch copies,
removed by temporary-directory lifecycle. No dataset blocker closes.

Native task-bound scorer inputs 2026-10-15 - w-tbi2: The seven remaining surveyed native actor-workdir routes alfworld, bird_minidev, ds1000, jericho, livecodebench, scienceworld and spreadsheetbench now bind their consumed expected-input inventory to the independently selected task, increasing route coverage from 12/19 to 19/19 with 0/19 unbound. Checks recompute per-file and canonical inventory SHA-256 while creating private copies and pass those copies to unchanged scoring branches; DS1000 now restages context and binds its four auxiliary CSVs, Jericho binds config/seed plus ROM, BIRD binds SQL plus DB, ScienceWorld binds config plus explicitly loaded world JAR, and SpreadsheetBench binds metadata plus golden workbook. All seven different-task cases and all 15 separate component substitutions are refused before scoring with no reward; native mismatches are null/unmeasured. Identical final focused controls change from 102 failed/7 passed to 109 passed, with 253 regressions passing. This supersedes only w-tbi's seven-unbound-input residual, not upstream provenance or runtime custody. S1 remains PARTIAL and still needs complete execution-selected interpreter/import/native/runtime custody; S3/S4/S5/S6 remain PARTIAL. scorer-offline-closure and every dataset blocker remain open, with statuses/next_actions/history/gates and production_authorized=false unchanged.
