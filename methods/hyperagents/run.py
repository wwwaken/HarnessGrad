#!/usr/bin/env python3
"""HyperAgents' parent-selection rule, as a HarnessGrad method.

Why this file exists
--------------------
HyperAgents keeps an archive and draws a parent from it. From its own code
(`utils/gl_utils.py`):

    mid = mean(top-3 scores)
    score_child_prop:  p(c) ∝ sigmoid(10*(score_c - mid)) * exp(-(children_c/8)^3)

The sigmoid is centred on the *mean of the top three*, not on a fixed 0.5 as DGM
centres it, and the child penalty is a **cube that only starts to bite past about
eight children** rather than DGM's `1/(1+children)`.

The finding this port exists to make checkable
----------------------------------------------
HyperAgents ships **two** selection functions that disagree, and the difference is
not the formula -- it is whether the formula is used at all:

* `utils/gl_utils.py:570-584` (`score_child_prop`, the CLI default,
  `generate_loop.py:1071`) really does sample proportional to
  `sigmoid(10*(s-mid)) * exp(-(c/8)^3)` via `random.choices(..., weights=...)`.
* `select_next_parent.py:49-57` (reached under `--edit_select_parent`) computes
  the same child counts, then ends in `random.choice(list(candidates.keys()))`.
  The counts and scores it just derived are **discarded**, and the line above is
  commented "keeping the search space open".

So the uniform branch is uniform because its weights are dead code, not because
the sigmoid cancels: a normalized sigmoid over candidates is *not* uniform, and a
first reading that says otherwise would turn "one of its two selectors ignores
its own statistics" into a much weaker "HyperAgents samples randomly by design".
This was checked against the source after the stronger claim failed a test, and
the claim that failed is recorded here rather than quietly dropped.

The method therefore records which setting ran and how far that setting's actual
probability vector is from uniform on this run, so the claim is checkable on real
data instead of asserted.

What is transplanted
--------------------
* Parent selection: `mid = mean(top-3)`, the sigmoid around it, the
  `exp(-(children/8)^3)` penalty (`gl_utils.py:570-584`).
* The **validity gate as a retention rule** (`generate_loop.py:706-714`): a node
  is a candidate for parenthood only if its run produced a score and the
  improvement mechanism compiled. Score never enters this gate.

What is not transplanted
------------------------
* **Staged-eval rescaling** (`gl_utils.py:38-44`, `:526`): with no full eval run,
  HyperAgents multiplies both the agent and ensemble scores by the domain's
  staged fraction. The platform's score is already a full-set measurement, so
  applying a discount would invent an advantage the platform did not grant.
* **`type="max"` over agent and ensemble scores**: needs several archive members
  evaluated together; mode A has none.
* **Multi-domain averaging**: the platform has one task set, so the mean is a
  no-op -- harmless, but it is a real loss of the structure the rule was tuned
  around.
* Docker, the meta-agent that rewrites its whole repo, and generation-level patch
  replay (`generate_loop.py:502-504`). The edit half here is the shared editor.

What mode A costs this method
-----------------------------
One candidate per round and an unconditional accept, so there is no "which of
several children to keep" and no true archive. What survives is the selection
rule and the validity gate; the method records what the archive would have done
rather than pretending it did it.
"""
from __future__ import annotations

import math
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import editor                                                  # noqa: E402
import protocol                                                # noqa: E402

#: The child penalty's scale and exponent (`gl_utils.py:570-584`).
CHILD_SCALE, CHILD_POWER = 8.0, 3.0
STEEP = 10.0

#: Which selection setting to actually build on. `score_child_prop` is
#: HyperAgents' CLI default (`generate_loop.py:1071`); `best` is its function
#: default (`gl_utils.py:511`) -- the program ships two different defaults, so the
#: one we use is named here and recorded on every point.
SETTING = os.environ.get("HG_HYPERAGENTS_SELECT", "score_child_prop")

