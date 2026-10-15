# HotpotQA historical receipt search — w-hotpotrec

**Finding: FOUND, partial recovery; no withdrawal proposed.** The candidate ID
`hotpotqa-h0-10pct-v4` is observed in a transcript of a successful read of
`/tmp/codex/qa-h0-incomplete-index.json`, paired with dataset `hotpotqa`, status
`incomplete`, and run directory `/tmp/harnessgrad-runs/hotpotqa-h0-10pct-v4`.
This is stronger than a guessed filename, but the output does **not** print that
record's completion count. Its independent binding to the journal's 94-trial
report remains **UNKNOWN**. The existing historical record therefore stays
incomplete, `run_id=null`, `effect=null`; the candidate is supplemental evidence,
not an edit to the pinned history. [E:889; registry/dataset-blockers.json:501]

Original files are **ABSENT now in the enumerated scope below**. They cannot be
called “never captured on this machine”: historical command output lists a v4
split, console log, budget ledger, and incomplete index, and reads the index
successfully. “Not published upstream” is **UNKNOWN**, not an absence claim;
no upstream service was queried. Thus the bird/DS-1000 withdrawal wording would
overstate this search. [E:889; E:949; registry/withdrawn-requirements.md:107]

`E` means the checked-in `registry/w-hotpotrec-evidence.json`; `E:889` is a
file:line citation into that file. Commands, verbatim selected output lines,
source transcript paths/lines, inventories and observed output digests are
retained there. The exact commands and outputs of validation are in
`registry/w-hotpotrec-validation.txt`. All original evidence was read-only.

## Recovered evidence and its limits

The source transcripts still exist:

- **T** = `/home/xubuqiang/.codex/sessions/2026/10/12/rollout-2026-10-12T13-19-24-01a12e8d-26bd-7c90-ab31-5ab4e04eaaa8.jsonl`.
- **L** = `/home/xubuqiang/.codex/sessions/2026/10/12/rollout-2026-10-12T13-14-44-01a12e88-df36-7711-a286-2fb124e3416d.jsonl`.
- **S** = `/home/xubuqiang/.codex/sessions/2026/10/12/rollout-2026-10-12T20-22-36-01a13010-98b4-7080-8469-ecc8e991627c.jsonl`.

These aliases designate literal file paths; every following `T:line`, `L:line`
or `S:line` is a source file:line citation, not a new receipt.

| Item | State and exact coverage | Evidence |
|---|---|---|
| v4 candidate ID | **FOUND**: incomplete-index tuple binds dataset/status/directory to `hotpotqa-h0-10pct-v4`. No independently observed 94-trial binding. | T:85; E:889 |
| v4 selected IDs, trial outcomes, error/timeout ledger | **ABSENT** as recoverable original files/content in the enumerated local scope. The v4 listing establishes filenames, not their contents. The 1,179-byte `*-ledger.json` is only a listed budget-ledger candidate; no per-trial contents were recovered. | L:16; E:949; search scope below |
| v5 selected train IDs | **FOUND**: all 492 ordered IDs, 492 unique, decoded from the explicitly v5 `selected meta` JSON. Saved in `registry/w-hotpotrec-v5-train-ids.json`. No question/gold payload or eval-side ID list is exported. These are **not authenticated v4 selections**. | T:102; registry/w-hotpotrec-v5-train-ids.json:4; validation recovery output |
| Split/manifest identity | **FOUND for v5**: `file:/tmp/codex/hotpotqa-10pct-v4-split.json`, observed `split_sha=a0ee939df43c61c0f5354f766515f0751d6d719ff7efac55edec3513fc239936`; train 492 / eval 6913; trials 3, jobs 1, sampling `all`. **UNKNOWN for v4** beyond the listed split filename and byte size. The filename containing v4 does not bind the v5 metadata to the v4 run. | T:119; E:919; L:16 |
| Model/endpoint/harness binding | **FOUND for v5**: model `qwen3.5-9b-local`, backend `openai`, framework `0.1.0`. **UNKNOWN** for v4 model, endpoint, harness identity/hash, and original source revision/content hash. No historical endpoint URL was recovered for either run. A sibling ALFWorld harness hash and today's adapter pin cannot fill those gaps. | T:102; T:119; E:919; registry/w-hotpotrec-v5-train-ids.json:10 |
| v5 event/lifecycle metadata | **FOUND, observation only**: T:129 reports 182 event envelopes, 13 `task` envelopes and no curve; S:73 later prints a snapshot with 214 envelopes, still 13 `task` envelopes, `mutable=true`, no curve, `active_at_snapshot`. These changing aggregate observations are not per-trial outcomes or measured counts. | E:934; E:971 |
| v5 observed artifact hashes | **FOUND in transcript only**: S:73 prints run-meta SHA-256 `85fba1e281b4e1eaf74cb8a99d9c762ad7df70051c9367e18ee8f5b5e443c949` and mutable-event snapshot SHA-256 `c665416e6ed81729d802776f1fa944dec59eefda2ec229196773285b4284d5e2`. Original bytes were not recovered, so neither hash was recomputed/authenticated. | E:989; E:1010 |
| Stop/cleanup reconciliation | **FOUND** only as the journal's user-stopped report. **ABSENT**: an original v4 terminal/cleanup receipt in scope. **UNKNOWN**: actual cleanup completion, original process lifecycle, and whether omitted/deleted/off-machine copies survive. | docs/adapter-integration-journal.md:349; scope below |

