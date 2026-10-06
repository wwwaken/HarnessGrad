import { Component, lazy, Suspense, type ReactNode } from "react";
import { FileCode2 } from "lucide-react";
import { EmptyState, ErrorState } from "@/components/common/states";
import { useT } from "@/i18n";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * The read-only code viewer, split out of the bundle.
 *
 * Monaco is the heaviest dependency in the app and only the harness diff needs it, so it
 * is `React.lazy`-loaded behind a Suspense boundary: the Experiments and Launch screens
 * never pay for it, and a diff panel that fails to download degrades to an explicit error
 * instead of an empty box. Both lazy components resolve from the same module, so the chunk
 * is fetched once.
 */
const LazyCode = lazy(() =>
  import("./monaco-view").then((m) => ({ default: m.MonacoCode })),
);
const LazyDiff = lazy(() =>
  import("./monaco-view").then((m) => ({ default: m.MonacoDiff })),
);

export interface CodeViewProps {
  original?: string;
  modified?: string;
  value?: string;
  language?: string;
  height?: number;
}

class ViewerBoundary extends Component<
  { children: ReactNode; fallback: ReactNode },
  { failed: string | null }
> {
  state: { failed: string | null } = { failed: null };
  static getDerivedStateFromError(error: unknown) {
    return { failed: error instanceof Error ? error.message : String(error) };
  }
  render() {
    if (this.state.failed) return this.props.fallback;
    return this.props.children;
  }
}

function Shell({
  empty,
  language,
  children,
}: {
  empty: string | null;
  language?: string;
  children: ReactNode;
}) {
  const t = useT();
  if (empty) {
    return (
      <EmptyState
        icon={<FileCode2 className="h-5 w-5" />}
        title={empty}
        description={t("common.diffHint")}
      />
    );
  }
  return (
    <div className="overflow-hidden rounded-md border border-border">
      <div className="flex items-center justify-between border-b border-border bg-muted/40 px-2 py-1">
        <span className="font-mono text-2xs text-muted-foreground">{language ?? "diff"}</span>
        <span className="text-2xs text-muted-foreground">{t("common.readOnly")}</span>
      </div>
      {children}
    </div>
  );
}

const FAILED = <ErrorState error={new Error("the code viewer failed to load")} className="m-3" />;

/** A single read-only file or patch. `language="diff"` gives unified-diff highlighting. */
export function CodeView({
  value,
  language = "diff",
  height = 360,
  emptyLabel,
}: CodeViewProps & { emptyLabel?: string }) {
  const t = useT();
  const empty = !value ? (emptyLabel ?? t("common.noPatch")) : null;
  return (
    <Shell empty={empty} language={language}>
      <ViewerBoundary fallback={FAILED}>
        <Suspense fallback={<Skeleton className="h-[360px] w-full" />}>
          <LazyCode value={value ?? ""} language={language} height={height} />
        </Suspense>
      </ViewerBoundary>
    </Shell>
  );
}

/** A side-by-side diff of two texts (e.g. two runs' candidate patches). */
export function DiffView({ original, modified, language = "diff", height = 360 }: CodeViewProps) {
  const t = useT();
  const empty = !original && !modified ? t("common.noPatchBoth") : null;
  return (
    <Shell empty={empty} language={language}>
      <ViewerBoundary fallback={FAILED}>
        <Suspense fallback={<Skeleton className="h-[360px] w-full" />}>
          <LazyDiff
            original={original ?? ""}
            modified={modified ?? ""}
            language={language}
            height={height}
          />
        </Suspense>
      </ViewerBoundary>
    </Shell>
  );
}
