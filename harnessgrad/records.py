"""Writing the record: curve points, diffs, states, traces, verdicts, run_meta.

Everything the platform persists goes through here, and the rule the module keeps is that a
number never travels without the thing that explains it. `_curve_point` builds the one shape
every consumer reads -- the panel, the method channel, the plotter, an exported record -- so
"what a point contains" has exactly one definition to change.

`_require_untampered` lives here because it guards the record: a point whose harness rewrote
the scorer is not a measurement, and the check that says so belongs next to the write that
would otherwise have happened.
"""

from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import time

from eval.console import CONSOLE as console
from eval.metrics import ci95
from eval.metrics import mean
from harnessgrad.environments import _env_record
from eval.tracing import task_file
from harnessgrad.methods import PlatformTampered

def _cost_of(res: dict | None, n_tasks: int, wall_s: float,
             method_claimed: int | dict | None = None) -> dict:
    """What this curve point cost, in the units a cost-aware method reasons about.

    `tokens` are the harness's own spend, read from its traces by the runner. They are
    what a method like RRSI needs for `Delta C`: it permits a candidate to spend more
    only in proportion to the score it gains, and a cost rule whose input is a constant
    zero permits everything.

    `harness_tokens` and `method_generation_tokens` are kept apart on purpose. They are
    different budgets -- the harness spends per model call while working, the method
    spends per round while improving -- and one number covering both could not tell a
    thrifty harness from a lazy method.

    `env_generation_tokens` is the **third** budget, kept apart for that reason plus the
    one §2.5.7 states: a simulated user spends tokens whether or not the harness is any
    good, so folding it into `harness_tokens` would feed a cost-aware acceptance rule a
    number its formula is not about. `None` when no service reported any, which is a
    different fact from zero.

    `method_claimed` is the step's `claimed_cost` block when the caller has one, and a bare
    number when it does not -- the trajectory has carried the split (input, output, calls,
    model) since the method started reporting what its own provider said, and the single
    number alone cannot answer why a round got expensive.
    """
    claimed = method_claimed or {}
    if isinstance(claimed, (int, float)):
        claimed = {"generation_tokens": int(claimed)}
    method_tokens = claimed.get("generation_tokens")
    tokens = (res or {}).get("tokens") or {}
    harness_tokens = None
    if tokens.get("tasks_reported"):
        harness_tokens = (tokens.get("input") or 0) + (tokens.get("output") or 0)
    env = (res or {}).get("env_usage") or {}
    env_tokens = None
    if env.get("services_reported"):
        env_tokens = (env.get("input") or 0) + (env.get("output") or 0)
    return {
        "evaluation_trials": n_tasks if res else 0,
        # Kept because curves recorded before the runner read usage have it, and a
        # reader should not have to guess which field is authoritative.
        "generation_tokens": method_tokens or 0,
        "method_generation_tokens": method_tokens,
        # The improver's own split, from what its provider reported. `None` and not 0 when
        # the method is older than this field or its endpoint reports no usage: "0 tokens
        # in" is a claim, and a method that was not asked cannot make it.
        "method_generation_input": claimed.get("method_input_tokens"),
        "method_generation_output": claimed.get("method_output_tokens"),
        "method_model_calls": claimed.get("method_model_calls"),
        "method_model": claimed.get("method_model"),
        "harness_tokens": harness_tokens,
        "harness_tokens_reported_by_tasks": tokens.get("tasks_reported", 0),
        "harness_model_calls": tokens.get("calls"),
        "env_generation_tokens": env_tokens,
        "env_services_reported": env.get("services_reported", 0),
        "wall_clock_s": round(wall_s, 1),
    }