HYPER_SYSTEM = """You are improving an agent harness, as one step of a self-referential
search. The archive has chosen which previous state to build on.

Reply with JSON only:

  {"files": [{"path": "<relative path>", "content": "<complete new file contents>"}],
   "hypothesis": "<one sentence: what you changed and why>",
   "predicted_affected": ["<task ids you expect to change>"]}

Rules:
- `path` is relative to the harness root. `harness.json` may not be changed, and
  neither may anything that selects or evaluates: those stay fixed by construction.
- `content` must be the COMPLETE new file, not a diff. This may create a new file.
- The harness may be changed anywhere else -- there is no single editable file.
- `predicted_affected` is a *pre-registration*: write it before you are measured.
- If the evidence does not support any change, reply {"no_change": "<reason>"}.
"""


def _score(point: dict) -> float:
    """The score on the side the method is shown, never the exam (§2.3, §2.6).

    `protocol.studied_score` decides which field that is, from the record's
    `score_kind`. This used to try `train_score` and fall back to `score`, which
    happens to be right on a §2.6 train run (`train_score` is null there) but is the
    wrong reason for the right answer -- and on any point where `score` is the exam it
    would have read the exam.
    """
    return protocol.studied_score(point) or 0.0


def _sigmoid(x: float) -> float:
    if x < -60:
        return 0.0
    if x > 60:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def _children(history: list[dict]) -> dict[int, int]:
    """Lineage as this method declared it, via `method_reported`.

    `method_reported` round-trips into the next round's history, so a method can
    keep its own record of which state each round was built on. On mode A's plain
    chain every count would be 1 and the penalty inert; it becomes informative
    exactly because this method may branch backwards to an earlier state.
    """
    counts: dict[int, int] = {}
    for point in history:
        declared = (point.get("method_reported") or {}).get("hyper_parent")
        if isinstance(declared, int):
            counts[declared] = counts.get(declared, 0) + 1
    return counts


def _valid(point: dict) -> bool:
    """The validity gate (`generate_loop.py:706-714`) -- never a score gate.

    HyperAgents never removes an archive entry for scoring badly. A node leaves
    the *candidate* set only when its run did not produce a usable result. Here
    that is: the round was measured, and the method's own edit was accepted as a
    change (a round that changed nothing is not a distinct state to build on).
    """
    if not point.get("measured_by_platform", True):
        return False
    reported = point.get("method_reported") or {}
    return not reported.get("rejected")


def weights_for(candidates: list[dict], scores: dict, children: dict,
                mid: float, kind: str) -> dict:
    """One setting's raw (unnormalized) weights, exactly as the source computes them.

    Module-level so the rule can be tested without going through the sampler. A
    rule that can only be observed through one sampled pick is a rule nobody can
    check -- and checking this one is the whole reason the port reports a table
    rather than a single choice.
    """
    out = {}
    top = max(scores.values()) if scores else 0.0
    for point in candidates:
        r = point.get("round", 0)
        if kind == "best":
            out[r] = 1.0 if scores[r] == top else 0.0
        elif kind == "uniform":
            out[r] = 1.0
        elif kind == "score_prop":
            out[r] = _sigmoid(STEEP * (scores[r] - mid))
        else:                                       # score_child_prop
            out[r] = (_sigmoid(STEEP * (scores[r] - mid))
                      * math.exp(-((children.get(r, 0) / CHILD_SCALE) ** CHILD_POWER)))
    return out


