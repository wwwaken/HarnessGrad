# SQLite WAL correctness risk and bounded refusal - w-wal

**A genuine correctness risk is reproduced and the bound native-input copy now refuses it before scoring. Generic selected-file export still requires an authoritative dependency-complete contract. No shared or dataset blocker closes; no production dataset is certified.**

Work is confined to registered `/tmp/hg-wal`, branch `wg-wal`, starting commit
`4967006c601acf39c91293403d9756cc98428134`. The existing
`reports/w-e5-equivalence.md` and its
`tests/fixtures/hg_we5/evidence/sqlite-wal-dependency/observations.json`, raw
reward files and raw main/WAL/SHM bytes were read first. They are unchanged.
`reports/w-wal-evidence/source-audit-final.stdout.txt` preserves their exact observations,
newly computed hashes, numbered source excerpts, baseline helper source and actual
worktree identity. This task does not merge to main.

## Reproduction and newly identified loss point

All new SQL uses a tiny authored table `t(value text)` with `base` checkpointed
into the main database and `wal-only` subsequently committed into its WAL.
There is no writer activity during copying. The prediction selects only `base`;
the gold selects both rows. The actual unchanged BIRD check entrypoint runs on
these authored inputs; no adapter task pool, released benchmark task, external
dataset, model, GPU, endpoint or Docker daemon is used.

| Observed path on authored inputs | Baseline | After fix | Raw evidence under `reports/w-wal-evidence/` |
| --- | --- | --- | --- |
| Original DB, legacy unbound check | EX=0, measured | EX=0, measured | `{baseline,fixed}/unbound-live/` |
| Native **bound** check, original DB still has WAL | **EX=1, measured, binding verified** | exit 3, unmeasured, no reward, binding unverified | `{baseline,fixed}/bound-live/` |
| Explicit main-only export, legacy unbound check | **EX=1**, structural receipt passes | **EX=1**, structural receipt passes | `{baseline,fixed}/unbound-main-only/`, `observations.json` |
| Actual `_materialize` main-file copy, then bound check | **EX=1, measured, binding verified** | exit 3, unmeasured, no reward | `{baseline,fixed}/bound-materialized/` |
| Export explicitly includes main + WAL + SHM, legacy unbound check | EX=0, measured | EX=0, measured | `{baseline,fixed}/unbound-full-export/` |
| Orderly closed/checkpointed DB, still WAL format | EX=0, measured | conservatively refused, no reward | `{baseline,fixed}/bound-closed-wal/` |
| Separately prepared, closed DELETE-mode DB | EX=0, binding verified | EX=0, binding verified | `{baseline,fixed}/bound-delete/` |

Each row has raw `stdout.txt`, `stderr.txt`, `result.json`, `evidence.json` and,
only when measured, `reward.txt`. Each collection has its exact command, raw
streams and actual return code in `baseline-collect.*` / `fixed-collect.*`.
The newer native-bound counterexample is stronger than the older manual E5
projection: **the private-copy boundary itself drops the WAL even if a preceding
filesystem copy or snapshot retained it**. Matching main-file hashes are insufficient.

Both collections preserve the original raw SQLite files in
`full-raw-before-close/` and the receipt-verified main-only projection in
`main-only-before-probe/`. The latter is saved **before** any SQLite reader can
create sidecars. `observations.json` records actual inventories, row sets,
contracts, native export receipts, execution identities, SQLite/Python versions,
closed/prepared header bytes and scratch cleanup. Reader activity changes SHM
bytes; the independent audit proves unchanged main/WAL/gold bytes during this
bounded interval, **not an unchanged whole tree or general quiescence**.

## Exact source boundaries and databases

Numbered excerpts and actual file hashes for these references are preserved in
`reports/w-wal-evidence/source-audit-final.stdout.txt`.

- **Generic pristine export:** `eval/admission/artifact_admission.py:354` loops
  only the declared files and copies raw bytes at `:373`. The rechecker at `:419`
  compares that same declared path set and `:443` checks its content seals. A
  contract naming only the main database can therefore be structurally valid
  while semantically incomplete. Quiescence does not checkpoint a WAL.
- **Current trusted staging:** `eval/observe/tracing.py:298` handles inputs;
  `:336` uses `shutil.copy2` for a single file. A `.sqlite` entry does not imply
  `-wal`/`-shm` entries, including when renamed. Directories use `copytree` at
  `:333`, which retains sidecars in that directory but provides no atomic live
  database snapshot. Host verification calls this at
  `eval/verification/verifier.py:567`; snapshot-service relative inputs call it
  at `:463` and copy only that entry into the container at `:464`.
