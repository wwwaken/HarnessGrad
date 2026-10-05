import { useCallback, useEffect, useState } from "react";

/**
 * The theme is one class on `<html>`, set before first paint by the inline script in
 * `index.html`. This hook is the only other place that writes it.
 *
 * All three states are real: "system" follows the OS and keeps following it, which is what
 * a researcher switching their laptop to dark at night expects. The choice is stored in
 * `localStorage` under `hg-theme`, the same key the inline script reads — if the two
 * disagree, the flash-of-wrong-theme bug is back.
 */

export type Theme = "light" | "dark" | "system";

export const THEME_STORAGE_KEY = "hg-theme";

export function getStoredTheme(): Theme {
  try {
    const value = localStorage.getItem(THEME_STORAGE_KEY);
    if (value === "light" || value === "dark" || value === "system") return value;
  } catch {
    /* storage disabled: fall through to the system preference */
  }
  return "system";
}

export function prefersDark(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches;
}

export function resolveTheme(theme: Theme): "light" | "dark" {
  if (theme === "system") return prefersDark() ? "dark" : "light";
  return theme;
}

export function applyTheme(theme: Theme): "light" | "dark" {
  const resolved = resolveTheme(theme);
  document.documentElement.classList.toggle("dark", resolved === "dark");
  return resolved;
}

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(() => getStoredTheme());
  const [resolved, setResolved] = useState<"light" | "dark">(() => resolveTheme(getStoredTheme()));

  useEffect(() => {
    setResolved(applyTheme(theme));
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch {
      /* storage disabled: the theme still applies for this session */
    }
    if (theme !== "system") return;
    const query = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => setResolved(applyTheme("system"));
    query.addEventListener("change", onChange);
    return () => query.removeEventListener("change", onChange);
  }, [theme]);

  const setTheme = useCallback((next: Theme) => setThemeState(next), []);
  return { theme, resolved, setTheme };
}
