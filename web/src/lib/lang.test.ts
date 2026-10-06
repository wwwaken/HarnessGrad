import { afterEach, describe, expect, it, vi } from "vitest";
import { detectLang, forgetLang, getLangChoice, LANG_STORAGE_KEY, rememberLang } from "@/lib/lang";

/**
 * Detection order is the whole behaviour of this module, and every branch of it is one a
 * reader can actually be in: a browser set to another language entirely, a browser whose
 * preference list starts with one this app does not ship, and a reader who has already
 * chosen.
 *
 * `localStorage` is stubbed rather than assumed, because these tests run in the node
 * environment the rest of the suite uses and there is no storage there — which is exactly why
 * `detectLang` is written to survive its absence.
 */
function storage(initial: Record<string, string> = {}) {
  const map = new Map(Object.entries(initial));
  const stub = {
    getItem: (k: string) => map.get(k) ?? null,
    setItem: (k: string, v: string) => void map.set(k, v),
    removeItem: (k: string) => void map.delete(k),
  };
  vi.stubGlobal("localStorage", stub);
  return map;
}

function langs(list: string[]) {
  vi.stubGlobal("navigator", { languages: list, language: list[0] });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("detectLang", () => {
  it("takes the first language it actually ships", () => {
    storage();
    langs(["zh-CN"]);
    expect(detectLang()).toBe("zh");
    langs(["en-GB"]);
    expect(detectLang()).toBe("en");
  });

  it("keeps scanning the list instead of giving up on the first entry", () => {
    storage();
    // The bug this guards: reading only `navigator.language`, which is the first element, so
    // a reader who lists Chinese second gets English.
    langs(["ja-JP", "zh-CN"]);
    expect(detectLang()).toBe("zh");
    langs(["fr-FR", "de-DE", "en-US"]);
    expect(detectLang()).toBe("en");
  });

  it("treats every Chinese tag as Chinese", () => {
    storage();
    for (const tag of ["zh", "zh-Hans", "zh-Hans-CN", "zh-TW", "ZH-cn"]) {
      langs([tag]);
      expect(detectLang(), tag).toBe("zh");
    }
  });

  it("falls back to English for a language it does not ship", () => {
    storage();
    langs(["ko-KR"]);
    expect(detectLang()).toBe("en");
  });

  it("lets an explicit choice beat the browser, in both directions", () => {
    const map = storage({ [LANG_STORAGE_KEY]: "en" });
    langs(["zh-CN"]);
    expect(detectLang()).toBe("en");
    map.set(LANG_STORAGE_KEY, "zh");
    langs(["en-US"]);
    expect(detectLang()).toBe("zh");
  });

  it("ignores a stored value that is not a language it ships", () => {
    storage({ [LANG_STORAGE_KEY]: "fr" });
    langs(["zh-CN"]);
    expect(detectLang()).toBe("zh");
  });

  it("survives a browser with no preference list at all", () => {
    storage();
    vi.stubGlobal("navigator", {});
    expect(detectLang()).toBe("en");
  });
});

describe("the remembered choice", () => {
  it("distinguishes \"automatic\" from a choice, which is the point of forgetLang", () => {
    const map = storage();
    langs(["zh-CN"]);
    expect(getLangChoice()).toBe("auto");

    rememberLang("en");
    expect(getLangChoice()).toBe("en");
    expect(detectLang()).toBe("en");

    // Forgetting must restore detection, not freeze today's answer: writing the detected
    // value back would look identical here and stop following the browser tomorrow.
    forgetLang();
    expect(getLangChoice()).toBe("auto");
    expect(detectLang()).toBe("zh");
    expect(map.has(LANG_STORAGE_KEY)).toBe(false);
  });
});
