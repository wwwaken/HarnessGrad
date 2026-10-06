import { renderToString } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { DICTIONARIES, translate, useT } from "@/i18n";
import { en, type TranslationKey } from "@/i18n/en";
import { zh } from "@/i18n/zh";

/**
 * `tsc` already proves that `zh` has exactly the keys `en` has — that is the reason this app
 * has no i18n library. These tests cover what the type checker cannot:
 *
 * * that a translation is a *translation* and not a copy of the English (an empty string or a
 *   verbatim duplicate type-checks perfectly);
 * * that placeholders survive translation, which is the failure mode that reaches a reader as
 *   a literal `{n}` in the middle of a sentence;
 * * that a component with no provider renders English, which is what keeps every other
 *   suite's assertions stable on a machine set to Chinese.
 */
const KEYS = Object.keys(en) as TranslationKey[];

describe("the dictionaries", () => {
  it("has the same keys in both languages", () => {
    expect(Object.keys(zh).sort()).toEqual([...KEYS].sort());
    for (const lang of ["en", "zh"] as const) {
      expect(Object.keys(DICTIONARIES[lang]).sort()).toEqual([...KEYS].sort());
    }
  });

  it("has no empty string", () => {
    for (const key of KEYS) {
      for (const lang of ["en", "zh"] as const) {
        expect(DICTIONARIES[lang][key].trim(), `${lang}:${key}`).not.toBe("");
      }
    }
  });

  it("actually translates — a Chinese string is not a copy of the English one", () => {
    // Not every key: `score`, `test_rate`, `harness sha` and the CLI tokens are deliberately
    // identical in both languages, because they are identifiers a reader matches against the
    // record. A handful of identical values is right; a dictionary of them is not.
    const identical = KEYS.filter((k) => en[k] === zh[k]);
    expect(identical.length / KEYS.length).toBeLessThan(0.15);
    for (const key of identical) {
      // Whatever is identical must be an identifier, not prose: no spaces-only sentence.
      expect(en[key], key).not.toMatch(/^[A-Z][a-z]+ [a-z]+ [a-z]+/);
    }
  });

  it("keeps every placeholder in every language", () => {
    const names = (text: string) => [...text.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort();
    for (const key of KEYS) {
      expect(names(zh[key]), `zh:${key} lost or renamed a placeholder`).toEqual(names(en[key]));
    }
  });

  it("translates and interpolates", () => {
    expect(translate("zh", "nav.experiments")).toBe("实验");
    expect(translate("en", "nav.experiments")).toBe("Experiments");
    const withParam = KEYS.find((k) => en[k].includes("{n}"));
    expect(withParam, "no key uses {n}, so this assertion needs rewriting").toBeDefined();
    const filled = translate("zh", withParam as TranslationKey, { n: 7 });
    expect(filled).toContain("7");
    expect(filled).not.toContain("{n}");
  });

  it("leaves an unknown placeholder alone rather than printing `undefined`", () => {
    const withParam = KEYS.find((k) => en[k].includes("{n}")) as TranslationKey;
    expect(translate("en", withParam, {})).toContain("{n}");
  });
});

function Probe() {
  const t = useT();
  return <span>{t("nav.experiments")}</span>;
}

describe("without a provider", () => {
  it("renders English, so a component test does not depend on the machine's locale", () => {
    // The provider is mounted only by `main.tsx`. Everything else — including every other
    // test in this suite — gets this detached, deterministic English context.
    expect(renderToString(<Probe />)).toContain("Experiments");
  });
});