Verbatim index output recovered at T:85 (selected output, not an executed new run):

```text
qa-h0-incomplete-index.json records [('bird_minidev', 'bird-minidev-h0-10pct-v4', 'incomplete', '/tmp/harnessgrad-runs/bird-minidev-h0-10pct-v4'), ('fever', 'fever-h0-10pct-v4', 'incomplete', '/tmp/harnessgrad-runs/fever-h0-10pct-v4'), ('hotpotqa', 'hotpotqa-h0-10pct-v4', 'incomplete', '/tmp/harnessgrad-runs/hotpotqa-h0-10pct-v4')]
```

Verbatim v4-related listing lines recovered at L:16:

```text
-rw-rw-r--    1 xubuqiang xubuqiang  235885 Oct 12 10:33 hotpotqa-10pct-v4-split.json
-rw-rw-r--    1 xubuqiang xubuqiang     290 Oct 12 10:40 hotpotqa-h0-10pct-v4-console.log
-rw-------    1 xubuqiang xubuqiang    1179 Oct 12 10:34 hotpotqa-h0-10pct-v4-ledger.json
-rw-rw-r--    1 xubuqiang xubuqiang    6417 Oct 12 11:02 qa-h0-incomplete-index.json
```

## Enumerated local scope and reproducible search

The assigned worktree's `runs/`, `runs_discarded_20260929-004559/` and
`.harnessgrad-state/` do not exist. Those three directories in the main checkout
were searched read-only. The exact regular-file inventory is external scratch
`/mnt/20t/xubuqiang/hg-work/hotpotrec/evidence/filesystem-files.json`, with its
observed digest in E:789. The inventory generator and search are committed as
`registry/w-hotpotrec-search.py`; they write only assigned scratch. [validation
path-existence output; E:5; E:789]

The following resolved roots were recursively enumerated, including hidden and
ignored regular files. File counts exclude the explicitly pruned paths described
after the table; there were zero inventory errors. [E:5]

