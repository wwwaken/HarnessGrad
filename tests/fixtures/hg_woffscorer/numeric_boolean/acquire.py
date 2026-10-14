#!/usr/bin/env python3
"""Acquire pinned public evaluator bytes; run separately from offline execution."""
import base64
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
PINS = [
    ("openai/grade-school-math", "3101c7d5072418e28b9008a6636bde82a006892c",
     "grade_school_math/dataset.py", "source/gsm8k/dataset.py"),
    ("openai/grade-school-math", "3101c7d5072418e28b9008a6636bde82a006892c",
     "README.md", "source/gsm8k/README.md"),
    ("allenai/strategyqa-evaluator", "49b88ed2b2f1b57385c13e8a0699dee1d227f83e",
     "evaluator/eval.py", "source/strategyqa/eval.py"),
    ("allenai/strategyqa-evaluator", "49b88ed2b2f1b57385c13e8a0699dee1d227f83e",
     "evaluator/sari.py", "source/strategyqa/sari.py"),
    ("allenai/strategyqa-evaluator", "49b88ed2b2f1b57385c13e8a0699dee1d227f83e",
     "evaluator/requirements.txt", "source/strategyqa/requirements.txt"),
    ("allenai/strategyqa-evaluator", "49b88ed2b2f1b57385c13e8a0699dee1d227f83e",
     "README.md", "source/strategyqa/README.md"),
    ("eladsegal/strategyqa", "1ba1e97452e189569357876f2854b01357ffbe37",
     "README.md", "source/strategyqa/paper-code-README.md"),
    ("eladsegal/strategyqa", "1ba1e97452e189569357876f2854b01357ffbe37",
     "src/data/dataset_readers/strategy_qa_reader.py", "source/strategyqa/paper-code-reader.py"),
]
receipts = []
for repo, revision, upstream_path, destination in PINS:
    url = f"https://api.github.com/repos/{repo}/contents/{upstream_path}?ref={revision}"
    with urllib.request.urlopen(url, timeout=30) as response:
        raw = json.load(response)
    data = base64.b64decode(raw["content"])
    blob_sha = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
    assert blob_sha == raw["sha"], (url, blob_sha, raw["sha"])
    output = ROOT / destination
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    receipts.append({"repo": repo, "revision": revision, "upstream_path": upstream_path,
                     "url": url, "destination": destination, "bytes": len(data),
                     "git_blob_sha1": blob_sha, "sha256": hashlib.sha256(data).hexdigest()})
print(json.dumps({"acquisition_only": True, "source_files": receipts}, indent=2, sort_keys=True))
