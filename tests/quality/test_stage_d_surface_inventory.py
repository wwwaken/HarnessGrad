"""Source-only Stage D surface ledger: stale rows AND uncovered additions fail.

The scanner deliberately over-selects. Every candidate must be either an inventory
row or an individually reviewed non-reference in the JSON. No filename whitelist,
adapter imports, receipt execution, network, model, or production writes are used.
The report/JSON and this scanner are excluded from scanning their own quotations.
Stage D must review/update this ledger together with the move; merely deleting old
rows cannot bless a new spelling. Static discovery cannot prove arbitrary Python
data flow; opaque loaders are candidates requiring a recorded human decision.
"""
from __future__ import annotations

import ast
from collections import Counter
import json
import os
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = "reports/stage-d-surface-inventory.json"
REPORT_PATH = "reports/stage-d-surface-inventory.md"
SELF_PATH = "tests/quality/test_stage_d_surface_inventory.py"
SELF_FILES = frozenset({JSON_PATH, REPORT_PATH, SELF_PATH})
# The harness appends this ignored invocation transcript while tools run. It
# quotes the inventory itself and is neither repository source nor a run receipt.
OBSERVATION_FILES = frozenset({"run.log"})
EXCLUDED_PARTS = frozenset({
    "runs", "current_harness", ".git", "__pycache__",
    "HarnessGrad-evidence-archive", ".pytest_cache",
})

# All text extensions and dotfiles are scanned, not just Python or git-tracked
# paths. Unknown binary files are skipped only when they contain NUL or fail UTF-8.
# The broad lexical pass also catches Python snippets inside strings/Markdown.
LEXICAL = re.compile(
    r"(?<![\w])data[./]|\b(?:from|import)\s+data\b|[\"']data[\"']|"
    r"\bDATASETS?_PACKAGE\b|\b(?:import_module|__import__|"
    r"spec_from_file_location|__getattr__)\b|"
    r"\.(?:r?glob)\s*\(\s*[\"']\*\.py[\"']|"
    r"\b(?:registry|adapter|module|dataset|base|qa)\.__file__\b|"
    r"\bgetattr\s*\(\s*(?:data|datasets|adapters)\b|"
    r"[\"'](?:adapter_module|dataset_module|module)[\"']\s*:|"
    r"dataset adapters|adapter modules|adapter under|globbing this directory|adapter into"
)


