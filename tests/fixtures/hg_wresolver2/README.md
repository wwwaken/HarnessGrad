# w-resolver2 evidence packet

This packet extends only the three failed default Python metadata resolver
profiles from `reports/w-resolver-payloads.md`. Read the new report at
`reports/w-resolver2-payloads.md`. No scoring task, model, GPU or endpoint runs.

Actual collection commands, in order:

```sh
python3 tests/fixtures/hg_wresolver2/obtain.py > tests/fixtures/hg_wresolver2/obtain.stdout.txt 2> tests/fixtures/hg_wresolver2/obtain.stderr.txt
unshare -Urn python3 tests/fixtures/hg_wresolver2/probe.py > tests/fixtures/hg_wresolver2/probe.stdout.txt 2> tests/fixtures/hg_wresolver2/probe.stderr.txt
python3 tests/fixtures/hg_wresolver2/coverage.py > tests/fixtures/hg_wresolver2/coverage.stdout.txt 2> tests/fixtures/hg_wresolver2/coverage.stderr.txt
python3 tests/fixtures/hg_wresolver2/retain_targets.py
```

The parallel source audit's generator commands and successful/failed assertion
outputs are preserved under `source/`. It reads unchanged repository source and
retained wheels, never imports dataset packages. `source-audit.json` binds exact
file/line text and original bytes. Fresh source lines supersede old citations.

Do not rerun collectors into this packet. They refuse existing capture outputs.
For another acquisition or resolution, use a new packet and fresh scratch paths.
`validate.py` is read-only by default; `--seal` creates the packet checksum list.
The exact final checks and their raw output are in
`reports/w-resolver2-validation.txt`.

`payloads/` commits the three exact requested wheels. `inputs.json` identifies
the full retained candidate directory, wheel versions, recomputed digests,
METADATA/WHEEL preimages and provenance. `index/` preserves exact versioned
PyPI JSON response bodies and response/GET status, URL, headers, size and digest
records for new downloads. Independent sha256sum output is in `raw/`.
The complete candidate corpus remains at the recorded external directory; the
three committed wheels alone are not a portable archive of complete profiles.

Each profile retains its previous root and every prior constraint verbatim,
then adds exact host-observed versions for missing default dependencies.
No arbitrary version, dependency stub, language model, extra, sdist or rebuilt
wheel is substituted. Official wheel metadata and an actual pip resolver,
rather than installed metadata alone, determine whether the graphs resolve.

`profiles/*/resolved.lock` pins actual pip selections and hashes. Offline
receipts use new independent venvs without system site packages or caches,
dependency processing enabled, `--ignore-installed --no-index` and wheel-only
selection, inside `unshare -Urn`. Hash-required installs and `pip check` succeed.
Removing each originally missing dependency gives a real resolver refusal
even after installing that profile. Scratch venvs/negative directories are
removed; the acquired candidate directory is deliberately retained.

`summary.json` and `dataset-coverage.json` recompute fractions from new receipts,
the prior successful receipts and the unchanged shared-blocker dataset refs.
Earlier successes and the Terminal-Bench task are carried forward, not rerun.
This is default Python metadata reconstruction only. Runtime ABI, optional
imports/models, task resources, selected execution, provenance, trusted
lifecycle and production admission remain separate obligations. Every shared
and dataset blocker stays open; S1/S3/S4/S5/S6 remain PARTIAL.

`registry-before.json` and `observation.txt` permit an exact additive-only audit:
only `scorer-offline-closure.observed` and three evidence references may change.
Statuses, next_actions, all dataset/history records, gates and
`production_authorized=false` remain unchanged.
