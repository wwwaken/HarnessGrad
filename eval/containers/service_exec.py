"""Run a task's harness *inside* its service container. INTERFACE.md §2.5.3.

Why this module exists
----------------------
Every `exec` environment declares a `placement`, and until this module existed nothing
read it. An environment that declared `placement: "inside"` and named a service got the
`exec` path in `eval/containers/container.py`: a **second** container from `env.image`,
beside the service, joined to the service's network. The service container -- the thing
the dataset actually declared as its environment, with the declared `cpus`/`memory_mb` --
ran the mock API and nothing else, and the harness's own container was bounded by
`env.cpus`/`env.memory_mb` while the environment that bounds *it* was invisible.

So this module makes the declaration real for the one case it can mean: a single named
service, `kind: "exec"`, `placement: "inside"`. The harness command is `docker exec`'d
into that service container instead of being launched as a second container.

What the exec'd process can see, and what it cannot
---------------------------------------------------
The mount plan is `mounts()` and it is deliberately short: the task directory (writable,
at its **host** path, so nothing the harness records gets translated), the harness tree
and its scratch directory (that is what the second container was already given), and the
infrastructure sockets at the same fixed destinations
`eval/containers/{model,tool}_route.py` publish them at. Nothing else is added, so this
does not widen the *harness's* view beyond the one it had -- what changes is that the
service container now also has it, and `services.py`'s own comment ("no host tree") no
longer holds for the one service the harness runs in.

Two consequences are stated rather than hidden, because they are properties of running
inside a container the dataset owns rather than of this code:

* **A service that declares `record: True` has its recording mounted into that same
  container**, so a process inside it can read the recording and write to it. The
  platform's rule (`eval/service/services.py`, `mounts_for("harness", ...)` returns
  nothing) is that the harness cannot see a recording. That rule holds for every other
  placement and **does not hold here**; `receipt()` records it so a reader of the run
  can see which world a score was measured in.
* **The service container's root filesystem is writable** (a service has to be), so the
  harness can write to the environment's files where the second-container path gave it a
  read-only root. The recording and the world both live behind a facade the harness can
  now edit.

Neither is fixable from this side without not running the harness in that container, so
this module measures what it is and records it instead of pretending otherwise.

The user and the working directory
----------------------------------
`docker exec -u <uid:gid> -w <task_dir>`. The user is the one `services.start` already
started the container with (`--user uid:gid`), so `exec_defaults` is the same identity
for the container and for the process this platform adds to it; an exec as root would be
a strictly larger privilege set than the environment was given. The working directory is
the task directory **at its host path**, not the environment's `workdir`: the task
directory is bound at the host path (see above), and for AppWorld the environment's
`workdir` is `/appworld`, which inside the service container is the world server's own
data root (`data/datasets/appworld/server.sh`). Binding the task over it would take the
service's data away and every action would fail for a reason nothing would name.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import eval.containers.container as container_mod
from eval.containers import model_route, tool_route, unix_socket_route


class ServiceExecUnavailable(RuntimeError):
    """The declared placement cannot be applied to this environment.

    Raised rather than degraded: a `placement: "inside"` that silently ran somewhere else
    would make the record say the harness ran in an environment it never saw, which is
    the one failure mode this module exists to prevent.
    """


@dataclass(frozen=True)
class Plan:
    """Which service container the harness runs in.

    A dataclass rather than a tuple because the *selection* is the decision
    (`placement`, `kind`, exactly one service) and the rest of the module is mechanics.
    """

    service: dict

    @property
    def name(self) -> str:
        return self.service["name"]

    @property
    def image(self) -> str:
        return self.service["image"]


def plan(env: dict | None) -> Plan | None:
    """The service container this environment runs inside, or `None` for "as before".

    `None` is the whole of "unchanged": `placement` absent, `"beside"`, any other word,
    a `files` environment, an `exec` environment with no service, or an environment whose
    state is the container's own filesystem (`state: "container"` is a different path
    entirely, and the registry already refuses it together with services).

    More than one service is refused rather than guessed. There is no field that says
    which of two sidecars *is* the environment, and picking one would put the harness in
    a container the dataset never nominated.
    """
    env = env or {}
    if env.get("kind") != "exec" or env.get("placement") != "inside":
        return None
    if env.get("state") == "container":
        return None
    services = env.get("services") or []
    if not services:
        return None
    if len(services) != 1:
        raise ServiceExecUnavailable(
            f"placement 'inside' names {len(services)} services "
            f"({', '.join(str(s.get('name')) for s in services)}); the environment is "
            f"the one service the harness runs in, and a dataset with several sidecars "
            f"has not said which. Declare exactly one, or declare placement 'beside'.")
    return Plan(service=services[0])


def user() -> str:
    """The identity the exec runs as: the one the service container was started with.

    `services.start` passes `--user {os.getuid()}:{os.getgid()}` on every service, so
    naming the same pair here is what makes the exec's defaults the environment's rather
    than docker's (`root`). It is computed rather than read back from
    `docker inspect` because the platform is the only thing that starts a service.
    """
    return f"{os.getuid()}:{os.getgid()}"


#: Docker's `--mount` syntax splits on commas, so a path containing one cannot be
#: expressed at all. Refused rather than escaped: docker has no escape for it, and a
#: path silently truncated at the comma would mount the wrong directory.
_UNEXPRESSIBLE = (",", "\n", "\r")


def _bind(source: Path, destination: str, *, readonly: bool) -> list[str]:
    source = Path(source)
    if any(c in str(source) + destination for c in _UNEXPRESSIBLE):
        raise ServiceExecUnavailable(
            f"{source} -> {destination} cannot be expressed in docker mount syntax")
    return ["--mount", f"type=bind,src={source},dst={destination}"
            + (",readonly" if readonly else "")]


def mounts(*, task_dir: Path, harness_root: Path, state_dir: Path | None = None,
           readonly_paths: tuple[Path, ...] = (),
           model_socket: Path | None = None, tool_socket: Path | None = None,
           stepwise_dir: Path | None = None,
           network: str | None = None) -> tuple[str, ...]:
    """The docker `--mount` arguments the service container must be started with.

    Only what the harness needs to run, which is the same set the second-container path
    gives it -- this is not a widening, it is the same view moved into the environment:

    * the **task directory**, writable and at its host path: it is what the harness is
      asked to change, and translating it is the one thing
      `eval/containers/sandbox.py` says a platform must never do;
    * the **harness tree** read-only at its host path, because its entrypoint is
      `<repo>/<entry>` and the container path already relies on that;
    * its **scratch directory** (`.state/`), writable: the entrypoint contract hands it
      `HARNESSGRAD_STATE` and a harness that cannot write there cannot work;
    * declared `readonly_paths` (the interpreter and any harness runtime overlay), the
      same argument the container path passes as `readonly_paths`;
    * the **model and tool sockets** at the fixed destinations their own route modules
      publish, plus the stepwise socket at its host path -- validated by
      `eval/containers/unix_socket_route.py` exactly as the bwrap path validates them, so
      the "no swap, no alias, no writable ancestor" rules are the same rules.

    Order is parent-before-child for readability only: docker sorts nested mounts by
    destination depth, measured in `eval/containers/container.py` (`_mounts`).
    """
    task_dir = Path(task_dir).resolve()
    plan_mounts: list[tuple[Path, str, bool]] = [
        (task_dir, str(task_dir), False),
        (Path(harness_root).resolve(), str(Path(harness_root).resolve()), True),
    ]
    if state_dir is not None:
        plan_mounts.append((Path(state_dir).resolve(), str(Path(state_dir).resolve()), False))
    for extra in readonly_paths:
        extra = Path(extra).resolve()
        plan_mounts.append((extra, str(extra), True))

    writable = (task_dir, *((Path(state_dir).resolve(),) if state_dir else ()))
    exposed = tuple(destination for _, destination, _ in plan_mounts)
    if model_socket is not None:
        unix_socket_route.verify(Path(model_socket), root=model_route.ROOT, label="model",
                                 network=network, exposed_paths=exposed,
                                 writable_paths=writable)
        plan_mounts += [(Path(model_socket), str(model_route.ROOT / "model.sock"), True),
                        (model_route.FORWARDER, str(model_route.ROOT / "forwarder.py"), True)]
    if tool_socket is not None:
        unix_socket_route.verify(Path(tool_socket), root=tool_route.ROOT, label="tool",
                                 network=network, exposed_paths=exposed,
                                 writable_paths=writable,
                                 require_network_none=False)
        plan_mounts += [(Path(tool_socket), str(tool_route.SOCKET), True),
                        (tool_route.TRANSPORT_SOURCE, str(tool_route.TRANSPORT), True)]
    if stepwise_dir is not None:
        # Its host path, not a fixed destination: the relay hands the harness that path in
        # `HG_STEPWISE_SOCKET`, so moving it would hand the harness a name that is not
        # there.
        stepwise = Path(stepwise_dir).resolve()
        plan_mounts.append((stepwise, str(stepwise), True))

    arguments: list[str] = []
    for source, destination, readonly in plan_mounts:
        arguments += _bind(source, destination, readonly=readonly)
    return tuple(arguments)


def argv(*, container: str, workdir: Path | str, command: list[str],
         env: dict[str, str] | None = None, run_as: str | None = None) -> list[str]:
    """The `docker exec` argv. Split out so a test can read it without a daemon."""
    cmd = ["docker", "exec", "-u", run_as or user(), "-w", str(workdir)]
    for key, value in sorted((env or {}).items()):
        cmd += ["-e", f"{key}={value}"]
    return cmd + [container, *command]


def run(command: list[str], *, container: str, workdir: Path | str,
        env: dict[str, str] | None = None, timeout_s: int = 3600,
        run_as: str | None = None):
    """`subprocess.run` shape, inside the running service container.

    Routed through `eval/containers/container.docker` on purpose: that is where a call
    made *inside a task* starts streaming and beating, so a harness that spends forty
    minutes inside one exec stops being indistinguishable from a dead driver
    (`eval/observe/progress.py`).

    On a timeout the docker client is killed, not the daemon-side exec: the process the
    harness started keeps running until the **container** goes away. That cleanup is
    `RunningServices.stop()`'s `docker rm --force` in `eval/run/runner.py`'s `finally`,
    which is the same structural teardown the second-container path gets from removing
    its container -- the difference is that here it happens at the end of the task rather
    than at the end of the exec, so anything the harness backgrounded is still running
    while the check does. Recorded in `receipt()`; see the module docstring.
    """
    return container_mod.docker(*argv(container=container, workdir=workdir,
                                      command=command, env=env, run_as=run_as)[1:],
                                timeout=timeout_s)


#: The same defaults `data/scaffolds/registry.py` fills an `exec` environment with
#: (`ENV_DEFAULTS`). Repeated rather than imported: the registry is dataset-side
#: scaffolding and this layer must not depend on it, but the probe needs the number the
#: declaration would have been normalized to.
ENV_BOUND_DEFAULTS = {"cpus": 2, "memory_mb": 4096}


def shape(plan: Plan | None, env: dict) -> tuple:
    """The container this environment runs in, as a cache key.

    `(image, cpus, memory_mb, network)` -- the four facts a receipt is about. Two tasks of
    one dataset share it, which is why one probe admits all of them; the network is the
    declared **policy** and not the per-task network name, because the names differ per
    task by construction and the probe resolves the policy itself.
    """
    if plan is None:
        raise ServiceExecUnavailable("this environment does not run inside a service")
    return (plan.image,
            str(env.get("cpus", ENV_BOUND_DEFAULTS["cpus"])),
            str(env.get("memory_mb", ENV_BOUND_DEFAULTS["memory_mb"])),
            env.get("network"))


def observation_spec(plan: Plan | None, env: dict) -> tuple[str, dict]:
    """The image and spec the admission probe must measure for this plan.

    The bounds that bind the harness are the **service container's**, so the probe
    measures that container and not `env.image`. It then refuses when the two disagree:
    a receipt that measured 2 cpus while the environment declared 4 would admit a task on
    evidence about a container the score does not describe, which is the one thing the
    receipt exists to prevent. A service that declares no `cpus`/`memory_mb` is unbounded
    by docker's default, so there is nothing to observe and nothing to admit.
    """
    if plan is None:
        raise ServiceExecUnavailable("this environment does not run inside a service")
    declared: dict[str, float] = {}
    applied: dict[str, float] = {}
    for field, default in ENV_BOUND_DEFAULTS.items():
        declared[field] = float(env.get(field, default))
        if field not in plan.service:
            raise ServiceExecUnavailable(
                f"service {plan.name!r} declares no {field!r}, so its container runs "
                f"with docker's default instead of the environment's {field}="
                f"{declared[field]:g}; the harness would be bounded by something other "
                f"than what the dataset declared")
        applied[field] = float(plan.service[field])
    mismatch = {field: (declared[field], applied[field])
                for field in declared if declared[field] != applied[field]}
    if mismatch:
        raise ServiceExecUnavailable(
            "the environment and the service it runs in declare different bounds "
            f"({', '.join(f'{k}: env {v[0]:g} vs service {v[1]:g}' for k, v in mismatch.items())}); "
            "the service container's bounds are the ones that apply to the harness, so a "
            "receipt for the environment's numbers would describe a different container")
    return plan.image, {field: plan.service[field] for field in ENV_BOUND_DEFAULTS}


def receipt(*, plan: Plan, container: str, workdir: Path | str, mounts_used,
            network: str | None, recorded: bool) -> dict:
    """What this path did, for the run's record.

    Includes the two properties this placement cannot promise, because a score measured
    here and one measured in a second container are not the same measurement: the service
    recording is readable from inside (`recorded`), and the environment's root filesystem
    is writable. `agent_placement` is the field a reader keys on.
    """
    return {
        "agent_placement": "inside-service",
        "service": plan.name,
        "container": container,
        "image": plan.image,
        "user": user(),
        "workdir": str(workdir),
        "network": network,
        "mounts": [m for m in mounts_used if m != "--mount"],
        "service_recording_visible": bool(recorded),
        "rootfs_writable": True,
        "teardown": "service container removal (RunningServices.stop)",
    }
