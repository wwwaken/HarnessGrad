import { useCallback, useEffect, useState } from "react";

/**
 * The interface language, resolved the same way the theme is: **detected first, remembered
 * after**. A reader whose browser asks for Chinese should not have to find a control before
 * the page is readable, and a reader who has chosen English on a Chinese machine should not
 * have the choice taken back on the next page load.
 *
 * The order is therefore: an explicit choice in `localStorage`, then `navigator.languages`,
 * then `navigator.language`, then English. `navigator.languages` is the full preference list
 * in order and is the one to read — `navigator.language` is only its first element, and on a
 * machine set to `["fr-FR", "zh-CN"]` the difference is between the correct fallback and
 * nothing.
 *
 * Only `zh` and `en` are shipped, so a preference list of `["ja-JP", "zh-CN"]` selects
 * Chinese rather than giving up at the first entry it does not have. That is what a reader
 * with that list is asking for; a browser that lists a language second still prefers it to a
 * language absent from the list entirely.
 */

export type Lang = "en" | "zh";

export const LANG_STORAGE_KEY = "hg-lang";

export const LANGS: readonly Lang[] = ["en", "zh"];

/** The label each language carries in its own language, which is how a switcher is read. */
export const LANG_LABEL: Record<Lang, string> = { en: "English", zh: "中文" };

function fromStorage(): Lang | null {
  try {
    const value = localStorage.getItem(LANG_STORAGE_KEY);
    if (value === "en" || value === "zh") return value;
  } catch {
    /* storage disabled: fall through to detection */
  }
  return null;
}

/** The reader's preference list, most preferred first. Never empty in a browser. */
function preferred(): readonly string[] {
  if (typeof navigator === "undefined") return [];
  const many = navigator.languages;
  if (many && many.length > 0) return many;
  return navigator.language ? [navigator.language] : [];
}

/**
 * The language the first paint should use: the remembered choice, else the first shipped
 * language the reader asked for, else English.
 */
export function detectLang(): Lang {
  const stored = fromStorage();
  if (stored) return stored;
  for (const tag of preferred()) {
    // `zh`, `zh-CN`, `zh-Hans-CN`, `zh-TW` all start with `zh`; the script and region
    // subtags would choose between Simplified and Traditional, which this app does not
    // ship, so the first two letters are the whole test. Scanning the **whole** list
    // rather than only its first entry is what makes `["ja-JP", "zh-CN"]` select Chinese:
    // a reader who lists a language second still prefers it to one they did not list.
    const primary = tag.toLowerCase().split("-")[0];
    if (primary === "en" || primary === "zh") return primary;
  }
  return "en";
}

/** Write the language onto `<html lang>`, which is what a screen reader and a font stack read. */
export function applyLang(lang: Lang): Lang {
  if (typeof document !== "undefined") document.documentElement.lang = lang === "zh" ? "zh-Hans" : "en";
  return lang;
}

export function rememberLang(lang: Lang): void {
  try {
    localStorage.setItem(LANG_STORAGE_KEY, lang);
  } catch {
    /* storage disabled: the language still applies for this session */
  }
}

/**
 * Forget the explicit choice, so detection applies again.
 *
 * This is the difference between "automatic" and "English". Removing the key is the only
 * way to express it: writing the *currently detected* value would freeze whatever the
 * browser happened to say today and stop following it tomorrow, which looks identical until
 * the reader changes their system language.
 */
export function forgetLang(): void {
  try {
    localStorage.removeItem(LANG_STORAGE_KEY);
  } catch {
    /* storage disabled: nothing was remembered anyway */
  }
}

/** What the reader chose, or `"auto"` when they have chosen nothing. */
export type LangChoice = Lang | "auto";

export function getLangChoice(): LangChoice {
  return fromStorage() ?? "auto";
}

/** The language as state, with the same shape as `useTheme`. */
export function useLang() {
  const [choice, setChoice] = useState<LangChoice>(() => getLangChoice());
  const [lang, setLangState] = useState<Lang>(() => detectLang());

  useEffect(() => {
    // `auto` re-detects on every mount rather than caching a value, because the browser's
    // preference can change between sessions and nothing else would notice.
    const next = choice === "auto" ? detectLang() : choice;
    setLangState(next);
    applyLang(next);
  }, [choice]);

  const setLang = useCallback((next: Lang) => {
    rememberLang(next);
    setChoice(next);
  }, []);

  const setAuto = useCallback(() => {
    forgetLang();
    setChoice("auto");
  }, []);

  return { lang, choice, setLang, setAuto };
}
