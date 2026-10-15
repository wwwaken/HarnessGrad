# Fold/archive finding — w-evidence

2026-10-16, read-only inventory. **FOUND:** the four existing archives contain zero verdict files. Both fold stages move selected progress records/traces and per-run curve/events/run_meta, then recursively delete their source directory; verdicts are never selected. That destroys the archive-side verdict bytes rather than leaving them in an unfurled directory. A future retention fix cannot recreate those deleted bytes. **UNKNOWN:** globally permanent loss or recovery from unsearched backups; the census originals are useful but are not a complete recovery source.

Exact inventory commands/code and output are reproduced in `registry/w-evidence-validation.txt`; machine observations are `registry/w-evidence-archive-observed.json:1` and exact fold-source reconciliation is `registry/w-evidence-archive-sources.json:1`. “Verdict files” means regular files with a `verdicts` path component; “records/traces” below means .json/.jsonl regular files under progress, not unique successful measured trials. Counts do not certify score coverage. File bytes were statted, not all payloads read.

## Existing archive contents

Enumerated scope is each complete `/mnt/20t/xubuqiang/HarnessGrad_experiments_result/<dataset>/loop_qwen3.5-9b-local` tree, recursively (all four dataset directories present at that root). Other files include scripts, summaries and metadata.

| dataset | regular files | progress .json records | progress .jsonl traces | other files | verdict directories/files | logical bytes |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| agentdojo | 1914 | 949 | 949 | 16 | 0/0 | 22670809001 |
| alfworld | 282 | 134 | 134 | 14 | 0/0 | 2921612 |
| gsm8k | 35184 | 8792 | 26376 | 16 | 0/0 | 30614422 |
| musique | 4903 | 2417 | 2466 | 20 | 0/0 | 261404153 |

## Scripts and exact deletion sites

All paths below are external to this Git worktree. Whole script source snapshots and observed SHA-256/byte sizes are retained at `registry/w-evidence-external-sources.md:1`; the hash is of the script read here, not a claimed execution version.

| dataset | script base directory | fold_runs selection → deletion | fold_to_full selection → deletion |
| --- | --- | --- | --- |
| agentdojo | `/mnt/20t/xubuqiang/HarnessGrad_experiments_result/agentdojo/loop_qwen3.5-9b-local/` | `fold_runs.py:49-75 → 76` | `fold_to_full.py:56-79 → 81` |
| alfworld | `/mnt/20t/xubuqiang/HarnessGrad_experiments_result/alfworld/loop_qwen3.5-9b-local/` | `fold_runs.py:49-75 → 76` | `fold_to_full.py:56-79 → 81` |
| gsm8k | `/mnt/20t/xubuqiang/HarnessGrad_experiments_result/gsm8k/loop_qwen3.5-9b-local/` | `fold_runs.py:50-76 → 77` | `fold_to_full.py:ABSENT at the exact requested path` |
| musique | `/mnt/20t/xubuqiang/HarnessGrad_experiments_result/musique/loop_qwen3.5-9b-local/` | `fold_runs.py:51-77 → 78` | `fold_to_full.py:55-78 → 80` |

The first pass retains only progress/round-0 traces (.jsonl), progress records (.json excluding traces), and three run metadata names. The full-pool pass selects the same progress classes plus metadata. Both delete the rest with shutil.rmtree. The current existence of source-deleting code proves the loss mechanism and present inventories prove no archived verdicts; original execution provenance and exact deletion time are UNKNOWN. No script was run or edited here.

**Version control:** `git -C <each script directory> rev-parse --show-toplevel` returns exit 128 for all four, empty stdout and the exact “not a git repository” stderr retained in the observation JSON/validation. All directory ancestors through `/` were also checked for `.git`, `.hg`, `.svn`: zero markers (`registry/w-evidence-archive-sources.json:1`). Thus no in-place Git/Mercurial/Subversion working-copy custody is observed; no tracked copy in an unrelated repository, prior versions, remote repo, or other VCS is claimed absent. The worktree’s tracked-path check returns no external fold script (validation). They are not HarnessGrad repository code under the observed paths.

## What survives, and what does not

