/**
 * Where the fixture files are, as URLs.
 *
 * The fixtures are fetched at runtime rather than imported as modules. That is deliberate:
 * the whole point of the fixture layer is to stand in for a read API that does not exist
 * yet, so it must have the same *shape* as one — asynchronous, fallible, and loading. A
 * static `import` would make every screen synchronously available and the loading and
 * error states would never be exercised.
 *
 * Each entry is written out longhand because Vite resolves `new URL(..., import.meta.url)`
 * statically; a template string built from a variable would not be emitted into `dist/`.
 * When the real API lands, this file is deleted and `lib/api.ts` keeps its signatures.
 */
export const fixtureUrls = {
  runsIndex: new URL("./data/runs-index.json", import.meta.url).href,
  launchOptions: new URL("./data/launch-options.json", import.meta.url).href,
  runBundles: {
    "ds-dgm": new URL("./data/run-ds-dgm.json", import.meta.url).href,
    "ds-rrsi": new URL("./data/run-ds-rrsi.json", import.meta.url).href,
  } as Record<string, string | undefined>,
  taskPages: {
    "ds-dgm/0/cobol-modernization":
      new URL("./data/task-ds-dgm-r0-cobol-modernization.json", import.meta.url).href,
    "ds-dgm/0/fix-git":
      new URL("./data/task-ds-dgm-r0-fix-git.json", import.meta.url).href,
  } as Record<string, string | undefined>,
} as const;
