"""Read a harness's trace. One reader, so two readers cannot disagree.

Why this module exists
----------------------
Two places parsed the same file with the same intent and *different rules*:

    driver.py             `_first_object()`   the first complete JSON object
    tools/serve_ui.py     `_first_json()`     the same idea, written again
    base_harness/loop     `_parse()`          the harness's own version, in its own file

That is how the panel once reported **"0 commands" for a trace that had ten**: the
harness's parser had been fixed to take the first object, the panel's had not, so the
panel looked at a two-object reply, failed, and showed nothing. A reader comparing the
panel against the trace saw two different runs.

The rule is one line and it is not obvious, which is exactly the kind of thing that must
not be written twice:

    take the first complete JSON object and ignore whatever follows

What lives here
---------------
* `first_object` -- the rule above.
* `loop_facts` -- what the harness *did*, counted from its trace: calls, commands,
  answers, whether the submit gate refused anything, and how the run ended. The panel and
  the method-facing channel both read this; before it existed, "the harness answered after
  one call" was invisible to a method, which then attributed a 0 to the environment.

Both are pure functions over text, so they are testable without docker, a model, or a run.
"""
from __future__ import annotations

import json

__all__ = ["first_object", "loop_facts", "ENDED_CRASHED", "ENDED_ANSWERED",
           "ENDED_PARSE_ERROR", "ENDED_BUDGET", "ENDED_UNKNOWN"]

#: How a harness run ended. Named constants because the method-facing channel and the
#: panel both branch on them, and a typo in a string literal would be a silent `unknown`.
ENDED_CRASHED = "crashed"
ENDED_ANSWERED = "answered"
ENDED_PARSE_ERROR = "parse_error"
ENDED_BUDGET = "budget_exhausted"
ENDED_UNKNOWN = "unknown"


