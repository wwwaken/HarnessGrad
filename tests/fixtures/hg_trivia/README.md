# w-trivia authoritative-origin evidence

Raw public HTTPS responses acquired through `HG_EGRESS_PROXY=http://172.17.0.1:17890`.
All 13 requests returned HTTP 200. TLS certificate and hostname verification stayed
at Python defaults; no credentials, insecure override, redirects or mirror requests.
The acquisition times and HTTP Date headers are retained separately.

`responses/*.body` contains exact entity bytes; `*.headers` preserves response
header fields serialized by Python's HTTP parser, not a wire/TLS transcript.
Each receipt records URL, response URL, method, proxy, status, times, sizes and
recomputed body/header SHA-256. `views/*.json` only pretty-prints the retained JSON;
the raw bodies remain the evidence. `verify.py` checks that the views decode to
the same JSON and independently recomputes every response digest and size.

`SHA256SUMS` covers every file in this directory except itself. Verify it from
this directory with `sha256sum -c SHA256SUMS`, then run `python3 verify.py`.
`review.json` records comparisons and reconstructed identities. Git tree/LFS
pointer reconstruction uses declared metadata; no Parquet/ZIP payload is fetched
or hashed. The reconstructed root tree is not an independently fetched Git
commit object. Payload SHA-256 and counts remain origin declarations.

The acquisition script lists exact requests and refuses to overwrite responses.
For a new acquisition use a fresh directory, not this historical evidence bundle.
The two commands used here were:

```sh
HG_EGRESS_PROXY=http://172.17.0.1:17890 python3 tests/fixtures/hg_trivia/acquire.py
HG_EGRESS_PROXY=http://172.17.0.1:17890 python3 tests/fixtures/hg_trivia/acquire.py hub-recursive-tree hub-initial-commits hub-added-selected-tree upstream-scorer upstream-license
```

At the first invocation the final five request names had not yet been added to
the script; it fetched only the initial eight. The present script lists all 13.
No source loader/evaluator was imported by acquisition or offline byte checks.
No task rows, dataset archives, benchmark runs, model, GPU or endpoint calls.
See `reports/w-trivia-review.md` for findings and limits.

## Request URL and recomputed response digest

| Name | URL | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `hub-added-selected-tree` | <https://huggingface.co/api/datasets/mandarjoshi/trivia_qa/tree/279d93a6e999c93dc992e1a705389e350ba7f706/rc.nocontext?recursive=false&expand=false> | 973 | `40b807247f15bb2f5522bc69d0c4c4a031f30eb23f2632a8526bfb53f8df1ce2` |
| `hub-commits` | <https://huggingface.co/api/datasets/mandarjoshi/trivia_qa/commits/0f7faf33a3908546c6fd5b73a660e0f8ff173c2f> | 7888 | `0f1c890e59a5e2e69f8c46efe68eeefdf766a081a067bbd6339cf1b772c00396` |
| `hub-discussion-8` | <https://huggingface.co/api/datasets/mandarjoshi/trivia_qa/discussions/8> | 13106 | `05e099be1b56ef18dc1e022459536cd44114f93cd1e2bf7df5b666d6b19126db` |
| `hub-initial-commits` | <https://huggingface.co/api/datasets/mandarjoshi/trivia_qa/commits/6baa09772e6ddf7e7b5d629ea64f1a8c1df21c3c> | 7052 | `7a386287343a75fdb7f09a924ab3d9b2b05856077947257adbb95e653d63c48d` |
| `hub-input-tree` | <https://huggingface.co/api/datasets/mandarjoshi/trivia_qa/tree/d63a76f01c8226449f76b437dd512cf8b17adf5d/data?recursive=false&expand=false> | 621 | `53718ecab96ddc19f326194a90967b4c8f21987fcdceb38d60b6b0b59b1d67cb` |
| `hub-predecessor-loader` | <https://huggingface.co/datasets/mandarjoshi/trivia_qa/raw/d63a76f01c8226449f76b437dd512cf8b17adf5d/trivia_qa.py> | 13317 | `b80c2307a37cfb261b66b7c73157de5495ae18add3f91f5f7d62f86620edc137` |
| `hub-predecessor-tree` | <https://huggingface.co/api/datasets/mandarjoshi/trivia_qa/tree/d63a76f01c8226449f76b437dd512cf8b17adf5d?recursive=false&expand=false> | 392 | `992511505f49ef7de5bb405fe8c5ce529ca00ac139ffaf1a597b74e1ca58f53a` |
| `hub-recursive-tree` | <https://huggingface.co/api/datasets/mandarjoshi/trivia_qa/tree/0f7faf33a3908546c6fd5b73a660e0f8ff173c2f?recursive=true&expand=false> | 46138 | `7e64db4f6e819643103cbb681778842a1aad623777d11cd4ab9dd18d3a7228c8` |
| `hub-revision` | <https://huggingface.co/api/datasets/mandarjoshi/trivia_qa/revision/0f7faf33a3908546c6fd5b73a660e0f8ff173c2f> | 25259 | `fd58143bcbfe06d8d63b4caf0c1068c8865e3d936d5de6078dc41af34dbb3fe5` |
| `hub-root-tree` | <https://huggingface.co/api/datasets/mandarjoshi/trivia_qa/tree/0f7faf33a3908546c6fd5b73a660e0f8ff173c2f?recursive=false&expand=false> | 1011 | `8d14e07783c5dcf3ac5c8fd30a3a480f0e167bed0b77cbb819d1530b41bffc54` |
| `hub-selected-tree` | <https://huggingface.co/api/datasets/mandarjoshi/trivia_qa/tree/0f7faf33a3908546c6fd5b73a660e0f8ff173c2f/rc.nocontext?recursive=false&expand=false> | 973 | `40b807247f15bb2f5522bc69d0c4c4a031f30eb23f2632a8526bfb53f8df1ce2` |
| `upstream-license` | <https://raw.githubusercontent.com/mandarjoshi90/triviaqa/ca43b5820b107f3970cf4b7d67f7db7a98117b79/LICENSE> | 11340 | `5cc548335f22310a53877044624711ac3e20e5ed1117617c1fd3fc462c54330e` |
| `upstream-scorer` | <https://raw.githubusercontent.com/mandarjoshi90/triviaqa/ca43b5820b107f3970cf4b7d67f7db7a98117b79/evaluation/triviaqa_evaluation.py> | 5710 | `51785a3bc2e02a8f1ebf9db3aa18834c6a5daa5089ee5d435c99e0babf4be682` |