- **Newly reproduced native loss:** `data/scaffolds/scorer_input.py:37` binds
  only the named byte inventory. `run_bound` at `:80` makes private copies of
  only the passed paths. The baseline copy loop, before this fix, is preserved
  verbatim as `HEAD:data/scaffolds/scorer_input.py:83:` in the source audit.
  The BIRD check passes only DB/gold at
  `data/datasets/bird_minidev/verify/check.py:103`, opens the private DB at `:116`,
  and compares query results at `:136` (the complete check is preserved in the
  repository). This can discard WAL contents even if they existed beside the
  scorer's input DB. Native binding then used to report `verified=true`.
- **BIRD Mini-Dev** uses the private authoritative SQLite source
  `dev_databases/<db_id>/<db_id>.sqlite`, staged as `database.sqlite` by
  `data/datasets/bird_minidev.py:254` and `:266`. At `:269` the adapter binds
  only `gold.sql` and `database.sqlite`; this is not an actor-submitted DB.
  The authored counterexample uses `database.sqlite`, its `-wal` and `-shm`.
  A score change is established for this authored query pair, **not an incidence
  claim about provisioned production BIRD databases**. No such database is opened.
- **AppWorld** also uses SQLite: the retained upstream
  `tests/fixtures/hg_woffscorer3/worlds/source/appworld/apps/model_lib.py:2201`
  creates `sqlite:///` disk engines; `:2195` creates named memory databases.
  `collections/models.py:79` names per-app `<app_name>.db` files, with mandatory
  `admin`/`supervisor` at `:69`. Its `environment.py:229` records the output
  `experiments/outputs/<experiment>/tasks/<task_id>/dbs` namespace; the evaluator
  reloads it at `evaluator.py:488`. These are read-only retained source evidence,
  not a new runtime observation. The retained `model_lib.py:296` uses SQLite
  backup for memory-related full saves, while `:299` has a disk-to-disk
  `shutil.copy` branch that would also require a safe standalone source.
  **Current HarnessGrad AppWorld grading replays the recorded API log in a fresh
  world**, rather than exporting the actor service's DB files:
  `data/datasets/appworld.py:279`,
  `data/datasets/appworld/verify/check.py:45` and `:47`. The recording mount is
  installed by `eval/service/services.py:406` and exposed read-only to verification
  at `:496`. No AppWorld score change or actual AppWorld WAL use is demonstrated
  here; its service/replay lifecycle and database completeness remain unvalidated.

## Is the committed snapshot supposed to retain sidecars?

**Ordinary files on the container writable layer, yes; arbitrary mounted state,
no.** The container-state route stops the whole container before commit at
`eval/containers/container_state.py:190` and `:191`.
`eval/containers/container.py:959` invokes `docker commit` for the whole image;
there is no SQLite filename filter or main-file-only selection there. The fresh
checker is created from that image at `eval/verification/verifier.py:302` with
its identity checked at `:307`. A WAL left after forced process termination is
still required for recovery and should travel alongside the main file in that
writable layer. Stopping a container is not proof of an orderly SQLite close.

This source trace does **not** demonstrate a Docker commit dropping a rootfs WAL.
No Docker command is executed here. New local controls show that explicitly
retaining the sidecars preserves this authored row state and EX. They do not
certify Docker, mounted volumes, atomic database backup, concurrent checkpointing
or production snapshot equivalence. Bind mounts, tmpfs and image-declared volumes
are separate state surfaces: `container.py:861`, `:865` and
`container_state.py:83` expose that distinction. A DB and its WAL on different
surfaces need an explicit complete snapshot contract. Existing inherited-volume
coverage remains open. Moreover, later main-file-only staging or native private
copy can lose sidecars **after** a correct full snapshot.

## Fix and deliberate remaining limits

`data/scaffolds/scorer_input.py:88` now retains the header from the **same bytes**
being copied and hashed. At `:100` a SQLite magic header with WAL read/write
format version 2 raises a binding refusal **before the scoring callback**.
The existing error path writes `measured=false`, `verified=false`, exits 3 and
cleans the private temporary directory. It creates no reward. This recognizes
`.sqlite`, `.db` and renamed inputs without a filename heuristic or any adjacent
file scan. Existing task/digest binding and native verdict enforcement remain.

