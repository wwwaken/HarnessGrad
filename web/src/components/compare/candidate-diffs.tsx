import { useState } from "react";
import { Columns2, FileDiff } from "lucide-react";
import { CodeView, DiffView } from "@/components/common/code-view";
import { EmptyState, ErrorState } from "@/components/common/states";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useRoundDiff } from "@/hooks/queries";
import { shortSha } from "@/lib/format";
import type { RunBundle, RoundDiff } from "@/types";
import type { RunComparison } from "@/logic/compare";

/**
 * The two runs' candidate diffs, for the compared rounds.
 *
 * Two view modes, because they answer different questions:
 *
 * * **Patches** — what did each method actually edit, against its own base? This is the
 *   `runs/<id>/diffs/round-<n>.patch` the platform saved, so it is the recorded artifact and
 *   not a reconstruction.
 * * **Patch vs patch** — where do the two edits disagree? Useful when both methods target the
 *   same harness and one works: the useful signal is the hunk the failing one did not make.
 *
 * Each patch is fetched from `GET /api/runs/:id/rounds/:n/diff`, the endpoint that carries
 * it: the run bundle holds the diff *stat* only. A round with no saved patch is a `404`
 * (round 0 by construction), rendered as an explicit absence rather than an empty editor.
 */
export function CandidateDiffs({
  comparison,
  leftBundle,
  rightBundle,
}: {
  comparison: RunComparison;
  leftBundle: RunBundle;
  rightBundle: RunBundle;
}) {
  const [mode, setMode] = useState<"side" | "compare">("side");
  const leftQuery = useRoundDiff(leftBundle.run_id, comparison.leftRound);
  const rightQuery = useRoundDiff(rightBundle.run_id, comparison.rightRound);

  const leftDiff: RoundDiff | null = leftQuery.data ?? null;
  const rightDiff: RoundDiff | null = rightQuery.data ?? null;

  if (leftQuery.isLoading || rightQuery.isLoading) {
    return (
      <div className="grid gap-3 xl:grid-cols-2">
        <Skeleton className="h-[520px] w-full" />
        <Skeleton className="h-[520px] w-full" />
      </div>
    );
  }
  if (leftQuery.error || rightQuery.error) {
    return (
      <div className="space-y-2">
        {leftQuery.error ? (
          <ErrorState error={leftQuery.error} onRetry={() => void leftQuery.refetch()} />
        ) : null}
        {rightQuery.error ? (
          <ErrorState error={rightQuery.error} onRetry={() => void rightQuery.refetch()} />
        ) : null}
      </div>
    );
  }

  if (!leftDiff && !rightDiff) {
    return (
      <EmptyState
        title="Neither run saved a diff for its compared round"
        description="Round 0 is the unmodified base harness and has no diff; older runs predate records.py:_save_round_diff, which persists the round's patch beside the point."
      />
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Button
            variant={mode === "side" ? "secondary" : "ghost"}
            size="xs"
            onClick={() => setMode("side")}
          >
            <Columns2 className="h-3 w-3" />
            Both patches
          </Button>
          <Button
            variant={mode === "compare" ? "secondary" : "ghost"}
            size="xs"
            onClick={() => setMode("compare")}
          >
            <FileDiff className="h-3 w-3" />
            Patch vs patch
          </Button>
        </div>
        <span className="text-2xs text-muted-foreground">
          read from <span className="font-mono">GET /api/runs/&lt;id&gt;/rounds/&lt;n&gt;/diff</span>
        </span>
      </div>

      {mode === "side" ? (
        <div className="grid gap-3 xl:grid-cols-2">
          <Side
            title={`${comparison.leftRunId} · round ${comparison.leftRound}`}
            diff={leftDiff}
          />
          <Side
            title={`${comparison.rightRunId} · round ${comparison.rightRound}`}
            diff={rightDiff}
          />
        </div>
      ) : (
        <div className="space-y-2">
          <p className="text-2xs text-muted-foreground">
            The left patch is the “original” and the right patch the “modified”. A hunk that
            appears only on one side is a change only one method made.
          </p>
          <DiffView
            original={leftDiff?.patch ?? ""}
            modified={rightDiff?.patch ?? ""}
            language="diff"
            height={560}
          />
        </div>
      )}
    </div>
  );
}

function Side({ title, diff }: { title: string; diff: RoundDiff | null }) {
  const statKnown = diff !== null && typeof diff.added === "number" && typeof diff.removed === "number";
  return (
    <div className="space-y-1.5">
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono text-xs font-medium">{title}</span>
        {diff ? (
          <>
            <Badge variant="muted" className="font-mono">
              {shortSha(diff.from)} → {shortSha(diff.to)}
            </Badge>
            {statKnown ? (
              <>
                <span className="tabular text-2xs text-pass">+{diff.added}</span>
                <span className="tabular text-2xs text-fail">−{diff.removed}</span>
              </>
            ) : (
              <Badge variant="warn">stat unreadable</Badge>
            )}
            <span className="text-2xs text-muted-foreground">
              {diff.files.map((f) => f.path).join(", ") || "no textual change"}
            </span>
          </>
        ) : (
          <Badge variant="muted">no patch saved</Badge>
        )}
      </div>
      <CodeView
        value={diff?.patch ?? ""}
        language="diff"
        height={520}
        emptyLabel="No patch saved for this round"
      />
    </div>
  );
}
