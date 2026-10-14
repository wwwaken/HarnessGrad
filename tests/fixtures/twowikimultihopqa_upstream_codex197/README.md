# Task 197: original 2WikiMultihopQA evaluator fixture

This is an exact **code-only** acquisition from the author-maintained
[Alab-NII/2wikimultihop](https://github.com/Alab-NII/2wikimultihop), pinned to
[`209e761834d1ce055856fc11072c0a5aab47601d`](https://github.com/Alab-NII/2wikimultihop/commit/209e761834d1ce055856fc11072c0a5aab47601d)
(Xanh Ho, 2020-12-08, “Update dataset with ids”). It includes the original
`2wikimultihop_evaluate.py` and the alias-aware `2wikimultihop_evaluate_v1.1.py`.
The latter matches the existing adapter's declared evaluator digest. Neither file
has been reformatted, rewritten or given a replacement JSON import.

The accompanying `LICENSE` is the exact upstream Apache-2.0 license at this
revision. Both evaluator headers retain their HotpotQA attribution. The pinned
root tree contains no `NOTICE`. The Apache license governs the acquired code;
this acquisition makes no assertion about dataset redistribution rights.

`provenance.json` records all file SHA-256 and Git blob SHA-1 pins, the acquisition
time, original paths, immutable commit and root tree, and dependency evidence.
The original GitHub API responses in `git-commit.json` and `git-tree.json` bind
the commit to the root tree and the code/license blobs to that tree. The offline
test reconstructs the Git tree SHA-1 and compares original blob hashes. Tests
also pin expected digests independently of the receipt. The commit is unsigned:
HTTPS GitHub metadata establishes the observed origin, rather than an upstream
cryptographic signature. Parent review remains pending.

Only explicitly selected evaluator, license and requirements blobs were
downloaded. No full repository/archive, README, baseline implementation,
prediction example, task, answer, alias table, split or heldout payload was
acquired. Root-tree entries are metadata only. The failed raw-host acquisition
reset its connection; successful acquisition used GitHub's Git blob API and
decoded the original bytes without modification.

## Official definitions in the pinned code

The evaluator emits sixteen independent aggregate fields. `f1` is **answer F1**;
`joint_f1` is **Joint F1**. They must retain distinct metric identities.

- Answer normalization lowercases, removes ASCII punctuation, removes the English
  articles `a/an/the`, then collapses whitespace. Token intersection uses
  multiset counts. Precision is overlap / predicted tokens; recall is overlap /
  gold tokens; F1 is their harmonic mean, with zero when overlap is zero. A
  mismatched normalized `yes`, `no` or `noanswer` forces all three to zero. Empty
  vs empty has EM=1 but F1=0.
- v1.0 scores the canonical answer only. v1.1 scores the canonical answer plus
  the aliases **and demonyms** associated with `answer_id`. It independently
  maximizes EM, F1, precision and recall across accepted strings. Joint uses
  those independently maximized precision/recall values; it does not choose a
  single best alias for every component.
- Supporting facts are `(title, sentence-index)` pairs. Both versions remove
  exact duplicates *before* lowercasing titles; they then count matching pairs.
  Precision/recall/F1 come from TP/FP/FN. Empty vs empty has EM=1 but F1=0.
- v1.0 evidence compares normalized triple sets. v1.1 constructs one group of
  subject/object alias alternatives per gold triple, including demonyms from
  the alias table, and counts each unique matching predicted triple once.
  Evidence normalization lowercases, removes ASCII punctuation and collapses
  whitespace; it does **not** remove articles. Relation strings are normalized
  too, but subject/object aliases are the channels expanded from IDs.
- For each gold ID, `joint_prec = answer_prec * sp_prec * evi_prec` and
  `joint_recall = answer_recall * sp_recall * evi_recall`. `joint_f1` is the
  harmonic mean of those products, zero when their sum is zero.
  `joint_em = answer_em * sp_em * evi_em`. Joint F1 is not the product of the
  three component F1s.
- A missing ID in any prediction channel adds zero for that channel and disables
  Joint for that ID. All gold rows remain in the denominator; extra prediction
  IDs are ignored. Accumulation follows gold-file order, then each field is
  divided by `len(gold)`, multiplied by 100, and rounded once to two decimals.
  Empty gold files and malformed input are exceptions, not ordinary zero scores.

Synthetic tests expose two upstream quirks rather than correcting them: separate
answer alias maxima can produce Ans F1=80 and Joint F1=100 on a single fabricated
row; multiple matching evidence alternatives for one gold group can produce
evidence recall=200 and Evi/Joint F1=133.33. Thus “always bounded by 100” is not a
valid assertion about v1.1. Finite tests and an unchanged transcription region
do not certify the platform wrapper, input validation, deployment or real-data
comparability.

## Dependency closure and its remaining boundary

Both evaluators have one external runtime import, `ujson`. v1.0 additionally
imports standard-library `sys/re/string/collections/pickle`; v1.1 also imports
`itertools/os`. There are no local helper-module dependencies or scorer network
calls. The upstream requirements manifest leaves `ujson` unpinned and also lists
`spacy`, `tqdm`, `torch==1.1.0` and `joblib`; none of those four is imported by
either evaluator. Installing the baseline stack is unnecessary for this gate.

The test requires the real installed `ujson==5.10.0` and records its native module
SHA-256, BSD-3-Clause license fingerprint and absence of runtime `Requires-Dist`.
No stdlib-JSON fallback, stub or optional skip is allowed. The observed test
environment is CPython 3.12.4, Linux x86_64, pytest 7.4.4; the exact observation is
in the receipt. Python/pytest are test-environment requirements, not extra
evaluator imports. No test automatically installs anything.

PyPI release metadata identifies the CPython 3.12 Linux x86_64 wheel
`ujson-5.10.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl`:
SHA-256 `f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1`.
The source distribution hash is
`b3cd8f3c5d8c7738257f1018880444f7b7d9b66232c64649f562d7ba86ad4bc1`.
These are observed metadata pins, not receipts for downloaded artifacts. Neither
artifact was downloaded under this code-only task. The installed extension has
not been linked to the published wheel. `readelf -d` identifies direct native
dependencies `libstdc++.so.6`, `libgcc_s.so.1` and `libc.so.6` in the installed
extension. Loader resolution/transitive native closure and fresh-environment
installation were not attested. Building from the sdist
would additionally require a build toolchain and build dependencies; that closure
is outside this runtime inspection.

**Clean-environment offline deployment closure remains open.** The environment
custodian should supply the pinned compatible wheel and its licenses, a receipt
linking installation to that wheel, and a supported Python/native-runtime image
receipt. Verify fresh offline imports and synthetic execution before claiming
deployment closure. This is a remaining dependency request, not a missing-source
request; authoritative evaluator source has been acquired.

## Focused verification

From `/tmp/hg-codex-197`:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/quality/test_twowikimultihopqa_provenance_codex197.py --basetemp=.scratch/twowikimultihopqa-codex197/pytest
```

The suite verifies source/license/metadata integrity, fails closed on drift and
missing license, checks import closure, and executes each entire unchanged
evaluator with its real `ujson` dependency on explicitly fabricated inputs.
Sockets are blocked and evaluator file access is restricted to those generated
inputs. It reads the production adapter as text solely to compare the transcribed
region; it never imports that adapter or builds a dataset pool.

This fixture is a provenance and synthetic preflight gate. It creates no
benchmark result, changes no production scorer, and authorizes no H0/model run.

The original Python files intentionally retain upstream trailing whitespace and
extra final blank lines. Preserve those bytes when reviewing this fixture;
whitespace cleanup would break the provenance pins.
