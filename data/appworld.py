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

1. **What is missing is the oracle.** Each task directory holds `specs.json` (the instruction
   and the supervisor), `dbs/*.jsonl` (the initial world state),
   `ground_truth/{public_data.json, private_data.json, evaluation.py, answer.json}` and a
   `metadata.json` that records `num_solution_code_lines` -- the *length* of a solution that
   was generated and is **not** in the release. So the metric is present and runnable (the
   official evaluator is `appworld.evaluator`, driven by each task's `evaluation.py`), while
   gate 1's oracle would have to be an **authored** API-call program validated by that state
   test. `data/qa/control.py --oracle` submits the dataset's own reference answer; AppWorld
   has none to submit. On 2026-10-08 the platform owner authorised exactly that contract
   change (authored, test-validated references, held out of the agent's view), so this refusal
   is now a **work item**: the onboarding has to build the world, the evaluator invocation and
   the authored reference, not re-decide the pool.

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
    "appworld: the pinned v0.1.3.post1/data-0.1.0 release carries each task's state test "
    "(ground_truth/evaluation.py) but **no reference solution** -- its metadata records "
    "num_solution_code_lines for a program that was never released -- and the answer contract "
    "has no channel for a reference action program, so gate 1's oracle would have to be "
    "authored and validated by the state test. The pool is not the obstacle: the release "
    "declares its own 732 tasks across train/dev/test_normal/test_challenge (90/57/168/417, "
    "all present), and the paper's 750 differs only in train and dev (105/60 -> 90/57, six "
    "scenarios). This adapter refuses until the platform's authored-reference contract is "
    "implemented, rather than shipping an oracle arm that has never run."
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

