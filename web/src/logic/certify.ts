import type { TranslationKey } from "@/i18n/en";

import type { CertifyResult, RunSummary } from "@/types";

/**
 * "Can I quote this number?" — the question `harnessgrad/store/schema.py:certify()` exists
 * to answer, and the one the Experiments screen is built around.
 *
 * The two properties are not a ladder from bad to good; they answer different questions:
 *
 * * **`valid`** — every point can be read, and every one was measured by the platform.
 * * **`certified`** — *additionally*, the record names the platform that produced it and
 *   the run did not touch the platform while it ran. A run that predates those fields is
 *   `valid` and **not** `certified`, which the schema calls "the honest reading": nothing
 *   on disk lets a reader compare it with a run made by different code.
 *
 * `valid` and `certified` are read straight off the record. Two UI-level classifications
 * are added on top, because the record's booleans alone would hide them:
 *
 * * **tampered** — `certify()` keeps `tampered` out of `problems`, so a tampered run is
 *   `valid: true, certified: false`. On screen that would read as merely old. It is not,
 *   so it gets its own level.
 * * **no points** — a run directory with no `curve.jsonl` measured nothing. `certify()`
 *   reports `valid: false, points: 0`; the badge says "not measured" rather than "invalid",
 *   because there is no number to be wrong about.
 */

export type CertifyLevel = "certified" | "valid" | "tampered" | "invalid" | "no-points";

export type BadgeTone = "pass" | "info" | "warn" | "fail" | "muted";

export interface CertifyBadge {
  level: CertifyLevel;
  /**
   * One word for the cell — as a **translation key**, so this module stays language-free.
   * `problems` and `certificationNote` below stay as recorded: they are the platform's own
   * sentences about this run, and a translated log is a log nobody can grep.
   */
  labelKey: TranslationKey;
  tone: BadgeTone;
  /** One sentence: what this level means for quoting the number. A key, for the same reason. */
  explanationKey: TranslationKey;
  problems: string[];
  notes: string[];
  /** The note that explains why a `valid` run is not `certified`, when there is one. */
  certificationNote: string | null;
  points: number;
  rounds: number[];
  finalScore: number | null;
}

export function badgeFor(certify: CertifyResult | null | undefined): CertifyBadge {
  if (!certify) {
    return {
      level: "no-points",
      labelKey: "record.certify.unknown",
      tone: "muted",
      explanationKey: "record.certify.unknownWhy",
      problems: [],
      notes: [],
      certificationNote: null,
      points: 0,
      rounds: [],
      finalScore: null,
    };
  }
  const base = {
    problems: certify.problems ?? [],
    notes: certify.notes ?? [],
    points: certify.points,
    rounds: certify.rounds ?? [],
    finalScore: certify.final_score,
    certificationNote: certificationNote(certify),
  };

  if ((certify.tampered ?? []).length > 0) {
    return {
      ...base,
      level: "tampered",
      labelKey: "record.certify.tampered",
      tone: "fail",
      explanationKey: "record.certify.tamperedWhy",
    };
  }
  if (certify.points === 0) {
    return {
      ...base,
      level: "no-points",
      labelKey: "record.certify.notMeasured",
      tone: "muted",
      explanationKey: "record.certify.notMeasuredWhy",
    };
  }
  if (!certify.valid) {
    return {
      ...base,
      level: "invalid",
      labelKey: "record.certify.invalid",
      tone: "fail",
      explanationKey: "record.certify.invalidWhy",
    };
  }
  if (certify.certified) {
    return {
      ...base,
      level: "certified",
      labelKey: "record.certify.certified",
      tone: "pass",
      explanationKey: "record.certify.certifiedWhy",
    };
  }
  return {
    ...base,
    level: "valid",
    labelKey: "record.certify.valid",
    tone: "info",
    explanationKey: "record.certify.validWhy",
  };
}

export function certificationNote(certify: CertifyResult): string | null {
  const note = (certify.notes ?? []).find(
    (n) => n.includes("content_sha") || n.includes("not certified"),
  );
  return note ?? null;
}

/** The badge level counts shown above the Experiments table. */
export function levelCounts(badges: CertifyBadge[]): Record<CertifyLevel, number> {
  const counts: Record<CertifyLevel, number> = {
    certified: 0,
    valid: 0,
    tampered: 0,
    invalid: 0,
    "no-points": 0,
  };
  for (const badge of badges) counts[badge.level] += 1;
  return counts;
}

export type ValidityFilter = "all" | "certified" | "quotable" | "valid" | "invalid" | "no-points";

/**
 * The Experiments filter.
 *
 * `quotable` is `valid || certified` and exists because it is the actual question the
 * screen was built for: "which of our 85 runs can I actually quote?" — which is a
 * different set from "which are certified".
 */
export function matchesValidity(badge: CertifyBadge, filter: ValidityFilter): boolean {
  switch (filter) {
    case "all":
      return true;
    case "certified":
      return badge.level === "certified";
    case "quotable":
      return badge.level === "certified" || badge.level === "valid";
    case "valid":
      return badge.level === "valid";
    case "invalid":
      return badge.level === "invalid" || badge.level === "tampered";
    case "no-points":
      return badge.level === "no-points";
  }
}

/** Free-text search over the fields a reader would type: run id, model, harness, dataset, improver. */
export function matchesSearch(row: RunSummary, query: string): boolean {
  const needle = query.trim().toLowerCase();
  if (!needle) return true;
  return [row.run_id, row.agent_model, row.harness, row.dataset, row.improver, row.mode]
    .filter((v): v is string => typeof v === "string")
    .some((v) => v.toLowerCase().includes(needle));
}

/**
 * The count a reader wants before they quote anything: how many runs are quotable at all,
 * and of those, how many are certified. Computed from the same `certify()` rows the table
 * renders, so the number and the table cannot disagree.
 */
export function quotableSummary(rows: RunSummary[]): {
  total: number;
  certified: number;
  valid: number;
  quotable: number;
  invalid: number;
  noPoints: number;
} {
  const counts = levelCounts(rows.map((r) => badgeFor(r.certify)));
  return {
    total: rows.length,
    certified: counts.certified,
    valid: counts.valid,
    quotable: counts.certified + counts.valid,
    invalid: counts.invalid + counts.tampered,
    noPoints: counts["no-points"],
  };
}
