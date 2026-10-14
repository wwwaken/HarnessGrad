# w-prov installed ReWOO byte custody

Evidence locators (literal strings for registry/journal references):

- w-prov physicsquestions installed CSV custody
- w-prov strategyqa installed CSV and evaluator custody
- w-prov sportsunderstanding installed CSV custody and metric divergence

The three adapters read a CSV with Python's standard-library `csv.DictReader`
from `/mnt/20t/xubuqiang/datasets/<dataset>/ReWOO-9cd0283043ff4be0c9d614fda2789d143ca6ffd1/data/bigbench/`.
Their graders are inline adapter functions. They import neither an installed
ReWOO evaluator package nor BIG-bench; `pyarrow==23.0.0` is declared in provisioning
but is unused on these CSV paths. Adapter source snapshots preserve that inspection.

Observed installed files were read without changing their roots; timestamps,
paths, sizes and real SHA-256 values are in `installed-observations.json`. Their
copies are `installed-*.csv`. Each matches its member of the full upstream archive
already preserved at `tests/fixtures/hg_e1_review/rewoo-archive.body` (6,225,904 bytes,
SHA-256 `7fe653d18faad40bf10ddcc7d85415782af975d80792bb26401393203b9ce136`).
All three installed `rewoo.tar.gz` files also had that digest. The archive's
`utils/Evaluator.py`, each installed but unused evaluator source, decoded GitHub
contents response and pinned raw response all match (8,584 bytes, SHA-256
`9194fa90f17dec47af827ca42cb1ef423166b30f9f330f4c6a1cc77356d73de3`).

| Dataset | Runtime member | Bytes | SHA-256 | Git blob SHA-1 |
| --- | --- | ---: | --- | --- |
| physicsquestions | `physics_question.csv` | 17953 | `7747cf185111aaa58493b5d804ba7b496cb152a6ae89a69a66a0c443adfd34aa` | `c31840a357210ea5b653aa457b6c8f1fe027075b` |
| strategyqa | `strategy_qa.csv` | 200453 | `c1fd0c271bf98741b68ac1ea3d167c5ccf2ed46da66645d5fc0ed6222e45f055` | `e372e1d0720b9160ec72366fbbd259f10ff6729a` |
| sportsunderstanding | `sports_understanding.csv` | 137846 | `5cfc24702b7a809409f42634f0b958f0d61c4d5aec8d732fd89889281c63d45e` | `4111fb257ab706d2e7edd85237511e805a1d57fa` |

GitHub contents responses were requested with exact ReWOO revision
`9cd0283043ff4be0c9d614fda2789d143ca6ffd1`. `verify.py` recomputes each decoded blob
object hash, binds its path and hash to the recursive Git tree, and reconstructs
all 20 tree objects including root `a617af22c7e487167fd671c60b2b0315d225de8a`, the
root advertised by the previously preserved commit response. The preserved HTTPS
responses authenticate the advertised revision; byte/object checks establish
content consistency. This is a GitHub lineage, with no HuggingFace export used by
these adapters. Previously acquired E1 FEVER Hub metadata concerns another dataset
and cannot be evidence of these CSVs' custody.

For physicsquestions, the installed 53 ordered CSV input/parsed-target-list pairs
match the 53 nonblank examples in BIG-bench's 54-example Physics task JSON pinned
at `092b196c1f8f14a54bbc62f24759d43bde46dd3b`. That JSON is 21,395 bytes, SHA-256
`ea55d3ee0d688b7f6f023f9d607313d8b7d3a4bd9151451141c239cd10d82eb5`.
It is a provenance reference, not a runtime data dependency.

For strategyqa, ReWOO's pinned `utils/Evaluator.py::normalize_answer` and
`Evaluator.get_metrics` identify the reference `em` comparison. Static AST
comparison proves the adapter's normalization expression is the same for string
inputs after ignoring type annotations/docstrings, inlining the upstream helper's
cached punctuation set, and explicitly accounting for the adapter's `str(s)`
coercion. This is not literal source equality for arbitrary object inputs or
evidence that the upstream evaluator (which also has an LLM judge path) ran.

For sportsunderstanding, pinned BIG-bench `sports_understanding/task.json` is
196,765 bytes, SHA-256
`925617612d19ca02d7b13bfb263300cc13701dca8851151a77be8ce986feadab`, blob
`406204f3540173ffc7a0ae1152a960c5af7628ff`. All 1,000 CSV pairs match in order:
CSV input is task JSON's `task_prefix` + one ASCII space + example input; its
target is the unique label with `target_scores == 1`. Its declared metric is
`multiple_choice_grade`. Authenticated BIG-bench `bigbench/api/task_metrics.py`
(19,463 bytes, SHA-256
`0d210ed501882ee38742f689b5e4bbc363a7481ef39dc8ee9959bfbc39903e73`, blob
`6e94e8be90c570065d32ca2df2f62e0d30f88b12`) chooses
`sample['choice'][argmax(sample['log_prob'])]` and adds that choice's
`target_scores` value. The adapter instead grades free text with word boundaries
and rejects text naming both labels. Authenticating the reference establishes
this mismatch; it does not establish scorer or metric equivalence. Both task and
scorer blobs bind to the exact BIG-bench revision via reconstruction of all 1,367
directory trees, including root `bd35c2e487af183ea54c4847f4824d36f7956f28`.

`*.body` preserves every acquired HTTP response body. A direct transport reset
acquired no response: its zero-byte `.body` file is a transport-failure sentinel,
explicitly labeled by the receipt's `body_kind`, not a raw upstream response.
Each `*.receipt.json` records request/final URLs, status, headers,
observation time, body byte count and SHA-256. Direct raw-host resets remain
preserved as failures; their empty-body hashes are not remote-artifact hashes.
Successful retries used the existing recorded public egress proxy and have
separate names. `acquire.py NAME URL [http://127.0.0.1:17891]` refuses to overwrite
receipts. No downloaded code was executed. Previously preserved responses used
by this packet are listed and hashed in `inherited-references.json`.

`SHA256SUMS` covers every other file in this subpacket. Reproduce from the repository
root, without network or access to the mutable installed dataset roots:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_wprov/rewoo/verify.py
```

`verified-custody.json` preserves that result. Python emits a SyntaxWarning while
parsing an invalid escape in the unmodified upstream scorer; parsing succeeds.
The verifier parses ASTs and data only, with no adapter, scorer, model, GPU, pilot,
LLM judge or official scorer execution.

This is an installed-byte observation, not a pristine-runtime attestation.
No selected run is declared or authenticated here. Split/eligibility manifests are
handled by the parent packet. Scorer dependency/offline closure, pristine trusted
verifier/runtime evidence, future selected-run manifest custody and the sports
metric mismatch remain open. No blocker is closed by this subpacket.
