# Runtime observation: the missing producer

**Status:** open. Nothing in this repository produces the observation; the platform only
validates one if it is handed over. This file specifies the piece that is missing, so a
container-backed dataset can be measured with a number that survives being questioned.

## The gap, precisely

`eval/admission/runner_admission.py::admit_runtime` is a strict checker. It compares a
declared policy against an **observed** one and refuses on any mismatch:

| refusal code | what it means |
| --- | --- |
| `resource_enforcement_unproven` | `observed.resource_backend` is not `cgroup-v1` / `cgroup-v2` |
| `deadline_enforcement_unproven` | `observed.timeout_backend` is not `host-supervisor` |
| `resource_limit_mismatch` | observed resources differ from the declared policy |
| `network_enforcement_unproven` | `observed.network != "none"` or `attachments != []` |
| `writable_root_unbounded` | `observed.read_only_root` is not `True` |
| `writable_surface_inventory_mismatch` | observed filesystem paths differ from the policy's |
| `filesystem_enforcement_unproven` | a surface's `backend` is not `tmpfs` / `project-quota` |
| `shared_quota_scope` | two surfaces report the same `scope_id` |
| `filesystem_limit_mismatch` | a surface's observed bytes/inodes differ from the policy |
| `stale_observation` | `observed.binding` is not the binding of the task being admitted |
| `invalid_evidence_hash` | `evidence_sha256` is missing or not a sha256 |

A repository-wide search finds those names **only in that file**. `runtime_observed` is a
parameter of `eval/admission/scorer_backend.py::admit` — supplied by the caller, produced by
nobody. There is no cgroup reader anywhere.

So the platform can check a fact it never collects, and
`eval/run/runner.py::_refuse_unobserved_policies` refuses every `exec` / container task before
staging with `backend_observation_unavailable`. **That is the whole reason a
container-backed dataset cannot be measured here.**

## Why this is not "just relax the gate"

Two different things, and only one of them is engineering:

* **A — produce the observation.** Write the thing that asks the kernel what limits are in
  force. This is what this brief specifies. When it exists, container datasets are admitted
  *with evidence*, and their scores mean what they say.
* **B — relax the refusal.** A policy decision for the operator, not a task. The decision
  record `docs/enforcement-proof-decision.md:45-46` deliberately kept this contract out of the
  2026-10-15 withdrawals, and the audit in `docs/paper-fidelity-audit-handoff.md:404` frames it
  as "(a) intended; or (b) the gate needs relaxing". Doing B as well as A would remove the
  property the platform exists to provide: a number nobody can look behind.

The one escape that exists today is
`driver.py --authorize-unobserved-diagnostic <reason>`: one train-side task, one trial, one job,
round 0, no method, and a record with `policy_enforcement_observed`, `measured`,
`production_authorized` and `comparable` all `False`. It answers "does the adapter run at all".
It cannot produce a comparable score, by design.

## The contract

`observed` is passed as the third argument of `admit_runtime(binding, policy, observed)`.
Note that `_object` is a **set equality** check, not a subset one: the dict must carry exactly
these nine keys, no more and no fewer.

```python
observed = {
    "binding":         {"adapter_id": str, "run_id": str, "trial_id": str,
                        "manifest_sha256": str},      # must equal the task's own binding
    "evidence_sha256": str,                           # sha256 over whatever the observer returns
    "resources":       {"cpu_millis": int, "memory_bytes": int,
                        "swap_bytes": int,            # the only key allowed to be 0/negative
                        "pids": int, "timeout_ms": int},
    "resource_backend": "cgroup-v1" | "cgroup-v2",
    "timeout_backend":  "host-supervisor",
    "network":          "none",
    "attachments":      [],                            # no extra network attachments
    "read_only_root":   True,
    "filesystems":      {"/abs/normalised/path": {
                            "bytes": int, "inodes": int,
                            "backend": "tmpfs" | "project-quota",
                            "scope_id": str,       # must be unique across the surfaces
                            "evidence_sha256": str}},
}
```

Rules the checker enforces and the observer must therefore satisfy:

* `observed["binding"]` equals the binding of the task being admitted (`stale_observation`
  otherwise) — the observation is bound to one task, not to a run;
* `observed["resources"]` equals `policy["resources"]` exactly, key for key;
* filesystem paths are absolute, `posixpath.normpath`-clean, not `/`, and at most
  `MAX_SURFACES = 32` of them; the observed path set equals the policy's;
* `policy["network"]` must already be `"none"` — a policy asking for anything else is refused
  before observation is even consulted (`network_policy_not_supported`).

## Where it plugs in

1. **The checker already exists** — call it, do not reimplement it:
   `eval/admission/runner_admission.py::admit_runtime(binding, policy, observed)`.
2. **The shape to copy** is the one existing caller:
   `eval/admission/scorer_backend.py:93`, which is handed `runtime_policy` and
   `runtime_observed` and calls `resources.admit_runtime(...)`. Its own admission receipt shows
   how the result is recorded (`evidence=dict(..., resources=resource_check)`).
3. **The two call sites that must learn about a task's observation** are the two calls to
   `_refuse_unobserved_policies` in `eval/run/runner.py` (line ~169 for the single-task path,
   line ~1147 for the round path). Today the function only has `diagnostic_authorization` as an
   alternative to refusing; it needs a second alternative that is *evidence*, not permission —
   an admitted runtime observation for that task and trial.

## One more gate, which observation cannot open: the network policy

