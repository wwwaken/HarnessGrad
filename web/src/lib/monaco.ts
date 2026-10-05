/**
 * Monaco, wired to the bundled package rather than a CDN.
 *
 * Two deliberate choices.
 *
 * **No CDN.** `@monaco-editor/react` loads Monaco from jsDelivr by default. That is wrong
 * here for the same reason the platform makes runs work with zero network: a reader opening
 * an old experiment should not need a third-party CDN to see a diff. `loader.config({ monaco })`
 * points it at the npm package, and the Vite `?worker` imports give it the editor and JSON
 * workers under the module graph, so the production build is self-contained.
 *
 * **Only the languages this app shows.** Importing the `monaco-editor` barrel pulls in every
 * bundled basic language (~50 chunks, and it is the reason the chunk warning exists). This
 * app shows a Python harness and unified diffs, so it imports `editor.all` for the editor
 * features (including the diff editor widget) and the Python grammar, and registers a small
 * Monarch tokenizer for unified diffs. Monaco is loaded through `React.lazy` from
 * `components/common/code-view.tsx`, so even this reduced chunk is only fetched by the
 * screens that show code.
 */
import * as monaco from "monaco-editor/esm/vs/editor/editor.api";
import "monaco-editor/esm/vs/editor/editor.all";
import "monaco-editor/esm/vs/basic-languages/python/python.contribution";
import { loader } from "@monaco-editor/react";
import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import jsonWorker from "monaco-editor/esm/vs/language/json/json.worker?worker";

declare global {
  interface Window {
    MonacoEnvironment?: monaco.Environment;
  }
}

self.MonacoEnvironment = {
  getWorker(_workerId: string, label: string) {
    if (label === "json") return new jsonWorker();
    return new editorWorker();
  },
};

/**
 * Monaco has no standalone `diff` grammar — its diff editor computes the diff itself and
 * leaves each side in its own language. A unified patch is the one thing this UI shows most,
 * so a small Monarch tokenizer gives it real colours: a green `+` line, a red `-` line, and
 * the `@@` hunk header.
 */
let diffLanguageRegistered = false;
function registerDiffLanguage() {
  if (diffLanguageRegistered) return;
  diffLanguageRegistered = true;
  monaco.languages.register({ id: "diff" });
  monaco.languages.setMonarchTokensProvider("diff", {
    tokenizer: {
      root: [
        [/^diff --git.*$/, "keyword"],
        [/^(index|new file mode|deleted file mode|similarity index|rename) .*$/, "comment"],
        [/^--- .*$/, "string.invalid"],
        [/^\+\+\+ .*$/, "string"],
        [/^@@.*@@.*$/, "number"],
        [/^\+.*$/, "string"],
        [/^-.*$/, "invalid"],
        [/^\\ No newline.*$/, "comment"],
      ],
    },
  });
  monaco.languages.setLanguageConfiguration("diff", {
    comments: { lineComment: "" },
  });
}

registerDiffLanguage();
loader.config({ monaco });

export { monaco };
export default monaco;
