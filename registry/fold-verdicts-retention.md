# Decision 5 — make the fold scripts keep `verdicts/`, for future folds only

Parent record, 2026-10-16. Implements the operator's decision 5 (goal item 21). **No external script was
edited:** the patch is written here, verified against copies, and handed to the operator. The scripts live
outside this repository at
`/mnt/20t/xubuqiang/HarnessGrad_experiments_result/<dataset>/loop_qwen3.5-9b-local/`, are under **no**
version control (`git`/`hg`/`svn` markers absent through every ancestor), and their ownership is not
established — so applying it is the operator's call.

## What is already lost, and what this fixes

**The four existing archives keep zero verdict files, and this patch cannot bring them back.** Parent-run:
all four trees contain **0** files with a `verdicts` path component. `hg-census/runs/` is only a *partial*
substitute — three AgentDojo fold sources are absent at the exact census paths and four further source runs
retain zero verdicts. This change helps **future folds only**.

## The mechanism, demonstrated rather than asserted

Synthetic harness, three fake source runs, each with one `verdicts/<task>-verdict.json` plus the usual
`progress/round-0` record, trace and `curve.jsonl`. Both scripts were run from a copy in `/tmp`; **the real
directories were never touched.**

| | pipeline | files in `full/` | verdict files in `full/` |
| --- | --- | ---: | ---: |
| **before** (shipped scripts) | `fold_runs.py` → `fold_to_full.py`, rc=0 | 10 | **0** |
| **after** (patched scripts) | same, rc=0 | 13 | **3** |

The surviving verdicts land correctly namespaced by their **original run id**, which is what makes them
attributable afterwards:

```
full/verdicts/agentdojo-qwen-t1-train4/rec1-verdict.json
full/verdicts/agentdojo-qwen-t1-train4-retry/rec2-verdict.json
full/verdicts/agentdojo-qwen-t1-eval4/rec3-verdict.json
```

Content is preserved byte-for-byte, and **nothing else changed**: `progress/round-0` records and traces,
the per-run `curve.<run-id>.jsonl` metadata and `MERGE.md` are identical in both runs (10 files before, the
same 10 plus 3 verdicts after). So this is not a rewrite of the folding rule, only a rescue of the class of
file it used to discard.

## The patch

`registry/fold-verdicts-retention.patch` — 7 files, 9,058 bytes. It inserts one block immediately before
each `shutil.rmtree(src, ignore_errors=True)`, which is the single point where the bytes are destroyed.
Two variants, because the two stages hold different things:

* `fold_runs.py` (stage 1) moves `src/verdicts/**` to `target/verdicts/<run_id>/**`;
* `fold_to_full.py` (stage 2) carries `src/verdicts/<run_id>/**` through unchanged, preserving the inner
  namespace rather than re-namespacing or flattening it.

Both refuse to overwrite: a destination that already exists raises `SystemExit` naming the path, so a
collision is loud instead of silent. `gsm8k/fold_to_full.py` **does not exist** at the exact requested path
(`gsm8k/fold_runs.py` does), so the patch covers 7 of the 8 possible files.

Verified before handing it over: `patch -p1 --dry-run` and a real `patch -p1` apply cleanly to copies of
all 7; every patched file passes `python3 -m py_compile`; and each patched file has `src_verdicts` assigned.
The anchor appears **exactly once** in every one of the 7, which is why a plain textual insert is safe.

Apply (operator):

```bash
cd /mnt/20t/xubuqiang/HarnessGrad_experiments_result
patch -p1 < /mnt/20t/xubuqiang/Study/HarnessGrad/registry/fold-verdicts-retention.patch
```

**Put the patched scripts under version control at the same time.** A fix that lives only in a file no VCS
tracks is exactly as fragile as the evidence it is meant to protect — this repository has already lost
evidence to a gitignore rule (`/docs/*`, which silently covers the fidelity handoff and several decision
documents), and here the fold scripts' own history is unavailable for the same reason, which is why the
destruction mechanism had to be inferred from the current file rather than from a diff. (An earlier version
of this sentence cited 47 untracked B5 bodies; those are payload by policy, not a gitignore accident, and
`registry/known-red-tests.md` records the correction.)

## What this does not do

* It does **not** restore any destroyed verdict. Nothing can; the bytes are gone from every enumerated
  scope, and running either script again on an existing archive is explicitly not authorized.
* It does **not** add the stronger guard the archive review proposed — refusing source deletion when a
  selected evidence move or the inventory verification fails. This patch preserves the verdicts; it does
  not make the rest of the deletion conditional. If that guard is wanted it is a separate, larger change to
  the same two functions.
* It does **not** parse, relabel or rescore anything. Verdicts are moved as bytes, so their original
  instrument stays attached to them.
* The measurement above uses a **synthetic** 3-run harness, not the real 134-row ALFWorld or 2,417-row
  MuSiQue runs. It establishes the mechanism and the no-regression property, not the real archives' future
  behaviour.

*Unverified:* whether these script versions are the ones that produced the existing archives — the
histories are not available, so the versions in place now are the only ones that can be reviewed, and the
patch is against those.
