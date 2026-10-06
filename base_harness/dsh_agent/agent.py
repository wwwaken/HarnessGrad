#!/usr/bin/env python3
"""Adapt DeepSeek Harness (`dsh`) to HarnessGrad's task/answer/trace contract.

DSH is an agent harness, so this file is a **launcher, not a loop**: the platform hands it
one task and one working directory, DSH does the work in that directory with its own tools,
and this file turns what it did into the two things the contract asks for.

    <entrypoint> --task <task.json> --workdir <dir>   ->  exit 0, answer.txt, trace.jsonl

**`cwd` is the whole interface.** Measured 2026-10-06: `dsh --profile headless "<task>"`
takes no `--cwd`/`--dir` flag (`dsh --profile headless --help` lists only `-h`), and it reads
and writes the process's working directory -- verified by running it from a temp directory and
watching the file it was asked for land there and nowhere else. It also picks up whatever
`AGENTS.md` the working directory carries, which for a task directory is the task's own
instructions. So the subprocess's `cwd` is the task, and nothing has to be translated.

**`agent_model` is DSH's own default, not the platform's `HG_AGENT_MODEL`.** This harness
does not read `HG_AGENT_MODEL`: DSH takes its model from its profile, whose
`agent-default-model` names `deepseek-flash`. Recording the platform's variable here would
put a model on the curve point that this harness never asked for -- the same "the record
names a party that did no work" defect the improver field exists to prevent.

**`--profile headless`.** DSH ships named profiles; the headless one is "answer one task,
stream reasoning to stderr, print the final assistant message, and exit" -- a one-shot agent
rather than a session, which is what a harness needs. Its `agent-default-model` names
`provider: deepseek-official, model: deepseek-flash` out of the box, so this harness measures
DSH with the model it ships with rather than with one this platform chose for it.

**DSH needs a profile, a container's `HOME` is empty, and the profile must not travel in this
tree.** Measured 2026-10-06. DSH resolves its plugin tree out of
`$HOME/.dsh/profiles/node_modules`: **277 absolute symlinks** into the DSH checkout, 90 KB, no
files of its own. An empty `HOME` means DSH composes no tree, and the headless runner then
returns *early and silently* -- exit 0, no output, no files
(`packages/bundle/headless/src/index.ts` returns when any of its `agents` /
`agentDefaultModel` / `sessions` services is missing). In a task container the failure is
louder (`Cannot find package '@deepseek-ai/cordis-plugin-timer'`), which is how it was found.

**Those symlinks cannot ship beside this file.** The platform stages a harness with
`shutil.copytree(harness_src, work)` (`ckpt/git_state.py:stage_workspace`) at its default
`symlinks=False`, so a link in this tree is *followed and copied* -- and these point into a 2 GB
dependency graph full of links of its own. Measured: the driver spun inside `shutil.copytree`
for over 800 s per attempt and produced nothing. So they are bound instead
(`harness.json`'s `runtime_paths` names `~/.dsh/profiles`), and `_install_profile` creates the
one link that joins them to the writable `HOME` the container gave this process.

**Credentials come from the agent's environment.** DSH reads a stored credential when it has
one and `DEEPSEEK_API_KEY` when it does not; measured with an empty `HOME` (which is what a
container gives it): the stored-credential path finds nothing and the environment variable is
what makes it work. So `HG_AGENT_API_KEY` -- the key the platform already gives the harness
for the *agent's* model, which is this harness's own model -- is passed through under DSH's
name. It is not written anywhere.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess

#: Where DSH lives and how to start it. Both are bound into the task container read-only by
#: `harness.json`'s `runtime_paths`, so these are the paths *inside* it.
#: **`node` version matters, and the failure is silent.** Measured 2026-10-06: the built
#: `apps/cli/lib/bin.js` runs under node **v22.19.0** and produces *nothing* under
#: **v22.16.0** -- exit code 0, no stdout, no stderr, no files, for every argv including
#: `--help`. The silence has a cause in DSH's own source: the headless runner returns early
#: when any of its `agents` / `agentDefaultModel` / `sessions` services is missing
#: (`packages/bundle/headless/src/index.ts`), so a tree that fails to compose exits as if it
#: had answered nothing to say. Both node binaries are on this host; this is the one that
#: works with the checkout as built.
DEFAULT_NODE = "/home/xubuqiang/.nvm/versions/node/v22.19.0/bin/node"
DEFAULT_DSH = "/mnt/20t/xubuqiang/deepseek-harness/apps/cli/lib/bin.js"

#: Where DSH keeps its own state. A container's `HOME` is a writable tmpfs, but it may be
#: unset entirely, and DSH resolves its home from it.
DEFAULT_HOME = "/tmp/dsh-home"


#: The plugin farm DSH's loader resolves its entries through, as **data**: one
#: `relative/name<TAB>absolute target` per line, 277 lines, 42 KB.
#:
#: It travels as text rather than as links because the platform stages a harness with
#: `shutil.copytree` (`ckpt/git_state.py:stage_workspace`), and a link in this tree is a
#: link the staging step has to decide about. Measured before it was fixed: 277 links into a
#: 2 GB DSH checkout made the driver recurse inside `copytree` for over 800 s per attempt and
#: produce nothing. Reproducing them here costs one `os.symlink` call each, into the writable
#: `HOME` the container gave this process, and leaves the harness tree nothing but text.
FARM_MANIFEST = Path(__file__).resolve().parent / "dsh_farm.tsv"


def _install_profile(home: Path) -> None:
    """Give DSH the two things an empty `HOME` is missing, and nothing else.

    **A directory it can write, and the module farm inside it.** Measured 2026-10-06, in a
    task container: DSH's `prepareProfile` writes `$HOME/.dsh/profiles/headless/cordis.yml`
    on every boot, so `profiles/` has to be a real writable directory -- pointing the whole
    of it at a read-only tree fails with `EROFS` on exactly that write. What DSH does *not*
    create for itself is `profiles/node_modules`, the farm its loader resolves loader-entry
    package names through; a container's `HOME` starts empty, the tree fails to compose, and
    the headless runner then returns *early and silently* (exit 0, no output, no files --
    `packages/bundle/headless/src/index.ts` returns when any of its `agents` /
    `agentDefaultModel` / `sessions` services is missing). In a container the boot failure is
    loud (`Cannot find package '@deepseek-ai/cordis-plugin-timer'`), which is how it was
    found.

    The farm is rebuilt from `dsh_farm.tsv` rather than copied, and the links point at
    absolute paths inside the DSH checkout -- which the container binds at the same path
    read-only (`harness.json`'s `runtime_paths`), so they resolve there.

    Idempotent, and it leaves an existing profile alone: an operator running this by hand
    keeps their own. Returns how many links it created, so the trace can say what happened
    rather than leaving a silent `except` to be guessed at.
    """
    if not FARM_MANIFEST.is_file():
        return -1
    dsh = home / ".dsh"
    dsh.mkdir(parents=True, exist_ok=True)
    profiles = dsh / "profiles"
    profiles.mkdir(parents=True, exist_ok=True)
    farm = profiles / "node_modules"
    if farm.exists():
        return -2
    farm.mkdir(parents=True, exist_ok=True)
    made = 0
    for line in FARM_MANIFEST.read_text(encoding="utf-8").splitlines():
        if "\t" not in line:
            continue
        name, _, target = line.partition("\t")
        link = farm / name
        try:
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(target)
            made += 1
        except OSError:
            # A filesystem that will not take one link is not a reason to fail the task:
            # DSH will try to materialise its own profile and the trace will say what
            # happened.
            continue
    return made


def command(prompt_path: Path) -> list[str]:
    """The argv that answers one task.

    The task text is passed as a single argument rather than on stdin: the headless app's
    own help says multiple words are joined by spaces, so an argv element is the shape it
    documents. It comes from a file because a task statement can be long enough to run into
    a command-line limit, and a truncated task is a task the agent was never given.
    """
    argv = shlex.split(os.environ.get("HG_AGENT_DSH_COMMAND", ""))
    if not argv:
        argv = [os.environ.get("HG_AGENT_NODE", DEFAULT_NODE),
                os.environ.get("HG_AGENT_DSH", DEFAULT_DSH)]
    if not argv:
        raise ValueError("HG_AGENT_DSH_COMMAND is empty")
    return argv + ["--profile", "headless", prompt_path.read_text(encoding="utf-8")]


def _deadline() -> float:
    """Seconds DSH is given: the environment's budget, less a margin, or a fallback.

    The margin matters here for the same reason it did for the codex adapter: the platform
    kills the container at the environment's own `agent_timeout_s` and does not tell the
    harness that number, so `HG_AGENT_DEADLINE_S` is exported for exactly this
    (`eval/container.py:container_env`). Stopping 90 s short lets DSH be reaped and the trace
    be written, so a run that ran out of time is recorded as a harness that stopped rather
    than as a container that was killed -- which reads like a harness that never started.
    """
    deadline = os.environ.get("HG_AGENT_DEADLINE_S")
    if deadline:
        return max(60.0, float(deadline) - float(os.environ.get("HG_AGENT_STOP_MARGIN_S", "90")))
    return float(os.environ.get("HG_AGENT_DSH_TIMEOUT_S", "780"))


def run(task: dict, workdir: Path) -> int:
    workdir = workdir.resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    answer = workdir / "answer.txt"
    answer.unlink(missing_ok=True)

    goal = task.get("goal") or task.get("instruction")
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError("task requires a non-empty goal")
    prompt = ("Complete the following task. Everything you need is in the current working "
              "directory, and the work is the files you leave there rather than a "
              "description of them.\n\n" + goal)
    if task.get("inputs"):
        prompt += "\n\nTask inputs:\n" + json.dumps(task["inputs"], ensure_ascii=False)
    prompt_path = workdir / ".dsh-task.txt"
    prompt_path.write_text(prompt, encoding="utf-8")

    env = {k: v for k, v in os.environ.items() if not k.startswith("HG_METHOD_")}
    env.setdefault("HOME", DEFAULT_HOME)
    home = Path(env["HOME"])
    home.mkdir(parents=True, exist_ok=True)
    farm_links = _install_profile(home)
    # DSH's own name for the key the platform gives the agent. Never logged, never written.
    if env.get("HG_AGENT_API_KEY") and not env.get("DEEPSEEK_API_KEY"):
        env["DEEPSEEK_API_KEY"] = env["HG_AGENT_API_KEY"]
    # A container has no `PATH` of its own for the bound node, and DSH's launcher is a node
    # script: `node` is named by absolute path in `command`, so nothing here needs `PATH`.

    timeout = _deadline()
    with (workdir / "trace.jsonl").open("w", buffering=1) as trace:
        def record(value: dict) -> None:
            trace.write(json.dumps(value, ensure_ascii=False) + "\n")

        record({"harness_identity": {"harness": "dsh-agent",
                                     "agent_backend": "dsh-headless",
                                     "agent_model": env.get("HG_AGENT_DSH_MODEL", "deepseek-flash")},
                "task_id": task.get("task_id")})
        # What the launcher did before it launched anything. A harness whose setup fails
        # silently fails in a way nobody can read afterwards: `-1` is "the manifest is not
        # beside me", `-2` is "the farm was already there", `>= 0` is how many links this
        # process made.
        # What the launcher did before it launched anything. A harness whose setup fails
        # silently fails in a way nobody can read afterwards: `-1` is "the manifest is not
        # beside me", `-2` is "the farm was already there", `>= 0` is how many links this
        # process made, and `probe_resolves` says whether the farm's links reach their
        # targets *here* -- which is the difference between "the links were not made" and
        # "they were made somewhere this process cannot see".
        probe = (home / ".dsh" / "profiles" / "node_modules" / "@deepseek-ai"
                 / "cordis-plugin-timer")
        record({"profile": {"home": str(home), "manifest": FARM_MANIFEST.is_file(),
                            "links_created": farm_links,
                            "probe_resolves": probe.exists()}})
        proc = subprocess.Popen(command(prompt_path), cwd=workdir, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            out, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
            _record_streams(out, err, record)
            record({"error": "dsh timed out", "timeout_s": timeout,
                    "deadline_s": float(os.environ.get("HG_AGENT_DEADLINE_S") or 0) or None})
            return 1
        _record_streams(out, err, record)
        final = (out or "").strip()
        if proc.returncode or not final:
            record({"error": "dsh failed or printed no final message",
                    "exit_code": proc.returncode})
            return proc.returncode or 1
        # The contract's answer file. For a task graded by its own tests this is a record of
        # what the agent said it did; for an answer-graded task it is the answer.
        answer.write_text(final + "\n", encoding="utf-8")
        record({"submitted": True, "answer": final[:4000]})
    return 0


def _record_streams(out: str, err: str, record) -> None:
    """DSH's two streams, as trace records.

    It streams its reasoning to **stderr** and prints the final assistant message to
    **stdout** (`dsh --profile headless --help`). Nothing here is machine-readable the way
    codex's `--json` events are, so the trace keeps the lines in order under two record
    kinds rather than pretending to a structure DSH does not emit. The distinction is the
    one that matters to a reader: `reasoning` is what it was thinking, `reply` is what it
    concluded.
    """
    for line in (err or "").splitlines():
        if line.strip():
            record({"reasoning": line.rstrip()})
    for line in (out or "").splitlines():
        if line.strip():
            record({"reply": line.rstrip()})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--workdir", required=True, type=Path)
    args = parser.parse_args()
    return run(json.loads(args.task.read_text()), args.workdir)


if __name__ == "__main__":
    raise SystemExit(main())