The census root had 35 direct run directories at initial observation and 43 during validation replay; other workers can add runs, while all four archive inventories and the dataset-prefix original-run observations remained identical (`registry/w-evidence-archive-observed.json`, original_run_directory_count). The source-name comparison below is against exactly the literal SIDES list in each fold_runs.py and exact same run basename under `/mnt/20t/xubuqiang/hg-census/runs/`. Repeated SIDES source paths are deduplicated. An absent directory is not an assertion that its verdict count was once zero.

| dataset | fold source basename | census directory | census verdict files |
| --- | --- | --- | ---: |
| agentdojo | `agentdojo-qwen-t1-train4` | ABSENT in exact census path | not observable |
| agentdojo | `agentdojo-qwen-t1-train4-retry` | ABSENT in exact census path | not observable |
| agentdojo | `agentdojo-qwen-t1-eval4` | ABSENT in exact census path | not observable |
| alfworld | `alfworld-qwen-t1-train2` | FOUND | 81 |
| alfworld | `alfworld-qwen-t1-eval2` | FOUND | 53 |
| gsm8k | `gsm8k-qwen-t3-train-full` | FOUND | 0 |
| gsm8k | `gsm8k-qwen-t3-train-resume-4367` | FOUND | 3106 |
| gsm8k | `gsm8k-qwen-t3-eval-full` | FOUND | 1319 |
| musique | `musique-full-qwen-t1-train` | FOUND | 0 |
| musique | `musique-full-qwen-t1-train-resume-915` | FOUND | 712 |
| musique | `musique-full-qwen-t1-eval` | FOUND | 0 |
| musique | `musique-full-qwen-t1-eval-resume-191` | FOUND | 0 |
| musique | `musique-full-qwen-t1-eval-last1` | FOUND | 1 |

Every enumerated original source directory is absent from its former archive-side path. ALFWorld’s exact two source runs retain 81+53 verdict files in the census. GSM8K’s original train-full has progress but zero verdicts, while its resume/eval retain 3106/1319. MuSiQue train/eval/eval-resume retain progress but zero verdicts; train-resume/last1 retain 712/1. The three AgentDojo train4/eval4 source runs are absent at the exact census paths; older train3/probe runs do have verdicts but must not substitute for those runs (`registry/w-evidence-archive-observed.json`, original_runs). These discrepancies defeat a blanket claim that the census can restore all archived verdicts.

**Copying boundary:** the handoff says the backup was made by copying (`/mnt/20t/xubuqiang/Study/HarnessGrad/docs/paper-fidelity-audit-handoff.md:367-368`). The two locations coexist and 2417 MuSiQue source progress records match archive peers byte-for-byte at distinct device/inode pairs; ALFWorld has 135 matches (including a repeated-version overlap), AgentDojo three older-run matches (`registry/w-evidence-archive-observed.json`, copy_correspondence). These are evidence of distinct surviving copies, not a recovered cp command or a complete copy-execution receipt. The initial GSM8K peer matcher used only one directory level and found no peers; that zero is a scope limitation, not evidence of differing GSM8K bytes. **UNKNOWN:** copy command/time/process identity, full backup completeness and original verdicts for the explicitly missing runs. Do not claim all original receipts survived merely because some did.

Progress summaries/traces survive for the recorded counts and may permit some future output recovery. A surviving scalar score does not reconstruct verifier component scores, budgets, invalid reasons, replay steps or a deleted official verdict. This review does not parse/rescore submissions and does not certify rescore eligibility per task.

## Minimal future change (proposal only)

Before either rmtree, preserve the complete verdicts tree in a run-namespaced path such as `verdicts/<original-run-id>/...`; copy bytes without parsing/relabeling the receipts. Carry that namespace unchanged through fold_to_full, detect collisions instead of silently overwriting, and refuse source deletion if any selected evidence move/copy or inventory verification fails. Preserve a source→destination inventory with byte hashes, sizes and counts before destructive cleanup. Keep per-trial distinctions; the driver itself notes that some on-disk records represent only the last trial (`eval/run/runner.py:1350-1354`), so folder retention alone does not create missing historical trial verdicts.

This helps **future folds only**. Do not rerun either script on the existing archives, create an old run id, manufacture missing verdicts from progress, or overwrite frozen records. Any recovery should be a separately named provenance-bound evidence supplement drawn only from verified surviving originals. The external scripts’ ownership is not established; no edits are made or authorized here. The parent/operator should put the reviewed script versions under explicit version control before another fold.
