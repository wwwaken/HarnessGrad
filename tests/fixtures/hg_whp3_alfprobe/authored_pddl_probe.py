"""Exercise ALFWorld's real synchronous PDDL wrapper using authored inputs only."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]


def authored_game():
    """No released game, trajectory, annotation, or reference contributes bytes."""
    return {
        "pddl_domain": """(define (domain authored)
  (:requirements :strips)
  (:predicates (ready ?o) (done ?o))
  (:action finish
    :parameters (?o)
    :precondition (ready ?o)
    :effect (and (done ?o) (not (ready ?o)))))""",
        "pddl_problem": """(define (problem authored-case)
  (:domain authored)
  (:objects object1)
  (:init (ready object1))
  (:goal (done object1)))""",
        "grammar": '''action finish {
  template :: "finish";
  feedback :: "done";
}
grammar :: """{
  "intro": [{"rhs": "An authored object is ready."}],
  "done": [{"rhs": "The authored action finished."}]
}""";
''',
    }


def main():
    spec = importlib.util.spec_from_file_location(
        "hg_whp3_alfprobe_gym_env", ROOT / "data/datasets/alfworld/lib/gym_env.py")
    gym_env = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gym_env)
    with tempfile.TemporaryDirectory(prefix="hg-hp3-alfprobe-") as directory:
        game = Path(directory) / "game.tw-pddl"
        game.write_text(json.dumps(authored_game(), indent=2) + "\n")
        env = gym_env.build(str(game))
        try:
            first = gym_env.reset(env)
            invalid = gym_env.step(env, "authored invalid command")
            finished = gym_env.step(env, "finish")
        finally:
            env.close()
        replay = gym_env.replay(str(game), ["authored invalid command", "finish"])
    paths = {module.__file__ for module in sys.modules.values()
             if getattr(module, "__file__", None)}
    package_roots = sorted({path.split("site-packages/", 1)[1].split("/", 1)[0]
                            for path in paths if "site-packages/" in path})
    print(json.dumps({"first": first, "invalid": invalid, "finished": finished,
                      "replay": replay, "package_roots": package_roots}, indent=2))
    assert first["won"] is False
    assert invalid["won"] is False
    assert finished["won"] is True and finished["done"] is True
    assert replay["won"] is True and len(replay["records"]) == 2


if __name__ == "__main__":
    main()
