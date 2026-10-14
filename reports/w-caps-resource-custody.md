# AppWorld resource custody - w-caps

2026-10-15; isolated worktree `/tmp/hg-caps`, branch `wg-caps`, baseline `3616713`.
Source review, archived receipt inspection and mocked command construction only.
No benchmark task, model, GPU, endpoint call or container start was performed.

**The service was simply unset, with no inherited platform resource envelope.** No
documented AppWorld exemption was found. This change declares service CPU/memory
and applies the existing container envelope: **2 CPUs, 4096 MiB, 1024 PIDs**.
Actor and verifier already receive those values from container defaults.
Resource-custody change only; no live post-change cgroup observation.

## Three roles and the actual source paths

Default image bindings (environment overrides remain possible):

| Role | Default reference | Declaration |
| --- | --- | --- |
| Actor `IMAGE` | `harnessgrad/appworld-agent@sha256:d3a04ec8e295710347e978d8e58c663161d829e7dfa544da4d82d0d67abbd8eb` | `data/datasets/appworld.py:53-56`; consumed at `:296` |
| Service `SERVICE_IMAGE` | `harnessgrad/appworld-service@sha256:db09e34ec90347e7d5271d95445f360222ba1aef3ca0eaa5614ce768bf23aca4` | `data/datasets/appworld.py:57-60`; consumed at `:304` |
| Verifier `VERIFIER_IMAGE` | `harnessgrad/appworld-service@sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca` | `data/datasets/appworld.py:61-64`; consumed at `:288` |

| Role | Before this change | Source after this change |
| --- | --- | --- |
| Actor | ENV declares `cpus=2`, `memory_mb=4096`; PID limit is not a dataset field. Its mount route actually uses the helper defaults: `--cpus 2 --memory 4g --pids-limit 1024`. | `data/datasets/appworld.py:294-300,322-325`; `eval/run/runner.py:461-471` calls `container.run`; `eval/containers/container.py:575-582,604-609` does not accept/forward an ENV limits argument; `:540-553` supplies defaults. This distinction matters: matching values do not establish general propagation of ENV resource overrides on the mount route. |
| Service | No declared CPU/memory/PID limits, no inherited ENV/container-helper defaults, no resource flags on its direct Docker command. | New explicit `cpus=2`, `memory_mb=4096` at `data/datasets/appworld.py:303-306`. `eval/service/services.py:399-403` now calls `container.limits_from(svc)` and emits `--cpus 2 --memory 4096m --pids-limit 1024`. `eval/containers/container.py:928-931` fixes the PID cap. |
| Verifier | VERIFY supplies image and 900-second timeout, no CPU/memory/PID fields. The separate verifier gets `--cpus 2 --memory 4g --pids-limit 1024` from the same helper defaults as actor. | `data/datasets/appworld.py:267-290`; `eval/verification/verifier.py:575-590` calls `container.run` without limits, using the verifier image and service network/recordings; `eval/containers/container.py:540-553,604-609`. No verifier/scoring code changed. |

Baseline source evidence is reproducible with `git show 3616713:<path>`:
`data/datasets/appworld.py:301-318` had no service resource declaration;
`data/scaffolds/registry.py:281-282,453-457` excluded/rejected resource fields;
`eval/service/services.py:382-406` directly assembled `docker run` without CPU,
memory, PID, tmpfs or storage flags. The baseline declarations and absent flags
are also extracted by the command saved in `reports/w-caps-validation.txt`.
The image names do not supply a hidden envelope: the archived three image
inspect objects' `Config` fields are extracted there, alongside the actual
running containers' `.Image` bindings. These are archived inspections, not new
daemon observations.

## Defaults, convention and decision

`data/scaffolds/registry.py:274-278,557-564` defaults an exec ENV to 2 CPUs,
4096 MiB and 3600-second actor/verifier deadlines. `container.command` and
`container.create` independently default to 2 CPUs / `4g` / 1024 PIDs
(`eval/containers/container.py:540-553,774-789`). `limits_from` translates ENV
to `4096m` and fixes PIDs at 1024 (`:928-931`). Container-state actor/verifier
routes do pass that translated envelope (`eval/containers/container_state.py:94,219`);
AppWorld declares `state="mount"`, so those are not its routes.
`INTERFACE.md:1009-1016` describes declared resources but retains historical
300-second defaults; current executable defaults above are 3600 seconds.

There was **no requirement or numeric default for a service role**. The original
service declaration contract (`git show 3616713:INTERFACE.md`, lines 621-645)
and rejected-field schema above establish that an AppWorld-only declaration
could not previously work. Other sidecar-bearing declarations are fixtures:
`data/verify_service.py:112-139` and `data/broken_service.py:40-61` declare no
caps. GAIA (`data/datasets/gaia.py:99-112`), Tau (`data/datasets/tau_bench.py:182-193`)
and Terminal-Bench (`data/datasets/terminal_bench.py:198-211`) declare task
CPU/memory but **empty service lists**; their task limits are not sidecar precedents.

