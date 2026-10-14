#!/usr/bin/env python3
"""Execute unchanged official function ASTs or existing local adapter score calls.

The full upstream module cannot import in this interpreter. This is transparently
restricted official metric FUNCTION execution: no imports or unrelated functions
from the full module execute. Function ASTs are not edited or reimplemented.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
sys.path.insert(0, str(REPO))
REVISION = "092b196c1f8f14a54bbc62f24759d43bde46dd3b"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_official_functions():
    import numpy as np

    path = ROOT / "official-task-metrics.py"
    source = path.read_text()
    names = ("exact_str_match_fn", "measure_multiple_choice_grade", "argmax")
    tree = ast.parse(source, filename=str(path))
    selected = [node for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in selected} == set(names)
    namespace = {"np": np, "hashlib": hashlib, "List": List, "Dict": Dict, "Any": Any}
    # Compile original nodes, preserving function bodies and source line numbers.
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)
    identity = {
        "upstream": "google/BIG-bench", "revision": REVISION,
        "source_path": str(path.relative_to(REPO)), "source_sha256": sha(path),
        "execution_profile": "unchanged selected official function ASTs; not complete module import or task runner",
        "functions": [{"name": node.name, "start_line": node.lineno,
                       "end_line": node.end_lineno,
                       "source_sha256": hashlib.sha256(ast.get_source_segment(source, node).encode()).hexdigest()}
                      for node in selected],
        "numpy": {"version": importlib.metadata.version("numpy"),
                  "module_path": np.__file__, "module_sha256": sha(np.__file__)},
        "injected_globals": ["actual numpy as np", "stdlib hashlib", "typing List, Dict, Any"],
        "limitation": "Unrelated BLEU/BLEURT/ROUGE functions and transitive T5 dependencies do not execute; dependency closure is not established.",
    }
    return namespace, identity


def official(inputs):
    functions, identity = load_official_functions()
    (ROOT / "official-source-identity.json").write_text(json.dumps(identity, indent=2) + "\n")
    outputs = {"execution_profile": identity["execution_profile"], "physicsquestions": [], "sportsunderstanding": []}
    for row in inputs["physicsquestions"]:
        sample = row["official_sample"]
        result = functions["exact_str_match_fn"]([sample["target"]], [sample["generative_response"]])
        outputs["physicsquestions"].append({"id": row["id"], "raw_official_return": result})
    samples = [row["official_sample"] for row in inputs["physicsquestions"]]
    outputs["physics_aggregate_raw_return"] = functions["exact_str_match_fn"](
        [sample["target"] for sample in samples], [sample["generative_response"] for sample in samples])
    for row in inputs["sportsunderstanding"]:
        sample = row["official_sample"]
        result = functions["measure_multiple_choice_grade"]([sample])
        index = int(functions["argmax"](sample["log_prob"]))
        outputs["sportsunderstanding"].append({"id": row["id"], "raw_official_return": result,
                                             "upstream_argmax_index": index,
                                             "upstream_candidate_choice": sample["choice"][index]})
    outputs["sports_aggregate_raw_return"] = functions["measure_multiple_choice_grade"](
        [row["official_sample"] for row in inputs["sportsunderstanding"]])
    return outputs


def local(inputs):
    from data.datasets import physicsquestions, sportsunderstanding

    assert all(module._SPEC._records == [] for module in [physicsquestions, sportsunderstanding])
    outputs = {"execution_profile": "direct existing adapter score calls; generic QA verifier preprocessing not executed"}
    outputs["adapter_identities"] = {module.__name__: {"path": str(Path(module.__file__).relative_to(REPO)),
                                                          "sha256": sha(module.__file__),
                                                          "import_load_error": module._SPEC.load_error}
                                    for module in [physicsquestions, sportsunderstanding]}
    for dataset, module in [("physicsquestions", physicsquestions), ("sportsunderstanding", sportsunderstanding)]:
        outputs[dataset] = [{"id": row["id"], "raw_local_return": module.score(row["local_prediction"], row["local_gold"])}
                            for row in inputs[dataset]]
    return outputs


def compare(inputs):
    official_outputs = json.loads((ROOT / "official-output.json").read_text())
    local_outputs = json.loads((ROOT / "local-output.json").read_text())
    result = {"control_label": inputs["control_label"], "sports_comparability": inputs["sports_comparability"]}
    for dataset in ["physicsquestions", "sportsunderstanding"]:
        official_rows = official_outputs[dataset]
        local_rows = local_outputs[dataset]
        rows = []
        for input_row, official_row, local_row in zip(inputs[dataset], official_rows, local_rows, strict=True):
            assert input_row["id"] == official_row["id"] == local_row["id"]
            official_score = official_row["raw_official_return"]
            if dataset == "physicsquestions":
                official_score = official_score["exact_str_match"]
            local_score = local_row["raw_local_return"]["reward"]
            rows.append({"id": input_row["id"], "official_score": official_score, "local_reward": local_score,
                         "agreement": official_score == local_score, "purpose": input_row["purpose"]})
        result[dataset] = {"input_count": len(rows), "agreement_count": sum(row["agreement"] for row in rows),
                           "divergence_count": sum(not row["agreement"] for row in rows),
                           "official_positive_count": sum(row["official_score"] == 1 for row in rows),
                           "local_positive_count": sum(row["local_reward"] == 1 for row in rows),
                           "rows": rows}
    return result


if __name__ == "__main__":
    mode = sys.argv[1]
    inputs = json.loads((ROOT / "inputs.json").read_text())
    print(json.dumps({"official": official, "local": local, "compare": compare}[mode](inputs), indent=2))
