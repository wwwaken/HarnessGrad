#!/usr/bin/env python3
"""Independent direct upstream calls or unchanged local fresh-world check calls."""
import contextlib
import gc
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
JRE = "/mnt/20t/xubuqiang/datasets/scienceworld/jre/jdk-17.0.20.1+1-jre"

def official(dataset, spec, case, workdir):
    if dataset == "jericho":
        from jericho import FrotzEnv
        env = FrotzEnv(str(workdir / spec["game"]["rom"]), seed=spec["game"]["seed"])
        observation, info = env.reset()
        maximum = env.get_max_score()
        initial_native_score = env.get_score()
    else:
        os.environ["JAVA_HOME"] = JRE
        os.environ["PATH"] = JRE + "/bin" + os.pathsep + os.environ.get("PATH", "")
        from scienceworld import ScienceWorldEnv
        env = ScienceWorldEnv("", None, envStepLimit=spec["budget"])
        task = spec["task"]
        env.load(task["task_name"], task["variation"], task["simplifications"], generateGoldPath=False)
        maximum = 100
        observation, info = None, None
        initial_native_score = env.server.getScore()
    steps = []
    try:
        for action in case["actions"]:
            obs, reward, done, raw_info = env.step(action)
            steps.append({"action": action, "observation": obs, "reward": reward,
                          "done": done, "info": raw_info})
            if done:
                break
        score = steps[-1]["info"]["score"] if steps else (
            initial_native_score if dataset == "jericho" else int(round(100 * initial_native_score)))
        return {"id": case["id"], "measured": True,
                "initial_observation": observation, "initial_info": info,
                "initial_native_score": initial_native_score,
                "score": score, "maximum": maximum,
                "official_normalized_fraction": score / float(maximum) if maximum else None,
                "raw_steps": steps,
                "empty_trace_score_contract": "actual upstream get_score() / JVM getScore() query; no local initialization borrowed"}
    finally:
        env.close()
        if dataset == "scienceworld":
            process = env._gateway.java_process
            try:
                status = process.wait(timeout=15)
            except Exception:
                process.kill()
                status = process.wait(timeout=5)
            print(json.dumps({"java_child_cleanup": {"case": case["id"], "returncode": status,
                                                     "terminated": process.poll() is not None}}), file=sys.stderr)

def local(dataset, spec, case, workdir):
    lib = REPO / "data/datasets" / dataset / "lib"
    sys.path.insert(0, str(lib))
    source = REPO / "data/datasets" / dataset / "verify/check.py"
    module_spec = importlib.util.spec_from_file_location("controlled_local_check", source)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    evidence = workdir / "evidence.json"
    reward_file = workdir / "reward.txt"
    argv = ["--workdir", str(workdir), "--evidence-file", str(evidence), "--reward-file", str(reward_file)]
    if dataset == "scienceworld":
        os.environ["HG_SCIENCEWORLD_JAVA"] = JRE
        argv += ["--budget", str(spec["budget"])]
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = module.main(argv)
    result = {"id": case["id"], "exit_code": code, "stdout": stdout.getvalue(), "stderr": stderr.getvalue(),
              "evidence": json.loads(evidence.read_text()) if evidence.exists() else None,
              "reward_file": reward_file.read_text() if reward_file.exists() else None}
    gc.collect()
    return result

def main():
    dataset, mode = sys.argv[1:3]
    spec = json.loads((HERE / "inputs.json").read_text())[dataset]
    result = {"dataset": dataset, "mode": mode, "production_runtime_observation": False,
              "cases": []}
    scratch = os.environ["HG_WOFFSCORER2_WORLD_SCRATCH"]
    for case in spec["cases"]:
        with tempfile.TemporaryDirectory(prefix=dataset + "-" + case["id"] + "-", dir=scratch) as task_dir:
            workdir = Path(task_dir)
            if dataset == "jericho":
                shutil.copyfile(HERE / "acorncourt.z5", workdir / "acorncourt.z5")
                (workdir / "jer_game.json").write_text(json.dumps(spec["game"]))
                logname = "jer_actions.jsonl"
            else:
                (workdir / "scw_task.json").write_text(json.dumps(spec["task"]))
                logname = "scw_actions.jsonl"
            (workdir / logname).write_text("".join(json.dumps({"kind": "action", "step": i, "action": a}) + "\n"
                                                for i, a in enumerate(case["actions"])))
            try:
                entry = (official if mode == "official" else local)(dataset, spec, case, workdir)
            except Exception as exc:
                entry = {"id": case["id"], "measured": False, "exception": type(exc).__name__,
                         "error": str(exc), "traceback": traceback.format_exc()}
            result["cases"].append(entry)
            print(json.dumps({"completed_case": case["id"], "mode": mode}), file=sys.stderr, flush=True)
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
