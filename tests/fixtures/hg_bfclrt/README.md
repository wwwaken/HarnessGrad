# w-bfclrt evidence packet

Entry point: `registry/w-bfclrt-custody.md`. Each JSONL line is one observed
record, and can be cited as `path:line`. `summary.jsonl:1` states the observed
counts and deliberately keeps `closure_complete=false`,
`official_scorer_executed=false`, and `production_authorized=false`.

This packet contains text only: inventories, hashes, original source locations,
verbatim license/notice copies and inspection/import output. Package archives,
ELF bytes, dataset payloads and the scratch symlink projection are not copied
into git. The inspection scripts read the local artifacts identified in their
outputs; they do not install packages, download, call a model, construct a
handler, or execute a scorer (see `collect.py:1`, `smoke.py:1`, `native.py:1`,
`artifacts.py:1`).

Reproduction commands and exact observed outputs, packet checks, checker output,
file sizes and the list of unverified matters are recorded in
`registry/w-bfclrt-validation.txt`. Runtime dependencies of these inspection
scripts themselves include the host `packaging`, `zstandard`, and `readelf`;
these are inspection utilities, not asserted BFCL import edges.

ABSENT is bounded to `search-scope.jsonl`; opaque pip bodies, unsearched
directories, unread import branches and exact compiled build provenance remain
UNKNOWN. `runtime-gaps-*.jsonl` names each unresolved target without guessing a
package/version/digest. The retained package licenses are not a certification
that every bundled component or installation has been licensed completely.
