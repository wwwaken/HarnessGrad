import Editor, { DiffEditor, type BeforeMount } from "@monaco-editor/react";
import "@/lib/monaco";
import { useTheme } from "@/lib/theme";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * The Monaco half of the app. Loaded through `React.lazy` from `code-view.tsx`, so the
 * ~3 MB editor is fetched only by the screens that show a harness diff.
 */

const defineThemes: BeforeMount = (monaco) => {
  monaco.editor.defineTheme("hg-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [],
    colors: {
      "editor.background": "#0e131b",
      "editorGutter.background": "#0e131b",
      "editorLineNumber.foreground": "#475569",
      "editorLineNumber.activeForeground": "#94a3b8",
      "diffEditor.insertedTextBackground": "#14532d55",
      "diffEditor.removedTextBackground": "#7f1d1d55",
    },
  });
  monaco.editor.defineTheme("hg-light", {
    base: "vs",
    inherit: true,
    rules: [],
    colors: {
      "editor.background": "#ffffff",
      "editorGutter.background": "#ffffff",
      "diffEditor.insertedTextBackground": "#bbf7d055",
      "diffEditor.removedTextBackground": "#fecaca66",
    },
  });
};

const BASE_OPTIONS = {
  readOnly: true,
  domReadOnly: true,
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  renderLineHighlight: "none" as const,
  fontSize: 12,
  lineHeight: 18,
  fontFamily: "var(--font-mono), ui-monospace, monospace",
  scrollbar: { verticalScrollbarSize: 8, horizontalScrollbarSize: 8 },
  overviewRulerLanes: 0,
  padding: { top: 8, bottom: 8 },
  wordWrap: "off" as const,
  automaticLayout: true,
};

export function MonacoCode({
  value,
  language,
  height = 360,
}: {
  value: string;
  language: string;
  height?: number;
}) {
  const { resolved } = useTheme();
  return (
    <Editor
      height={height}
      language={language}
      value={value}
      theme={resolved === "dark" ? "hg-dark" : "hg-light"}
      beforeMount={defineThemes}
      loading={<Skeleton className="h-full w-full" />}
      options={{ ...BASE_OPTIONS, lineNumbers: "on" }}
    />
  );
}

export function MonacoDiff({
  original,
  modified,
  language,
  height = 360,
}: {
  original: string;
  modified: string;
  language: string;
  height?: number;
}) {
  const { resolved } = useTheme();
  return (
    <DiffEditor
      height={height}
      language={language}
      original={original}
      modified={modified}
      theme={resolved === "dark" ? "hg-dark" : "hg-light"}
      beforeMount={defineThemes}
      loading={<Skeleton className="h-full w-full" />}
      options={{ ...BASE_OPTIONS, renderSideBySide: true, originalEditable: false }}
    />
  );
}