def select_parent(history: list[dict], round_index: int) -> tuple[dict, dict]:
    """Returns (chosen point, a report comparing all three settings."""
    candidates = [p for p in history if _valid(p)]
    if not candidates:
        candidates = history[-1:] or [{}]

    scores = {p.get("round", 0): _score(p) for p in candidates}
    top3 = sorted(scores.values(), reverse=True)[:3]
    mid = sum(top3) / len(top3) if top3 else 0.0
    children = _children(history)

    table = {k: weights_for(candidates, scores, children, mid, k)
             for k in ("score_child_prop", "score_prop", "uniform", "best")}
    chosen_weights = table.get(SETTING, table["score_child_prop"])
    total = sum(chosen_weights.values())

    # A degenerate weight vector (all zero, or a single candidate under `best`)
    # falls back to uniform, which is where HyperAgents lands anyway when the
    # weights do not normalize (`gl_utils.py:565-568`).
    if total <= 0:
        chosen_weights = {r: 1.0 for r in chosen_weights}
        total = float(len(chosen_weights))

    rng = random.Random(round_index * 104729)
    pick = rng.random() * total
    chosen, running = candidates[-1], 0.0
    for point in candidates:
        running += chosen_weights[point.get("round", 0)]
        if pick <= running:
            chosen = point
            break

    best = max(candidates, key=_score)
    # How far the setting that actually ran is from uniform, computed rather than
    # asserted. `score_prop` is NOT uniform -- a normalised sigmoid over
    # candidates keeps its ordering. The uniform branch is uniform only because
    # `select_next_parent.py` discards the weights it just computed, and an
    # earlier version of this file claimed the stronger, wrong thing.
    uniform = {r: 1.0 / len(candidates) for r in scores}
    chosen_total = sum(chosen_weights.values()) or 1.0
    max_dev = max(abs(chosen_weights[r] / chosen_total - uniform[r]) for r in scores)

    report = {
        "rule": "HyperAgents score_child_prop: sigmoid(10*(s-mid)) * exp(-(c/8)^3)",
        "setting": SETTING,
        "mid_of_top3": round(mid, 4),
        "candidates": [p.get("round") for p in candidates],
        "child_counts": {str(k): v for k, v in sorted(children.items())},
        "weights": {str(r): round(w, 6) for r, w in sorted(chosen_weights.items())},
        "selected_parent": chosen.get("round"),
        "best_round": best.get("round"),
        "chose_something_other_than_best": chosen.get("round") != best.get("round"),
        "is_uniform": max_dev < 1e-9,
        "deviation_from_uniform": round(max_dev, 9),
        "note": "gl_utils.py:570-584 uses the child counts; select_next_parent.py:"
                "49-57 computes them and then discards them in random.choice, which "
                "is why that branch -- and only that branch -- is uniform",
        "seed": round_index * 104729,
    }
    return chosen, report


