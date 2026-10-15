#!/usr/bin/env python3
"""Read-only source audit of profiles outside this bounded acquisition selection.

Never imports adapters or benchmark modules, starts containers, calls endpoints,
executes task contexts, or reads gold/candidate/reference solution payloads.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import platform
import re
import sys

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = OUT / "gap-source"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def retain(path: Path, relative: str, excerpt_pattern: str | None = None) -> dict:
    raw = path.read_bytes()
    target = SOURCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    assert target.read_bytes() == raw
    text = raw.decode("utf-8")
    lines = text.splitlines()
    pattern = re.compile(excerpt_pattern or r"^\s*(?:from |import )|import_module|pip install|uv pip|uvx|uv run|apt-get|^FROM |code_context|exec\(|check_program|check_correctness|^dependencies:|^  - |^      - ")
    excerpts = [{"line": n, "text": line} for n, line in enumerate(lines, 1) if pattern.search(line)]
    imports = []
    if path.suffix == ".py":
        tree = ast.parse(text, filename=str(path))
        for node in sorted(ast.walk(tree), key=lambda n: (getattr(n, "lineno", 0), getattr(n, "col_offset", 0))):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({"line": node.lineno, "module": alias.name, "level": 0,
                                    "text": lines[node.lineno - 1]})
            elif isinstance(node, ast.ImportFrom):
                imports.append({"line": node.lineno, "module": node.module or "", "level": node.level,
                                "text": lines[node.lineno - 1]})
    return {"source_path": str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path),
            "preimage": str(target.relative_to(REPO)), "bytes": len(raw), "sha256": digest(raw),
            "line_count": len(lines), "excerpts": excerpts, "imports_ast": imports}


repo_paths = [
    "data/datasets/ds1000.py", "data/datasets/ds1000/verify/check.py",
    "data/datasets/appworld.py", "data/datasets/appworld/Dockerfile",
    "data/datasets/appworld/Dockerfile.agent", "data/datasets/appworld/verify/check.py",
    "data/datasets/appworld/service.py", "data/datasets/gaia.py",
    "data/datasets/gaia/Dockerfile", "data/datasets/gaia/verify/check.py",
    "data/datasets/gaia/prepare.py", "data/datasets/tau_bench.py",
    "data/datasets/tau_bench/Dockerfile", "data/datasets/tau_bench/verify/check.py",
    "data/datasets/tau_bench/image/tau_cli.py", "data/datasets/terminal_bench.py",
]
repo_paths.extend(str(p.relative_to(REPO)) for p in sorted((REPO / "data/datasets/tau_bench/lib").rglob("*.py")))
files = [retain(REPO / rel, "repository/" + rel) for rel in repo_paths]
external = {
    "ds1000/environment.yml": Path("/mnt/20t/xubuqiang/datasets/ds1000/_src/DS-1000-b39aab71/environment.yml"),
    "ds1000/execution.py": Path("/mnt/20t/xubuqiang/datasets/ds1000/_src/DS-1000-b39aab71/execution.py"),
    "gaia/scorer.py": Path("/mnt/20t/xubuqiang/datasets/gaia/_src/scorer.py"),
}
files.extend(retain(path, "external/" + rel) for rel, path in external.items())

terminal_root = Path("/mnt/20t/xubuqiang/datasets/terminal-bench")
terminal_tasks = sorted(p for p in terminal_root.iterdir() if p.is_dir() and (p / "task.toml").is_file())
terminal = []
for task in terminal_tasks:
    task_sources = []
    for rel in ["task.toml", "environment/Dockerfile", "tests/test.sh"]:
        source = retain(task / rel, "external/terminal-bench/" + task.name + "/" + rel)
        files.append(source)
        task_sources.append(source["preimage"])
    terminal.append({"task_id": task.name, "sources": task_sources})

by_path = {item["source_path"]: item for item in files}


def literal(path: str, needle: str) -> dict:
    item = by_path[path]
    lines = (REPO / item["preimage"]).read_text().splitlines()
    hits = [{"line": i, "text": line} for i, line in enumerate(lines, 1) if needle in line]
    assert hits, (path, needle)
    return {"source_path": path, "preimage": item["preimage"], "sha256": item["sha256"], "matches": hits}


tau_source = [item for item in files if item["source_path"].startswith("data/datasets/tau_bench/lib/")
              or item["source_path"] in {"data/datasets/tau_bench/verify/check.py", "data/datasets/tau_bench/image/tau_cli.py"}]
tau_imports = [imp | {"source_path": item["source_path"]} for item in tau_source for imp in item["imports_ast"]]
tau_external = [imp for imp in tau_imports if imp["level"] == 0
                and imp["module"].split(".")[0] not in sys.stdlib_module_names | {"tau_bench"}]
assert tau_external == [], tau_external

facts = {
    "ds1000": {
        "classification": "not-demonstrated; dynamic per-context graph and upstream target mismatch",
        "reason": "The checker constructs programs from task code_context and executes the upstream runner. A host import inventory does not derive a complete requirement set for all included contexts. Upstream environment.yml specifies Python 3.10 and both Conda channel-qualified packages and pip tensorflow-cpu; a host CPython 3.12 wheel solve would need an explicit distinct reconstruction scope. No missing-wheel or unobtainability conclusion is made.",
        "evidence": [literal("data/datasets/ds1000/verify/check.py", 'task["code_context"]'),
                     literal("data/datasets/ds1000/verify/check.py", "from execution import check_correctness"),
                     literal(str(external["ds1000/execution.py"]), "exec(check_program, exec_globals)"),
                     literal(str(external["ds1000/environment.yml"]), "python=3.10"),
                     literal(str(external["ds1000/environment.yml"]), "pytorch::"),
                     literal(str(external["ds1000/environment.yml"]), "tensorflow-cpu==2.16.1")],
    },
    "appworld": {
        "classification": "not-demonstrated; Python 3.11 image graph not reconstructed",
        "reason": "The verifier imports AppWorld from its scorer image. The checked-in action-service Dockerfile declares appworld==0.1.3.post1 and uvicorn<1 on Python 3.11-slim, then executes the appworld CLI installer. These exact package roots are finite; this audit does not reconstruct the scorer image's complete Python graph or installer output for that target. It does not establish a missing distribution or unobtainability.",
        "evidence": [literal("data/datasets/appworld/verify/check.py", "from appworld import AppWorld"),
                     literal("data/datasets/appworld/Dockerfile", "FROM "),
                     literal("data/datasets/appworld/Dockerfile", "pip install"),
                     literal("data/datasets/appworld/Dockerfile", "appworld.cli install"),
                     literal("data/datasets/appworld.py", '"HG_APPWORLD_VERIFIER_IMAGE"'),
                     literal("data/datasets/appworld/service.py", "from fastapi"),
                     literal("data/datasets/appworld/service.py", "from munch")],
    },
    "gaia": {
        "classification": "not-demonstrated; finite image roots, scorer NumPy graph not reconstructed",
        "reason": "The imported upstream scorer has a direct NumPy import. The Python 3.12-slim task-image build declares six bare pip roots (numpy, openpyxl, pillow, requests, beautifulsoup4, lxml), separately from native apt packages; prepare.py imports pyarrow.parquet conditionally. A complete source-scoped choice of scorer/image/preparation roots and image-matching metadata reconstruction was not performed. None of these sources establishes unobtainability.",
        "evidence": [literal("data/datasets/gaia/verify/check.py", "from scorer import question_scorer"),
                     literal(str(external["gaia/scorer.py"]), "import numpy as np"),
                     literal("data/datasets/gaia/Dockerfile", "FROM "),
                     literal("data/datasets/gaia/Dockerfile", "RUN pip install"),
                     literal("data/datasets/gaia/prepare.py", "import pyarrow.parquet as pq")],
    },
    "tau_bench": {
        "classification": "no-third-party-requirement-on-inspected-vendored-route; no nonempty solve counted",
        "reason": "The entire checked-in vendored tool tree, CLI and verifier were parsed without executing them. All absolute import roots are Python standard-library modules or vendored tau_bench; relative imports remain within that tree. The verifier dynamically imports one of the two vendored tool collections. Dockerfile uses Python 3.11-slim, copies lib and tests imports, and declares no pip installation. Thus a nonempty third-party wheel profile is absent on this inspected route, rather than failed or unobtainable; source custody and image/runtime verification remain separate.",
        "evidence": [literal("data/datasets/tau_bench/verify/check.py", 'importlib.import_module(f"tau_bench.envs.{domain}.tools")'),
                     literal("data/datasets/tau_bench/Dockerfile", "FROM "),
                     literal("data/datasets/tau_bench/Dockerfile", "COPY lib"),
                     literal("data/datasets/tau_bench/Dockerfile", "import tau_bench.envs.retail.tools")],
        "parsed_python_files": len(tau_source),
        "ast_import_records": len(tau_imports),
        "absolute_import_roots": sorted({imp["module"].split(".")[0] for imp in tau_imports if imp["level"] == 0}),
        "third_party_absolute_import_records": tau_external,
        "stdlib_names_interpreter": platform.python_version(),
        "dynamic_import_domain_preimages": [p for p in repo_paths if p.endswith("tools/__init__.py")],
    },
    "terminal_bench": {
        "classification": "one-prior-task-tooling-profile; complete per-task reconstruction not demonstrated",
        "reason": "The adapter uses each task.toml image and executes that task's /tests/test.sh; there is no single shared dependency profile. Every task.toml, environment/Dockerfile and tests/test.sh in the current external checkout was hashed and retained. Task scripts include uvx, direct pip, uv pip and native apt installers with different declared requirements, while Dockerfiles add further environment roots and targets. Prior OpenSSL tooling resolution does not reconstruct the other task-specific graphs or the image dependencies; no artifact unobtainability is inferred.",
        "evidence": [literal("data/datasets/terminal_bench.py", '"image": env_meta["docker_image"]'),
                     literal("data/datasets/terminal_bench.py", '"argv": ["bash", "/tests/test.sh"]')],
        "task_count_from_directory_scan": len(terminal_tasks),
        "task_source_preimages": terminal,
    },
}
packet = {
    "scope": "w-resolver3 remaining-gap read-only source audit; no solver/scorer/runtime execution",
    "selection_rule": "Audit the five remaining profiles whose image, dynamic task context or vendored-source scope is outside this packet's bounded host wheel reconstruction selection. The parent separately selects host-reconstructable remaining profiles.",
    "command": "python3 tests/fixtures/hg_wresolver3/gap-audit.py",
    "runtime": {"python": sys.version, "executable": sys.executable, "platform": platform.platform()},
    "sources": files,
    "datasets": facts,
    "non_actions": ["No network or package index request", "No adapter/module import", "No task context execution", "No model/server/container/image operation", "No dataset blocker or gate edit", "No run/receipt read or write", "No gold/candidate/reference payload read"],
}
(OUT / "gap-audit.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
print(json.dumps({"source_files": len(files), "retained_source_bytes": sum(f["bytes"] for f in files),
                  "terminal_task_count": len(terminal_tasks), "tau_parsed_python_files": len(tau_source),
                  "tau_ast_import_records": len(tau_imports), "tau_third_party_import_records": tau_external,
                  "datasets": {name: item["classification"] for name, item in facts.items()}}, indent=2, sort_keys=True))
for source in files:
    print(f'{source["sha256"]}  {source["preimage"]}  {source["bytes"]} bytes')
for name, item in facts.items():
    print(f'\n{name}: {item["reason"]}')
    for evidence in item["evidence"]:
        for match in evidence["matches"]:
            print(f'{evidence["preimage"]}:{match["line"]}: {match["text"]}')
print("gap-audit.json SHA256 " + digest((OUT / "gap-audit.json").read_bytes()))
