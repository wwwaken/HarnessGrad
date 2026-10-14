"""AppWorld 0.1.3 as a service-backed tool dialogue dataset.

The encrypted 0.1.0 release declares four files: ``train`` (90), ``dev`` (57),
``test_normal`` (168), and ``test_challenge`` (417).  The adapter uses the release's
own declaration (``SPLIT_SOURCE = "declared"``), places train and dev on the study
side, and scores the two test files on the eval side.  ``dev`` is included with train
because the release calls both non-test files development material; this is stated here
rather than silently dropping 57 released tasks.

The paper-era build (Trivedi et al., ACL 2024, arXiv 2407.18901v2) reported
105/60/168/417 tasks, totaling 750. The pinned release has 18 fewer train/dev
tasks; both test split counts match the paper.

AppWorld's environment server is a sidecar service.  The task container only gets the
small ``aw`` client; the service owns the world and writes its API-call log through the
platform recording mount.  A fresh verifier reads that log and replays every request in
a new AppWorld world before calling the released ``ground_truth/evaluation.py``.  A
process started by the agent would not survive the platform's fresh verification
container, which is why the server is declared in ``services``.

The release bundle contains generated solution artifacts for train and dev tasks. Their
released API-call logs are used as the oracle only for those covered tasks; uncovered
test tasks raise from ``oracle_files`` rather than receiving an empty reference.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shlex
import shutil
import zipfile
from pathlib import Path

from eval.policy.appworld_reporting import make_manifest

KIND = "dataset"
DATASET_ROOT = Path("/mnt/20t/xubuqiang/datasets/appworld")
SRC_DIR = DATASET_ROOT / "_src"
BUNDLE = SRC_DIR / "data-0.1.0.bundle"
UNPACKED = SRC_DIR / "unpacked"
POOL = DATASET_ROOT / "pool.jsonl"
TASKS_IN_RELEASE = 732
SPLIT_SIZES = {"train": 90, "dev": 57, "test_normal": 168, "test_challenge": 417}
PAPER_SPLITS = {"train": 105, "dev": 60, "test_normal": 168, "test_challenge": 417}
SPLIT_SOURCE = "declared"
ORACLE_SOURCE = "released"
ORACLE_VALIDATED_BY = (
    "AppWorld's released ground_truth/evaluation.py, executed by appworld.evaluator.TestTracker"

)
IMAGE = os.environ.get(
    "HG_APPWORLD_IMAGE",
    "harnessgrad/appworld-agent@sha256:d3a04ec8e295710347e978d8e58c663161d829e7dfa544da4d82d0d67abbd8eb",
)
SERVICE_IMAGE = os.environ.get(
    "HG_APPWORLD_SERVICE_IMAGE",
    "harnessgrad/appworld-service@sha256:db09e34ec90347e7d5271d95445f360222ba1aef3ca0eaa5614ce768bf23aca4",
)
VERIFIER_IMAGE = os.environ.get(
    "HG_APPWORLD_VERIFIER_IMAGE",
    "harnessgrad/appworld-service@sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca",
)
POOL_SHA256 = "970c39331bc350ce9d3ed91a75fd32b554c257fc48fc31633dfccdde74164e65"
WORKDIR = "/app"
PASSWORD = "WEquKLy##9M@qu"
SALT = b"Nvx#rYcYQ2%btf"


def bundle_zip(bundle_path: Path | str | None = None) -> zipfile.ZipFile:
    """Decrypt the official bundle in memory using AppWorld's public constants."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    path = Path(bundle_path) if bundle_path else BUNDLE
    data = path.read_bytes()
    key = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=SALT, iterations=100000
    ).derive(PASSWORD.encode())
    decryptor = Cipher(algorithms.AES(key), modes.CFB(data[:16])).decryptor()
    return zipfile.ZipFile(io.BytesIO(decryptor.update(data[16:]) + decryptor.finalize()))


def task_ids(bundle_path: Path | str | None = None) -> list[str]:
    with bundle_zip(bundle_path) as archive:
        prefix, suffix = "data/tasks/", "/ground_truth/evaluation.py"
        return sorted(
            {
                name[len(prefix) : -len(suffix)]
                for name in archive.namelist()
                if name.startswith(prefix) and name.endswith(suffix)
            }
        )


def split_ids(bundle_path: Path | str | None = None) -> dict[str, list[str]]:
    with bundle_zip(bundle_path) as archive:
        return {
            split: [line.strip() for line in archive.read(f"data/datasets/{split}.txt").decode().splitlines() if line.strip()]
            for split in SPLIT_SIZES
        }


