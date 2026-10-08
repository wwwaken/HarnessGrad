"""AppWorld v0.1.3.post1: refused -- no reference solution in the release, and the released
pool is not the published suite.

Two measurements decide this, and the first version of this file stated only the weaker one
(a task-count mismatch) while inventing a stronger one it had not checked ("the protected
evaluator ... is unreproducible"). Both are now measured, and the order matters: the
*contract* reason is the one that blocks gate 1, because the release ships the state tests
and not the solution.

1. **The release ships `ground_truth/evaluation.py` and no solution program.** Each task
   directory holds `specs.json` (the instruction and the supervisor), `dbs/*.jsonl` (the
   initial world state), `ground_truth/{public_data.json, private_data.json, evaluation.py,
   answer.json}` and a `metadata.json` that records `num_solution_code_lines` -- the
   *length* of a solution that was generated and is **not** in the release. So the metric is
   present and runnable (the official evaluator is `appworld.evaluator`, driven by each
   task's `evaluation.py`), while gate 1's oracle would have to be an **authored** API-call
   program validated by that state test. `data/qa/control.py --oracle` submits the dataset's
   own reference answer; AppWorld has none to submit, which is a contract change and a
   platform decision, not an adapter detail.

2. **The released pool is 732 tasks; the published suite is 750.** Decrypting the pinned
   `data-0.1.0.bundle` (34,280,074 bytes, sha256
   `fd9f9608c2ec71ed0ac25c3633a738b9129a318a129e31230425b9188e508250`) yields a zip of
   14,696 members and exactly **732** `tasks/<id>/ground_truth/evaluation.py` files. The
   paper describes "a suite of 750 natural, diverse, and challenging autonomous agent
   tasks" (Trivedi et al., ACL 2024, arXiv 2407.18901v2). Eighteen tasks are therefore not
   in the release, and nothing in it says which: a score over 732 cannot be compared with a
   published number, and the scenario metric's grouping by generator id does not fix that.

The decryption is not an obstacle and is reproduced in the test rather than asserted:
AES-256-CFB with `iv = ciphertext[:16]` and a PBKDF2-HMAC-SHA256 key, using the **public**
constants in the pinned package (`appworld/common/constants.py`:

    PASSWORD = "WEquKLy##9M@qu"
    SALT = b"Nvx#rYcYQ2%btf"

which upstream annotates "These do not have to be hidden; it's just to prevent automated
scraping"), transcribed from `appworld/common/utils.py::encryption_key` (2442-2454),
`::decrypt_bytes` (2471-2481) and `::unpack_bundle` (2570-2584). Running the evaluator
itself needs the pinned `appworld` package installed, because `evaluation.py` imports
`appworld.apps.*`, `appworld.collections.models` and `appworld.evaluator.TestTracker`.

What would make it reachable: name the exact released split (so a number can say which 732
tasks it is over) and decide the authored-oracle contract, or pin a release that matches the
published suite. Either one is a real task, which is why this is a refusal and not a
half-onboarding.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

KIND = "dataset"
DATASET_ROOT = Path("/mnt/20t/xubuqiang/datasets/appworld")
#: The released pool, re-derived by the test (decrypt -> count `ground_truth/evaluation.py`).
TASKS_IN_RELEASE = 732
#: The published suite size (arXiv 2407.18901v2, abstract). Recorded because the difference
#: is the comparability problem, not because it is the number to use.
PUBLISHED_SUITE = 750

REFUSED = (
    "appworld: the pinned v0.1.3.post1/data-0.1.0 release carries each task's state test "
    "(ground_truth/evaluation.py) but **no reference solution** -- its metadata records "
    "num_solution_code_lines for a program that was never released -- so gate 1's oracle "
    "would have to be authored and validated by the state test, and the answer contract has "
    "no channel for a reference action program. The released pool is also 732 tasks while "
    "the published suite is 750 (arXiv 2407.18901v2), with nothing in the bundle saying "
    "which 18 are missing, so a score over it is not comparable with a published number. "
    "Onboarding this dataset needs two decisions, not an implementation: name the exact "
    "released subset, and adopt an authored-oracle contract (or pin a release that matches "
    "the published suite). This adapter refuses rather than reporting a nearby 732-task "
    "number under the benchmark's name."
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


def downloads() -> list[dict]:
    return [{"kind": "http", "name": "AppWorld data bundle",
             "version": "v0.1.3.post1/data-0.1.0",
             "url": "https://s3.us-west-2.amazonaws.com/appworld.dev/data-0.1.0.bundle",
             "dst": "_src/data-0.1.0.bundle", "size": "34280074 bytes",
             "sha256": "fd9f9608c2ec71ed0ac25c3633a738b9129a318a129e31230425b9188e508250",
             "note": "Official encrypted AppWorld bundle. Decryptable offline with the public PASSWORD/SALT in the pinned package (see this module): 14,696 members, 732 task directories, each with its state test and no solution program, against a published suite of 750. The evaluator additionally needs `appworld==0.1.3.post1` installed, which is why the bundle alone cannot make the dataset runnable."}]


def load():
    raise ValueError(REFUSED)


def provision_status() -> dict:
    return {"root": str(DATASET_ROOT),
            "present": (DATASET_ROOT / "_src" / "data-0.1.0.bundle").is_file(),
            "tasks": TASKS_IN_RELEASE}


__all__ = ["KIND", "DATASET_ROOT", "REFUSED", "TASKS_IN_RELEASE", "PUBLISHED_SUITE",
           "PASSWORD", "SALT", "bundle_zip", "task_ids", "downloads", "load",
           "provision_status"]
