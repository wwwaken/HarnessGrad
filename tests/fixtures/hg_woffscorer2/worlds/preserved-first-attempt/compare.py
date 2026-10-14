#!/usr/bin/env python3
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
result = {}
for dataset in ("jericho", "scienceworld"):
    official = json.loads((HERE / f"{dataset}-official.json").read_text())
    local = json.loads((HERE / f"{dataset}-local.json").read_text())
    local_by_id = {c["id"]: c for c in local["cases"]}
    rows = []
    for upstream in official["cases"]:
        local_case = local_by_id[upstream["id"]]
        evidence = local_case.get("evidence") or {}
        measured = upstream.get("measured", False) and evidence.get("measured", False)
        row = {"id": upstream["id"], "both_measured": measured,
               "official_score": upstream.get("score"), "official_maximum": upstream.get("maximum"),
               "official_normalized_fraction": upstream.get("official_normalized_fraction"),
               "local_score": evidence.get("score"), "local_reward": evidence.get("reward"),
               "local_exit_code": local_case.get("exit_code"),
               "agreement": (upstream["score"] == evidence["score"] and
                             upstream["official_normalized_fraction"] == evidence["reward"]) if measured else None}
        if not measured:
            row["official_error"] = upstream.get("error")
            row["local_error"] = local_case.get("error") or evidence.get("error")
        rows.append(row)
    result[dataset] = {"inputs": len(rows), "agreements": sum(r["agreement"] is True for r in rows),
                       "divergences": sum(r["agreement"] is False for r in rows),
                       "unmeasured": sum(not r["both_measured"] for r in rows), "rows": rows}
(HERE / "comparison.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, indent=2, sort_keys=True))
