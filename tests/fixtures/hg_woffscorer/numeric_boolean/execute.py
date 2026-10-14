#!/usr/bin/env python3
"""Execute unmodified official modules or actual local score() on shared controls."""
import argparse
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_source(path, name):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", choices=["gsm8k", "strategyqa"])
    parser.add_argument("scorer", choices=["official", "local"])
    parser.add_argument("--canonical-boolean-projection", action="store_true")
    args = parser.parse_args()
    cases = json.loads((ROOT / "inputs.json").read_text())[args.dataset]
    identity = {"dataset": args.dataset, "scorer": args.scorer}
    if args.canonical_boolean_projection:
        assert (args.dataset, args.scorer) == ("strategyqa", "local")
        cases = [x for x in cases if x["panel"] == "valid_official_boolean"]
        identity["fixture_prediction_projection"] = "canonical Boolean true/false to local Yes/No"
    if args.scorer == "official":
        filename = "dataset.py" if args.dataset == "gsm8k" else "eval.py"
        source = ROOT / "source" / args.dataset / filename
        module = load_source(source, "controlled_official_scorer")
        identity.update(source=str(source.relative_to(REPO)), source_sha256=digest(source))
        if args.dataset == "gsm8k":
            import torch
            identity["torch_version"] = torch.__version__
            identity["torch_source_sha256"] = digest(Path(torch.__file__))
        else:
            import numpy
            identity["numpy_version"] = numpy.__version__
            identity["sari_source_sha256"] = digest(source.parent / "sari.py")
            identity["numpy_source_sha256"] = digest(Path(numpy.__file__))
    else:
        sys.path.insert(0, str(REPO))
        # PyArrow's native parquet reader bypasses Python's open audit hook.
        # Refuse table reads before the adapter's eager _SPEC.build(); score() and
        # every production source byte are untouched. Restore the helper afterward.
        from data.scaffolds.qa import base
        original_reader = base.parquet_rows
        def refuse_parquet_rows(path):
            raise PermissionError("controlled scorer import excludes parquet payloads")
        base.parquet_rows = refuse_parquet_rows
        try:
            module = importlib.import_module(f"data.datasets.{args.dataset}")
        finally:
            base.parquet_rows = original_reader
        source = Path(module.__file__)
        identity.update(source=str(source.relative_to(REPO)), source_sha256=digest(source),
                        qa_base_sha256=digest(REPO / "data/scaffolds/qa/base.py"),
                        import_only_parquet_reader_override="refuse before native read; restored before score()",
                        dataset_load_error=module._SPEC.load_error)
        assert not module._SPEC.ensure(), "No released dataset records may be loaded"

    results = []
    for case in cases:
        prediction = case["prediction"]
        canonical_gold = case["gold_answer"]
        if args.scorer == "official" and args.dataset == "gsm8k":
            raw = {"extracted_prediction": module.extract_answer(prediction),
                   "extracted_gold": module.extract_answer(canonical_gold),
                   "is_correct": module.is_correct(prediction, {"answer": canonical_gold})}
            verdict = raw["is_correct"]
        elif args.scorer == "official":
            evaluator = module.AnswerEvaluator(None)
            evaluator({"answer": canonical_gold}, prediction)
            raw = evaluator.get_metrics()
            verdict = raw["Accuracy"] == 1
        else:
            if args.dataset == "gsm8k":
                gold = module._gold({"answer": canonical_gold})
            else:
                # Official gold is a JSON Boolean; the adapter requires its Yes/No label.
                # Prediction values remain unchanged, including out-of-contract probes.
                gold = {"answer": "Yes" if canonical_gold else "No"}
            passed_prediction = prediction
            if args.canonical_boolean_projection:
                passed_prediction = "Yes" if prediction else "No"
            raw = module.score(passed_prediction, gold)
            verdict = raw["correct"]
        results.append({"id": case["id"], "panel": case.get("panel", "completion_strings"),
                        "prediction": prediction, "canonical_gold": canonical_gold,
                        "correct": verdict, "raw_output": raw})
        if args.canonical_boolean_projection:
            results[-1]["passed_prediction"] = passed_prediction
    output = {"identity": identity, "results": results}
    if args.dataset == "strategyqa" and args.scorer == "official":
        evaluator = module.AnswerEvaluator(None)
        for case in cases:
            evaluator({"answer": case["gold_answer"]}, case["prediction"])
        output["raw_aggregate_metrics"] = evaluator.get_metrics()
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