def declarations(root: Path) -> dict[str, Path]:
    """Discover literal KIND declarations in either layout without importing code."""
    found = {}
    for directory in (root / "data", root / "data" / "datasets"):
        for path in sorted(directory.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    targets = node.targets
                elif isinstance(node, ast.AnnAssign):
                    targets = [node.target]
                else:
                    continue
                if any(isinstance(t, ast.Name) and t.id == "KIND" for t in targets):
                    if isinstance(node.value, ast.Constant) and node.value.value == "dataset":
                        assert path.stem not in found, f"duplicate adapter: {path.stem}"
                        found[path.stem] = path
    return found


def _source_files(root: Path):
    for directory, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = sorted(d for d in directories if d not in EXCLUDED_PARTS)
        for filename in sorted(filenames):
            path = Path(directory) / filename
            relative = path.relative_to(root).as_posix()
            if relative in SELF_FILES | OBSERVATION_FILES or filename in EXCLUDED_PARTS or path.is_symlink():
                continue
            raw = path.read_bytes()
            if b"\0" in raw:
                continue
            try:
                source = raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
            yield relative, source


def candidates(root: Path, names: set[str]) -> dict[tuple[str, int], str]:
    """Independent, deterministic candidate scan; never consult inventory entries."""
    found = {}
    filenames = re.compile(r"\b(?:" + "|".join(map(re.escape, sorted(names))) + r")\.py\b")
    for relative, source in _source_files(root):
        lines = source.splitlines()
        selected = {i for i, line in enumerate(lines, 1)
                    if LEXICAL.search(line) or filenames.search(line)}
        if relative.startswith("data/") or relative == "tools/new_dataset.py":
            selected.update(i for i, line in enumerate(lines, 1) if "__file__" in line)
        if relative.endswith(".py"):
            try:
                tree = ast.parse(source, filename=relative)
            except SyntaxError:
                tree = None  # The lexical pass still covers source fragments.
            if tree is not None:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        module = getattr(node, "module", "") or ""
                        imported = {a.name.split(".")[0] for a in node.names}
                        relevant = (
                            module == "data" or module.startswith("data.")
                            or (isinstance(node, ast.Import) and "data" in imported)
                            or (getattr(node, "level", 0) and (
                                bool(imported & names) or module.split(".")[0] in names))
                        )
                        if relevant:
                            selected.update(range(node.lineno, node.end_lineno + 1))
                    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                        # Decoded / adjacent string literals and multiline strings.
                        # Only use the node's whole range when lexical scanning could
                        # not see the spelling at all (avoids quoting huge docstrings).
                        if re.search(r"\bdata[./]", node.value) and not any(
                                LEXICAL.search(line) for line in
                                lines[node.lineno - 1:node.end_lineno]):
                            selected.update(range(node.lineno, node.end_lineno + 1))
        found.update({(relative, i): lines[i - 1] for i in sorted(selected)})
    return found


def load_inventory():
    return json.loads((ROOT / JSON_PATH).read_text(encoding="utf-8"))


def render_report(inventory: dict) -> str:
    """Make the Markdown a checked view of the same JSON, including exact strings."""
    def code(value):
        # JSON string literals preserve indentation, quotes and control characters.
        value = json.dumps(value, ensure_ascii=False).replace("|", "\\u007c")
        fence = "`" * (max((len(m[0]) for m in re.finditer(r"`+", value)), default=0) + 1)
        return fence + value + fence

    out = ["# Stage D adapter surface inventory", "", *inventory["notes"], "",
           "## Verified adapter layout", "",
           "Literal `KIND = \"dataset\"` declarations were read with AST; no adapter was imported.", "",
           "| Adapter | Module file | Private asset directory |",
           "| --- | --- | --- |"]
    for adapter in inventory["adapters"]:
        out.append(f'| {adapter["name"]} | `{adapter["module_file"]}` | '
                   f'{code(adapter["asset_directory"]) if adapter["asset_directory"] else "absent (verified; uses shared scaffolding or external data)"} |')
    out += ["", "## References", "",
            "One row is one physical source line. Multiple occurrences on that line share a full-line replacement. "
            "Categories may overlap; counts below count rows carrying each category. "
            "Current and replacement cells are JSON string literals, so decoding them gives the exact text, including indentation. "
            "A null replacement means **needs human decision**; the note explains why. "
            "An unchanged replacement is an intentional retain decision, not a missed edit.", "",
            "| ID | File:line | Categories | Adapter(s) | Exact current text | Exact replacement text | Decision / note |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
    for entry in inventory["references"]:
        out.append(f'| {entry["id"]} | `{entry["file"]}:{entry["line"]}` | '
                   f'{", ".join(map(str, entry["categories"]))} | '
                   f'{", ".join(entry["adapters"])} | {code(entry["text"])} | '
                   f'{code(entry["replacement"])} | {entry["decision"]}: {entry["note"]} |')
    out += ["", "## Reviewed non-references", "",
            "These broad-scan hits are pinned individually in JSON and checked just like references. "
            "They are shared scaffolds, fixtures, upstream data/code, unrelated Python data variables or unrelated loaders; "
            "Stage D must not replace their `data` prefix. New hits have no automatic exemption.", "",
            "| File:line | Exact current text | Reason |", "| --- | --- | --- |"]
    for entry in inventory["non_references"]:
        out.append(f'| `{entry["file"]}:{entry["line"]}` | {code(entry["text"])} | {entry["reason"]} |')
    out += ["", "## Counts per category", "",
            "| Category | Meaning | Rows |", "| --- | --- | --- |"]
    meanings = {1: "Python import", 2: "Dynamic module / lazy loading", 3: "Filesystem path / discovery",
                4: "Schema or data field", 5: "Documentation of layout"}
    counts = Counter(c for e in inventory["references"] for c in e["categories"])
    out += [f"| {c} | {meanings[c]} | {counts[c]} |" for c in range(1, 6)]
    decisions = Counter(e["decision"] for e in inventory["references"])
    out += ["", f'Total: {len(inventory["references"])} reference lines; '
            f'{len(inventory["non_references"])} reviewed non-reference lines. '
            + "; ".join(f"{k}: {v}" for k, v in sorted(decisions.items())) + ".", "",
            "## References a naive grep-and-replace would get WRONG", ""]
    for case in inventory["naive_replacement_hazards"]:
        out.append(f'- {case["explanation"]} References: {", ".join(case["references"])}.')
    return "\n".join(out) + "\n"


def assert_coverage(root: Path, inventory: dict):
    names = {a["name"] for a in inventory["adapters"]}
    actual = candidates(root, names)
    recorded = {}
    for entry in inventory["references"] + inventory["non_references"]:
        key = (entry["file"], entry["line"])
        assert key not in recorded, f"duplicate inventory row: {key}"
        recorded[key] = entry["text"]
        path = root / entry["file"]
        assert path.is_file(), f"stale inventory file: {key}"
        lines = path.read_text(encoding="utf-8").splitlines()
        assert 0 < entry["line"] <= len(lines), f"stale line number: {key}"
        assert lines[entry["line"] - 1] == entry["text"], f"stale inventory text: {key}"
    missing = sorted(set(actual) - set(recorded))
    stale = sorted(set(recorded) - set(actual))
    assert not missing, "uncovered Stage D candidates (review, do not auto-approve):\n" + "\n".join(
        f"{p}:{n}: {actual[p, n]}" for p, n in missing)
    assert not stale, f"inventory rows no longer detected: {stale}"
    assert recorded == actual


def test_inventory_has_no_stale_rows_or_uncovered_references():
    assert_coverage(ROOT, load_inventory())


def test_inventory_schema_adapter_files_assets_and_report():
    inventory = load_inventory()
    assert inventory["schema_version"] == 1
    adapters = inventory["adapters"]
    assert len(adapters) == 28
    discovered = declarations(ROOT)
    assert set(discovered) == {a["name"] for a in adapters}
    for adapter in adapters:
        assert discovered[adapter["name"]] == ROOT / adapter["module_file"]
        asset = discovered[adapter["name"]].with_suffix("")
        if adapter["asset_directory"] is None:
            assert not asset.exists(), f"new private asset directory: {asset}"
        else:
            assert asset == ROOT / adapter["asset_directory"]
            assert asset.is_dir()
            assert sorted(p.relative_to(asset).as_posix() for p in asset.rglob("*")
                          if p.is_file() and "__pycache__" not in p.parts) == adapter["asset_files"]
    ids = [e["id"] for e in inventory["references"]]
    assert len(ids) == len(set(ids))
    names = set(discovered)
    assert names <= {name for entry in inventory["references"] for name in entry["adapters"]}
    for entry in inventory["references"]:
        assert entry["categories"] and set(entry["categories"]) <= {1, 2, 3, 4, 5}
        assert entry["adapters"] and (entry["adapters"] == ["all adapters"]
                                      or set(entry["adapters"]) <= names)
        assert entry["note"]
        assert entry["decision"] in {"replace", "retain", "needs human decision"}
        if entry["decision"] == "needs human decision":
            assert entry["replacement"] is None
        else:
            assert isinstance(entry["replacement"], str)
            assert (entry["replacement"] == entry["text"]) == (entry["decision"] == "retain")
    for case in inventory["naive_replacement_hazards"]:
        assert case["references"] and set(case["references"]) <= set(ids)
    assert inventory["category_counts"] == {
        str(c): sum(c in e["categories"] for e in inventory["references"])
        for c in range(1, 6)
    }
    assert inventory["decision_counts"] == dict(Counter(
        e["decision"] for e in inventory["references"]))
    assert all(e["reason"] for e in inventory["non_references"])
    assert (ROOT / REPORT_PATH).read_text(encoding="utf-8") == render_report(inventory)


@pytest.mark.parametrize("source", [
    "import data.gsm8k\n", "from data.gsm8k import load\n", "from data import gsm8k\n",
    "from data import (\n    gsm8k,\n)\n", "from . import gsm8k\n",
    "from .gsm8k import load\n", 'getattr(data, name)\n',
    'loader(f"data.{name}")\n', 'loader("data." + name)\n',
    'importlib.import_module(prefix + name)\n', 'def __getattr__(name): ...\n',
    'path = ROOT / "data" / "gsm8k.py"\n', 'path = "data/gsm8k.py"\n',
    'paths = (root / "data").glob("*.py")\n',
    '{"module": "data.gsm8k"}\n', '"The adapter lives in data/gsm8k.py"\n',
    'path = "da" "ta/gsm8k.py"\n', 'import data.datasets.gsm8k\n',
])
def test_scanner_detects_new_references_without_using_the_ledger(tmp_path, source):
    (tmp_path / "new_consumer.py").write_text(source, encoding="utf-8")
    assert candidates(tmp_path, {"gsm8k"}), source


def test_scanner_includes_untracked_hidden_json_docs_and_excludes_frozen_trees(tmp_path):
    for name in ("untracked.json", ".hidden", "notes.md"):
        (tmp_path / name).write_text('{"module": "data.gsm8k"}\n', encoding="utf-8")
    for name in EXCLUDED_PARTS:
        (tmp_path / name).mkdir()
        (tmp_path / name / "frozen.py").write_text("import data.gsm8k\n", encoding="utf-8")
    (tmp_path / "image.bin").write_bytes(b"\0data/gsm8k.py")
    actual = candidates(tmp_path, {"gsm8k"})
    assert {p for p, _ in actual} == {"untracked.json", ".hidden", "notes.md"}


@pytest.mark.parametrize("mutation", ["new", "changed", "deleted", "unlisted"])
def test_guard_rejects_new_stale_and_missing_inventory_rows(tmp_path, mutation):
    path = tmp_path / "consumer.py"
    path.write_text("import data.gsm8k\n", encoding="utf-8")
    inventory = {
        "adapters": [{"name": "gsm8k"}],
        "references": [{"file": "consumer.py", "line": 1, "text": "import data.gsm8k"}],
        "non_references": [],
    }
    assert_coverage(tmp_path, inventory)
    if mutation == "new":
        (tmp_path / "new.json").write_text('{"module": "data.gsm8k"}\n', encoding="utf-8")
    elif mutation == "changed":
        path.write_text("import data.datasets.gsm8k\n", encoding="utf-8")
    elif mutation == "deleted":
        path.unlink()
    else:
        inventory["references"].clear()
    with pytest.raises(AssertionError):
        assert_coverage(tmp_path, inventory)