def _state_dir(base: Path, round_no) -> str | None:
    import json
    index = editor.channel(base) / "states" / "index.json"
    if not index.exists():
        return None
    try:
        data = json.loads(index.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return (data.get(f"round-{round_no}") or {}).get("harness_dir")


def build_prompt(base: Path, req: dict, parent: dict, report: dict) -> str:
    sources = editor.load_sources(base)
    # **Traces come from the *incumbent*, sources from the parent.** The parent is a staged
    # state (`states/round-<n>/`) and a staged state is a harness commit -- it carries no
    # `_harnessgrad/`, so `load_traces(parent)` returns the literal sentence "the platform
    # staged no traces for this round". Measured tonight: codex-on-the-local-model was handed
    # that prompt and correctly answered that there was no evidence; the method then reported
    # "no usable edit". The rule's whole point is to build on an old state, and the evidence
    # about how that state behaved is the *round's*, which lives in the incumbent's channel.
    traces = editor.load_traces(Path(req["base_harness"]), limit=6,
                                order=editor.failing_first(Path(req["base_harness"])))
    return (
        f"HyperAgents round {req.get('round_index', 1)}. The archive chose round "
        f"{parent.get('round')} as this round's parent (score {_score(parent):.3f} on "
        f"the tasks you can see; the best candidate is round {report['best_round']}).\n\n"
        f"## What the harness did on the parent\n{traces}\n\n"
        "## The parent's sources\n"
        + "\n\n".join(f"### {k}\n```\n{v}\n```" for k, v in sources.items())
        + "\n\nPropose one change to this parent, or say no_change."
    )


def main() -> int:
    """**A B-shaped submission: one call, `k` children from sampled parents.**

    HyperAgents' rule is a population rule -- parent weights are a sigmoid centred on the
    top-three mean, times `exp(-(children/8)^3)`, and both terms are *about siblings*. Our
    port was one-candidate-per-round to fit mode A, so the population never existed and the
    child-count term was dead code (`hyperagents/run.py` says as much in its own notes about
    `select_next_parent` being the branch that actually used the statistics). One call now
    draws `HG_HYPERAGENTS_CHILDREN` parents (default 3, from the same weight function) and
    submits one child per parent; every child is measured, and the platform's budget caps how
    many states the run pays for.
    """
    req = editor.read_request()
    editor.require_api(req)
    base = Path(req["base_harness"])
    history = editor.load_history(base)
    round_index = int(req.get("round_index", 1))
    children = max(1, int(os.environ.get("HG_HYPERAGENTS_CHILDREN", "3")))
    remaining = int(req.get("epochs_remaining") or req.get("epochs_total") or children)
    children = max(1, min(children, remaining))

    steps: list[dict] = []
    reports: list[dict] = []
    errors: list[BaseException] = []
    for child in range(children):
        parent, report = select_parent(history, round_index + child)
        report["child"] = child + 1
        report["children_this_call"] = children
        report["parent_round"] = parent.get("round")
        parent_dir = _state_dir(base, parent.get("round"))
        if not parent_dir or not Path(parent_dir).is_dir():
            reports.append({**report, "why": "the selected state is not staged"})
            continue

        dest = editor.candidate_path(req, f"child{child + 1}")
        try:
            reply = editor.ask(build_prompt(Path(parent_dir), req, parent, report),
                               system=HYPER_SYSTEM, base=base, parent=Path(parent_dir))
        except SystemExit:
            raise
        except Exception as exc:                                       # noqa: BLE001
            errors.append(exc)
            reports.append({**report, "why": f"{type(exc).__name__}: {exc}"[:160]})
            continue

        edits = [] if "no_change" in reply else reply.get("files")
        changed, files, note = editor.apply_edits(Path(parent_dir), dest, edits)
        if "no_change" in reply:
            hypothesis = str(reply["no_change"])[:200]
        elif not changed:
            hypothesis = f"unusable proposal: {note}"
        else:
            hypothesis = str(reply.get("hypothesis", ""))[:200]
        # The pre-registration goes into the record whether or not the edit landed, so the
        # next round can grade the prediction against what actually flipped.
        if isinstance(reply.get("predicted_affected"), list):
            report["predicted_affected"] = reply["predicted_affected"]
        reports.append({**report, "changed": bool(changed), "why": hypothesis})
        steps.append({
            "harness_dir": dest, "changed": changed, "files": files,
            "label": ((f"[HyperAgents parent r{parent.get('round')}] " + hypothesis[:50])
                      if changed else
                      f"HyperAgents: no edit (parent r{parent.get('round')})"),
            "edit_kind": "hyperagents_rule", "hypothesis": hypothesis,
            "method_reported": {"hyperagents": report,
                                "hyper_parent": parent.get("round"),
                                "hyper_parents": [r.get("parent_round") for r in reports],
                                "child": child + 1},
        })

    measured = [step for step in steps if step.get("changed")]
    parents = [r.get("parent_round") for r in reports]
    carried = {"hyperagents": reports,
               "hyper_parent": parents[0] if parents else None,
               "hyper_parents": parents,
               "children_this_call": children}
    if not measured:
        # A total outage is `fail` (the call did not run); a draw where the model declined
        # is a report with `stop: false`, because one unlucky sample of parents is not a
        # reason to give up the rest of the budget -- the population draws again.
        if errors:
            return editor.fail(req, method="hyperagents", exc=errors[0], base=base,
                               state=carried)
        reasons = []
        for report in reports:
            why = str(report.get("why") or "")
            if why and why not in reasons:
                reasons.append(why)
        return editor.report(
            req, method="hyperagents", harness_dir=base, changed=False,
            hypothesis=(f"{len(steps)} child(ren) drew no usable edit this call: "
                        + " | ".join(reasons))[:200],
            edit_kind="hyperagents_rule", method_reported=carried,
            acceptance_rule=("HyperAgents' validity gate never looks at score; the "
                             "platform's measurement decides the score"),
            stop=False, label="HyperAgents: no child produced")

    return editor.report_many(
        req, method="hyperagents", steps=measured,
        acceptance_rule=("HyperAgents' validity gate never looks at score; the "
                         "platform's measurement decides the score"),
        stop=True,
        note=f"HyperAgents: {len(measured)} child(ren) submitted in one call",
        extra={"children_this_call": len(measured)},
    )


if __name__ == "__main__":
    raise SystemExit(main())