This is a conservative detection fix, not database recovery or automatic
normalization. A cleanly checkpointed WAL-mode main file and one whose WAL was
already lost have indistinguishable relevant headers. Both must refuse in this
byte-only bound path. The orderly-close case from E5 is still valid as a bounded
logical-state observation; it is not sufficient evidence for this new gate.
The control's explicit external `PRAGMA journal_mode=DELETE` happens only on its
fresh authored scratch DB after closing the writer; production never runs it.
Future support needs a separately authenticated database-aware snapshot/preparation
contract with transaction consistency, selected-only bounds and writer custody.
A merely matching main hash, a close claim or an absent adjacent file cannot supply it.

**Explicit remaining limitation:** the generic `export_state` / `_materialize`
APIs still implement declared byte copying. Their main-only counterexample remains
reproducible, as do manual unbound calls. Extending the allowlist implicitly would
read undeclared actor/private state, alter names/budgets and still fail to prove
an atomic multi-file snapshot. This task therefore records this limit and fixes
the current bound SQLite consumer's unsafe acceptance. It does not claim that the
export checker discovers semantic dependencies or that all consumers reject
incomplete projections. Other sidecar formats, hot rollback journals and
application-specific external files remain outside this WAL-header fix; even a
rollback-mode input needs trustworthy standalone preparation and custody.
AppWorld replay does not use this native binding helper and is not repaired or
certified by it. Dataset blockers and shared next_actions remain open.

## Tests, preserved attempts and validation limits

`tests/quality/test_w_wal.py` checks real bound BIRD refusals on authored live,
main-only copied and closed WAL DBs; filename-independent callback exclusion;
DELETE-mode measured binding; ordinary payload byte integrity and private-copy
cleanup; and the remaining generic export counterexample with its explicit
sidecar-preserving control. The **same final tests**, run before and after the
production edit, change from **6 failed, 3 passed** to **9 passed**:
`baseline-corrected-tests.stdout.txt` and `fixed-tests.stdout.txt`.

The first test attempt is also preserved as `baseline-tests.*`: three
callback-spy cases initially passed for the wrong reason (an incomplete test
inventory was refused). The tests were corrected to supply gold as well, and
rerun **before** the production edit. No early result is substituted for the
corrected baseline.

The related suite records **161 passed, 3 xfailed, 1 failed** in
`related-tests.stdout.txt`. The failure is
`test_complete_packet_including_wal_and_retained_attempts`: E5's immutable source
pins already differ from the starting commit for BIRD and SpreadsheetBench files.
`source-audit-final.stdout.txt` under `INHERITED E5 PIN DRIFT` independently hashes each
pinned file from both **HEAD** and the working tree; the differing files have
identical HEAD/working hashes. This is inherited drift, not a new failure caused
by the changed helper. Frozen pins/tests are neither refreshed nor weakened.
The per-pair E5 checks in that suite still pass. The final focused plus registry/journal
suite reports **68 passed, 3 xfailed** in `final-focused.stdout.txt`.
The first scope-audit attempt used a brittle journal line offset; its assertion
failure is retained in `final-scope-audit.*`, and the corrected heading lookup is
validated separately in `final-scope-audit-corrected.*`.

`tests/fixtures/hg_wwal/verify.py` independently reconciles raw scorer output,
main/sidecar digests, both export receipts, measured/refused classifications,
pre/post rows and scratch cleanup; see `packet-audit.*`.
`reports/w-wal-validation.txt` records exact command receipts and raw test output.
All collection/tests run beneath the existing kernel socket-denial wrapper;
its stderr preserves denial probes, actual interpreter/library hashes, CPU/FD
limits and blocked-external-dataset-read observations. Commands have an outer
150-second deadline. This is offline authored evidence, never a pilot receipt,
benchmark utilization or production authorization.

## Registry observation - w-wal

SQLite WAL loss is reproduced in selected-file export, single-file staging and
native bound private copying; the latter now refuses WAL-format SQLite bytes
before scoring, including previously copied and cleanly checkpointed inputs.
Generic byte projections, other sidecars, mounted-state completeness and AppWorld
replay equivalence remain explicit limitations. E4/E5/E6 remain PARTIAL. Both
shared blockers, every dataset blocker, all next_actions/history and production
authorization remain unchanged. No frozen receipt or `runs/` path is modified.