def _save_round_state(run_dir: Path, round_no: int, work: Path) -> None:
    """Keep the harness as it stands at the end of a round, inside the run's record.

    **An eval run measures a state, so a state has to survive the run that made it.**
    It did not: the round's trees were written into `method_root`, a `tempfile.mkdtemp`
    that is deliberately outside the platform and outside the work root -- which is the
    right place for a *method's* inputs, because a method must not be able to write into
    the record, but it means the states were gone when the run ended and there was
    nothing for an eval run to point at.

    Copied **after** the round, from `work`, so it is the state the round produced rather
    than the one it started from. `.git` is excluded for the same reason `base_dir`
    excludes it: the tree is what a harness is, and the history is already in the record
    as per-round diffs.

    Round 0 included, because "measure H0 on the exam" is the most useful baseline there
    is and it needs the same thing a later round does.
    """
    dest = run_dir / f"state_after_round{round_no}"
    if dest.exists():
        shutil.rmtree(dest)
    try:
        shutil.copytree(work, dest, ignore=shutil.ignore_patterns(".git"))
    except OSError as exc:
        # Not fatal: the round's numbers are already recorded, and a run that measured
        # correctly must not be lost because a copy failed.
        console.note(f"could not keep the round {round_no} state for later evaluation: "
                     f"{exc}", level="warn")

def _scored(res, ids) -> list[str]:
    """The ids that actually produced a score.

    A task whose environment was invalid is **absent** from `per_task`
    (INTERFACE.md §2.5.7), so a caller cannot zip ids with scores without filtering
    both -- and a misalignment here would attribute one task's score to another, which
    is worse than the missing task it came from.
    """
    per_task = (res or {}).get("per_task") or {}
    return [t for t in ids if t in per_task]

def test_rate_fields(res: dict | None) -> dict:
    """The check's own tally, as the arguments `_curve_point` takes.

    One place, because there are three call sites (the base point, a round point, and the
    eval-side point) and a field added to one of them is a field missing from the other two
    -- which is how `per_task_trials` first shipped. A caller that forgets this loses the
    finer signal without losing the point, so the failure is silent; that is the argument
    for it being a function rather than five keyword arguments copied three times.
    """
    res = res or {}
    return {
        "per_task_test_rate": res.get("per_task_test_rate"),
        "test_rate": res.get("test_rate"),
        "test_rate_n_tasks": res.get("test_rate_n_tasks"),
        "tests_passed": res.get("tests_passed"),
        "tests_total": res.get("tests_total"),
        "per_task_test_rate_trials": res.get("per_task_test_rate_trials"),
    }


