# Journal coverage clause audit — w-journalcov

This packet contains inert default-path byte/row/source observations, not a run
selection, selected-only export, benchmark score or admission receipt. No adapter,
upstream scorer, generator, model, endpoint, container or server was executed.
External dataset bytes were read only; no runs/ or frozen receipts were modified.

`registry-before.json` preserves the starting six next_actions and shared records.
`observations.json` records all missing run/selection/split-side/trial fields as
null. `<dataset>-inventory.json` preserves every ordered parsed-row digest, task ID
and imposed side; it never declares that inventory to be an authorized selection.
SpreadsheetBench additionally pins each init/golden path and archive member.
FEVER retains its installed SHA-256 and independently recomputed Git blob SHA-1
comparison to the E1 authenticated revision/tree metadata. Original evidence-group
correspondence is explicitly false/unknown, never inferred from blob equality.

`file-hashes.json` records every directly read file's size and recomputed SHA-256.
`independent-sha256sum.stdout.txt` independently hashes those same paths with the
actual sha256sum command and retains raw output; its command JSON has exact argv.
`source-lines.txt` preserves numbered current source as lossless JSON-quoted lines
and whole-file hashes; quoting keeps empty/trailing source whitespace intact.
`prior-file-hashes.json` and `prior-sha256sum.stdout.txt` pin additional historical
evidence cited in the review. No expected answers or workbook payloads are copied
into this new packet; inventories contain content digests only.

Commands numbered 0–5 retain argv, exits, stdout and stderr. Command 0 failed on a
fixture path typo before reading datasets; command 4 failed on an AST f-string
literal before producing final output. Command 5 is the successful complete audit;
commands 1–3 recheck old row/split and ReWOO/Reasoning Gym provenance packets.
These are fixture failures, not scorer results. E1 integrity passes separately.

The inherited w-prov root verifier refuses a changed current qa/base.py. Its
preserved source snapshots still pin historical bytes; the new audit independently
binds current source. The inherited w-offscorer2 root verifier fails at missing
bird_ds/SHA256SUMS, and its spreadsheetbench subpacket is absent. Preserve these
limitations: historical report claims are not freshly replayed/fully validated
production scorer execution. The ReWOO/Reasoning Gym subpacket and row/split checks
pass separately. No historical artifact is repaired, overwritten or resumed.

Reproduce read-only current observations and enforce the allowed registry delta:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_wjournalcov/audit.py --check
sha256sum -c tests/fixtures/hg_wjournalcov/SHA256SUMS
python3 tools/check_dataset_blockers.py
```

The SHA256SUMS paths are repository-relative. It covers this packet except itself
and Python caches. The audit --check also needs the unchanged external installed
files; its output is preserved in the report validation log. Cold copying this
packet does not provision an offline scorer runtime. Complete validation commands,
raw output and expected historical validation failures are recorded in
reports/w-journalcov-validation.txt.
