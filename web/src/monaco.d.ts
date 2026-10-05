/**
 * `monaco-editor` ships `.d.ts` files for its API but not for the side-effect
 * contributions, so the two imports `src/lib/monaco.ts` needs for the editor features and
 * the Python grammar are declared here rather than silenced with a cast.
 *
 * `editor.all` pulls in every editor contribution (find, hover, the diff editor widget, …)
 * without any language grammar; the grammars are imported one at a time.
 */
declare module "monaco-editor/esm/vs/editor/editor.all";