def _curve_point(*, run_id, round_index, identity, sampling, scores, task_ids,
                 cost, cumulative, selection=None, label="",
                 method_reported=None, train_scores=None, train_ids=None,
                 split=None, env_record=None, invalid=None, harness_failed=None,
                 model_gateway=None, harness_runtime=None, hypothesis=None,
                 edits_applied=None, files_claimed=None, candidate_problems=None,
                 side="train", evaluated_from=None,
                 n_trials=None, score_std=None, per_task_std=None,
                 per_task_trials=None, cached_tasks=None,
                 per_task_test_rate=None, test_rate=None, test_rate_n_tasks=0,
                 tests_passed=0, tests_total=0,
                 per_task_test_rate_trials=None) -> dict:
    lo, hi = ci95(scores)
    return {
        "run_id": run_id, "round": round_index, "label": label,
        "identity": identity,
        # Which side of the split this point measures, and therefore what `score` *is*.
        #
        # `score` cannot be null on a train run: the method's acceptance rule reads it
        # (RRSI permits more spend only in proportion to score gain), so a train run
        # needs one. But a train score is **guaranteed to be inflated** -- the method has
        # read the traces of exactly these tasks -- so it is a progress indicator and not
        # a result, and `score_kind` is what stops it being quoted as one. A field a
        # reader can check beats a convention they have to remember.
        "side": side,
        "score_kind": "exam" if side == "eval" else "training",
        **({"evaluated_from": evaluated_from} if evaluated_from else {}),
        # Where this measurement was taken (INTERFACE.md §2.5.4). A `files` curve and
        # an `exec` curve are different quantities, and so are two `exec` curves under
        # different image digests -- so the environment travels with the number, on
        # every point, rather than only in `run_meta.json`.
        "env": {**(env_record or _env_record({}, [])),
                "model_gateway": model_gateway,
                # Which interpreter ran the harness, and where its own dependencies came
                # from (`eval/harness_runtime.py`). A list because the version is a
                # property of each task's image and a run may cross several -- the same
                # reason `variants` exists above. `[]` means the harness declared no
                # dependencies at all, which is a fact rather than a missing field.
                "harness_runtime": list(harness_runtime or [])},
        "sampling": dict(sampling),
        # What the method claimed for this state, kept beside what the platform
        # measured. The gap between the two is itself a reportable finding, so
        # the platform never overwrites one with the other.
        "method_reported": method_reported or {},
        # The method's own word for what kind of change this was. The platform
        # never interprets, validates or constrains it -- it only makes it
        # readable. Seven published methods were checked and none of them makes
        # this machine-readable: AHE declares `constraint_level:
        # middleware|tool_impl|tool_desc|skill|prompt` in its prompt and no code
        # reads it. A vocabulary that only exists in prose cannot be analysed,
        # which is why the field is recorded here rather than asked for in a
        # template.
        "edit_kind": None,
        "score": mean(scores), "score_ci95": [lo, hi],
        # **How noisy this number is.** One evaluation per (harness, task) is one sample,
        # and measured on this platform the *same* unmodified harness scored 0.333 in one
        # run and 0.000 in the next -- the agent model intermittently emits a tool call the
        # harness cannot parse and the task ends there. A curve that does not say how much
        # of a difference is noise cannot support "this edit helped", which is the whole
        # claim the platform exists to make. Present only when the run asked for more than
        # one trial (`--trials`): absent means "one sample", not "no spread".
        **({"n_trials": int(n_trials)} if n_trials and n_trials > 1 else {}),
        **({"score_std": round(float(score_std), 6)}
           if n_trials and n_trials > 1 and score_std is not None else {}),
        **({"per_task_std": {k: round(float(v), 6) for k, v in (per_task_std or {}).items()}}
           if n_trials and n_trials > 1 else {}),
        # **The trials themselves**, not only their mean and spread. A mean of 0.667 over
        # three trials is two passes and one failure, and which one failed -- and why --
        # decides whether the number is saying something about the harness or about the
        # check. Measured on `B2-noop` (2026-10-04): `cobol-modernization` produced a
        # byte-identical trajectory and scored 2/3 in one measurement and 3/3 in the next,
        # so the *reward* varies for one artifact; that claim cannot be made, or checked,
        # from a mean and a standard deviation.
        **({"per_task_trials": {k: [round(float(x), 6) for x in v]
                                for k, v in (per_task_trials or {}).items()}}
           if n_trials and n_trials > 1 else {}),
        # Which tasks this round did not measure, because the same (harness, task, trials)
        # had already been measured. A reused number and a fresh one that happens to agree
        # are different facts, and the point has to say which it is -- otherwise a flat
        # control curve reads as a deterministic harness.
        **({"n_cached": len(cached_tasks), "cached_tasks": sorted(cached_tasks)}
           if cached_tasks else {}),
        "per_task": dict(zip(task_ids, scores)),
        # **The same measurement at the resolution the check already provides.** A task set
        # of ten all-or-nothing checks has a resolution of 0.1 and, measured on this
        # platform, a noise band of about +/-0.1: the instrument cannot see the effect it
        # exists to measure. Most `command` checks tally individual tests, and that tally
        # was already parsed (`eval/runner.py:_test_report_failures`) and already saved in
        # the verdict's `detail` string -- this is that number, as a number.
        #
        # **Always present, `null` when nothing reported.** The rest of this file omits a
        # field that does not apply, and for a *fact about the harness* that is fine. Here
        # it is not: `test_rate` missing because no check tallies tests and `test_rate`
        # missing because this point predates the field are different, and a reader cannot
        # tell them apart -- which is the defect that let a non-functional candidate be
        # read as a +0.100 gain (`docs/experiment_noise.md`). `null` says the platform
        # looked and no check reported a tally; `test_rate_n_tasks` says how many did.
        "test_rate": (None if test_rate is None else round(float(test_rate), 6)),
        "test_rate_n_tasks": int(test_rate_n_tasks or 0),
        "per_task_test_rate": {k: round(float(v), 6)
                               for k, v in sorted((per_task_test_rate or {}).items())},
        # Pooled over every trial and every reporting task, so a reader can compute the
        # rate themselves and cannot be misled by the mean-of-means above.
        "tests_passed": int(tests_passed or 0),
        "tests_total": int(tests_total or 0),
        **({"per_task_test_rate_trials": {k: [round(float(x), 6) for x in v]
                                          for k, v in per_task_test_rate_trials.items()}}
           if n_trials and n_trials > 1 and per_task_test_rate_trials else {}),
        # How many tasks were scored, and how many of them earned full credit.
        #
        # These two are what a method is allowed to know about the eval side's
        # *distribution* (§2.3): the aggregate breakdown without the identities.
        # They exist because withholding `per_task` alone would have cost real
        # fidelity -- HarnessX's acceptance gate decides on an absolute count of
        # passing tasks, and reconstructing that count from the mean is exact for
        # 0/1 scores but approximate for a fractionally-graded dataset. A count
        # carries no per-task information, so it can be given back whole.
        "n_scored": len(scores),
        "n_passed": sum(1 for s in scores if s >= 1.0),
        # Tasks the platform could not measure, kept apart from tasks that scored
        # nothing. `n_invalid` + the attribution is what makes "the mock API never came
        # up" distinguishable from "the harness failed", which is the distinction
        # this platform exists to preserve (INTERFACE.md §2.5.7).
        "n_invalid": len(invalid or {}),
        **({"invalid": dict(invalid)} if invalid else {}),
        # Tasks that *were* measured but whose harness left no trace, with the exit code
        # and the tail of its stderr. Separate from `invalid` because the score here is
        # real; what is missing is the evidence that the harness ever got to work.
        "n_harness_failed": len(harness_failed or {}),
        **({"harness_failed": dict(harness_failed)} if harness_failed else {}),
        # **Why the method did what it did**, in its own words. `method_reported` carries
        # numbers the method claims; this is the sentence it wrote. It was dropped on the
        # floor: `editor.report` has always sent `hypothesis` and `driver.py` never read
        # it, so a round that declined to edit recorded only the method's own label --
        # measured, `RRSI rule: no edit (b_t=4)`, which credits the *rule* for a decision
        # the **model** made, and says nothing about why. That is the one sentence a
        # reader asking "why no edit" needs, and it was being thrown away.
        "method_hypothesis": hypothesis,
        # **The files whose content actually changed in this round**, from the platform's
        # own git diff of the round (`_save_round_diff`), never from the method's word.
        #
        # This field used to carry the method's claimed `files` list, and on `B2-llm`
        # (2026-10-04) that list said `["agent.py"]` for two rounds whose patch was **0
        # bytes** and whose `harness_sha` never moved: the local model re-wrote the same
        # broken file with the same broken content, so rounds 2 and 3 read as two new
        # candidates when they were the same tree, already cached. A curve that counts
        # those as attempts is counting intent, and intent is not a measurement.
        "edits_applied": list(edits_applied or []),
        # What the method said it changed. Kept beside the fact rather than dropped: a
        # method that names a file it did not change is itself a finding, and silently
        # overwriting the claim with the fact would erase it.
        **({"files_claimed": list(files_claimed)} if files_claimed is not None else {}),
        **({"candidate_problems": list(candidate_problems)}
           if candidate_problems else {}),
        # The same measurement on the side the method was allowed to study. It is
        # recorded, never scored: `score` above is the exam. The pair is the whole
        # point -- an eval that is flat while train climbs is a method that fitted
        # its diagnostics, and that is invisible if only one of the two is kept.
        # Absent on a train run, because there it would be a **copy** of `per_task`:
        # one run has one task set, and a duplicate field invites a reader to think two
        # sets were measured. On an eval run there is no train set either, so `train_*`
        # only ever means something on a point that carries both -- and under the
        # separate-sides design no point does. Kept in the schema rather than deleted
        # because curves recorded before the split exist and a reader must be able to
        # tell "no second side" from "this field was never written".
        "train_score": None if (side != "eval" or train_scores is None)
                       else mean(train_scores),
        "train_per_task": (dict(zip(train_ids or [], train_scores or []))
                           if side == "eval" else {}),
        # Which tasks were which. Stored per point rather than only in run_meta
        # because a curve point is the unit that gets exported, compared and
        # plotted, and a point that does not carry its own split cannot be read
        # correctly on its own.
        "split": split or {"train": [], "eval": list(task_ids)},
        # Was this number the max over N evaluations on the same set it is
        # reported on? Cheap, unambiguous, and omitted almost everywhere.
        "selection_effect": selection or {
            "selected_on_reported_set": None, "selection_pool_size": None,
        },
        "cost": cost, "cumulative": dict(cumulative),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

def _require_untampered(res: dict | None) -> None:
    """Stop the run if the harness wrote into the platform.

    A harness is arbitrary code the platform did not write, and it runs with the
    platform on disk. Appending to `eval/runner.py` is the cheapest way to raise a
    score, and the result would be a curve that looks like progress. The check
    costs one pair of hashes per evaluation; the failure is fatal on purpose,
    because a run containing one such evaluation is not a measurement with a
    defect, it is not a measurement.
    """
    changes = (res or {}).get("tampered") or {}
    touched = changes.get("added", []) + changes.get("removed", []) \
        + changes.get("modified", [])
    if not touched:
        return
    shown = ", ".join(sorted(set(touched))[:8])
    console.note(
        "the harness modified the platform",
        level="error",
        human=f"\nFAILING RUN: the harness modified the platform: {shown}\n"
              f"  The harness runs with the platform on disk and is arbitrary code.\n"
              f"  Every number this run produced is therefore not a measurement.\n"
              f"  Restore the named files from your backup or a clean checkout, then\n"
              f"  re-run. `git status --short` shows what moved.")
    raise PlatformTampered(changes)

_PLATFORM_RECORD: dict | None = None


def _platform_record() -> dict:
    """Which code decided what this run's numbers mean.

    **Stamped by the writer, not passed by the caller.** There are two call sites for
    `_write_run_meta` and both would have to remember; a run record that omits this is
    indistinguishable from one produced by different code, which is exactly the state
    measured on 2026-10-05: 82 run directories, none naming its platform, and one run
    invalidated mid-flight by an edit to `eval/` that no reader could detect.

    `content_sha` is over the platform's own files (`eval/integrity.snapshot`), so an
    uncommitted edit changes it -- `git rev-parse HEAD` would not have caught the run that
    was actually invalidated. `git_sha` is recorded beside it because a human reading a
    directory wants the revision they can check out.

    **Computed once per process, and that is a correctness property.** This runs when the
    run starts and again when it ends. Without the cache, a platform file edited during the
    run would be recorded at its *new* hash by the second write -- the record would then
    attest to code the run never executed, which is the one thing this field exists to
    prevent. The cache makes both writes report the tree the process loaded. Tampering is
    still detected independently and at the end (`_require_untampered`); this field is what
    a reader months later compares against.
    """
    global _PLATFORM_RECORD
    if _PLATFORM_RECORD is not None:
        return _PLATFORM_RECORD
    from eval.integrity import PLATFORM_ROOT, content_sha
    record: dict = {"content_sha": content_sha(PLATFORM_ROOT)}
    try:
        import subprocess
        git_sha = subprocess.run(["git", "-C", str(PLATFORM_ROOT), "rev-parse", "HEAD"],
                                 capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:                                                 # noqa: BLE001
        git_sha = ""
    if git_sha:
        record["git_sha"] = git_sha
    try:
        dirty = subprocess.run(["git", "-C", str(PLATFORM_ROOT), "status", "--porcelain"],
                               capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:                                                 # noqa: BLE001
        dirty = ""
    # A fact a reader needs: the content hash covers uncommitted edits, but knowing
    # whether there *were* any is how someone reproduces the exact tree.
    record["dirty"] = bool(dirty)
    _PLATFORM_RECORD = record
    return record


def _write_run_meta(run_dir: Path, fresh: bool = False, **fields) -> None:
    """Record what the run was, for readers that only have the run directory.

    Written before the first round as well as at the end, because a run can stop
    early -- the control harness reports no change and mode A writes no metadata of
    its own. A run whose record is only written on success is missing exactly for
    the runs someone wants to inspect.

    `fresh=True` is for the run's *first* write and drops anything already there.
    Without it a reused run id inherits the previous run's fields, because the merge
    below cannot tell "this run wrote a partial record and is now completing it"
    from "a different run wrote this file earlier". Measured: a run directory whose
    `method_entrypoint` said `rrsi` carried `rounds_measured: 7` and
    `final_score: 1.0` from a previous DGM run, so the two runs read as one.

    `workspace` is here rather than recomputed by readers: the working tree moved
    outside the platform tree, so `runs/<id>/workspace` no longer exists, and the
    commits that hold every checkpoint live in the tree that does. Readers that
    guess the path wrong lose the checkpoints, not just the convenience.

    A field passed as `None` is left unchanged rather than written: `None` is how a
    caller says "I have nothing to say about this", and the workspace path recorded
    before round 0 must survive a later call that does not repeat it.
    """
    # **Which platform produced these numbers, on every write.** Not a parameter: see
    # `_platform_record`. A caller that passes its own value overrides this, which is
    # what a test with a synthetic platform wants.
    fields.setdefault("platform", _platform_record())
    path = run_dir / "run_meta.json"
    existing = {}
    if path.exists() and not fresh:
        try:
            existing = json.loads(path.read_text())
        except json.JSONDecodeError:
            existing = {}
    existing.update({k: v for k, v in fields.items() if v is not None})
    path.write_text(json.dumps(existing, indent=1))

def _save_traces(run_dir: Path, round_no: int, traces: dict,
                 task_ids: list[str] | None, split: dict | None = None,
                 trial_traces: dict | None = None) -> None:
    """Persist one round's traces beside the run, for a human to inspect.

    **Every task, both sides** -- and this reverses a deliberate earlier decision, so the
    reasoning is recorded rather than the conclusion alone.

    The first version wrote the **train side only**, on this argument: "writing the eval
    side's traces here would put them on disk under the run directory and one `cp -r`
    away from a method -- which is the leak the split exists to prevent". That is a
    defence-in-depth argument and it was sound as far as it went. What it never priced
    was its cost: the eval traces were **discarded**, so the most valuable question a
    human can ask about a run -- *why did the harness fail the exam task?* -- had no
    answer anywhere, and the UI's trace viewer could only ever show the half nobody
    needed to look at. Measured: 37 train traces on disk and 25 eval tasks whose
    behaviour was gone.

    What makes this safe is not that the eval traces are absent from the disk. It is
    that **the method cannot reach the disk**: `_method_sandbox_plan` hides the platform
    and allows exactly one tree, `methods/`. `tests/quality/test_isolation.py` pins that
    with a probe method that tries to read this directory and is asserted to fail. A
    guarantee by mount rule is stronger than a guarantee by absence, and it is the one
    the rest of the platform already rests on -- the platform is not hidden from a
    harness by deleting it, but by not mounting it.

    An exported record therefore *does* carry the exam's behaviour, which is the point of
    exporting it, and `.sides.json` says which traces are which so an exporter that means
    to hand a record to a method can strip them. That is the operator's decision to make
    with the facts in front of them, rather than one the platform made for them by
    throwing the evidence away.
    """
    if not traces:
        return
    dest = run_dir / f"round{round_no}_traces"
    dest.mkdir(parents=True, exist_ok=True)
    for tid, body in traces.items():
        task_file(dest, f"{tid}.jsonl").write_text(body)

    # **And one file per trial, when a task was measured more than once.** `<task>.jsonl`
    # above is the last trial only, which is what every reader had; with `--trials 3` that
    # meant a score of 0.667 came with the trace of a trial that passed, and the missing
    # trial -- the one that failed -- was not on disk at all (`B2-noop`,
    # `cobol-modernization`, 2026-10-04). The trials are numbered from 1 and always start
    # there, so `trial1` is the first measurement in both a 1-trial and a 3-trial run.
    for tid, bodies in (trial_traces or {}).items():
        for index, body in enumerate(bodies, start=1):
            task_file(dest, f"{tid}.trial{index}.jsonl").write_text(body)

    # Which side each trace belongs to, so the directory is readable on its own. Named
    # with a leading dot because it sits beside files named after task ids and must not
    # ever be mistaken for one.
    sides = {"train": [], "eval": []}
    known = split or {}
    for tid in sorted(traces):
        if tid in set(known.get("eval") or []):
            sides["eval"].append(tid)
        elif tid in set(known.get("train") or []):
            sides["train"].append(tid)
        else:
            # No split declared: everything is the exam, matching how the point is
            # scored and how the method channel behaves.
            sides["eval"].append(tid)
    (dest / ".sides.json").write_text(json.dumps(
        {**sides, "task_ids": task_ids, "round": round_no}, indent=1))

def _save_verdicts(run_dir: Path, round_no: int, res: dict | None,
                   task_ids) -> None:
    """Persist, per task, **why** the score is what it is.

    A curve point says `per_task: {"bn-fit-modify": 0.0}` and nothing else. Everything
    that could explain that number already existed inside `evaluate` -- the verifier's
    `detail` (reward, exit code, and the tail of the check's own stdout) and the harness's
    stderr -- and every bit of it died with the process. Measured: answering "why 0?" for
    one run meant re-reading five traces by hand and reproducing a task's own test script
    outside the platform.

    On disk rather than only in the event stream, for the same reason traces are: a run
    gets exported, read months later, and grepped. `runs/<id>/verdicts/round-N/<task>.json`
    is the level at which the question is actually asked -- one task at a time -- so that
    is the shape of the file.
    """
    if res is None:
        return
    verdicts = res.get("verdicts") or {}
    scores = res.get("per_task") or {}
    dest = run_dir / "verdicts" / f"round-{round_no}"
    dest.mkdir(parents=True, exist_ok=True)
    # Keep selected invalid tasks too, with score=None; absence must not erase why
    # a task was unmeasured when these files are consumed by a later report.
    for tid in sorted(set(scores) | (set(task_ids) & set(res.get("invalid") or {}))):
        v = dict(verdicts.get(tid) or {})
        entry = {
            "task_id": tid,
            "round": round_no,
            "score": scores.get(tid),
            "kind": v.get("kind"),
            "passed": v.get("passed"),
            "detail": v.get("detail"),
        }
        # **The check's own tally, which was being thrown away.** `_test_report_failures`
        # has parsed `{"passed": 4, "failed": 1}` out of the CTRF report since 2026-10-04
        # (`eval/runner.py`), the runner set `verdict["tests"]`, and this function -- the
        # only thing that writes a verdict to disk -- copied six named fields and dropped
        # it. So the number a reader needs to tell "the artifact got worse" from "nothing
        # happened" lived in a prose `detail` string and nowhere else. Measured: a harness
        # edit took `large-scale-text-editing` from 4 of 5 tests to 3 of 5; both scored
        # 0.0, and the curve said the edit changed nothing.
        if isinstance(v.get("tests"), dict):
            entry["tests"] = v["tests"]
        if isinstance(v.get("evidence"), dict):
            entry["evidence"] = v["evidence"]
        harness_out = (res.get("harness_output") or {}).get(tid)
        if harness_out:
            entry["harness"] = harness_out
        if tid in (res.get("invalid") or {}):
            entry["invalid"] = res["invalid"][tid]
        # **Every trial's reason, not only the last one's.** `entry` above describes the
        # last trial (`res["verdicts"][tid]`), while `entry["score"]` is the mean over
        # all of them -- so a task that passed 2 of 3 used to be written as
        # `score 0.667, passed: true`, and the trial that failed left no record at all.
        # Measured on `B2-noop` (2026-10-04): `cobol-modernization` was 0.667, the saved
        # verdict said `passed`, and the question the number raises -- which trial
        # failed, and why -- had no answer anywhere on disk.
        trials_v = (res.get("trial_verdicts") or {}).get(tid)
        if trials_v and len(trials_v) > 1:
            entry["trial_scores"] = [float((t or {}).get(
                "score", 1.0 if (t or {}).get("passed") else 0.0)) for t in trials_v]
            entry["trials"] = [{"passed": (t or {}).get("passed"),
                                "kind": (t or {}).get("kind"),
                                "detail": (t or {}).get("detail"),
                                # The per-trial tally too, for the same reason the per-trial
                                # score is here: "2 of 3 trials passed" and "the tests went
                                # 4/5, 5/5, 3/5" are different claims about the artifact.
                                **({"tests": t["tests"]} if isinstance((t or {}).get("tests"), dict)
                                   else {}),
                                **({"evidence": t["evidence"]}
                                   if isinstance((t or {}).get("evidence"), dict)
                                   else {})} for t in trials_v]
        task_file(dest, f"{tid}.json").write_text(
            json.dumps(entry, indent=1, ensure_ascii=False), encoding="utf-8")

        # One line per task on the terminal; the body goes to the panel collapsed. The
        # score is in this line on purpose: "0.000 + the check's first line" is the
        # pairing that makes a zero diagnosable at a glance instead of after an
        # archaeology session.
        console.log(source="check", task=f"round {round_no} · {tid}",
                    exit_code=None, round_no=round_no,
                    detail=str(v.get("detail") or entry.get("invalid") or ""),
                    body=str(harness_out.get("stderr") if harness_out else ""),
                    level="error" if not scores.get(tid) else "info")

def _write_curve(path: Path, curve: list[dict]) -> None:
    with path.open("w") as fh:
        for point in curve:
            fh.write(json.dumps(point) + "\n")

def _keep_method_logs(method_ws: Path, run_dir: Path | None, round_no: int) -> None:
    """Copy a method's own `*.log` files into the record before its scratch dir goes.

    The method workspace is temporary by design -- a temp directory, deleted when the
    round ends -- and that is right for the *candidate harness*, which the platform has
    already copied out, and wrong for the method's own diagnostics. Measured with the
    CLI improver: its entire transcript (up to 200 kB: what it read, what
    it tried, why it changed nothing) went to `<workspace>/improver.log`, and every run
    that had to answer "why did the improver change nothing?" had thrown that file away
    with the scratch directory. The question is normally asked after the run.

    The convention is deliberately narrow -- files named `*.log` at the root of the
    method's workspace -- so it is a rule a method can follow rather than a licence to
    fill the record, and so the platform does not have to know which method it is.
    """
    if run_dir is None or not method_ws.is_dir():
        return
    logs = sorted(p for p in method_ws.glob("*.log") if p.is_file())
    if not logs:
        return
    dest = run_dir / "method_logs" / f"round-{round_no}"
    dest.mkdir(parents=True, exist_ok=True)
    for path in logs:
        shutil.copy2(path, dest / path.name)


def _save_round_diff(run_dir: Path, round_no: int, work: Path,
                     prev_sha: str, sha: str) -> dict:
    """Persist one round's diff as part of the experiment record.

    Why not just read it back from git later: mode A ends with `reset_hard`, so the
    round's commit becomes a *dangling* object. `git diff` still resolves it until a
    `git gc` collects it, and then the diff is gone -- an experiment record that
    survives only until housekeeping runs is not a record. The panel shows per-step
    diffs, and that view has to work on an old run.

    Written even when empty, so "this round changed nothing" is a recorded fact rather
    than a missing file that a reader has to interpret.
    """
    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", str(work), *args],
                              capture_output=True, text=True).stdout

    diff = git("diff", prev_sha, sha)
    stat = git("diff", "--numstat", prev_sha, sha)

    files = []
    for line in stat.splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            added, removed, name = parts
            files.append({"path": name,
                          "added": int(added) if added.isdigit() else None,
                          "removed": int(removed) if removed.isdigit() else None})

    out_dir = Path(run_dir) / "diffs"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"round-{round_no}.patch").write_text(diff)
    (out_dir / f"round-{round_no}.json").write_text(json.dumps(
        {"round": round_no, "from": prev_sha, "to": sha, "files": files,
         "added": sum(f["added"] or 0 for f in files),
         "removed": sum(f["removed"] or 0 for f in files)}, indent=1))
    return {"files": files, "added": sum(f["added"] or 0 for f in files),
            "removed": sum(f["removed"] or 0 for f in files)}
