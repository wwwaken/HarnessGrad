# Reasoning Gym installed-byte custody - w-prov

`w-prov reasoning_gym installed package and generated-pool custody`

The adapter reads `/mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl` for
questions/entry gold. Its scorer imports the installed `reasoning_gym.create_dataset`
and calls each family's `score_answer`; it does not read a downloaded benchmark split.
The generator pin in `data/datasets/reasoning_gym/prepare.py` is version 0.1.25,
seed 20261008, 89 listed families, and 20 entries per family. This provenance tool directly invoked no scorer, model, GPU,
or benchmark pilot; direct scorer absence is source-inspected, not transitive instrumentation.

## Public artifact and revision binding

Preserved `responses/` bodies are the actual HTTP bytes; each has response headers,
request/final URL, status, timestamp, size and body/header SHA-256 receipt. Acquisition
used Python urllib with `Accept-Encoding: identity`; the two `acquire-*-recorded.py`
files preserve that code with worktree-dependent paths made relative for replay.
Replaying acquisition contacts public PyPI/GitHub and replaces responses; offline
verification does not contact the network.

- PyPI `reasoning_gym-0.1.25-py3-none-any.whl`: 6,985,897 bytes,
  SHA-256 `7f17a3eddb13c015d7d4a755ed576a061df889faf9468bcc2cca334ebe9e0435`.
- PyPI `reasoning_gym-0.1.25.tar.gz`: 6,789,585 bytes,
  SHA-256 `932247c760dd23e09fb14d013d29ec4c8804e62846bd50473f6915dc854adad2`.
- Both sizes and digests match the preserved PyPI release JSON.
- The preserved GitHub tag response maps `v0.1.25` to commit
  `21e6d2a9a581b3e11aafe711abfd37402f8482d5`, whose tree is
  `7b504fd884ea8a07914aa5e4e042c26fb563fc10`.
- For **all 200 `reasoning_gym/` code/data members**, the wheel and sdist contain
  identical bytes, and `SHA1("blob " + decimal_size + NUL + member_bytes)` matches
  the exact path's Git blob in that commit's preserved, nontruncated recursive tree.
  Every wheel member also passes its archived `RECORD` SHA-256 and size.

This is a byte-level source-payload binding to the named commit, independently of a
version string. GitHub's API reports a verified commit signature; this tool does not
independently verify that signature. PyPI's artifact provenance endpoints returned
404 for both artifacts, preserved verbatim. No build attestation establishes the
uploader/builder identity or proves the wheel's generated packaging metadata was
built by that commit. The exact published archives and their runtime package payload
are nevertheless pinned by real SHA-256s and the source-content comparison above.

## Actual installed package

`capture_installed.py` reads the observed interpreter's distribution via
`importlib.metadata` without importing generators. `installed-members.json` records
all 205 wheel paths, actual installed path/size/SHA-256 and wheel path/size/SHA-256.
The interpreter is `/mnt/8t/xubuqiang/anaconda3/bin/python3`, Python 3.12.4.
All 200 package code/data members and the four other non-RECORD metadata members
match the published wheel byte for byte. The sole difference is pip's rewritten
`reasoning_gym-0.1.25.dist-info/RECORD`; its exact installed bytes are preserved in
`installed-RECORD.body`. No additional non-pycache package files were found.
`direct_url.json` was absent, so the historical installer command/source URL cannot
be recovered; observed byte equality is the custody evidence. This does not bind
transitive dependencies or a pristine production verifier namespace.

## Pool, family structure and selection

The parent fixture preserves the actual pool as `../installed/reasoning_gym.jsonl`.
It is 3,315,981 bytes, SHA-256
`c0ff4eaef318cd59afcc61472ebe206362fc0211c4b589ed0d53946a569bd177`, exactly the
adapter's declared pool digest. Offline inspection confirms 1,780 rows, 89 families
in family-major order with indices 0–19, nonempty entry answers, and IDs
`reasoning_gym/eval/<row_position>`. The adapter loads all rows. Its hash-third
platform rule derives 1,216 train and 564 eval IDs; this is a platform division,
not an upstream official split or a pilot selection. No run-specific selected
manifest was supplied or acquired. The parent structural manifest records selection
as null; this tool does not invent one.

Nonempty answers and family/index structure are statically verified. The family
eligibility claim (reference scores 1.0, empty scores 0.0) and the deterministic,
offline scorer claim remain untested here. Those require the remaining official
scorer/offline/runtime gates. Public sources alone cannot authenticate the original
local generation event or a run selection: no public published pool or selected manifest was authenticated from the
acquired sources.