Decision: fix the AppWorld omission, rather than retroactively call it a deliberate
unlimited-resource policy. The selected values reuse the platform envelope and
match both other AppWorld roles; they are not a measured service-sizing claim.
The necessary small plumbing accepts/validates optional service `cpus` and
`memory_mb`, preserves them in normalization (`data/scaffolds/registry.py:282-283,460-467,545-555`),
emits resource flags on opt-in, and records the effective three-field `limits`
in `env.services` (`harnessgrad/environments.py:130-137`). Declaring only one
resource uses the helper default for the other. Services declaring neither
remain unset; enclosing ENV limits do not flow into them. This is explicit in
`INTERFACE.md:643-647`. No global service-default change was made.

## Other caps and lifetime

Actor/verifier use read-only rootfs plus `/tmp` tmpfs
`rw,exec,nosuid,size=512m,mode=1777` (`eval/containers/container.py:543-553`);
the service command has neither (`eval/service/services.py:382-414`). A
read-only service would also conflict with the existing startup's sibling-task
removal and experiments symlink writes (`data/datasets/appworld/server.sh:18-30`),
so this change does not impose one.

AppWorld declares actor/verifier deadlines 900 s and service health budget 60 s
(`data/datasets/appworld.py:289,315,324-325`; phase selection at
`eval/run/runner.py:218-220`). Health budget is not a service lifetime cap:
`eval/service/services.py:435-450` polls readiness; the `docker run` client has
a 180-second launch timeout (`:414`); service teardown removes containers and
network (`:206-233`). These are distinct from CPU execution-time limits.

The complete run/create/service command builders cited above emit no explicit
swap, shared-memory-size, ulimit, block-I/O or writable-layer/storage quota
flags. The existing byte-capacity preflight explicitly disclaims filesystem
quota/inode enforcement (`eval/containers/container.py:119,172`). No such
enforcement is added or claimed here. Docker-observed swap/shm configuration
is retained below; absent flags are not converted into invented limits.

## Archived observations, not a new live control

The preserved run is `w-appworld-20261014T225023Z-f02d7cd5`, task `cf6abd2_2`.
`reports/w-appworld-receipts.md:104-125` already records the old resources.
The extraction command in `reports/w-caps-validation.txt` re-reads
`reports/w-appworld-evidence/role-observations.json`, checks each running
inspect object against `container-observations.jsonl`, and prints its exact
configuration. It also reads the existing image and cgroup observations.

| Historical running role | NanoCpus | Memory bytes | PidsLimit | ReadonlyRootfs | Tmpfs |
| --- | --- | --- | --- | --- | --- |
| Actor | `2000000000` | `4294967296` | `1024` | `true` | `/tmp: rw,exec,nosuid,size=512m,mode=1777` |
| Verifier | `2000000000` | `4294967296` | `1024` | `true` | `/tmp: rw,exec,nosuid,size=512m,mode=1777` |
| Service | `0` | `0` | `null` | `false` | absent |

All three running inspections have `ShmSize=67108864`, `Ulimits=[]` and no
`StorageOpt` field. Actor/verifier have `MemorySwap=8589934592`; service has
`MemorySwap=0`. These are saved Docker configuration values, not proof of
effective swap enforcement or whole-filesystem quotas. They were not explicitly
declared by the adapter/launch code.

| Historical cgroup sample | cpu.max raw | memory.max raw | pids.max raw |
| --- | --- | --- | --- |
| Verifier PID 483087 | `200000 100000\n` | `4294967296\n` | `1024\n` |
| Service PID 471632 | `max 100000\n` | `max\n` | `308691\n` |
| Actor | not sampled | not sampled | not sampled |

Raw paths/times/values are in
`reports/w-appworld-evidence/cgroup-live-observations.json:3-32,37-66`.
The actor had exited before those reads (`reports/w-appworld-receipts.md:123`).
The service's finite `308691` is an observed cgroup value whose origin was
not separately traced; it is not an AppWorld-declared or platform-default PID cap.
Point samples are not peaks. The old Docker/cgroup values remain historical;
new service flags are demonstrated only by mocked command construction.

## Validation and closure boundary

Focused tests cover optional/default service limits through validation,
normalization, image resolution, metadata and mocked launch; refusal of invalid
resource values; untouched omitted-resource behavior; AppWorld's static declaration;
and cleanup/admission/registry controls. The live Docker test is explicitly
excluded. Commands and output are saved in `reports/w-caps-validation.txt`.

Only `scorer-offline-closure.observed` and its evidence list are sharpened in the
blocker registry. Both shared blockers remain `code-solvable`; S5 remains partial.
AppWorld `successful-task-evidence` remains `measurement`, unchanged. No
authentic successful measured task, new policy-enforcement observation, complete
offline closure, filesystem quota, post-change live resource control or pilot
authorization is established. Historical receipts/runs/archives are preserved.
