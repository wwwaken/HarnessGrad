# w-fevobj — complete request inventory

Generated offline from plans and immutable per-attempt receipts. No new requests.

## loader-raw-proxy

Command: python3 tests/fixtures/hg_fevobj/fetch.py tests/fixtures/hg_fevobj/plan-01.json

Exact URL: https://huggingface.co/datasets/copenlu/fever_gold_evidence/raw/1776db7e9abab525eae8e59c5015e3589dfe371b/fever_gold_evidence.py

Receipt: tests/fixtures/hg_fevobj/loader-raw-proxy.request.json:1

Proxy: http://172.17.0.1:17890; exact request headers: {"Accept-Encoding": "identity", "Connection": "close", "Host": "huggingface.co", "User-Agent": "HarnessGrad-fevobj-provenance/1"}

Final HTTP status: null; response bytes: null; response SHA-256: null.

No HTTP response/body observed. Exact error: URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1000)>

## generated-tree-proxy

Command: python3 tests/fixtures/hg_fevobj/fetch.py tests/fixtures/hg_fevobj/plan-01.json

Exact URL: https://huggingface.co/api/datasets/copenlu/fever_gold_evidence/tree/ad8321607bcad0e534c243ec8c108a5787cea6c8?recursive=true

Receipt: tests/fixtures/hg_fevobj/generated-tree-proxy.request.json:1

Proxy: http://172.17.0.1:17890; exact request headers: {"Accept-Encoding": "identity", "Connection": "close", "Host": "huggingface.co", "User-Agent": "HarnessGrad-fevobj-provenance/1"}

Final HTTP status: null; response bytes: null; response SHA-256: null.

No HTTP response/body observed. Exact error: URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1000)>

## loader-raw-direct

Command: python3 tests/fixtures/hg_fevobj/fetch.py tests/fixtures/hg_fevobj/plan-02.json

Exact URL: https://huggingface.co/datasets/copenlu/fever_gold_evidence/raw/1776db7e9abab525eae8e59c5015e3589dfe371b/fever_gold_evidence.py

Receipt: tests/fixtures/hg_fevobj/loader-raw-direct.request.json:1

Proxy: None; exact request headers: {"Accept-Encoding": "identity", "Connection": "close", "Host": "huggingface.co", "User-Agent": "HarnessGrad-fevobj-provenance/1"}

Final HTTP status: null; response bytes: null; response SHA-256: null.

No HTTP response/body observed. Exact error: URLError: <urlopen error [Errno 101] Network is unreachable>

## generated-tree-direct

Command: python3 tests/fixtures/hg_fevobj/fetch.py tests/fixtures/hg_fevobj/plan-02.json

Exact URL: https://huggingface.co/api/datasets/copenlu/fever_gold_evidence/tree/ad8321607bcad0e534c243ec8c108a5787cea6c8?recursive=true

Receipt: tests/fixtures/hg_fevobj/generated-tree-direct.request.json:1

Proxy: None; exact request headers: {"Accept-Encoding": "identity", "Connection": "close", "Host": "huggingface.co", "User-Agent": "HarnessGrad-fevobj-provenance/1"}

Final HTTP status: null; response bytes: null; response SHA-256: null.

No HTTP response/body observed. Exact error: URLError: <urlopen error [Errno 101] Network is unreachable>

## loader-resolve-download-proxy

Command: python3 tests/fixtures/hg_fevobj/fetch.py tests/fixtures/hg_fevobj/plan-03.json

Exact URL: https://huggingface.co/datasets/copenlu/fever_gold_evidence/resolve/1776db7e9abab525eae8e59c5015e3589dfe371b/fever_gold_evidence.py?download=true

Receipt: tests/fixtures/hg_fevobj/loader-resolve-download-proxy.request.json:1

Proxy: http://172.17.0.1:17890; exact request headers: {"Accept-Encoding": "identity", "Connection": "close", "Host": "huggingface.co", "User-Agent": "HarnessGrad-fevobj-provenance/1"}

Final HTTP status: 200; response bytes: 7897; response SHA-256: ad33cbaed338e94670d8d661c74fa9b8ababb3e4679f89d63bea661c0df9e35f.

Raw response: tests/fixtures/hg_fevobj/loader-resolve-download-proxy.body

Automatically followed redirect: {"body": "loader-resolve-download-proxy.redirect-0.body", "bytes": 220, "request": "loader-resolve-download-proxy", "sha256": "2a8daf43b1178039fad7f477790b82d1c85b2f5e7deebf9580c44cfb6e933110", "status": 307, "url": "https://huggingface.co/datasets/copenlu/fever_gold_evidence/resolve/1776db7e9abab525eae8e59c5015e3589dfe371b/fever_gold_evidence.py?download=true"}

All redirect headers, location and lossless body hex: same request receipt.

## generated-tree-expand-proxy

Command: python3 tests/fixtures/hg_fevobj/fetch.py tests/fixtures/hg_fevobj/plan-03.json

Exact URL: https://huggingface.co/api/datasets/copenlu/fever_gold_evidence/tree/ad8321607bcad0e534c243ec8c108a5787cea6c8?recursive=true&expand=true&limit=100

Receipt: tests/fixtures/hg_fevobj/generated-tree-expand-proxy.request.json:1

Proxy: http://172.17.0.1:17890; exact request headers: {"Accept-Encoding": "identity", "Connection": "close", "Host": "huggingface.co", "User-Agent": "HarnessGrad-fevobj-provenance/1"}

Final HTTP status: 200; response bytes: 4596; response SHA-256: 04f6cc689ac503f4d83fa5e97249b935efafe3b77cfa66a9388da7123fc91a4b.

Raw response: tests/fixtures/hg_fevobj/generated-tree-expand-proxy.body