def _db_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((root / "dbs").glob("*.jsonl")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def prepare() -> Path:
    """Decrypt/materialize the release and write compact per-task metadata.

    The heavy task databases stay under the external dataset root.  Importing this adapter
    reads only ``pool.jsonl``; it does not walk the 14,696-member archive or task trees.
    """
    UNPACKED.mkdir(parents=True, exist_ok=True)
    marker = UNPACKED / "data" / "version.txt"
    if not marker.is_file():
        with bundle_zip() as archive:
            for member in archive.infolist():
                target = UNPACKED / member.filename
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)

    rows: list[dict] = []
    declared = split_ids(BUNDLE)
    for split, ids in declared.items():
        for task_id in ids:
            root = UNPACKED / "data" / "tasks" / task_id
            specs = json.loads((root / "specs.json").read_text())
            metadata = json.loads((root / "ground_truth" / "metadata.json").read_text())
            rows.append(
                {
                    "task_id": task_id,
                    "split": split,
                    "difficulty": metadata["difficulty"],
                    "num_api_calls": metadata["num_api_calls"],
                    "num_apps": metadata["num_apps"],
                    "instruction": specs["instruction"],
                    "dbs": _db_digest(root),
                    "released_oracle": (root / "ground_truth" / "api_calls.json").is_file(),
                }
            )
    POOL.parent.mkdir(parents=True, exist_ok=True)
    with POOL.open("w", encoding="utf-8") as output:
        for row in sorted(rows, key=lambda value: value["task_id"]):
            output.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return POOL


def _pool() -> list[dict]:
    if not POOL.is_file():
        prepare()
    actual = hashlib.sha256(POOL.read_bytes()).hexdigest()
    if actual != POOL_SHA256:
        raise ValueError(f"appworld: pool digest {actual} != pinned {POOL_SHA256}")
    return [json.loads(line) for line in POOL.read_text(encoding="utf-8").splitlines() if line.strip()]


def _oracle_ids() -> set[str]:
    return {row["task_id"] for row in _pool() if row.get("released_oracle")}


def oracle_files(task: dict) -> dict[str, str]:
    task_id = task["task_id"]
    if task_id not in _oracle_ids():
        raise ValueError(
            f"appworld: no released reference for {task_id}; coverage={ORACLE_COVERAGE}"
        )
    path = UNPACKED / "data" / "tasks" / task_id / "ground_truth" / "api_calls.json"
    if not path.is_file():
        raise ValueError(f"appworld: released API-call log missing for {task_id}")
    calls = json.dumps(json.loads(path.read_text()))
    return {"reference.py":
            f"import json\ncalls = json.loads({calls!r})\n" +
            "for call in calls:\n" +
            "    method = call.get('method', 'get').lower()\n" +
            "    requester_call = f\"requester.{method}({call['url']!r}, data={call.get('data') or {}!r}, client=requester.client)\"\n" +
            "    exec(requester_call)\n"}


ORACLE_COVERAGE = (
    f"{len(_oracle_ids())} of {TASKS_IN_RELEASE} tasks (released train+dev coverage)"
)

_ROWS = {row["task_id"]: row for row in _pool()}
SPLIT = {
    "train": [row["task_id"] for row in _ROWS.values() if row["split"] in {"train", "dev"}],
    "eval": [row["task_id"] for row in _ROWS.values() if row["split"] in {"test_normal", "test_challenge"}],
}
OFFICIAL_EVAL = [row["task_id"] for row in _ROWS.values() if row["split"] in {"test_normal", "test_challenge"}]


def _goal(row: dict) -> str:
    return row["instruction"]


def _runtime_prompt(task_id: str) -> str:
    task_arg = shlex.quote(task_id)
    action = f"./aw action --task {task_arg} --code"
    discovery = action + " 'print(apis.api_docs.show_app_descriptions())'"
    return f"""AppWorld provides a shell CLI in the working directory: ./aw.
Use your harness's shell/command tool to run these commands; Python snippets
belong in --code, not in the local shell or a local Python process.

Initialize once: `./aw init --task {task_arg}`
This returns the task, supervisor identity and current datetime. Reinitializing
resets the world, so keep using action after initialization.

Execute Python in the service: `{action} '<python>'`
The service interpreter already defines `apis`. Variables and API state persist
between action calls. Each action executes a whole Python snippet, which may
include multiple API calls, assignments, loops and conditionals. Print the
responses you need to inspect; one action is not one API call. Local files and
imports do not provide AppWorld APIs.

Start discovery with this executable API action: `{discovery}`
Then discover the relevant app's methods with
`apis.api_docs.show_api_descriptions(app_name="<discovered app>")` and inspect
parameters with `apis.api_docs.show_api_doc(app_name="<discovered app>",
api_name="<discovered API>")`, each inside a printed --code action.
Call the documented methods as `apis.<app>.<api>(...)`. Discover supervisor
APIs for account credentials when needed; use returned values and documented
parameters rather than guessing method names, passwords or IDs.

Perform the requested changes through these API actions, inspect their results,
then give your final answer through your harness. A local script, plain text
answer or print-only snippet does not change the world. The service records API
calls automatically; its recording is not an actor file to create or edit.
CLI syntax help: `./aw --help` and `./aw action --help`.
"""


