import type { Presence } from "@/types";

/**
 * The three-state read of a field.
 *
 * `schema.py` is explicit that "absent" (the code path never set it, or the point
 * predates the field) and "null" (the platform looked and found nothing) are different
 * facts with, on disk, one spelling. `docs/refactor_references.md` §6.3 makes rendering
 * all three a requirement of this UI, because collapsing them is how a non-functional
 * candidate was read as a gain.
 */
export function presenceOf(
  object: Record<string, unknown> | null | undefined,
  key: string,
): Presence {
  if (!object || !(key in object)) return "absent";
  return object[key] === null ? "null" : "present";
}

/** True when the field is present and not null. */
export function has(
  object: Record<string, unknown> | null | undefined,
  key: string,
): boolean {
  return presenceOf(object, key) === "present" && (object as Record<string, unknown>)[key] !== undefined;
}

/**
 * A field's value, its presence, and — when it is absent — the date it was added, so the
 * UI can say "added 2026-10-05" rather than "missing".
 *
 * The dates mirror `ADDED_LATER` in `harnessgrad/store/schema.py`.
 */
export const ADDED_LATER: Record<string, string> = {
  test_rate: "2026-10-05 (stage 0): the check's own test tally, as a number",
  test_rate_n_tasks: "2026-10-05 (stage 0): how many tasks reported a tally",
  per_task_test_rate: "2026-10-05 (stage 0)",
  tests_passed: "2026-10-05 (stage 0)",
  tests_total: "2026-10-05 (stage 0)",
  no_loadable_change:
    "2026-10-05: every changed file is outside the entrypoint's import closure, so the " +
    "score is not evidence about the edit",
  startup_failure: "2026-10-05: the harness never started on any task",
  per_task_trials: "2026-10-04 (`--trials > 1`)",
  score_std: "2026-10-04 (`--trials > 1`)",
  n_trials: "2026-10-04 (`--trials > 1`)",
  kept_round: "2026-10-05: which state the method decided to keep",
  step_index: "2026-10-05: which step of its submission this point is",
  steps_in_submission: "2026-10-05: how many steps one call bought",
};

/** The one-line explanation shown beside a value, whatever its presence. */
export function explainPresence(presence: Presence, key: string): string | null {
  if (presence === "present") return null;
  if (presence === "null") return "null — the platform looked and found nothing";
  const added = ADDED_LATER[key];
  return added ? `absent — added ${added}` : "absent — the recording code path did not set it";
}

/** The glyph used for an absent or null numeric field, never `0`. */
export const ABSENT = "—";