def first_object(text: str) -> dict | None:
    """The first complete JSON object in `text`, or None.

    `raw_decode` from the first `{` rather than `json.loads(text)`: the measured model
    emits several objects in one reply (`{"tool": ...}}\\n{"answer": ""}` -- note the stray
    brace), and a parser that insists on the whole string being one object treats that as
    a harness failure. `base_harness/loop/agent.py::_parse` follows the same rule; if the
    two ever disagree, the panel's view of a run stops matching the run.
    """
    if not text:
        return None
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def loop_facts(trace_text: str) -> dict:
    """What the harness did, counted from its own trace.

    Every field answers a question a reader of the *score* cannot answer:

        model_calls           the model was asked N times
        commands              N shell commands actually executed (a `command` record)
        answers               N replies carried a final answer
        submit_rejected       the submit gate refused N times (needs `base_harness/loop`)
        missing_at_submit     which paths the task named and the harness had not written
        multi_object_replies  N replies carried more than one JSON object
        parse_errors          N replies could not be parsed at all
        empty_commands        N executed commands were the empty string (nothing ran)
        duplicate_keys        N JSON keys the parser had to repair (the model repeated one)
        context_trims         how many times history was shortened after the model refused
                              a too-long prompt
        output_clipped_events / _chars   how often a command's output was clipped for the
                              model, and how much was hidden
        history_dropped       N old messages dropped from the model's view
        ended                 see the ENDED_* constants

    `commands == 0` with `answers == 1` is the shape that mattered most: the harness
    answered without doing anything, and the platform scored the task 0. Without this
    count, that is indistinguishable from "it worked and failed".

    Two of the fields are read together on purpose:

        multi_object_replies > 0, parse_errors == 0   the parser absorbed it
        multi_object_replies > 0, parse_errors > 0    it did not

    A method that sees only the first number will "fix" a parser that is not broken --
    measured: three consecutive rounds of one method diagnosed a parser bug that had been
    fixed a round earlier.
    """
    steps = commands = answers = rejected = parse_errors = multi_object = 0
    #: **The interface events, counted as their own facts.** Every one of these is a case
    #: where the harness changed what the model did or what it saw, and the summary a method
    #: reads first did not mention any of them. Measured on `local-floor-9`
    #: (`cancel-async-tasks`): the summary said `commands: 13` while **ten of them executed
    #: the empty string** -- the model's real command had been replaced by a duplicated JSON
    #: key -- and a method reading `13 commands, 0 parse errors` sees a healthy trajectory.
    #: Counting them separately is what makes "the harness dropped the actions" a fact a
    #: method can act on instead of something only an operator with grep can find.
    empty_commands = duplicate_keys = context_trims = 0
    clipped_events = clipped_chars = history_dropped = 0
    repeated_commands = repeat_nudges = 0
    seen_commands: set[str] = set()
    missing: list[str] = []
    usage: dict = {}
    for line in str(trace_text or "").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record.get("usage"), dict):
            usage = record["usage"]
        if "reply" in record:
            steps += 1
            reply = str(record["reply"])
            action = first_object(reply)
            if action is not None:
                if "answer" in action:
                    answers += 1
                close = reply.find("}")
                if close != -1 and "{" in reply[close:]:
                    multi_object += 1
        if "command" in record:
            commands += 1
            cmd = str(record.get("command") or "").strip()
            if not cmd:
                empty_commands += 1
            elif cmd in seen_commands:
                # **A command this run had already issued.** The score cannot see this and
                # the existing facts did not count it: measured on the 9B
                # (`large-scale-text-editing`, 2026-10-05), 24 of 31 executed commands were
                # re-issues of earlier ones, the harness's repeat nudge fires only on an
                # *immediately* consecutive repeat, and the round recorded a plain 0.000 --
                # a harness burning its whole step budget in a loop is a harness fact, and
                # the method reading the summary had no number for it.
                repeated_commands += 1
            else:
                seen_commands.add(cmd)
        if "repeat_nudge" in record:
            repeat_nudges += 1
        if record.get("duplicate_keys"):
            duplicate_keys += len(record["duplicate_keys"])
        if record.get("context_trims"):
            context_trims = max(context_trims, int(record["context_trims"]))
        if "output_clipped" in record:
            clipped_events += 1
            clipped_chars += int(record.get("output_clipped") or 0)
        if record.get("history_dropped"):
            history_dropped += int(record["history_dropped"])
        if "parse_error" in record:
            parse_errors += 1
        if "submit_rejected" in record:
            rejected += 1
            missing.extend(record.get("submit_rejected") or [])

    return {
        "model_calls": steps,
        "commands": commands,
        "answers": answers,
        "submit_rejected": rejected,
        "missing_at_submit": sorted(set(missing)),
        "multi_object_replies": multi_object,
        "parse_errors": parse_errors,
        # The harness-side events. `empty_commands` is the one that mattered most: it is a
        # step that ran nothing while reporting success, which the score cannot distinguish
        # from a model that did the wrong thing.
        "empty_commands": empty_commands,
        "duplicate_keys": duplicate_keys,
        # Re-issues of a command this run had already executed, and how often the harness's
        # own repeat nudge fired. Two numbers, because the gap between them *is* the bug:
        # the nudge only sees a repeat that arrives immediately after itself.
        "repeated_commands": repeated_commands,
        "repeat_nudges": repeat_nudges,
        "context_trims": context_trims,
        "output_clipped_events": clipped_events,
        "output_clipped_chars": clipped_chars,
        "history_dropped": history_dropped,
        "tokens": (usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0),
        "ended": _ended(usage, answers, parse_errors, commands, steps),
    }


def _ended(usage: dict, answers: int, parse_errors: int, commands: int,
           steps: int) -> str:
    """How the run ended, by evidence strength. The order is the whole content here.

    `crashed` first: the harness writes `usage` as its **last** record, so a missing one
    means it never reached its own end (killed, or an exception out of a model call).
    Measured: a task with 10 calls reported as `budget_exhausted` was in fact an
    `APIConnectionError` -- and "ran out of steps" sends a reader to the wrong place.
    """
    if not usage:
        return ENDED_CRASHED
    if answers:
        return ENDED_ANSWERED
    if parse_errors and not commands:
        return ENDED_PARSE_ERROR
    if steps and commands:
        return ENDED_BUDGET
    return ENDED_UNKNOWN
