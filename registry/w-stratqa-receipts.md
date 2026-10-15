# w-stratqa: original StrategyQA scorer and split source receipts

## Determinations

**Scorer: FOUND.** The original code README explicitly links the official evaluator;
its answer metric is raw Python equality followed by correct/total, with no text
normalisation. The retained evaluator is bound to
`allenai/strategyqa-evaluator@49b88ed2b2f1b57385c13e8a0699dee1d227f83e`.
Sources: `tests/fixtures/hg_stratqa/official-README.md:148`,
`tests/fixtures/hg_stratqa/original-eval.py.txt:7`,
`tests/fixtures/hg_stratqa/git-bindings.json:24`.

**Split: UNKNOWN** for the requested exact original train/dev membership or a
complete reproducible generator. The readable code README calls its train/dev
split **unofficial** and gives only “90%/10% random”; those words do not specify
membership, seed, ordering or a complete generator. The paper describes an
annotator-based split and reports **Train/Test**, not the local hash division.
Sources: `tests/fixtures/hg_stratqa/official-README.md:41`,
`tests/fixtures/hg_stratqa/arxiv-paper-html.body:701`,
`tests/fixtures/hg_stratqa/arxiv-paper-html.body:708`,
`tests/fixtures/hg_stratqa/arxiv-paper-html.body:797`.

**Comparability: different for the metric; exact split alignment remains
undetermined.** This partially resolves the old source gap, and does not permit
an original-benchmark result claim. The local metric remains local normalised
whole-answer EM. Its comparison is not the original evaluator's Accuracy, even
though both can average binary hits. See the hand-worked examples below;
`data/datasets/strategyqa.py:66`, `:84`, `:89` and
`tests/fixtures/hg_stratqa/original-eval.py.txt:12` are the definitions compared.
The proposal's `comparability: different` records this demonstrated metric
difference; it does **not** assert resolved split membership.

## Authority and retained bytes — FOUND

All fixture paths below are under `tests/fixtures/hg_stratqa/`. Exact request URLs,
HTTP statuses, byte lengths and SHA-256 digests are enumerated at the end of this
file and in `tests/fixtures/hg_stratqa/requests.json:1`. Individual
`*.receipt.json` files retain response headers and transport failures. The capture
command uses `ssl.create_default_context()` for certificate/hostname validation,
permits only HTTPS (including redirects), requests identity encoding, and caps
each body at 950,000 bytes (`tests/fixtures/hg_stratqa/acquire.py:1`). A `null`
status means no HTTP status was observed; it is not a 404. `complete: true` means
the requested HTTP body was retained, not that a Range response is a whole ZIP.

1. **Paper artefact record — FOUND.**
   `https://aclanthology.org/2021.tacl-1.21/` returns the record for *Did Aristotle
   Use a Laptop? A Question Answering Benchmark with Implicit Reasoning
   Strategies*. Its metadata identifies TACL, 2021, pages 346–361 and DOI
   `10.1162/tacl_a_00370` (`tests/fixtures/hg_stratqa/acl-record.body:1`).
   Verbatim metadata excerpts:

   ```html
   <meta content="Did Aristotle Use a Laptop? A Question Answering Benchmark with Implicit Reasoning Strategies" name=citation_title>
   <meta content="10.1162/tacl_a_00370" name=citation_doi>
   ```

   The retained full paper text is the ar5iv rendering of arXiv:2101.02235,
   linked by the official code README (`tests/fixtures/hg_stratqa/official-README.md:3`).
   It is a rendered preprint, not an independently compared copy of the final
   publisher PDF. The final PDF and arXiv source archive were not downloaded.
   Paper rendering: `https://ar5iv.labs.arxiv.org/html/2101.02235`, HTTP 200,
   200954 bytes, SHA-256
   `349e3bc2781e5aae797cff1d23fe3f4ab37c2f35e7ff3ed321a885080cff0292`.
   The paper links the dataset/codebase page verbatim:
   `https://allenai.org/data/strategyqa`
   (`tests/fixtures/hg_stratqa/arxiv-paper-html.body:163`).

