FOUND: Four scorer fixes with synthetic fail-before/pass-after evidence. The original
code reference is `38a302e5c5edb9d1b26b0e642a40301f013f5cad`
(`registry/w-metricfix-validation.txt:172`). All four new tests failed before the
scorer edits (`registry/w-metricfix-validation.txt:90`); the final focused suite has
46 passes (`registry/w-metricfix-validation.txt:183`). Exact commands and captured
output are in `registry/w-metricfix-validation.txt:45` onward.

| Item | Change and regression | Observed synthetic pre/post grade |
| --- | --- | --- |
| Physics Questions | Both prediction and gold apply `strip().rstrip(".")`; other normalization is unchanged (`data/datasets/physicsquestions.py:93`). Test checks accepted punctuation and rejects case, unit spacing, and numeric variants (`tests/quality/test_w_metricfix.py:105`). | `7 km.` against accepted `7 km`: **0 -> 1** (`registry/w-metricfix-validation.txt:49`, `registry/w-metricfix-validation.txt:109`). |
| Sports Understanding | Immediate negation maps a label to its complement; literal `names_both` rejection remains (`data/datasets/sportsunderstanding.py:76`, `data/datasets/sportsunderstanding.py:81`, `data/datasets/sportsunderstanding.py:103`). Test checks both directions, word boundaries, contractions, and ambiguous answers (`tests/quality/test_w_metricfix.py:115`). | `not plausible` against `implausible`: **0 -> 1**; against `plausible`: **1 -> 0** (`registry/w-metricfix-validation.txt:50`, `registry/w-metricfix-validation.txt:110`). |
| GSM8K | First `####` marker takes precedence; flexible last-number extraction applies only without a marker. A malformed first marker does not fall back. Evidence records the extraction used (`data/datasets/gsm8k.py:132`, `data/datasets/gsm8k.py:156`). The numeric comparison remains exclusive `1e-6` (`data/datasets/gsm8k.py:144`). Test covers later numbers/markers, malformed markers, decimal/comma handling, fallback, and tolerance (`tests/quality/test_w_metricfix.py:134`). The existing strict-extraction expectation now selects the first marker (`tests/quality/test_gsm8k_official_scorer.py:119`). | `#### 18 then the total is 20` against `18`: **0 -> 1**; flexible evidence stays `20`, scored strict value is `18` (`registry/w-metricfix-validation.txt:51`, `registry/w-metricfix-validation.txt:111`). |
| LiveCodeBench | Remove the inner `min(600, ...)`; retain upstream-shaped `(6+1)*n_tests+5`, timeout kill behavior, and the adapter's 900 s declaration (`data/datasets/livecodebench/verify/check.py:177`, `data/datasets/livecodebench.py:281`). The docstring explains the former child-wait bound and the retained outer bound (`data/datasets/livecodebench/verify/check.py:21`). Test uses a virtual clock and stubs aggregation, and checks scaling, expiry, and the adapter bound (`tests/quality/test_w_metricfix.py:54`, `tests/quality/test_w_metricfix.py:152`). | 103 authored tests, virtual child finishing at 650 s: **0 -> 1**; join budget **600 -> 726 s**, killed **true -> false** (`registry/w-metricfix-validation.txt:53`, `registry/w-metricfix-validation.txt:113`). |

FOUND: Sports handles immediately preceding `not`, `no`, standalone `n't`, and
contractions such as `isn't` and `wasn't`, including curly apostrophes. Double
negation, intervening words, trailing negation, synonyms, and sarcasm are outside
the documented rule (`data/datasets/sportsunderstanding.py:81`). Punctuation between
negator and label is also outside the whitespace-only matcher
(`data/datasets/sportsunderstanding.py:97`).

FOUND: The task goal now describes GSM8K marker precedence
(`data/datasets/gsm8k.py:201`); LiveCodeBench adapter documentation no longer describes
a 600 s cap (`data/datasets/livecodebench.py:36`). Its adapter edit changes comments
and documentation only, with `timeout_s` still 900
(`data/datasets/livecodebench.py:281`).

FOUND: `python3 tools/check_dataset_blockers.py` returned
`{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}`
(`registry/w-metricfix-validation.txt:142`).

ABSENT: Edits to the three protected files and the ten other enumerated verifier
scripts in the exact scope printed by `protected-scope-and-cleanup`; that command
returned `changed protected paths: []`
(`registry/w-metricfix-validation.txt:201`, `registry/w-metricfix-validation.txt:235`).
Its `/tmp/metricfix-*` search also returned an empty list
(`registry/w-metricfix-validation.txt:236`).

UNKNOWN: No real long-running LiveCodeBench executor was tested. The virtual child
and aggregator exercise the wrapper's scoring branches, not upstream execution
(`tests/quality/test_w_metricfix.py:65`, `tests/quality/test_w_metricfix.py:85`). The
pool histogram and number of affected released problems were not inspected. The
synthetic formula gives 719 s for 102 tests and 726 s for 103 tests; these are fixture
calculations, not pool measurements (`tests/quality/test_w_metricfix.py:152`). This
runtime gap is the primary uncertainty for parent review. The explicit list of
unverified work is in `registry/w-metricfix-validation.txt:27`.
