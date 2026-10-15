# Offline scorer payload evidence — w-wheelhouse

`manifest.json` records exact-version downloads, source URLs, compatible tags,
recomputed SHA-256 values, HTTP metadata, and the retained local payload directory.
`index/` preserves the actual PyPI version responses. `built-artifacts.json` links
network-denied wheel builds to their exact sdist hashes, including prior failures.
`payload-index.json`, `SHA256SUMS.payloads`, and `sha256sum.payloads.txt` identify all
retained source/wheel bytes. Large payloads live outside git at the path in these
receipts; this directory commits acquisition/build/install receipts, not a portable
binary archive. Moving this evidence alone does not move its installation payloads.

The installable wheelhouse is the `payload_directory` in `manifest.json`.
Hash-locked, dataset-specific `*.lock` files are installed with:

```sh
python3 -m venv /tmp/hg-wheelhouse-review-venv
unshare -Urn /tmp/hg-wheelhouse-review-venv/bin/python -m pip install \
  --no-index --no-cache-dir --no-deps --require-hashes \
  --find-links=/tmp/hg-wwheelhouse-payloads-e5uywviu \
  -r tests/fixtures/hg_wwheelhouse/chessbench_puzzles.lock
```

This is a reproduction recipe; actual commands and raw output are in
`offline/*.receipt.json`, `offline/*.stdout.txt`, and `offline/*.stderr.txt`.
`offline.py` creates separate fresh venvs with `system_site_packages=False`.
`*-network.json` records the empty routing table and external-connect ENETUNREACH.
The first build receipt's `interfaces` field came from the host-mounted sysfs;
its empty route and failed connection are real. Later receipts use namespace-local
`socket.if_nameindex()` and show only loopback.

`--no-deps` deliberately installs the inspected import set, rather than expanding
unused actor/CLI/extras dependencies. These are import profiles, not complete
upstream `Requires-Dist` locks. Build-only tools and Torch import-time native
providers have distinct manifest roles. No scorer, task, constructor, JVM, model,
GPU computation or endpoint is run. Imports use `CUDA_VISIBLE_DEVICES=''`.

`source-imports.json` reads and hashes current source; `audit/` records fresh
package-only imports in kernel network namespaces. `installed-distributions.json`
maps every imported Python distribution to file+line witnesses.
`ds1000-context-imports.json` contains import statements and source locations only,
not complete tasks, answers or contexts. `dataset-payloads.json` states exact
coverage and remaining gaps. A successful public-wheel profile does not reproduce
the Conda native provider, nor certify task-selected runtime custody.