| Absolute root | Regular files |
|---|---:|
| `/mnt/20t/xubuqiang/Study/HarnessGrad/runs` | 11886 |
| `/mnt/20t/xubuqiang/Study/HarnessGrad/runs_discarded_20260929-004559` | 953 |
| `/mnt/20t/xubuqiang/Study/HarnessGrad/.harnessgrad-state` | 3 |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive` | 168 |
| `/mnt/20t/xubuqiang/Study/hg-backup-20261014` | 5 |
| `/mnt/20t/xubuqiang/Study/hg-backup-20261014-pre-rewrite` | 1 |
| `/mnt/20t/xubuqiang/Study/hg-logs` | 6 |
| `/mnt/20t/xubuqiang/harnessgrad_work` | 31 |
| `/mnt/20t/xubuqiang/Study/harnessgrad_work` | 1535 |
| `/mnt/20t/xubuqiang/Study/harnessgrad_cli` | 1 |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-real-work-20261117` | 4 |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-real-work-20261117c` | 5 |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-appworld-controls-20261117` | 770 |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-gaia-controls-20261117` | 899 |
| `/mnt/20t/xubuqiang/hg-census` | 64859 |

Total observed inventory: 81,126 regular files. Content screening used `rg -l -i
--null 'hotpot(?:qa)?|1,?476|1,?382' -- <enumerated files>` in batches of 300:
1,149 matching files, no stderr/errors (113 batches exit 0, 158 exit 1). Narrowing
to the Hotpot token leaves 33 files: source/test/journal mentions, an unrelated
MTEB trace, and a later source-inventory hash, not the historical Hotpot ledger.
Filename screening of all 81,126 paths for `hotpot|qa-h0|h0-10pct` finds only the
two frozen-copy adapter filenames. [E:630; E:643; validation filesystem-narrowing
output]

Raw `.git` directories and the two backup `dot-git` directories were pruned from
filesystem content screening and inspected separately with Git, below. Nested
run-workspace `.git` stores, symlink targets, and named refused dataset directories
were excluded; exact exclusions are in scratch `inventory.txt` (digest in E).
Nested Git-object contents are **UNKNOWN**, not covered by the absence claim.
No arbitrary size cutoff was used for regular files or scanned blobs.
[registry/w-hotpotrec-search.py:28; E:5; E:799]

Git scope was the assigned worktree's shared object database and **all observed
137 local branches**, not the task's anticipated 129. Branch names and exact
observed tips are enumerated at E:646. Commands were:

```text
git for-each-ref --format=%(refname:short) %(objectname) refs/heads
git log --all --format=%H %s
git log --all --format=%H %s --pickaxe-all -S<TOKEN> -- :(exclude)data/datasets/api_bank/** :(exclude)data/datasets/nestful/** :(exclude)data/datasets/sotuqa/** :(exclude)data/datasets/tau2_bench/**
git stash list
git reflog --all --format=%H %gs
git cat-file --batch-all-objects --batch-check
git rev-list --objects --all
```

Tokens were literally `hotpot`, `hotpotqa`, `492`, `1476`, `1382`, `94/`, `v4`.
Exact argument arrays, exit codes, raw-output counts/digests are in E:116.
Observed: 718 log entries; pickaxe results 163/132/234/104/106/86/169 entries in
that token order; empty stash output; 109 reflog entries; 23,773 objects including
unreachable objects. These are search counts, not benchmark coverage. [E:116]

The four additional Git stores were enumerated with `for-each-ref`, `log --all`,
`rev-list --objects --all`, and `cat-file --batch-all-objects --batch-check`:

```text
/mnt/20t/xubuqiang/Study/hg-backup-20261014/dot-git
/mnt/20t/xubuqiang/Study/hg-backup-20261014-pre-rewrite/dot-git
/mnt/20t/xubuqiang/Study/HarnessGrad-appworld-controls-20261117/.git
/mnt/20t/xubuqiang/Study/HarnessGrad-gaia-controls-20261117/.git
```

Their observed object counts were 4208/4361/2707/4307. Blob contents were streamed
through `git cat-file --batch`, deduplicated by object ID across stores, and
screened for case-insensitive `hotpot(?:qa)?`; eligible unique blob counts were
17479/318/21/235/22 for shared/backup/backup-pre/frozen-AppWorld/frozen-GAIA,
with 944/65/8/0/1 matching blobs respectively. All five batch processes exited
0. No `hotpotqa-h0`, `hotpotqa-10pct-v4` or `qa-h0-incomplete-index` string was
found in these Hotpot-containing blob lines. No original v4 trial ledger was
recovered. Refused-path blobs were excluded and are outside this claim.
[E:348; E:586; validation object narrowing output]

Transcript scope was all recursively enumerated
`/home/xubuqiang/.codex/sessions/**/*.jsonl`, plus
`/home/xubuqiang/.codex/history.jsonl` and `/home/xubuqiang/.bash_history`: 734
files / 3,054,290,948 observed bytes at inventory time. The same content regex
matched 499 files; all three batches exited 0 without stderr. Original execution
outputs were distinguished from repeated journal reads and this worker's own
transcript. Only cited historical execution output supports the recovery.
History/bash exact Hotpot/run-root/index search returned no lines, exit 1.
[E:112; E:637; validation history search output]

Adaptive existence checks also covered `/tmp/codex`, `/tmp/harnessgrad-runs`,
the archive's exact cited `codex/qa-h0-incomplete-index.json`, and the listed
Hotpot/QA glob paths. They are currently absent (exact commands/output in
validation). This is read-only inspection of `/tmp`, with no scratch writes
there. The parent may reproduce the full search with:

```bash
export TMPDIR=/mnt/20t/xubuqiang/hg-work/hotpotrec/tmp
python3 registry/w-hotpotrec-search.py inventory
python3 registry/w-hotpotrec-search.py filesystem
python3 registry/w-hotpotrec-search.py transcripts
python3 registry/w-hotpotrec-search.py git
python3 registry/w-hotpotrec-search.py gitstores
python3 registry/w-hotpotrec-search.py blobs
python3 registry/w-hotpotrec-search.py executions
python3 registry/w-hotpotrec-search.py recover
```

Inventories and Git refs are mutable; a later search must record its own output,
not silently substitute it for the observed counts here.

## Residual and arithmetic

**FOUND:** an incomplete v4 candidate ID/index tuple; historical filename/size
listings; a separately bound v5 train ID list, model/split metadata and lifecycle
aggregate observations. [E:877; registry/w-hotpotrec-v5-train-ids.json:4]

**ABSENT in the enumerated local scope:** current original v4 selected-ID
manifest, per-trial outcomes and error/timeout ledger, original source/model/
endpoint/harness provenance, terminal/cleanup receipt, and the exact journal-cited
incomplete-index file. This describes recoverability now, not proof that they
never existed. [Scope and exact outputs above; validation existence output]

**UNKNOWN:** authentic binding of the v4 candidate to the 94 report; v4 measured/
invalid/unmeasured and unique-task/trial/error counts; historical cleanup;
contents of excluded nested Git stores/symlink targets/refused locations; deleted
or off-machine copies; upstream publication. No machine-wide completeness or
“never captured” assertion is made. [T:85 prints only a tuple; explicit scope
exclusions above]

No v4 per-trial ledger was found. **The reported 94 / 1382 / 1476 values are not
recomputed or independently certified.** The 492 recovered IDs belong to v5 and
cannot reconcile v4. Preserve the journal/registry report as stated, including
incomplete status and `effect=null`. The 3600-second verifier limit and 60-minute
note remain configuration/anecdote, not measured timeout counts. Synthetic
timeout classification/persistence/aggregation closure is unchanged.
[registry/dataset-blockers.json:458; docs/adapter-integration-journal.md:350;
tests/quality/test_hotpot_timeout_admission_w_hotpot.py:1]

The proposal's `outcome=found` means **partial historical metadata recovery**, not
measurement admission or full blocker closure. `withdrawal_entry=null` prevents
an unsupported never-captured/not-published withdrawal. Keep current selected
scorer/control admission as the actionable residual; historical missing originals
remain an explicit comparability limit. No shared withdrawn gate is reinstated.
[registry/proposals/w-hotpotrec.json:1; registry/withdrawn-requirements.md:17;
registry/withdrawn-requirements.md:44]

**Validation limitation:** the required checker failed on the untouched baseline
with `{"valid": false, "error": "bfcl_v3: missing evidence tests/fixtures/hg_bfcl/README.md"}`.
No registry, journal, fixture, historical run or main working-tree file was edited.
The parent must resolve that independent baseline problem; this worker does not
claim a passing checker. [registry/w-hotpotrec-validation.txt]
