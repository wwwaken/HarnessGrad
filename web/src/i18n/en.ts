import { common, compare, experiments, launch, nav, record, run, task } from "./parts";

/**
 * The English dictionary, and the source of truth for what a key is.
 *
 * Every other language is declared `Record<TranslationKey, string>`, so this file decides
 * the shape of all of them and a key added here without a translation is a compile error
 * rather than a string that reaches a reader in the wrong language.
 *
 * Keys are dotted and flat (`"run.tasksScored"`) rather than nested. Two reasons: a nested
 * tree makes `keyof` a path type that has to be built by hand, and a flat map is what a
 * translator actually works in — one line, one string, greppable.
 */
export const en = {
  ...common.en,
  ...nav.en,
  ...experiments.en,
  ...run.en,
  ...task.en,
  ...compare.en,
  ...launch.en,
  ...record.en,
} as const;

export type TranslationKey = keyof typeof en;
