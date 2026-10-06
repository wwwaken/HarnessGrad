import { createContext, useCallback, useContext, useMemo, type ReactNode } from "react";
import { en, type TranslationKey } from "@/i18n/en";
import { zh } from "@/i18n/zh";
import { useLang, type Lang, type LangChoice } from "@/lib/lang";

/**
 * Two dictionaries and one function, instead of an i18n library.
 *
 * **Why not `react-i18next`.** The completeness guarantee here is the type checker, not a
 * runtime fallback. `en` is the source of truth, `TranslationKey` is its key union, and
 * `zh` is declared `Record<TranslationKey, string>` — so a key that exists in one language
 * and not the other is a `tsc` error, and a key that does not exist at all is a `tsc` error
 * at the call site. A missing translation cannot reach a reader as an untranslated string,
 * because it cannot reach `main`. That is worth more than plural rules and lazy namespaces
 * for an app with two languages and a few hundred fixed strings.
 *
 * **What is deliberately not translated.** Strings the *record* produced: check output,
 * verdict details, harness-failure reasons, `certify` notes, raw trace bodies, run ids. They
 * are evidence, and evidence is quoted in the language it was recorded in — a translated
 * log is a log nobody can grep. The boundary is therefore "the app's own voice is
 * translated; the platform's recorded voice is not", and the components that render the
 * latter say so where a reader might otherwise think a translation is missing.
 */

export const DICTIONARIES: Record<Lang, Record<TranslationKey, string>> = { en, zh };

export type Translate = (key: TranslationKey, params?: Record<string, string | number>) => string;

export interface I18n {
  /** The language in effect. */
  lang: Lang;
  /** What the reader chose; `"auto"` means "follow the browser". */
  choice: LangChoice;
  setLang: (lang: Lang) => void;
  /** Return to following the browser, forgetting any explicit choice. */
  setAuto: () => void;
  t: Translate;
}

/** `{name}` placeholders, so a translated sentence can put its values in its own order. */
function interpolate(text: string, params?: Record<string, string | number>): string {
  if (!params) return text;
  return text.replace(/\{(\w+)\}/g, (whole, name: string) =>
    Object.prototype.hasOwnProperty.call(params, name) ? String(params[name]) : whole);
}

export function translate(lang: Lang, key: TranslationKey, params?: Record<string, string | number>): string {
  return interpolate(DICTIONARIES[lang][key], params);
}

/**
 * `null` when there is no provider.
 *
 * A component tested on its own then renders **English**, deterministically, instead of
 * whatever language the test runner's `navigator` happens to report — a test that asserts a
 * label should fail because the label changed, not because the machine is set to Chinese.
 * The provider, which only the app mounts, is where detection happens.
 */
const I18nContext = createContext<I18n | null>(null);

const DETACHED: I18n = {
  lang: "en",
  choice: "auto",
  setLang: () => {},
  setAuto: () => {},
  t: (key, params) => translate("en", key, params),
};

export function I18nProvider({ children }: { children: ReactNode }) {
  const { lang, choice, setLang, setAuto } = useLang();
  const t = useCallback<Translate>((key, params) => translate(lang, key, params), [lang]);
  const value = useMemo<I18n>(
    () => ({ lang, choice, setLang, setAuto, t }),
    [lang, choice, setLang, setAuto, t],
  );
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18n {
  return useContext(I18nContext) ?? DETACHED;
}

/** The common case: a component that only needs to say something. */
export function useT(): Translate {
  return useI18n().t;
}
