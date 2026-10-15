# Authored ALFWorld synchronous PDDL feasibility probe

`authored_pddl_probe.py` defines its own PDDL domain, problem and TextWorld grammar.
It calls the unchanged repository `gym_env.build`, `reset`, `step` and `replay`.
No released task, trajectory, annotation, reference answer, model, endpoint or network
is used. Temporary game files are created outside the repository and removed by
`TemporaryDirectory`.

`probe-01.*` preserves the first grammar-schema failure. The corrected probe is
`probe-02.*`; `probe-trace.*` repeats it with raw `execve`/`openat` tracing. These
are current-host feasibility controls, not sealed-closure or benchmark execution
evidence. `probe-sha256sum.*` independently hashes the final generator.

The successful output records initial `won=false`, an invalid action preserving
`won=false`, then the authored `finish` action producing `won=true`. The replay
returns the same two action outcomes. Its imported package-root inventory is
retained verbatim in stdout. FastDownward copies its package shared library into
private temporary storage before an in-process ctypes load; the trace retains
both opens. This synchronous wrapper does not start an external planner process.

`blocker-check.*` records the unchanged valid registry. No production source,
registry, journal, `runs/` path or frozen receipt is modified by this child packet.