2. **Original code repository — FOUND.**
   GitHub's repository record identifies `eladsegal/strategyqa` as the official
   code, and supplies the same dataset homepage
   (`tests/fixtures/hg_stratqa/github-repository.body:1`). The observed `main`
   commit is `1ba1e97452e189569357876f2854b01357ffbe37`, tree
   `b31bdc2f04bb48d60672e606ad5974a83f70127f`
   (`tests/fixtures/hg_stratqa/github-head.body:1`). This is a pinned observed
   revision, not a claim that it is the first publication commit. The recursive
   tree is complete (`tests/fixtures/hg_stratqa/github-tree.pretty.json:829`).
   The README was decoded from GitHub's base64 blob response and checked against
   the tree's Git blob ID, `feee1f309586a3cfb4151570af2763dc0726a3f6`.
   Extracted bytes: 11408; SHA-256
   `80ab310e481985c8fdd8913b9e250c0d5e83fc9edde27d4770b6d08436bcd34e`
   (`tests/fixtures/hg_stratqa/git-bindings.json:2`). Verbatim decisive excerpts:

   > This repository contains the official code of the paper:

   (`tests/fixtures/hg_stratqa/official-README.md:3`, opening substring.)

   > The official evaluation script can be found [here](https://github.com/allenai/strategyqa-evaluator).

   (`tests/fixtures/hg_stratqa/official-README.md:148`, complete line.)

3. **Official evaluator — FOUND.**
   `https://api.github.com/repos/allenai/strategyqa-evaluator/commits/main`
   binds observed commit `49b88ed2b2f1b57385c13e8a0699dee1d227f83e` and tree
   `4f0051627e208629fffb1eacedd454f2cd89cf47`
   (`tests/fixtures/hg_stratqa/evaluator-head.body:1`). The complete recursive
   tree names `evaluator/eval.py`, size 5797, Git blob
   `9717ac6bfd7f3428cb15aa87f3e0ab5873458ce1`
   (`tests/fixtures/hg_stratqa/evaluator-tree.pretty.json:45`, `:109`).
   Raw/CDN attempts and a rate-limited GitHub blob request did not retrieve it;
   the small pinned source archive **did**:

   `https://codeload.github.com/allenai/strategyqa-evaluator/zip/49b88ed2b2f1b57385c13e8a0699dee1d227f83e`

   HTTP 200, 19726 bytes, SHA-256
   `fd656478f987622655eca17a3a42995d83aaa407df05e71488146c2d47f0f1ba`
   (`tests/fixtures/hg_stratqa/evaluator-codeload.receipt.json:1`).
   The exact source is retained as `original-eval.py.txt`, 5797 bytes, SHA-256
   `68c0edcd2fd26daf2cec368302d9f564cbf351288aa4a2c265f47bdc00704044`.
   Its Git blob ID and length reproduce the authenticated tree entry
   (`tests/fixtures/hg_stratqa/git-bindings.json:24`). The evaluator README is
   independently bound the same way; its opening describes the StrategyQA
   leaderboard evaluator (`tests/fixtures/hg_stratqa/evaluator-README.md:3`,
   `tests/fixtures/hg_stratqa/git-bindings.json:13`).

## Original answer metric — FOUND

Verbatim complete answer-evaluator class
(`tests/fixtures/hg_stratqa/original-eval.py.txt:7`):

```python
class AnswerEvaluator:
    def __init__(self, args):
        self._correct = 0.0
        self._total = 0.0

    def __call__(self, gold, prediction):
        self._correct += int(gold["answer"] == prediction)
        self._total += 1

    def get_metrics(self):
        return {"Accuracy": self._correct / self._total}
```

Definition at this revision: no lowercase conversion, punctuation deletion,
article removal, whitespace normalisation, stringification, answer extraction
or coercion. The comparison is Python `==` on the JSON-loaded gold answer and
prediction value, **not** a type-strict Boolean assertion. Each call contributes
one denominator unit. For a nonempty, successfully evaluated answer stream,
Accuracy is sum of these binary equality results divided by the number of gold
instances. The outer loop visits every supplied gold instance and indexes each
prediction by its `qid`; it does not skip missing/unmeasured instances
(`tests/fixtures/hg_stratqa/original-eval.py.txt:102`). The CLI checks prediction
count against gold count and checks consistent prediction keys
(`tests/fixtures/hg_stratqa/original-eval.py.txt:116`). Missing IDs, cardinality
errors and empty-denominator failures are not specified as ordinary zero hits.
When no answer stream is submitted the wrapper's default `Accuracy: 0.0` is not
evidence of measured answer performance (`:91`, `:127`). The actual submitted
gold file determines the denominator; it is not hard-coded to a published split
count (`:104`, `:112`). No scorer or wrapper was imported or executed here.

The local comparator, after shared QA handling, stringifies, lowercases,
deletes ASCII `string.punctuation`, removes word-boundary articles `a|an|the`,
collapses whitespace and compares whole strings
(`data/datasets/strategyqa.py:66`, `:84`, `:89`). Its run reward is an arithmetic
mean over **measured_tasks** (`data/aggregation_policies.json:27`), whereas the
original source above loops over the supplied gold collection. Conditional
agreement on some canonical values or finite complete binary vectors is not
equality of these input contracts. ReWOO's retained EM and its parser distinction
remain as previously established (`registry/w-metriccmp-comparability.md:258`).
F1, LLM-judge accuracy, SARI and retrieval metrics are outside this comparison.

### Minimal discriminating examples, worked by hand only

At the two comparison functions' string boundary, choose synthetic prediction
`"No!"` and synthetic gold `{"answer": "No"}`. Local normalisation produces
`"no"` and `"no"`, hence hit **1**. The original class computes
`"No" == "No!"`, hence hit **0**. This is a synthetic evaluator-accepted string
input, not an assertion that the official gold distribution uses strings:
neither the class nor its JSON loader enforces an answer type
(`data/datasets/strategyqa.py:69`, `:81`, `:86`;
`tests/fixtures/hg_stratqa/original-eval.py.txt:12`, `:116`).

For the representation boundary, the first public evaluator sample's answer is
Boolean (`tests/fixtures/hg_stratqa/first-sample-answer.excerpt.txt:1`, verbatim
`        "answer": false,`). Only that first sample object was decoded to
establish the type; only its answer line was retained separately. The sample
member's bytes were checked against its tree blob, with exact extraction scope
and digest in `tests/fixtures/hg_stratqa/first-sample-answer.provenance.json:1`;
the complete response archive remains retained. This does not attest every gold
row's type. For synthetic semantic answer “no”, explicitly represent the gold as
Boolean `false` for the official evaluator and string `"No"` for the installed
local task. Submit the same answer text `"No!"`: original `False == "No!"`
is **0**, local normalised `"no" == "no"` is **1**. The mapping of semantic
labels is explicit in this example, not an observed runtime converter. The
installed adapter accepts `Yes`/`No` labels (`data/datasets/strategyqa.py:60`,
`:118`). No real prediction, benchmark row or measured score is used.

## Exact original split — UNKNOWN

Readable split evidence, kept separate from an exact definition:

1. **FOUND — paper-level Train/Test description.** Table 4 names Train and Test
   and reports 2290 and 490 questions, respectively
   (`tests/fixtures/hg_stratqa/arxiv-paper-html.body:701`, `:708`). Its decisive
   prose is verbatim:

   > This results in a collection of 2,780 verified strategy questions, for which we create an annotator-based data split

   (`tests/fixtures/hg_stratqa/arxiv-paper-html.body:797`, substring before the
   citation markup.) This is not an executable assignment rule or ID manifest.

2. **FOUND — explicitly unofficial code train/dev description.** Verbatim:

   > To train our baseline models, we created a 90%/10% random split of the official train set to get an *unofficial* train/dev split: `data/strategyqa/[train/dev].json`.

   (`tests/fixtures/hg_stratqa/official-README.md:43`; two trailing Markdown
   spaces are omitted from the quotation.) The complete code tree identifies
   `data/strategyqa/dev.json` and `data/strategyqa/train.json`
   (`tests/fixtures/hg_stratqa/github-tree.pretty.json:215`, `:270`). The byte
   sizes and Git blob IDs are observed tree metadata, not retrieved membership.
   Neither file's rows were downloaded/read. “90%/10% random” lacks the seed,
   input ordering and sampling implementation needed to regenerate membership;
   no such missing detail is invented from the local hash split.

3. **FOUND — dataset-distribution inventory.** The official code README links
   model objects in the `ai2i/strategyqa/` GCS namespace
   (`tests/fixtures/hg_stratqa/official-README.md:71`, `:79`). Searching its
   `strategyqa/data/` prefix retrieved the complete XML listing at
   `https://storage.googleapis.com/ai2i?prefix=strategyqa%2Fdata%2F&max-keys=100`:
   HTTP 200, 1043 bytes, SHA-256
   `5ad36b9105f97db169fbcddd907e898c87feba1fe8c092a14047471dd0be3fb6`.
   It lists `strategyqa/data/strategyqa_dataset.zip`, generation
   `1610016136750122`, size 3434332 bytes and `IsTruncated=false`
   (`tests/fixtures/hg_stratqa/dataset-gcs-list-quoted.body:1`). This is an
   observed distribution candidate in the author's linked bucket, not a
   recovered link from the inaccessible dataset landing page. The landing-page
   endorsement of this exact object remains **UNKNOWN**.

   A generation-pinned suffix Range GET returned **only** bytes
   `3430236-3434331/3434332`, HTTP 206, 4096 bytes, SHA-256
   `f764dced89fb17e3abb3f212aecad208b7a5cd238ffe0d5a786def584951df4b`
   (`tests/fixtures/hg_stratqa/dataset-zip-tail.receipt.json:1`). Its end-of-ZIP
   directory has four entries. Exact range request, binary parsing command and
   output are in `registry/w-stratqa-validation.txt`. The complete member-name
   inventory, without opening any dataset member, is retained at
   `tests/fixtures/hg_stratqa/dataset-zip-inventory.json:4`:

   ```text
   strategyqa_test.json
   strategyqa_train.json
   strategyqa_train_filtered.json
   strategyqa_train_paragraphs.json
   ```

   These are verbatim member names, not reconstructed split membership. The
   full ZIP was not downloaded and its SHA-256 was **not observed**. Header
   hashes/ETags are retained as server metadata and not substituted for a
   locally computed full-object digest.

4. **ABSENT, strictly bounded — dev/split-documentation member in that ZIP.**
   Scope is exactly the four central-directory members enumerated above, at the
   observed pinned GCS generation. No `dev`, README or split-generator member
   occurs in that complete inventory. Reproduce using the Range capture and
   `struct.unpack_from` enumeration recorded in validation; the named scope and
   observed entries are `tests/fixtures/hg_stratqa/dataset-zip-inventory.json:4`.
   This says nothing about unsearched archive contents, other objects, branches,
   tags, historical revisions or an external membership manifest.

5. **ABSENT, strictly bounded — GitHub Releases in the original code repo.**
   GET `https://api.github.com/repos/eladsegal/strategyqa/releases?per_page=100`
   returned HTTP 200 and exactly `[]` (2 bytes), SHA-256
   `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
   (`tests/fixtures/hg_stratqa/github-releases.body:1`). This is only the Releases
   endpoint's enumerated scope, not absence of Git tags or historical files.

6. **UNKNOWN — landing page and other distribution/history scopes.** The paper-
   and code-linked AllenAI landing page, with and without trailing slash,
   returned HTTP 403; it did not provide split definitions
   (`tests/fixtures/hg_stratqa/original-project.receipt.json:1`,
   `tests/fixtures/hg_stratqa/original-project-slash.receipt.json:1`). Candidate
   alternative domains and CDN attempts are separately enumerated below. The
   S3 candidate returned `NoSuchBucket`, and the guessed GitHub Pages path
   returned 404; neither establishes absence of original split definitions
   elsewhere (`tests/fixtures/hg_stratqa/dataset-s3-list-quoted.body:1`,
   `tests/fixtures/hg_stratqa/dataset-github-pages.receipt.json:1`). Tags, earlier
   Git history, evaluator Releases, leaderboard platform code and dataset rows
   were not searched. No whole-pool row matching was attempted.

What would settle the remaining clause: readable authoritative split membership
IDs (with original official Train/Test distinguished from the code's unofficial
train/dev), or a complete author-endorsed generator including input identity,
ordering, seed and assignments, followed by an independently authorized mapping
to local task IDs. A prose percentage, table count or filename is insufficient.
The local hash split is separately defined in `data/scaffolds/qa/base.py:299`;
none of the acquired sources supplies a membership equivalence proof.

## Parent integration and limits

The proposal preserves installed/ReWOO custody and the first-five packet. Its
replacement action retains the unresolved run-manifest/export reconciliation,
chosen split mode/side, applicable deterministic offline dependencies,
dataset-specific trusted runtime, execution equivalence and all coverage fields;
withdrawn shared requirements stay withdrawn
(`registry/dataset-blockers.json:1`, `registry/withdrawn-requirements.md:18`,
`:44`, `:60`). It does not authorize a diagnostic, execution or a pristine
opt-in. Existing F1/judge exclusions remain.

Selection discrepancy noted for review: the task brief says selected side eval,
but the retained packet explicitly has `side: "mixed"`, four train IDs and one
eval ID (`tests/fixtures/hg_wsel/strategyqa.json:45`). This worker does not change
any task, ordering, side or export, and the proposal preserves the existing
mixed-side reconciliation obligation. The packet itself declares no execution
authorization (`tests/fixtures/hg_wsel/strategyqa.json:6`).

No scorer, model endpoint, GPU, benchmark, dependency installation or historical
run was used. Apart from the first public sample object's answer-type inspection
documented above, no dataset row was decoded; the GCS ZIP's dataset members were
never opened. Frozen receipts and existing registry/journal files are unchanged;
the validation transcript records the source-only checks and the explicit list
of unverified properties (`registry/w-stratqa-validation.txt`).

## Complete request ledger

The following ledger is generated from each retained request receipt. FOUND
means the requested record/body is readable, not that either target definition
was found there. ABSENT is confined to the exact 404 URL. UNKNOWN covers denied
or unobserved content. Transport errors have no response digest because no
response body was observed. Query-quoting mistakes and their corrected requests
are preserved, with exact shell commands/output, in validation.

| Capture | Requested URL | State / HTTP status | Bytes; SHA-256 of exact response body | Retained evidence |
|---|---|---|---|---|
| `acl-record` | `https://aclanthology.org/2021.tacl-1.21/` | FOUND / 200 | 42676; `29498e7ea07a6ef1644287ce345653721a9fcfb97965145fa9904d9a86207dc3` | `tests/fixtures/hg_stratqa/acl-record.receipt.json:1` and `tests/fixtures/hg_stratqa/acl-record.body` |
| `arxiv-paper-html` | `https://ar5iv.labs.arxiv.org/html/2101.02235` | FOUND / 200 | 200954; `349e3bc2781e5aae797cff1d23fe3f4ab37c2f35e7ff3ed321a885080cff0292` | `tests/fixtures/hg_stratqa/arxiv-paper-html.receipt.json:1` and `tests/fixtures/hg_stratqa/arxiv-paper-html.body` |
| `dataset-gcs-list-quoted` | `https://storage.googleapis.com/ai2i?prefix=strategyqa%2Fdata%2F&max-keys=100` | FOUND / 200 | 1043; `5ad36b9105f97db169fbcddd907e898c87feba1fe8c092a14047471dd0be3fb6` | `tests/fixtures/hg_stratqa/dataset-gcs-list-quoted.receipt.json:1` and `tests/fixtures/hg_stratqa/dataset-gcs-list-quoted.body` |
| `dataset-gcs-list` | `https://storage.googleapis.com/ai2i?prefix=strategyqa%2Fdata%2F` | FOUND / 200 | 1021; `8072400b5f7ca7ecbecbe8df025519d465bd0b79bafac37ad6dd1582299e2b42` | `tests/fixtures/hg_stratqa/dataset-gcs-list.receipt.json:1` and `tests/fixtures/hg_stratqa/dataset-gcs-list.body` |
| `dataset-github-pages` | `https://allenai.github.io/strategyqa/` | ABSENT at URL / 404 | 9115; `70d613e3acfba24fd2876fcbacaf639e1e111ef4d54baf70761c47673f37d6a3` | `tests/fixtures/hg_stratqa/dataset-github-pages.receipt.json:1` and `tests/fixtures/hg_stratqa/dataset-github-pages.body` |
| `dataset-s3-list-quoted` | `https://strategyqa.s3.us-east-2.amazonaws.com/?list-type=2&prefix=data%2F&max-keys=100` | ABSENT at URL / 404 | 320; `25de5b558ecfc023960ca595d5b380be6c100b4bae4a24bad225e5fd66e48f47` | `tests/fixtures/hg_stratqa/dataset-s3-list-quoted.receipt.json:1` and `tests/fixtures/hg_stratqa/dataset-s3-list-quoted.body` |
| `dataset-s3-list` | `https://strategyqa.s3.us-east-2.amazonaws.com/?list-type=2` | ABSENT at URL / 404 | 320; `b1a5084824c6c4567dc93f8a3bf0db5448bf0b9107b0e747c547bae296ea3e48` | `tests/fixtures/hg_stratqa/dataset-s3-list.receipt.json:1` and `tests/fixtures/hg_stratqa/dataset-s3-list.body` |
| `dataset-zip-tail` | `https://storage.googleapis.com/ai2i/strategyqa/data/strategyqa_dataset.zip?generation=1610016136750122` | FOUND / 206 | 4096; `f764dced89fb17e3abb3f212aecad208b7a5cd238ffe0d5a786def584951df4b` | `tests/fixtures/hg_stratqa/dataset-zip-tail.receipt.json:1` and `tests/fixtures/hg_stratqa/dataset-zip-tail.body` |
| `evaluator-code-api` | `https://api.github.com/repos/allenai/strategyqa-evaluator/git/blobs/9717ac6bfd7f3428cb15aa87f3e0ab5873458ce1` | UNKNOWN / 403 | 279; `fdfea826e425097e5c9a8837c28e99ba8458ba5b55987f027beb9c87b208284b` | `tests/fixtures/hg_stratqa/evaluator-code-api.receipt.json:1` and `tests/fixtures/hg_stratqa/evaluator-code-api.body` |
| `evaluator-code-cdn` | `https://cdn.jsdelivr.net/gh/allenai/strategyqa-evaluator@49b88ed2b2f1b57385c13e8a0699dee1d227f83e/evaluator/eval.py` | UNKNOWN / unobserved: URLError: <urlopen error [Errno 104] Connection reset by peer> | No response body observed | `tests/fixtures/hg_stratqa/evaluator-code-cdn.receipt.json:1` |
| `evaluator-code-raw` | `https://raw.githubusercontent.com/allenai/strategyqa-evaluator/49b88ed2b2f1b57385c13e8a0699dee1d227f83e/evaluator/eval.py` | UNKNOWN / unobserved: URLError: <urlopen error [Errno 104] Connection reset by peer> | No response body observed | `tests/fixtures/hg_stratqa/evaluator-code-raw.receipt.json:1` |
| `evaluator-codeload` | `https://codeload.github.com/allenai/strategyqa-evaluator/zip/49b88ed2b2f1b57385c13e8a0699dee1d227f83e` | FOUND / 200 | 19726; `fd656478f987622655eca17a3a42995d83aaa407df05e71488146c2d47f0f1ba` | `tests/fixtures/hg_stratqa/evaluator-codeload.receipt.json:1` and `tests/fixtures/hg_stratqa/evaluator-codeload.body` |
| `evaluator-head` | `https://api.github.com/repos/allenai/strategyqa-evaluator/commits/main` | FOUND / 200 | 5461; `892b546fd96f1c7844c9dee0b9bb28baa6a65aea0c0cee64af87015d4e42658b` | `tests/fixtures/hg_stratqa/evaluator-head.receipt.json:1` and `tests/fixtures/hg_stratqa/evaluator-head.body` |
| `evaluator-html` | `https://github.com/allenai/strategyqa-evaluator/tree/49b88ed2b2f1b57385c13e8a0699dee1d227f83e` | UNKNOWN / unobserved: TimeoutError: The read operation timed out | No response body observed | `tests/fixtures/hg_stratqa/evaluator-html.receipt.json:1` |
| `evaluator-readme-cdn` | `https://cdn.jsdelivr.net/gh/allenai/strategyqa-evaluator@49b88ed2b2f1b57385c13e8a0699dee1d227f83e/README.md` | UNKNOWN / unobserved: URLError: <urlopen error [Errno 104] Connection reset by peer> | No response body observed | `tests/fixtures/hg_stratqa/evaluator-readme-cdn.receipt.json:1` |
| `evaluator-repository` | `https://api.github.com/repos/allenai/strategyqa-evaluator` | FOUND / 200 | 6516; `63679ea662992fb261b311eef9364e8080d081e51e00871bea0f4be3674a9102` | `tests/fixtures/hg_stratqa/evaluator-repository.receipt.json:1` and `tests/fixtures/hg_stratqa/evaluator-repository.body` |
| `evaluator-tree` | `https://api.github.com/repos/allenai/strategyqa-evaluator/git/trees/4f0051627e208629fffb1eacedd454f2cd89cf47?recursive=1` | FOUND / 200 | 3243; `0c8c9b22f3afecaee917310f44b3de108fd89c5307ea1d60267f428bc3bf8174` | `tests/fixtures/hg_stratqa/evaluator-tree.receipt.json:1` and `tests/fixtures/hg_stratqa/evaluator-tree.body` |
| `github-head` | `https://api.github.com/repos/eladsegal/strategyqa/commits/main` | FOUND / 200 | 5659; `af0365d7c5a609118929baa31a3535f752c9d10ae08616bde1fcacd8be56bb54` | `tests/fixtures/hg_stratqa/github-head.receipt.json:1` and `tests/fixtures/hg_stratqa/github-head.body` |
| `github-releases` | `https://api.github.com/repos/eladsegal/strategyqa/releases?per_page=100` | FOUND / 200 | 2; `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | `tests/fixtures/hg_stratqa/github-releases.receipt.json:1` and `tests/fixtures/hg_stratqa/github-releases.body` |
| `github-repository` | `https://api.github.com/repos/eladsegal/strategyqa` | FOUND / 200 | 5469; `94a2b37515343a41ec3f0856edf6034c4c64eb1d03df13ad1e21c7d1488c9339` | `tests/fixtures/hg_stratqa/github-repository.receipt.json:1` and `tests/fixtures/hg_stratqa/github-repository.body` |
| `github-tree` | `https://api.github.com/repos/eladsegal/strategyqa/git/trees/b31bdc2f04bb48d60672e606ad5974a83f70127f?recursive=1` | FOUND / 200 | 25366; `0351f169ea413b2114dcbbd3fe205f9e1054e7427437c98ba381f49e0aafbbee` | `tests/fixtures/hg_stratqa/github-tree.receipt.json:1` and `tests/fixtures/hg_stratqa/github-tree.body` |
| `official-config-cdn` | `https://cdn.jsdelivr.net/gh/eladsegal/strategyqa@1ba1e97452e189569357876f2854b01357ffbe37/configs/strategy_qa/base.jsonnet` | UNKNOWN / unobserved: URLError: <urlopen error [Errno 104] Connection reset by peer> | No response body observed | `tests/fixtures/hg_stratqa/official-config-cdn.receipt.json:1` |
| `official-config` | `https://raw.githubusercontent.com/eladsegal/strategyqa/1ba1e97452e189569357876f2854b01357ffbe37/configs/strategy_qa/base.jsonnet` | UNKNOWN / unobserved: URLError: <urlopen error [Errno 104] Connection reset by peer> | No response body observed | `tests/fixtures/hg_stratqa/official-config.receipt.json:1` |
| `official-evaluate` | `https://raw.githubusercontent.com/eladsegal/strategyqa/1ba1e97452e189569357876f2854b01357ffbe37/run_scripts/evaluate.py` | UNKNOWN / unobserved: URLError: <urlopen error [Errno 104] Connection reset by peer> | No response body observed | `tests/fixtures/hg_stratqa/official-evaluate.receipt.json:1` |
| `official-readme` | `https://raw.githubusercontent.com/eladsegal/strategyqa/1ba1e97452e189569357876f2854b01357ffbe37/README.md` | UNKNOWN / unobserved: URLError: <urlopen error [Errno 104] Connection reset by peer> | No response body observed | `tests/fixtures/hg_stratqa/official-readme.receipt.json:1` |
| `original-project-ai2` | `https://ai2.org/data/strategyqa` | UNKNOWN / unobserved: URLError: <urlopen error [Errno -5] No address associated with hostname> | No response body observed | `tests/fixtures/hg_stratqa/original-project-ai2.receipt.json:1` |
| `original-project-slash` | `https://allenai.org/data/strategyqa/` | UNKNOWN / 403 | 134; `c996c0469ef05ff6fdd1f7cefbc3f7e109bb21969de42fcf591498a828a7ad5f` | `tests/fixtures/hg_stratqa/original-project-slash.receipt.json:1` and `tests/fixtures/hg_stratqa/original-project-slash.body` |
| `original-project` | `https://allenai.org/data/strategyqa` | UNKNOWN / 403 | 134; `c996c0469ef05ff6fdd1f7cefbc3f7e109bb21969de42fcf591498a828a7ad5f` | `tests/fixtures/hg_stratqa/original-project.receipt.json:1` and `tests/fixtures/hg_stratqa/original-project.body` |
| `readme-api` | `https://api.github.com/repos/eladsegal/strategyqa/git/blobs/feee1f309586a3cfb4151570af2763dc0726a3f6` | FOUND / 200 | 16014; `5b2a93ec88615e11b89616e381660f2795b8d32dee37e5611549bfd45bb1c8fc` | `tests/fixtures/hg_stratqa/readme-api.receipt.json:1` and `tests/fixtures/hg_stratqa/readme-api.body` |
