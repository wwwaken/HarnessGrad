"""The dataset chooser offers datasets, and the fixture agrees with the chooser.

Two things drifted apart here, in opposite directions, and both were visible to a reader on
the Launch form.

`web/server/launch.py` built its list by globbing `data/*.py` and `data/datasets/*.py` and
keeping whatever declared a *zero-argument* `load()`. `data/scaffolds/registry.py:published()`
is documented as "the one answer to which datasets exist" and applies a different rule -- a
module is a dataset only if it declares `KIND = "dataset"`; anything undeclared is the
platform's own fixture. The glob therefore kept the three top-level fixtures, which declare
`KIND = "fixture"` and were never offered by the registry, and dropped `musique`, which
declares a keyword-only `load(*, mode=...)` and so failed the zero-argument test. Measured
before the fix: 33 names offered, six of them scaffolding, with `musique` missing.

`web/scripts/build_fixtures.py` globbed a *third* time with its own filter, so
`src/fixtures/data/launch-options.json` said the machine offered four datasets while the API
said 33. The fixture had also gone stale in the other direction -- it predated the 27 real
datasets and the `dsh_agent` harness.

All three now read one function. This file keeps them reading it.
"""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _launch_module():
    spec = importlib.util.spec_from_file_location(
        "hg_web_server_launch", ROOT / "web" / "server" / "launch.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _declared_kinds(directory: Path) -> dict[str, str]:
    """`{module: KIND}` parsed independently of the code under test.

    `ast`, not an import, and not a substring match: `agentdojo` spells the value
    `'dataset'` while the other 27 use double quotes, so a text match on
    `KIND = "dataset"` misses it.
    """
    out: dict[str, str] = {}
    for path in sorted(directory.glob("*.py")):
        if path.stem in ("__init__",):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        for node in tree.body:
            if (isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "KIND" for t in node.targets)):
                try:
                    out[path.stem] = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    pass
                break
    return out


def test_the_chooser_offers_declared_datasets_and_nothing_else():
    launch = _launch_module()
    offered = launch.dataset_names(ROOT)

    declared = _declared_kinds(ROOT / "data" / "datasets")
    datasets = sorted(name for name, kind in declared.items() if kind == "dataset")
    fixtures = sorted(name for name, kind in declared.items() if kind != "dataset")

    assert offered == datasets, (
        "the Launch form must offer exactly the modules that declare KIND = 'dataset'")
    assert len(offered) == 28, f"expected the registry's 28 datasets, got {len(offered)}"
    assert not (set(offered) & set(fixtures)), f"fixtures offered: {sorted(set(offered) & set(fixtures))}"

    # The three top-level scaffolding modules call themselves fixtures in their own source.
    for name in ("demo", "probe_set", "broken_service"):
        assert _declared_kinds(ROOT / "data")[name] == "fixture", f"{name} is not declared a fixture"
        assert name not in offered, f"{name} is the platform's scaffolding, not a dataset"


def test_musique_is_offered_even_though_its_load_takes_a_keyword():
    """The dataset the zero-argument `load()` test silently dropped.

    `data/datasets/musique.py:265` is `def load(*, mode=DEFAULT_MODE)`. A predicate that
    requires an argument-free `load()` reads that as "not a dataset", which is why a real
    dataset was missing from the chooser while scaffolding was present in it.
    """
    source = (ROOT / "data" / "datasets" / "musique.py").read_text(encoding="utf-8")
    assert "def load(*, mode=" in source, "musique's signature changed; this test needs re-reading"
    assert "musique" in _launch_module().dataset_names(ROOT)


def test_the_shipped_fixture_matches_the_api():
    """`launch-options.json` is generated; it must not disagree with the API that falls back to it.

    It did: the fixture listed four datasets (three of them scaffolding) while the API returned
    33, because the generator globbed on its own. The web app reads the fixture whenever
    `web/server/` is not running, so the two lists are the same list to a user.
    """
    launch = _launch_module()
    fixture = json.loads(
        (ROOT / "web" / "src" / "fixtures" / "data" / "launch-options.json").read_text(encoding="utf-8"))
    assert fixture["datasets"] == launch.dataset_names(ROOT), (
        "regenerate with: cd web && python3 scripts/build_fixtures.py")
    assert fixture["harnesses"] == sorted(
        d.name for d in (ROOT / "base_harness").iterdir() if (d / "harness.json").is_file())
