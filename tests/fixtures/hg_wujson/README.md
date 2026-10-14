# w-ujson immutable-image runtime evidence

The complete successful run is `deployment-v6` / `runtime-v9`.
`provenance.json` states the image/wheel identities and remaining original wheel
source/build custody gap. The active blocker remains external.

The deployment image includes the exact wheel, both original supplemental
notices, unchanged evaluator code/license and custody observations. Runtime
network is denied by Docker; no benchmark data or model is used.

`SHA256SUMS` covers every fixture file except itself. Verify from this directory
with `sha256sum -c SHA256SUMS`. Full commands, raw output locations, failure
history and interpretation are in `../../../reports/w-ujson-receipts.md`.

For a fresh replay of the retained local image, choose an unused receipt prefix:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_wujson/launch.py \
  --image-inspect deployment-v6-inspect.stdout.txt --prefix NEW-UNUSED-PREFIX
```

Do not overwrite or resume any retained receipt. Each attempt's `*.command.json`
contains exact argv and execution status; original stdout/stderr are alongside.
Build contexts are separately hash-locked by their own `INPUTS.sha256`.
