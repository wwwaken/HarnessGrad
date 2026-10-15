#!/usr/bin/env python3
"""Source-only denominator and numbered source custody; never import adapters."""
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from tools.check_dataset_blockers import published_declarations

GROUPS = {
    "scalar QA": ["gsm8k", "triviaqa", "strategyqa", "sportsunderstanding", "physicsquestions", "reasoning_gym", "bfcl_v3", "chessbench_puzzles"],
    "pair evidence JSON": ["fever", "hotpotqa", "musique"],
    "triple evidence JSON in answer.txt": ["twowikimultihopqa"],
    "GAIA answer normalizer": ["gaia"],
    "SQL plus private SQLite": ["bird_minidev"],
    "workbook pointer plus XLSX": ["spreadsheetbench"],
    "source program reconstruction": ["ds1000", "livecodebench"],
    "ordered native action replay": ["alfworld", "scienceworld", "jericho"],
    "service recording replay": ["appworld"],
    "JSON DB hash plus dialogue gates": ["tau_bench"],
    "single action replay": ["agentdojo"],
    "arbitrary task snapshot": ["terminal_bench"],
    "refused": ["api_bank", "nestful", "sotuqa", "tau2_bench"],
}
RANGES = {
    "eval/admission/artifact_admission.py": [(144, 177), (182, 205), (326, 446)],
    "eval/verification/pristine.py": [(96, 142)],
    "eval/verification/verifier.py": [(470, 493), (557, 568)],
    "eval/observe/tracing.py": [(310, 337)],
    "data/scaffolds/qa/base.py": [(323, 358)],
    "data/scaffolds/qa/verify/check.py": [(163, 220), (251, 265)],
    "data/scaffolds/qa/prediction.py": [(1, 38)],
    "data/datasets/twowikimultihopqa.py": [(411, 496)],
    "data/datasets/gaia/verify/check.py": [(68, 100)],
    "data/datasets/bird_minidev/verify/check.py": [(92, 133)],
    "data/datasets/spreadsheetbench/verify/check.py": [(163, 214), (237, 250), (328, 378)],
    "data/datasets/ds1000/verify/check.py": [(26, 57)],
    "data/datasets/livecodebench/verify/check.py": [(150, 175)],
    "data/datasets/alfworld/verify/check.py": [(147, 175)],
    "data/datasets/scienceworld/verify/check.py": [(140, 175)],
    "data/datasets/jericho/verify/check.py": [(98, 135)],
    "data/datasets/appworld/verify/check.py": [(35, 70)],
    "data/datasets/tau_bench/verify/check.py": [(109, 118), (184, 200), (284, 315)],
    "data/datasets/agentdojo/verify/check.py": [(18, 38)],
    "data/datasets/terminal_bench.py": [(231, 245)],
    "data/datasets/api_bank.py": [(169, 170)],
    "data/datasets/nestful.py": [(51, 52)],
    "data/datasets/sotuqa.py": [(157, 158)],
    "data/datasets/tau2_bench.py": [(150, 151)],
}


def main():
    published = set(published_declarations())
    assigned = [name for names in GROUPS.values() for name in names]
    assert len(assigned) == len(set(assigned)) and set(assigned) == published
    summary = json.loads((HERE / "evidence/summary.json").read_text())
    covered = set(summary["datasets"])
    opted = []
    for name in sorted(published):
        source = (ROOT / "data/datasets" / (name + ".py")).read_text()
        if any(isinstance(n, ast.Constant) and n.value == "pristine-offline" for n in ast.walk(ast.parse(source))):
            opted.append(name)
    for name in GROUPS["refused"]:
        tree = ast.parse((ROOT / "data/datasets" / (name + ".py")).read_text())
        load = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "load")
        assert any(isinstance(n, ast.Raise) for n in load.body)
    groups = [{"shape": shape, "datasets": names, "covered_datasets": sorted(covered & set(names)),
               "coverage": f"{len(covered & set(names))}/{len(names)}"} for shape, names in GROUPS.items()]
    inventory = {"published": sorted(published), "published_count": len(published),
                 "implemented_route_count": len(published) - len(GROUPS["refused"]),
                 "authored_paired_dataset_count": len(covered), "groups": groups,
                 "grouped_implemented_shapes": len(GROUPS) - 1,
                 "shapes_with_bounded_pairs": sum(bool(g["covered_datasets"]) for g in groups),
                 "pristine_dataset_literal_opt_ins": opted,
                 "production_pristine_datasets_certified_by_packet": 0,
                 "denominator_note": "Manually source-audited scorer read shapes, not demand x surface or exercises; partial authored controls only."}
    (HERE / "coverage.json").write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    print(json.dumps(inventory, indent=2, sort_keys=True))
    with (HERE / "source-audit.txt").open("x") as out:
        for rel, ranges in RANGES.items():
            raw = (ROOT / rel).read_bytes()
            out.write(f"FILE {rel} SHA256 {hashlib.sha256(raw).hexdigest()}\n")
            lines = raw.decode().splitlines()
            for start, end in ranges:
                for number in range(start, min(end, len(lines)) + 1):
                    out.write(f"{number:5d} {lines[number - 1]}\n")
    pins = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [HERE / "collect.py", HERE / "worker.py", HERE / "commands.sh",
             ROOT / "tests/fixtures/hg_woffscorer3/gaia_tau/offline_exec.py"]}
    (HERE / "execution-source-pins.json").write_text(json.dumps(pins, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
