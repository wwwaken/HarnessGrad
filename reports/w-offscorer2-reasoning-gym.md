# Reasoning Gym controlled official execution - w-offscorer2

The complete installed `reasoning-gym==0.1.25` package imports offline. Direct upstream
`create_dataset(family, seed=20261008, size=20).score_answer(answer, entry)` is compared
with unchanged `data.datasets.reasoning_gym.score` on the same authored predictions
and entries. No generated item (`dataset[index]`) or released pool row is accessed.
Scope: `chain_sum`, `letter_counting`, `word_sorting`, three admitted families only;
this does not execute every admitted family or establish family eligibility.

Upstream `open-thought/reasoning-gym`, tag `v0.1.25`, commit
`21e6d2a9a581b3e11aafe711abfd37402f8482d5`. `run.py` recomputes the published wheel
SHA-256 `7f17a3eddb13c015d7d4a755ed576a061df889faf9468bcc2cca334ebe9e0435`,
checks it against preserved PyPI release JSON, then rehashes all 200 actual installed
package members and checks byte equality with that wheel and Git blob equality with
the preserved nontruncated tree. Prior provenance responses are in
`tests/fixtures/hg_wprov/reasoning_gym/responses/`; their newly recomputed digests,
all installed member paths/digests and selected callable identities are retained in
both `official.json` and `local.json`. The package manifest hash includes actual
installed paths; it is an observation, not a portable dependency closure.

Recomputed source-file hashes:

| Method | Source | SHA-256 |
| --- | --- | --- |
| `chain_sum` | `reasoning_gym.arithmetic.chain_sum.ChainSumDataset.score_answer` | `7e811214e9e31aa67eeb5490a0cf8eb275fceab609c4523bb38ceec9f8dbcb9f` |
| `letter_counting` | `reasoning_gym.dataset.ProceduralDataset.score_answer` | `480caacca5b12865e13bac68937687a799977e040ace5ae0496e71c1d77971e6` |
| `word_sorting` | `reasoning_gym.algorithmic.word_sorting.WordSortingDataset.score_answer` | `32d554acf0613b0cec4236a806165bebb426420a851a9e5468943a0cb8deff41` |

`chain_sum` also calls unchanged `reasoning_gym.utils.compute_decimal_reward`;
its containing file is part of the freshly verified package member manifest.
`letter_counting` inherits `ProceduralDataset.score_answer`.

Exact executed command, repository-root cwd:

```sh
bash tests/fixtures/hg_woffscorer2/reasoning_gym/commands.sh
```

The checked-in script expands to each of `official`, `local`, `compare`:

```sh
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 tests/fixtures/hg_woffscorer2/reasoning_gym/offline_exec.py tests/fixtures/hg_woffscorer2/reasoning_gym/run.py official > tests/fixtures/hg_woffscorer2/reasoning_gym/official.json 2> tests/fixtures/hg_woffscorer2/reasoning_gym/official-offline.txt
```

The other two invocations replace `official` with `local` / `compare` in both
argument and output basenames. `offline_exec.py` is copied byte-for-byte from
`tests/fixtures/hg_wverify/scorers/offline_exec.py`; its kernel seccomp filter denies
all socket APIs and io_uring_setup before importing scorers, with real IPv4/IPv6/UNIX
EPERM probes in all three `*-offline.txt` receipts. Limits are wall 150 s, CPU 120 s,
file descriptors 256. The local adapter import attempts one Python open of
`/mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl`; the audit hook denies it
before any content read, and the adapter catches that import-time provisioning
failure. Its record cache is asserted empty before and after direct scoring.
`local-offline.txt` preserves that denied open; official/compare denial lists are
empty. No native table reader or adapter `load()` call is invoked. This is a
fixture guard, not a production verifier/runtime observation.

Measured: **27 authored inputs; 24 numeric comparisons; 24 agreements; 0 numeric
divergences; 3 official and 3 local errors on the same 3 malformed inputs.**
The nullable predictions are explicit API-boundary controls. Malformed entries are
deliberate invalid-schema probes, excluded from numeric agreement counts. Raw
tracebacks remain in both outputs. Partial substring credit (including `1000.1`
against `1000`) is an observed upstream return and adapter agreement, not an accuracy
claim. No exceptions are converted to zeros.

All component paths below resolve under `tests/fixtures/hg_woffscorer2/reasoning_gym/`:
`inputs.json`, full `official.json` / `local.json`, and `compare.json`.

| Input | Prediction | Official | Local | Outcome |
| --- | --- | --- | --- | --- |
| `chain_sum-01` | `"1000"` | 1.0 | 1.0 | agree |
| `chain_sum-02` | `"+01,000.00"` | 1.0 | 1.0 | agree |
| `chain_sum-03` | `"1000.1"` | 0.6666666666666666 | 0.6666666666666666 | agree |
| `chain_sum-04` | `"value=1000"` | 0.4 | 0.4 | agree |
| `chain_sum-05` | `""` | 0.0 | 0.0 | agree |
| `chain_sum-06` | `null` | 0.0 | 0.0 | agree |
| `chain_sum-07` | `"wrong"` | 0.0 | 0.0 | agree |
| `chain_sum-08` | `" 1000 "` | 1.0 | 1.0 | agree |
| `letter_counting-01` | `"42"` | 1.0 | 1.0 | agree |
| `letter_counting-02` | `"042"` | 0.6666666666666666 | 0.6666666666666666 | agree |
| `letter_counting-03` | `"x42"` | 0.6666666666666666 | 0.6666666666666666 | agree |
| `letter_counting-04` | `"42x"` | 0.6666666666666666 | 0.6666666666666666 | agree |
| `letter_counting-05` | `" 42 "` | 0.5 | 0.5 | agree |
| `letter_counting-06` | `""` | 0.0 | 0.0 | agree |
| `letter_counting-07` | `"wrong"` | 0.0 | 0.0 | agree |
| `letter_counting-08` | `null` | 0.0 | 0.0 | agree |
| `word_sorting-01` | `"alpha, beta, gamma"` | 1.0 | 1.0 | agree |
| `word_sorting-02` | `"gamma, beta, alpha"` | 0.3333333333333333 | 0.3333333333333333 | agree |
| `word_sorting-03` | `"alpha, gamma, beta"` | 0.3333333333333333 | 0.3333333333333333 | agree |
| `word_sorting-04` | `" alpha , beta,gamma"` | 1.0 | 1.0 | agree |
| `word_sorting-05` | `""` | 0.0 | 0.0 | agree |
| `word_sorting-06` | `null` | 0.0 | 0.0 | agree |
| `word_sorting-07` | `"wrong"` | 0.0 | 0.0 | agree |
| `word_sorting-08` | `"alpha, alpha, alpha"` | 0.3333333333333333 | 0.3333333333333333 | agree |
| `chain_sum-malformed-entry` | `"x"` | KeyError | KeyError | error; unscored |
| `letter_counting-malformed-entry` | `"x"` | KeyError | KeyError | error; unscored |
| `word_sorting-malformed-entry` | `"x"` | KeyError | KeyError | error; unscored |

The malformed `chain_sum` / `letter_counting` entries each raise `KeyError('answer')`;
`word_sorting` raises `KeyError('metadata')`, independently in official and local
calls. These six exceptions constitute three nonnumeric inputs. No divergence was
measured in the numeric domain covered. No claims extend to the other families,
all dependency ABIs, selected private input custody, exported state equivalence or
live harness execution. Shared and dataset blockers remain open.
