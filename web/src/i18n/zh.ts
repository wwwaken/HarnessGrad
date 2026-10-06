import { common, compare, experiments, launch, nav, record, run, task } from "./parts";
import type { TranslationKey } from "./en";

/**
 * The Chinese dictionary.
 *
 * `Record<TranslationKey, string>` is the whole point: `tsc --noEmit` fails if a key exists
 * in `en` and not here, and fails again if a key here does not exist in `en`. There is no
 * runtime fallback to English and no "missing translation" state, because neither can reach
 * `main` — which is a stronger guarantee than a library's fallback chain gives, and it costs
 * one line per string.
 *
 * Two conventions worth stating because they are choices, not accidents:
 *
 * * **Chinese spacing.** A Latin word or a bare number inside a Chinese sentence is padded
 *   with a space (`共 {n} 题`, `读 API`), which is the conventional typography and also what
 *   keeps a run id from colliding with the character before it.
 * * **Recorded text stays as recorded.** Verdict details, check output, harness-failure
 *   reasons, `certify` notes and raw traces are quoted, not translated — see the note in
 *   `src/i18n/index.tsx`. Where such a value is interpolated into a translated sentence, the
 *   value itself is left alone.
 */
export const zh: Record<TranslationKey, string> = {
  ...common.zh,
  ...nav.zh,
  ...experiments.zh,
  ...run.zh,
  ...task.zh,
  ...compare.zh,
  ...launch.zh,
  ...record.zh,
};
