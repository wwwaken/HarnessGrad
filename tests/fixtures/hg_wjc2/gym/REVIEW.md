# Reasoning Gym original-generation record follow-up — w-jc2

`w-jc2 reasoning_gym effective-date and historical-pin corroboration; original generation record not recovered`

This packet partially advances the next action in reports/w-journalcov-review.md.
It does not satisfy that action and does not close a dataset or shared blocker.
Only the original-generation-record branch is inspected here. No generator,
score_answer, model, endpoint, selected manifest or benchmark run is executed.

## What moved

The actual pool was freshly read and independently hashed. Its SHA-256 remains
`c0ff4eaef318cd59afcc61472ebe206362fc0211c4b589ed0d53946a569bd177`,
3,315,981 bytes, 1,780 rows (`observations.json:3`, `independent-digests.stdout.txt:1`).
The nine time-only metadata rows, indices 0, 2, 7, 8, 9, 10, 15, 18 and 19,
all retain start and end calendar dates `2026-10-08`; their exact pool line numbers,
values and recomputed count/date sets are in `observations.json:12` and
`observations.json:77`. These are effective dates carried in stored entries,
not authenticated timestamps of the original process.

The current installed source shows why calendar date is an input even though
these questions only display times. The generator calls `date.today()` at
`/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym/arithmetic/time_intervals.py:167`,
formats time-only strings, then calls `parser.parse(start_time)` without a default
at the same file's line 104 (end time at line 105). The installed dateutil parser
uses `datetime.datetime.now()` for the unspecified calendar fields at
`/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/dateutil/parser/_parser.py:637`.
The generator serializes the parsed result into metadata at time_intervals.py:142.
Lossless JSON-quoted source lines, including every locator just cited, are retained
in `source-lines.txt:105`, `source-lines.txt:143`, `source-lines.txt:168` and
`source-lines.txt:2795`. Their whole-file SHA-256 values are independently recomputed:
time_intervals.py `b42d9a9f992eead49d028f13e0ffd454b24676f92402e1a323cbabdd74d20100`
and dateutil _parser.py `ee494377289c92c401fd7825fb7500981c33098a2bd40219aa4948713e9d1fff`
(`independent-digests.stdout.txt:2`, `independent-digests.stdout.txt:3`).
The present dateutil bytes are a current source observation, not an authenticated
record of the original process's dependency version.

`git log --all --follow` reaches the original introduction commit
`0f47b1240c739fefb0472e4f73ac71a2c8b6d927`, recorded with author/commit date
2026-10-08 (`generation-history.stdout.txt:17`). Its original adapter already pins
this exact pool digest (`original-reasoning_gym.py:73`) and its original generator
records version 0.1.25, seed 20261008 and per-family count 20
(`original-prepare.py:39`, `original-prepare.py:44`, `original-prepare.py:45`).
The recovered generator's SHA-256 is
`0ac637564179a4008504707f5b92c0ce13e10013e30151fe4bfa09636f199ce9`;
the original adapter's is
`65f8dffb19af3c32c124a0edcadd8d6df0f12716cbee7271ea25b9a59d68beab`
(`independent-digests.stdout.txt:4`, `independent-digests.stdout.txt:5`).
The captured original-to-current generator diff changes path spelling and root-depth
only (`historical-prepare-diff.stdout.txt:1`); it adds no historical environment pin.
Current pool mtime/ctime are 2026-10-08T06:12:33.442175+00:00
(`observations.json:8`). Those filesystem values and commit dates corroborate the
stored effective date but cannot authenticate the generation command, process
clock, timezone, hash secret or dependency environment.

Fresh offline verification of the inherited authenticated package/source/member
custody passes (`old-provenance-verify.stdout.txt:1`). This rechecks existing PyPI/
GitHub source-payload evidence, including the earlier failed byte reproduction;
it neither reacquires public sources nor reruns generation. No new HTTP request
or source response is claimed in this packet.

## What did not move

The exact original launch/environment receipt was not recovered from the inspected
locations: the installed dataset directory inventory (`local-files.stdout.txt:1`),
current generator/adapter/docs and preserved attempt command fields
(`current-record-search.command.json:2`), original introduction-commit files
(`historical-record-search.command.json:2`) and scoped tracked generator/adapter/test
history (`git-tracked-environment-search.command.json:2`). This is not an exhaustive
absence claim for the machine, private operator records, shell/session logs or
external archives. The dataset directory inventory lists the pool only; existing
pool filesystem metadata supplies no environment record.

The original generator and adapter declare the package/seed/count, but no launch
hash-order setting or full dependency lock at those inspected source locations.
Current package metadata has loose SymPy/PyYAML/pytz/zss constraints
(`source-lines.txt:1979`); today's installed versions are not historical pins.
The inspected immutable code still consumes unordered letter sets, frozensets,
neighbor sets and SymPy itermonomials before random choice
(`corrected-source-locators.stdout.txt:4`, `corrected-source-locators.stdout.txt:20`,
`corrected-source-locators.stdout.txt:23`, `corrected-source-locators.stdout.txt:52`).
A date clue cannot recover those process-specific inputs. The old completed
regeneration receipt remains unequal with 84 mismatching rows in six families
(`old-provenance-verify.stdout.txt:3`). No attempt is replaced or resumed.

## Single remaining blocker to this next action

The upstream/operator input needed is the original pool producer's process receipt,
bound to the exact pool digest above: invocation and interpreter/build identity;
original effective clock date/timezone; launch-time PYTHONHASHSEED plus interpreter
hash implementation (or retained effective set/iteration order/hash-secret evidence
if the process used randomized hashing); and the dependency/artifact/build lock,
particularly the generator's SymPy and dateutil environment. An unset/random hash
seed alone would not recover the realized process hash secret. This input must come
from the original producer's preserved environment/launch records, not a new chosen
seed, current environment snapshot, or date-matched rerun. Without it, an exact
historical-environment reconstruction and justified byte-reproduction attempt remain
unavailable. The carried date narrows that request but does not satisfy its process
record clause. All other existing selection, behavioral eligibility, runtime and
shared-admission obligations remain unchanged.

## Raw output and validation

`capture.py` retains each command's argv/cwd/time/exit and exact stdout/stderr.
Git raw outputs with whitespace-only lines and the first staged-check output use reversible JSON-quoted
lines, marked stdout_storage in their command receipts; decoded raw SHA-256 remains
the original command output. Source snapshots are also JSON-quoted line by line.
`inspect_provenance.py` performs read-only parsing, hashing and git-show capture;
it never imports reasoning_gym. `observations.json` is reproduced by
`inspect-with-parser.command.json`; `independent-digests.command.json` is an
independent sha256sum check. The earlier `inspect` failure is retained: naming the
first script inspect.py shadowed the standard library; it was renamed before the
successful inspection. `source-locators` retains an incorrect word_ladder path and
its nonzero exit; `corrected-source-locators` uses the real algorithmic path.
The original/current diff intentionally exits 1 for differing files. These are
inspection/tool-development outcomes, not scoring results.

A checksum invocation from repo cwd found no files because SHA256SUMS paths are
packet-relative; that raw failure is preserved, followed by the corrected cwd check.
An initial staged whitespace check rejected git output whitespace-only lines;
reversible JSON quoting preserves those raw bytes and makes the final check pass.

Registry checks before and after pass. No registry, journal, production source,
runs/, frozen receipt or main checkout is changed by this child task. The parent
owns the combined report, any qualified observed update and journal entry.