## Bounded provenance regeneration

`regenerate.py` performs an independent CPU-only regeneration in a new `/tmp`
scratch directory, using the authenticated installed package and the declared seed,
family list and item count. It never calls `score_answer`. It limits CPU to 120 s,
address space to 4 GiB and the recorded shell command adds a 180 s wall timeout.
Python audit hooks deny socket/process operations and confine writes to scratch;
bytecode writing is disabled. The policy is a provenance-tool check, not proof of
production sandbox enforcement. Declared dependency versions are recorded, but
those dependencies are not independently authenticated artifacts in this fixture.
Each attempt's exact script, raw stdout/stderr and outcome are preserved; only a
whole-pool byte equality can support reproduction in the observed environment.

- Attempt 1 (exit 1): global write denial rejected matplotlib's idempotent mkdir of
  its existing config directory. No pool reproduction was completed.
- Attempt 2 (exit 1): permitting only existing directory mkdir reached all 1,780
  rows, but CodeIO index 9's generator writes a CSV; denying that write produced its
  documented empty I/O fallback. Generated bytes were 3,315,876 with SHA-256
  `624b5598b38a4a22cd163aef2afe5f0d4c01a3534bdb4f20e724a061d7993efe`; this constrained
  mismatch does not establish that the original pool seed is wrong.
- Attempt 3 (exit 1): scratch-only writes were allowed, but receipt construction
  used a relative prepare path after changing into scratch, causing a
  FileNotFoundError. No successful equality receipt was emitted.
- Attempt 4 (exit 1): generation completed, but the audit hook mishandled
  dir_fd-relative tempfile cleanup after returning to the repository cwd. No
  completed equality receipt was emitted. `attempt-4-cleanup-recovery.json` and
  `attempt-4-scratch-file.body` preserve the 190-byte generated CSV's digest and
  subsequent cleanup recovery; the leftover scratch directory was removed.
- Attempt 5 (exit 1): generation and scratch cleanup completed. Raw JSON stdout
  records 1,780 rows, 3,315,958 generated bytes and SHA-256
  `d00b2b1cb8134ee37c7b76fce5547cb3e2c44a247dfa07beaa984385532cffd1`, with
  whole-pool equality **false**. Exactly 84 rows differ across six families:
  `isomorphic_strings` (20), `knight_swap` (16), `polynomial_multiplication` (12),
  `ransom_note` (20), `time_intervals` (9), and `word_ladder` (7).
  The byte count/hash and coordinate list are observed process outputs; the
  complete newly generated pool was retained only in memory, not preserved as a
  new dataset. `attempts.json` binds each executed script snapshot and stdout/stderr
  bytes, exit codes and full reproduction command. The final script SHA-256 in
  its raw JSON must match `attempt-5-script.py` and `regenerate.py`.

Consequently the installed pool digest is authenticated as local bytes, but a
complete package/seed-to-pool reproduction is **not** established. The immutable
source payload exposes additional environment-sensitive inputs: isomorphic strings
and ransom note use `rng.choice(list(set_of_letters))`; knight swap traverses
frozensets; word ladder's BFS traverses neighbor sets; polynomial multiplication
materializes SymPy `itermonomials` before random choice; time intervals uses
`date.today()` when creating metadata. These are concrete static limitations of a
version-plus-seed-only declaration. This does not identify the original generation
process's hash randomization state, date or full environment, nor prove each
mismatch's precise causal path. No environment search, family changes, generator
patching or rerun to force the published digest was performed.

Run offline verification after integration:

```sh
python3 tests/fixtures/hg_wprov/reasoning_gym/verify.py
```

Recheck actual installed bytes into a new observation (writes only the requested
receipt and installed RECORD copy), or rerun bounded generation explicitly:

```sh
python3 tests/fixtures/hg_wprov/reasoning_gym/capture_installed.py --output /tmp/hg-rg-new-installed-members.json
PYTHONDONTWRITEBYTECODE=1 timeout 180s python3 tests/fixtures/hg_wprov/reasoning_gym/regenerate.py --prepare data/datasets/reasoning_gym/prepare.py --pool /mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl
```

No blocker is closed. Remaining work includes selected-manifest custody,
behavioral family eligibility, transitive dependency/offline scorer closure,
pristine trusted-verifier/runtime evidence and all shared admission gates.
