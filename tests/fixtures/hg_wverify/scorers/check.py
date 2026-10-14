"""Independent bounded scorer calls; authored controls precede fixture cross-checks."""
import ast
import contextlib
from copy import deepcopy
import hashlib
import importlib
import importlib.util
import io
import json
from pathlib import Path
import sys
from typing import Any, Dict, List

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def load_source(name):
    path = HERE / "source" / (name + ".py")
    spec = importlib.util.spec_from_file_location("verification_" + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def local_import(name):
    from data.scaffolds.qa import base
    original = base.QASpec.records
    def refuse_records(spec):
        raise PermissionError("w-verify: synthetic inputs only; refuse all dataset records")
    base.QASpec.records = refuse_records
    try:
        module = importlib.import_module("data.datasets." + name)
    finally:
        base.QASpec.records = original
    assert module._SPEC._records == []
    return module


def authored_cases():
    gsm = [{"id": "own-g" + str(i), "prediction": p, "gold_answer": g}
           for i, (p, g) in enumerate([
               ("#### 42", "#### 42"), ("42", "#### 42"),
               ("#### 42.0", "#### 42"), ("#### 0042", "#### 42"),
               ("#### 42\n#### 9", "#### 42"), ("#### 9\n#### 42", "#### 42"),
               ("#### 42.0000004", "#### 42"), ("#### -6.75", "#### -6.75"),
               ("no answer", "#### 42"), ("#### 43", "#### 42"),
           ])]
    physics = [{"id": "own-p" + str(i), "official_sample": {"target": t, "generative_response": p},
                "local_gold": {"accepted": t}, "local_prediction": p}
               for i, (p, t) in enumerate([
                   ("9 m/s", ["9 m/s", "9 metres per second"]),
                   (" 9 m/s ", ["9 m/s"]), ("9 m/s", ["9 m/s."]),
                   ("9 m/s.", ["9 m/s."]), ("9 m/s", [" 9 m/s "]),
                   ("9 M/S", ["9 m/s"]), ("9 m/s.", ["9 m/s"]), ("", [""]),
               ])]
    gold = {"id": "own-w", "type": "synthetic", "answer": "silver river", "aliases": [],
            "supporting_facts": [["East bank", 0], ["West bank", 2]],
            "evidences": [["Orin", "located in", "Vale"]], "evidences_id": [], "evidence_aliases": {}}
    pred = {"schema_version": 1, "answer": "silver river", "supporting_facts": deepcopy(gold["supporting_facts"]),
            "evidence": deepcopy(gold["evidences"])}
    wiki = []
    for i, label in enumerate(["exact", "normalization", "partial", "wrong", "empty-support", "missing-evidence", "alias", "entity-alias"]):
        g, p = deepcopy(gold), deepcopy(pred)
        g["id"] = "own-w" + str(i)
        if label == "normalization": p["answer"] = "The SILVER, river!"
        if label == "partial": p["answer"] = "silver"
        if label == "wrong": p["answer"] = "bronze"
        if label == "empty-support": p["supporting_facts"] = []
        if label == "missing-evidence": del p["evidence"]
        if label == "alias":
            g["aliases"] = ["Argent Stream"]
            p["answer"] = "Argent Stream"
        if label == "entity-alias":
            g["evidences_id"] = [["Qown1", "located in", "Qown2"]]
            g["evidence_aliases"] = {"Qown1": ["O"], "Qown2": ["V"]}
            p["evidence"] = [["O", "located in", "V"]]
        wiki.append({"id": g["id"], "purpose": label, "gold": g, "prediction": p})
    return {"gsm8k": gsm, "physicsquestions": physics, "twowikimultihopqa": wiki}


def wiki_official(module, row, panel):
    g, p, ident = deepcopy(row["gold"]), deepcopy(row["prediction"]), row["id"]
    # Serialize the public structured channels into the upstream file contract.
    answer_id = ident + "-Qanswer"
    gold = {"_id": ident, "answer": g["answer"], "answer_id": answer_id,
            "supporting_facts": g["supporting_facts"], "evidences": g["evidences"],
            "evidences_id": g.get("evidences_id", [])}
    aliases = {answer_id: g.get("aliases", []), **g.get("evidence_aliases", {})}
    prediction = {"answer": {}, "sp": {}, "evidence": {}}
    for src, dst in [("answer", "answer"), ("supporting_facts", "sp"), ("evidence", "evidence")]:
        if src in p:
            prediction[dst][ident] = p[src]
    directory = HERE / "serialized" / panel / ident
    directory.mkdir(parents=True, exist_ok=True)
    save(directory / "gold.json", [gold])
    save(directory / "prediction.json", prediction)
    (directory / "aliases.jsonl").write_text("".join(json.dumps({"Q_id": k, "aliases": v, "demonyms": []}) + "\n" for k, v in aliases.items()))
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        raw_return = module.eval(str(directory / "prediction.json"), str(directory / "gold.json"), str(directory / "aliases.jsonl"))
    raw_stdout = capture.getvalue()
    return {"raw_return": raw_return, "raw_stdout": raw_stdout, "metrics": json.loads(raw_stdout[raw_stdout.index("{"):])}


def main():
    inputs = authored_cases()
    save(HERE / "authored-inputs.json", inputs)
    gsm = load_source("gsm8k")
    wiki = load_source("twowiki")
    namespace = {"List": List, "Dict": Dict, "Any": Any}
    source = HERE / "source/bigbench.py"
    tree = ast.parse(source.read_text())
    selected = [x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == "exact_str_match_fn"]
    assert len(selected) == 1
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(source), "exec"), namespace)
    local = {ds: local_import(ds) for ds in inputs}
    outputs = {}
    # Execute independent controls first; only then read the old synthetic cases.
    for panel in ["authored", "crosscheck"]:
        if panel == "crosscheck":
            inputs = {"gsm8k": json.loads((HERE / "crosscheck/gsm8k.json").read_text())["gsm8k"],
                      "physicsquestions": json.loads((HERE / "crosscheck/bigbench.json").read_text())["physicsquestions"],
                      "twowikimultihopqa": json.loads((HERE / "crosscheck/twowiki.json").read_text())["cases"]}
        outputs[panel] = {}
        for ds, rows in inputs.items():
            results = []
            for row in rows:
                p = row.get("prediction", row.get("local_prediction"))
                if ds == "gsm8k":
                    official_raw = {"prediction_extracted": gsm.extract_answer(p), "gold_extracted": gsm.extract_answer(row["gold_answer"]),
                                    "correct": gsm.is_correct(p, {"answer": row["gold_answer"]})}
                    local_raw = local[ds].score(p, local[ds]._gold({"answer": row["gold_answer"]}))
                    differences = [] if official_raw["correct"] == local_raw["correct"] else ["correct"]
                elif ds == "physicsquestions":
                    s = row["official_sample"]
                    assert row["local_prediction"] == s["generative_response"] and row["local_gold"]["accepted"] == s["target"]
                    official_raw = namespace["exact_str_match_fn"]([s["target"]], [s["generative_response"]])
                    local_raw = local[ds].score(p, row["local_gold"])
                    differences = [] if official_raw["exact_str_match"] == local_raw["reward"] else ["reward"]
                else:
                    official_raw = wiki_official(wiki, row, panel)
                    local_raw = local[ds].score_prediction(deepcopy(p), deepcopy(row["gold"]))
                    differences = [key for key, value in official_raw["metrics"].items()
                                   if value != round(local_raw["official"][key] * 100, 2)]
                results.append({"id": row["id"], "official": official_raw, "local": local_raw, "differences": differences})
            outputs[panel][ds] = {"inputs": len(results), "agree": sum(not r["differences"] for r in results),
                                  "diverge": sum(bool(r["differences"]) for r in results),
                                  "divergent_metric_cells": sum(len(r["differences"]) for r in results), "rows": results}
            if ds == "twowikimultihopqa":
                golds, predictions, aliases = [], {"answer": {}, "sp": {}, "evidence": {}}, {}
                for row in rows:
                    directory = HERE / "serialized" / panel / row["id"]
                    golds.extend(json.loads((directory / "gold.json").read_text()))
                    for channel, values in json.loads((directory / "prediction.json").read_text()).items():
                        predictions[channel].update(values)
                    for line in (directory / "aliases.jsonl").read_text().splitlines():
                        value = json.loads(line)
                        assert value["Q_id"] not in aliases or aliases[value["Q_id"]] == value
                        aliases[value["Q_id"]] = value
                directory = HERE / "serialized" / panel / "aggregate"
                directory.mkdir(exist_ok=True)
                save(directory / "gold.json", golds)
                save(directory / "prediction.json", predictions)
                (directory / "aliases.jsonl").write_text("".join(json.dumps(v) + "\n" for v in aliases.values()))
                capture = io.StringIO()
                with contextlib.redirect_stdout(capture):
                    wiki.eval(str(directory / "prediction.json"), str(directory / "gold.json"), str(directory / "aliases.jsonl"))
                raw = capture.getvalue()
                official_metrics = json.loads(raw[raw.index("{"):])
                local_metrics = local[ds].evaluate_predictions({r["id"]: deepcopy(r["prediction"]) for r in rows},
                                                              [deepcopy(r["gold"]) for r in rows])
                outputs[panel][ds]["aggregate"] = {"official_stdout": raw, "official_metrics": official_metrics,
                    "local_metrics": local_metrics, "differences": [k for k in official_metrics if official_metrics[k] != local_metrics[k]]}
    assert all(m._SPEC._records == [] for m in local.values())
    outputs["identity"] = {"python": sys.version, "local_source_sha256": {
        ds: hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest() for ds, m in local.items()},
        "cached_dataset_records": {ds: len(m._SPEC._records) for ds, m in local.items()},
        "physics_profile": "unchanged upstream exact_str_match_fn AST; not full module import",
        "twowiki_scale": "round(local fraction * 100, 2) vs official published percentages"}
    save(HERE / "output.json", outputs)
    print(json.dumps({panel: {ds: {**{k: v for k, v in values.items() if k not in {"rows", "aggregate"}},
                                  **({"aggregate_differences": values["aggregate"]["differences"]} if "aggregate" in values else {})}
                             for ds, values in outputs[panel].items()}
                      for panel in ["authored", "crosscheck"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