def _setup(task_id: str) -> dict:
    return {"files": [{"path": "aw", "from": str(ASSETS / "cli" / "aw")}],
            "runtime_prompt": _runtime_prompt(task_id)}


def load():
    tasks = [{"task_id": row["task_id"], "goal": _goal(row), "inputs": []} for row in _ROWS.values()]
    return tasks, {task["task_id"]: "AppWorld TestTracker.success" for task in tasks}


def reporting_manifest(task_ids: list[str]) -> list[dict]:
    """Trusted, selected-only reporting metadata derived from public IDs/splits.

    Never add this manifest to actor tasks or SETUP. No instruction, database,
    difficulty, solution, evaluator or gold-derived metadata is exported.
    """
    return make_manifest([{"task_id": tid, "split": _ROWS[tid]["split"]}
                          for tid in task_ids])


ASSETS = Path(__file__).parent / "appworld"
SETUP = {
    task_id: _setup(task_id)
    for task_id in _ROWS
}
VERIFY = {
    task_id: {
        "kind": "command",
        "scorer_bundle": {"isolation_class": "snapshot-service"},
        "argv": [
            "python3",
            "verify/check.py",
            "--task-id",
            task_id,
            "--source-split",
            _ROWS[task_id]["split"],
            "--log",
            f"/recordings/appworld/experiments/outputs/harness/tasks/{task_id}/logs/api_calls.jsonl",
            "--reward-file",
            "/verifier/reward.txt",
            "--evidence-file",
            "/verifier/evidence.json",
        ],
        "inputs": [{"path": "verify/check.py", "from": str(ASSETS / "verify" / "check.py")}],
        "reward_file": "/verifier/reward.txt",
        "evidence_file": "/verifier/evidence.json",
        "image": VERIFIER_IMAGE,
        "timeout_s": 900,
    }
    for task_id in _ROWS
}

DEFAULT_ENV = {
    "kind": "exec",
    "image": IMAGE,
    "workdir": WORKDIR,
    "state": "mount",
    "network": "services",
    "placement": "inside",
    "services": [
        {
            "name": "appworld",
            "image": SERVICE_IMAGE,
            "cpus": 2,
            "memory_mb": 4096,
            "command": ["/usr/local/bin/appworld-server"],
            "port": 8000,
            "health": {
                "argv": [
                    "python",
                    "-c",
                    "import urllib.request as u; u.urlopen('http://localhost:8000/').read()",
                ],
                "timeout_s": 60,
            },
            "record": True,
            "needs_seed": False,
            "needs_model": False,
        }
    ],
    "cpus": 2,
    "memory_mb": 4096,
    "agent_timeout_s": 900,
    "verify_timeout_s": 900,
}
ENV = {task_id: DEFAULT_ENV for task_id in _ROWS}


def downloads() -> list[dict]:
    return [
        {
            "kind": "http",
            "name": "AppWorld encrypted data bundle",
            "version": "0.1.0",
            "url": "https://s3.us-west-2.amazonaws.com/appworld.dev/data-0.1.0.bundle",
            "dst": "_src/data-0.1.0.bundle",
            "size": "34280074 bytes",
            "sha256": "fd9f9608c2ec71ed0ac25c3633a738b9129a318a129e31230425b9188e508250",
            "note": "Official encrypted AppWorld 0.1.0 bundle. prepare.py decrypts and extracts it under the external dataset root, then writes pool.jsonl; the trusted service image contains the pinned appworld package and task data.",
        }
    ]


def provision_status() -> dict:
    return {
        "root": str(DATASET_ROOT),
        "present": BUNDLE.is_file() and POOL.is_file(),
        "bundle": str(BUNDLE),
        "pool": str(POOL),
        "tasks": len(_ROWS),
    }


__all__ = [
    "KIND", "DATASET_ROOT", "TASKS_IN_RELEASE", "SPLIT_SIZES", "SPLIT_SOURCE",
    "OFFICIAL_EVAL", "ORACLE_SOURCE", "ORACLE_VALIDATED_BY", "ORACLE_COVERAGE",
    "bundle_zip", "task_ids", "split_ids", "prepare", "load", "downloads",
    "provision_status", "oracle_files", "reporting_manifest", "SETUP", "VERIFY", "ENV", "DEFAULT_ENV", "SPLIT",
]
