"""AppWorld v0.1.3.post1: refused -- the release ships the state tests and no reference
solution.

**The pool is settled and is not a reason to refuse.** The first version of this file refused
partly because the release holds 732 tasks while the paper describes 750, and claimed that
"nothing in it says which 18 are missing". The release answers both halves itself: it carries
its own split files, and both published bundles declare **732** tasks --

    data/datasets/train.txt            90    (the paper says 105)
    data/datasets/dev.txt              57    (the paper says  60)
    data/datasets/test_normal.txt     168    (the paper says 168)
    data/datasets/test_challenge.txt  417    (the paper says 417)

Every declared id is present in the bundle, the four files sum to 732, and each of the 732
task directories appears in exactly one of them. `data-0.2.0.bundle` -- a later build
(Last-Modified 2025-10-14) -- adds a `_base_` template world and nothing else: the same 732
tasks with identical split membership. So the published **750** ("250 task scenarios with 3
tasks each, totaling 750 tasks, split into Train (105), Dev (60), Test-N (168), and Test-C
(417)", Trivedi et al., ACL 2024, arXiv 2407.18901v2) is the paper-era build, and the delta
is confined to train and dev: 105 -> 90 and 60 -> 57 is exactly 18 tasks = **six scenarios**,
while both test splits are unchanged. A run over the release is therefore a run over the
release's own declared division -- `SPLIT_SOURCE == "declared"`, not a hash -- and the
adapter names which of the four splits it scores.

1. **The release *does* ship reference programs -- for 147 of the 732 tasks, and this module
   said otherwise for a round.** Measured from the pinned bundle: `ground_truth/solution.py`,
   `ground_truth/compiled_solution.py` and `ground_truth/api_calls.json` exist for exactly
   **train (90) + dev (57) = 147** tasks, and for **zero** of `test_normal` (168) +
   `test_challenge` (417), which ship `ground_truth/evaluation.py` only. The earlier claim
   ("its metadata records `num_solution_code_lines` for a program that was never released") was
   generalised from a single task -- `92fe421_3`, which happens to sit in `test_challenge`. That
   matters, because `api_calls.json` is a list of `{method, url, data}`: the benchmark's own
   **replayable action log**, i.e. exactly the log-replay mechanism `appworld verify tasks` uses,
   so the oracle for those 147 tasks is *released data* rather than anything we author.
   `ORACLE_SOURCE` is therefore `released` with a declared `ORACLE_COVERAGE` of 147 of 732, and
   `oracle_files()` raises for the other 585 -- which are scorable (their state tests are
   present) but whose zeros the oracle control cannot vouch for. Nothing here needs the
   authored-reference contract after all.
2. **What is genuinely missing is the action surface**, which is why this is still a refusal:
   the tasks are interactive (the agent calls app APIs and the world's state is graded), so the
   dataset needs an `exec` environment, a way for the agent to act across many steps, and a check
   that replays the log and runs the official evaluator. `tools/dataset_lint.py` refuses a
   dataset whose tasks cannot run, and there is no half-onboarding that proves gates 1 and 2.

The decryption is not an obstacle and is reproduced by the test rather than asserted:
AES-256-CFB with `iv = ciphertext[:16]` and a PBKDF2-HMAC-SHA256 key, using the **public**
constants in the pinned package (`appworld/common/constants.py`:

    PASSWORD = "WEquKLy##9M@qu"
    SALT = b"Nvx#rYcYQ2%btf"

which upstream annotates "These do not have to be hidden; it's just to prevent automated
scraping"), transcribed from `appworld/common/utils.py::encryption_key` (2442-2454),
`::decrypt_bytes` (2471-2481) and `::unpack_bundle` (2570-2584). The bundle's own
`README_BEFORE_SHARING.md` also carries the licence's extra requirement that any public
redistribution of it *or of its derivatives* be encrypted, which is one more reason the data
stays outside the repository and is fetched from the official URL by digest.

Running the evaluator itself needs the pinned `appworld` package installed, because
`evaluation.py` imports `appworld.apps.*`, `appworld.collections.models` and
`appworld.evaluator.TestTracker`.

What would make it reachable: the authored-reference contract (decided) plus the adapter work
it needs -- an `exec` environment, the pinned package, and one reference program per task the
control arm is expected to prove reachable. Until that lands this adapter refuses, rather
than shipping a half-onboarding whose oracle arm nobody has run.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

KIND = "dataset"
DATASET_ROOT = Path("/mnt/20t/xubuqiang/datasets/appworld")
#: The released pool, re-derived by the test (decrypt -> read the split files -> count).
TASKS_IN_RELEASE = 732
#: The release's own four splits, and how many tasks each declares. These are the division
#: the platform will use (`SPLIT_SOURCE == "declared"`), so they are constants rather than
#: folklore.
SPLIT_SIZES = {"train": 90, "dev": 57, "test_normal": 168, "test_challenge": 417}
#: The paper's build (arXiv 2407.18901v2). Recorded because the difference between this and
#: `SPLIT_SIZES` is the whole of the "732 vs 750" question: it is confined to train and dev.
PAPER_SPLITS = {"train": 105, "dev": 60, "test_normal": 168, "test_challenge": 417}

REFUSED = (
    "appworld: the oracle is **released**, not missing -- train (90) + dev (57) = 147 of the 732 "
    "tasks ship ground_truth/solution.py and a replayable ground_truth/api_calls.json, while the "
    "585 test tasks ship state tests only, so the declaration is `released` with an "
    "ORACLE_COVERAGE of 147 of 732. What this dataset cannot express yet is the **action "
    "surface**: the answer contract grades a finished artifact (a file, a query, a patch), and "
    "these tasks are graded on the state a world is left in after a sequence of app API calls, "
    "which the platform expresses as an `exec` environment plus a `services` sidecar holding the "
    "world and its log. Until that is built there is no oracle arm an author could run, and this "
    "adapter refuses rather than shipping one that has never been shown to reach 1."
)


def bundle_zip(bundle_path: Path | str | None = None) -> zipfile.ZipFile:
    """The decrypted bundle, in memory: `unpack_bundle` without writing 14,696 files.

    In-memory because the only reason this module decrypts at all is to *count* -- the
    refusal's numbers are measurements, and a measurement that needs a scratch directory is
    a measurement that will not be re-run. `cryptography` is imported here rather than at
    module level so that `data/registry.py::published()` can import this module on a machine
    without it.
    """
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    path = Path(bundle_path) if bundle_path else DATASET_ROOT / "_src" / "data-0.1.0.bundle"
    data = path.read_bytes()
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=SALT,
                     iterations=100000).derive(PASSWORD.encode())
    decryptor = Cipher(algorithms.AES(key), modes.CFB(data[:16])).decryptor()
    plain = decryptor.update(data[16:]) + decryptor.finalize()
    return zipfile.ZipFile(io.BytesIO(plain))


#: `appworld/common/constants.py`, which upstream says need not be hidden.
PASSWORD = "WEquKLy##9M@qu"
SALT = b"Nvx#rYcYQ2%btf"


def task_ids(bundle_path: Path | str | None = None) -> list[str]:
    """Every task the release contains, sorted -- `tasks/<id>/ground_truth/evaluation.py`."""
    with bundle_zip(bundle_path) as archive:
        prefix, suffix = "data/tasks/", "/ground_truth/evaluation.py"
        ids = {name[len(prefix):-len(suffix)] for name in archive.namelist()
               if name.startswith(prefix) and name.endswith(suffix)}
    return sorted(ids)


def split_ids(bundle_path: Path | str | None = None) -> dict[str, list[str]]:
    """The release's **own** division, from `data/datasets/<split>.txt` inside the bundle.

    This is the file that settles "732 or 750", and the platform's division should be this
    rather than a hash: the benchmark states its own two test splits, so a run can say which
    of them it scored. The four files are the release's, not a reconstruction -- each of the
    732 task directories appears in exactly one of them and every declared id is present.
    """
    with bundle_zip(bundle_path) as archive:
        return {name: [line.strip() for line in
                       archive.read(f"data/datasets/{name}.txt").decode("utf-8").splitlines()
                       if line.strip()]
                for name in SPLIT_SIZES}


def downloads() -> list[dict]:
    return [{"kind": "http", "name": "AppWorld data bundle",
             "version": "v0.1.3.post1/data-0.1.0",
             "url": "https://s3.us-west-2.amazonaws.com/appworld.dev/data-0.1.0.bundle",
             "dst": "_src/data-0.1.0.bundle", "size": "34280074 bytes",
             "sha256": "fd9f9608c2ec71ed0ac25c3633a738b9129a318a129e31230425b9188e508250",
             "note": "Official encrypted AppWorld bundle. Decryptable offline with the public PASSWORD/SALT in the pinned package (see this module): 14,696 members, 732 task directories across the release's own four splits (90/57/168/417), each with its state test and no solution program. `data-0.2.0.bundle` is a later build of the same 732 (plus a `_base_` template world). The evaluator additionally needs `appworld==0.1.3.post1` installed, which is why the bundle alone cannot make the dataset runnable. The bundle's README_BEFORE_SHARING.md requires that any public redistribution of it or its derivatives stay encrypted, which is one more reason the data is fetched here and never committed."}]


def load():
    raise ValueError(REFUSED)


def provision_status() -> dict:
    return {"root": str(DATASET_ROOT),
            "present": (DATASET_ROOT / "_src" / "data-0.1.0.bundle").is_file(),
            "tasks": TASKS_IN_RELEASE,
            "splits": dict(SPLIT_SIZES)}


__all__ = ["KIND", "DATASET_ROOT", "REFUSED", "TASKS_IN_RELEASE", "SPLIT_SIZES",
           "PAPER_SPLITS", "PASSWORD", "SALT", "bundle_zip", "task_ids", "split_ids",
           "downloads", "load", "provision_status"]