A container task that needs to reach its own service must not assume the observation is the only
obstacle. It is not, and the second gate is the harder one because it is a **policy precondition
rather than a missing fact**:

```python
# eval/admission/runner_admission.py:151
_require(policy["network"] == "none", "network_policy_not_supported")
# eval/policy/runtime_policy.py:17
if network not in (None, "none"):
    raise ValueError(f"unsupported native sandbox network policy: {network!r}")
```

Both are evaluated before any observation is consulted, so **a perfect observer still refuses a
task that declares a `services` network**. Widening this is not part of producing the
observation; it is a change to the contract, and it means admitting tasks whose network
enforcement is not `none` — a different decision with a different owner.

**The platform already has the pattern for reaching a platform-side service with the network
off, twice.** `eval/service/unix_model_relay.py` is documented as *"Agent-only HTTP over
AF_UNIX, with a fixed localhost:8002 model route"*, and `eval/service/unix_stepwise_relay.py`
hands a harness `HG_STEPWISE_SOCKET` for the same purpose. In both, the service lives on the
platform side, is published as an **AF_UNIX socket**, and the harness is told the path through an
environment variable — inside `unshare-net`, with `network: "none"` intact.

So the shape to reach for is a third instance of that pattern, not a new network policy:

* the service stays a separate process; it simply does not need a container network identity;
* it is published as a unix socket, and the harness receives the path in an env var;
* `policy["network"]` stays `"none"`, so the gate above is satisfied rather than widened;
* the resource observation from the rest of this file is then the only remaining gap.

The two existing relays are written against a *fixed* route, so a general-purpose service relay
is new code — but of a shape that already exists twice in this tree.

A workdir that is an ordinary bind mount also cannot be admitted: each declared surface must
report `backend` in `("tmpfs", "project-quota")` with matching `bytes`/`inodes` and a unique
`scope_id`. `tmpfs` gives both trivially; `project-quota` needs the host provisioning named in
`docs/filesystem-quota-backends.md`.

## Prerequisite: decide this on the machine that will run the dataset

**This is the go / no-go, and it is not a code question.** cgroup limits exist only where the
host's hierarchy allows the user to create a subtree and write limit files. Run these on the
machine that will execute the dataset — the answers are not asserted here:

```bash
cat /sys/fs/cgroup/cgroup.controllers        # cgroup v2 controllers available to us
cat /sys/fs/cgroup/cgroup.subtree_control    # what is delegated to children
cat /proc/self/cgroup                        # which subtree we are in
mkdir /sys/fs/cgroup/hg-probe-$$ && \
  cat /sys/fs/cgroup/cgroup.subtree_control && \
  echo '+memory +cpu' > /sys/fs/cgroup/cgroup.subtree_control
# then, inside the new subtree:
echo $((256*1024*1024)) > memory.max && cat memory.max
cat /sys/fs/cgroup/hg-probe-$$/cpu.max
rmdir /sys/fs/cgroup/hg-probe-$$
```

* If the writes succeed, A is implementable on that host.
* If they are denied, the host needs administrator provisioning before any code matters. The
  two roles and what each owes are already written down in
  `docs/filesystem-quota-backends.md` ("Host operator (external)" and "Backend implementer
  (pending code + runtime)").

On a shared machine this is the likely blocker: `/` is shared with other users, and cgroup
delegation is normally an administrator's decision.

## Deliverable

One module that collects the observation for a running container and returns the dict above,
plus the wiring at the two runner call sites.

**The observer must read the kernel, not echo the policy.** That is the entire point: if the
module returns the numbers it was asked for, it is a restatement of the declaration and the
platform is no better off than before. Read `memory.max`, `cpu.max`, `pids.max` and the
process's own cgroup path back out of the filesystem after the container is running; enumerate
the actual network attachments; and for the deadline, record *which* process is the supervisor
and its observed deadline.

## Acceptance

Two tests, and the second one is the one that matters:

1. **It admits.** A container started with a declared policy produces an observation that
   `admit_runtime` accepts, and the resulting curve point records the admitted limits.
2. **It refuses a liar.** Feed `admit_runtime` an observation whose `resources` do not match the
   policy, whose `network` is `"bridge"`, whose `attachments` is non-empty, whose
   `resource_backend` is missing, whose `read_only_root` is `False`, and whose two surfaces share
   a `scope_id`. Each must be refused with the code in the table above. The existing tests in
   `tests/quality/test_runner_admission.py` are the place to add these.

A test that only proves the happy path proves nothing here: the value of this module is what it
does when the enforcement is *not* what was declared.

## What not to do

* Do not treat a launch flag, a config value, an environment variable, an adapter's own claim or
  a cached verdict as an observation. `runner.py`'s docstring says so explicitly, and it is the
  same class of mistake as fabricating a score.
* Do not have the process that *applies* the limit also be the only thing that *certifies* it
  without reading the kernel back.
* Do not add a path that yields a comparable score without the admission receipt. `measured`,
  `production_authorized` and `comparable` stay `False` until an observation says otherwise.
* Do not read operator authorization as observation. The existing contract already states that
  permission "is never treated as backend observation or production admission".

## Definition of done

* [ ] the observation for a running container is collected from the kernel, not restated;
* [ ] `admit_runtime` accepts it for a correctly limited container;
* [ ] every refusal code above has a test that triggers it;
* [ ] a curve point from such a run carries the admitted limits, so a reader can see the basis;
* [ ] `docs/paper-fidelity-audit-handoff.md:404` can be closed as answered by measurement
      rather than by relaxing the gate.
