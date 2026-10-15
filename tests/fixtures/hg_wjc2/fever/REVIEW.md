# FEVER original-ID and evidence-group correspondence — w-jc2

The installed export now has independently checked original-claim and individual
complete-group correspondence. Its producing conversion revision remains unbound;
FEVER and both shared blockers stay open. This is a read-only provenance audit,
without selected manifest, run ID, scorer/model execution or endpoint access.

## What moved

The public FEVER download page identifies `shared_task_dev.jsonl` as the labelled
development release (`tests/fixtures/hg_wjc2/fever/fever-download-page.lines.jsonl:218`)
and publishes the Zenodo mirror URL
(`tests/fixtures/hg_wjc2/fever/fever-download-page.lines.jsonl:60`). Both downloads returned
HTTP 200 and byte-identical bodies. Recomputed original SHA-256 is
`e89865bfe1b4dd054e03dd57d7241a6fde24862905f31117cf0cd719f7c78df7`;
recomputed MD5 `4eecc1018b3d2bd46089ca36d886f439` matches Zenodo's received checksum
header (`tests/fixtures/hg_wjc2/fever/observations.json:7`,
`tests/fixtures/hg_wjc2/fever/original-zenodo.receipt.json:15`). Full original bodies
are preserved losslessly as `.body.gz`, with URL/status/headers and body/gzip hashes
in the corresponding receipts; no mutable URL alone is treated as a revision pin.

Actual installed `valid.jsonl` remains SHA-256
`5da0ccc0ccf77f974611de13f8aac6f78c6bba6293912835099eb6029baa85d9`,
Git blob SHA-1 `ae61c5b6cb11eafcc7d6c33069c68dd5c848f91f`
(`tests/fixtures/hg_wjc2/fever/observations.json:5`). All 15,935 rows carry
`original_id`, all map to the public original release, and all claim/label/verifiable
values agree. They represent 9,835 distinct original claims. All 9,525 non-NEI rows
match one complete original evidence group in both pair order and pair-set content,
after NFC page normalization and integer line conversion
(`tests/fixtures/hg_wjc2/fever/observations.json:11`). The 6,410 NEI rows match original
claims/labels, while their retrieved sentences are not original NEI gold evidence.
No original Wikipedia sentence-text authenticity is inferred from pair identity.

Every row's installed line/export ID/original ID/original line, canonical parsed-row
digests and matching original-group indices are retained in
`row-correspondence.jsonl.gz`; its decompressed SHA-256 is
`aaea48decd7e67f10b7db4512cf9b15f32ee9f49c338c6dd1a187f78097daf55`
(`tests/fixtures/hg_wjc2/fever/observations.json:32`). Canonical row encoding is
UTF-8 JSON with sorted keys, no ASCII escaping, compact separators and no NaN.
Raw installed/original sample lines and their complete-file hashes are preserved
in `tests/fixtures/hg_wjc2/fever/source-examples.jsonl:1`.

Producer-side corroboration also moved: the repository collaborator's issue reply
explicitly points to the Hub dataset
(`tests/fixtures/hg_wjc2/fever/producer-issue5-comments.body:1`), and the revision-pinned
README documents gold-group extraction, Papelo NEI retrieval and merging
(`tests/fixtures/hg_wjc2/fever/producer-readme.lines.jsonl:36`). Freshly fetched README,
merge and NEI bytes recompute to the preserved authenticated Git-tree blobs at
`aaa126ec4f3cf7163f69b82a0a0976d2579a04a6`
(`tests/fixtures/hg_wjc2/fever/observations.json:40`). Their recomputed SHA-256 values
are respectively `374052abccfd55c67e5d1a94f3c05b82de4426f2ce1c5e9efdd9c5daa7164a34`,
`960f0540bb4c1e1c80027c88f256906b3c5d2124d5629e1fea0fdd7f32e36cfd`, and
`cf9d2d241577666b8cd7a52d041d3b09863d24dce8c503e3ce98c36f471a69fd`.

## What did not move

Complete-group correspondence of each exported row does not establish preservation
of all alternative original groups or local strict-score equivalence. Among 6,551
represented non-NEI original IDs, 51 distinct original groups from 42 IDs do not
appear in the installed validation export
(`tests/fixtures/hg_wjc2/fever/observations.json:26`). This says nothing about their
presence in uninspected Hub splits or the producer's intended partition/filter.

There are 1,400 multisentence non-NEI export rows. In 1,395 rows, at least one export
sentence alone satisfies no complete original group; there are 3,046 such singleton
occurrences (`tests/fixtures/hg_wjc2/fever/observations.json:20`). For example, installed
line 20/original ID 10947 contains `[Fist_of_Legend,2]` plus `[Fist_of_Fury,0]`; the latter
alone is insufficient under every original group
(`tests/fixtures/hg_wjc2/fever/examples.json:3`). Local code still promotes each flat
sentence to an independently sufficient singleton at
`data/scaffolds/qa/evidence_scorers.py:161`, whose fresh SHA-256 is
`a962f23e0c0f704b31294902ddaae3facee0e7496dfc43041bf973a912043729`
(`tests/fixtures/hg_wjc2/fever/observations.json:36`). These are structural predicate
counterexamples from actual installed rows, not observed scorer returns or task scores.

The inspected pinned scripts do not authenticate the exact Hub-producing revision,
UUID-style export-ID assignment, added `original_id`, line-string conversion or
validation partition/filter. The merge script additionally expects an `annotation`
field (`tests/fixtures/hg_wjc2/fever/producer-merge.body:24`); the inspected extraction
script preserves original fields (`tests/fixtures/hg_e1_review/fever-create-nli-dataset.py:72`).
A repository-to-Hub link is corroboration, not a conversion receipt. Hub commit-history
GETs failed twice with preserved TLS EOF errors
(`tests/fixtures/hg_wjc2/fever/hub-commits-retry.receipt.json:8`); the issue GET initially
failed and its retry succeeded. This bounded source search cannot prove that a producing
record does not exist elsewhere.

## Single remaining input to this next-action closure

Obtain the producer-authenticated conversion receipt for the exact bound
`valid.jsonl` blob: executable conversion/export revision and input pins, ID/group
mapping, and declared split/filter/omission rules accounting for the 51 absent
alternative groups and NEI retrieval inputs. This missing upstream record is now
precise; merely another full-pool inventory or an invented selection cannot supply it.
The independently recomputed mapping here advances correspondence, but does not
satisfy the producing-record clause or prove complete-group metric preservation.
Selection/export, chosen run split/side, pristine execution and shared admission
evidence remain separate later requirements. No closure or diagnostic authorization.

## Validation

`python3 tests/fixtures/hg_wjc2/fever/audit.py --check` is read-only: it recomputes all
download/checksum, row/group, producer-blob and source-digest observations and compares
the exact derived files. Its stdout/stderr are preserved in `reproduction.*.txt`;
initial generation stdout/stderr are `audit.*.txt`. Acquisition commands' exact bodies,
URL/status/time/transport/headers/error and raw stdout/stderr are preserved per name.
Before/after registry checks are in `registry-before.stdout.txt` and
`registry-after.stdout.txt`; both remain valid with production authorization false.
Registry, journal, production code, runs and frozen receipts are unchanged here.
Two upstream source bodies contain original trailing whitespace; their exact bytes
remain in gzip and their line preimages are losslessly JSON-quoted in `.lines.jsonl`
(including line terminators). The initial staged-whitespace failure is retained in
`whitespace-initial.json`; no fetched source bytes were cleaned or overwritten.
