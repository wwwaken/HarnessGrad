# E1 evidence packet

Only FEVER, Physics Questions and Bird MiniDev are reviewed here. Original
registry records and exact next actions are in `starting-gates.json`.

`acquire.py NAME URL` preserves one request's response body and receipt. It
refuses to overwrite an existing receipt. HTTP/transport failures are recorded;
its process exit code alone is not an acquisition-success assertion. Inspect
`status` and `error`. An empty-body digest on a failed request is not a digest
of the requested remote artifact.

The optional third argument is the existing documented public egress proxy
`http://127.0.0.1:17891`. Receipts record that route. Direct failures remain
preserved when this route succeeds. No system network configuration is changed.

Successful immutable GitHub contents responses are decoded into the matching
source files. Both response bytes and decoded bytes remain checked in. The
declared ReWOO archive is preserved in full; only its Physics CSV is extracted.
No acquired code or other benchmark data is executed.

`bird-search.json` binds the raw repository search to base commit `13fa17c`.
It does not inspect the external archive cited by the journal or certify a
complete inventory of ignored runtime files.

`SHA256SUMS` covers all other packet files. Run the offline custody and ordered
content-linkage checks from the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_e1_review/verify.py
```

Results and the cited established/open/status review are in
`reports/e1-evidence-verification.json` and
`reports/e1-fever-physics-bird-review.md`. The packet establishes no installed
dataset, selected manifest, offline/pristine runtime or measured run coverage.
