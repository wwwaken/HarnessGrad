# w-2wiki public documentation custody

Acquired 2026-10-14 UTC / 2026-10-15 Asia/Shanghai in registered worktree
`/tmp/hg-2wiki`, starting commit `2c82417955798e6f00474bcbf49a80c4811d8df1`.
Four documentation requests produced five HTTP response hops. Raw entities,
parsed response-header serializations and URL/status/time receipts are retained
unchanged. SHA256SUMS covers every fixture file except itself. `evidence.json`
contains recomputed byte identities, inherited input pins and derived findings.

The original Dropbox URL returns a disabled-link HTML error page. No dataset
archive or dataset file was requested or acquired. The PDF is the publisher's
paper; its SHA-256 is a paper digest, never a data-archive digest. The mirror card
is documentation (including its own example); its example is not used as a row
binding or a task. `LICENSE.decoded` is losslessly decoded from the GitHub raw
API entity, and `extracted.txt` is derived with `pdftotext -layout` from the PDF.
The originals remain authoritative.

Normal TLS certificate validation was used through canonical
`HG_EGRESS_PROXY=http://172.17.0.1:17890`. No credentials, paid service, model,
GPU, endpoint, benchmark, dataset conversion or scorer execution was involved.
HTTPS origin custody and matching Git blob identities are reproducible; no
publisher signature is asserted. `main` in the license URL is a mutable query,
whose returned immutable blob identity and acquired bytes are recorded.

Acquisition is append-only and refuses an existing attempt directory:

```sh
HG_EGRESS_PROXY=http://172.17.0.1:17890 python3 tests/fixtures/hg_2wiki/acquire.py
```

Do not run that command over these saved attempts. A future acquisition must use
a new directory/name and retain this evidence. Offline verification:

```sh
python3 tests/fixtures/hg_2wiki/verify.py
(cd tests/fixtures/hg_2wiki && sha256sum -c SHA256SUMS)
python3 tools/check_dataset_blockers.py
```

The verifier checks every acquired body/header, license decoding/Git identity,
card Git identity against the existing exact-revision canonical Hub response,
paper text extraction/counts, conflicting mirror counts, inherited selected-ID
list hashes and narrowly scoped registry/journal edits. It reads repository
source and prior metadata only, never dataset files, runs/ or frozen originals.

`hub-data-provenance` remains **external** for missing substantive evidence.
No human or custodian approval gate is imposed. See
`reports/w-2wiki-review.md` for findings and file+line references and
`reports/w-2wiki-validation.txt` for exact validation commands and output.
