import { CodeView } from "@/components/common/code-view";
import { EmptyState, ErrorState } from "@/components/common/states";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useRoundDiff } from "@/hooks/queries";
import { shortSha } from "@/lib/format";
import type { RoundDiff } from "@/types";

/**
 * The candidate diff for one round: what the method actually changed.
 *
 * `harnessgrad/records.py:_save_round_diff` persists the round's git diff beside the curve
 * point precisely so this view works on an old run after `git gc` has collected the dangling
 * commit. Two facts are shown before the patch:
 *
 * * `from` → `to`, the harness sha before and after — the identity the next point's score
 *   belongs to;
 * * the numstat row, because a diff that reports `0` added and `0` removed lines is the
 *   "non-functional candidate" case that a score alone read as a gain.
 *
 * **The patch comes from its own endpoint.** `GET /api/runs/:id` carries the diff *stat*
 * only; `GET /api/runs/:id/rounds/:n/diff` carries `{stat, patch}` and answers `404` when a
 * round has no saved patch. That `404` is an absence, not a failure — round 0 is the
 * unmodified base harness, so it has no diff by construction — and `getRoundDiff` resolves
 * it to `null` before the query can enter an error state.
 */
export function RoundDiffPanel({ runId, round }: { runId: string; round: number | null }) {
  const query = useRoundDiff(runId, round);

  if (round === null) {
    return <EmptyState title="No round selected" description="Pick a round to see its candidate diff." />;
  }
  if (query.isLoading) {
    return <Skeleton className="h-[420px] w-full" />;
  }
  if (query.error) {
    return <ErrorState error={query.error} onRetry={() => void query.refetch()} />;
  }

  const diff: RoundDiff | null = query.data ?? null;
  if (!diff) {
    return (
      <EmptyState
        title={`No saved diff for round ${round}`}
        description={
          round === 0
            ? "Round 0 is the unmodified base harness, so there is no candidate edit to show. Its `identity.harness_sha` is the baseline every later round is compared against."
            : "The platform did not save a diff for this round. Older runs predate `records.py:_save_round_diff`; the diff is not recoverable from disk."
        }
      />
    );
  }

  // A patch can exist while its sibling stat file is half-written. When that happens the
  // numbers are absent, not zero, and the panel says so instead of printing +0 / −0.
  const statKnown = typeof diff.added === "number" && typeof diff.removed === "number";

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-2 text-2xs">
        <Badge variant="muted" className="font-mono">
          {shortSha(diff.from)} → {shortSha(diff.to)}
        </Badge>
        {statKnown ? (
          <>
            <span className="tabular text-pass">+{diff.added}</span>
            <span className="tabular text-fail">−{diff.removed}</span>
            <span className="text-muted-foreground">
              {diff.files.length} file{diff.files.length === 1 ? "" : "s"} changed
            </span>
            {diff.added === 0 && diff.removed === 0 ? (
              <Badge variant="warn">no textual change — a score here is not evidence about the edit</Badge>
            ) : null}
          </>
        ) : (
          <Badge variant="warn">
            the saved diff stat is unreadable — the patch is shown without a numstat
          </Badge>
        )}
      </div>
      {!statKnown && diff.stat_error ? (
        <p className="text-2xs text-warn">{diff.stat_error}</p>
      ) : null}
      {statKnown && diff.files.length ? (
        <div className="overflow-hidden rounded-md border border-border">
          <Table>
            <TableHeader className="bg-muted/40">
              <TableRow className="hover:bg-transparent">
                <TableHead>File</TableHead>
                <TableHead className="w-16 text-right">Added</TableHead>
                <TableHead className="w-20 text-right">Removed</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {diff.files.map((file) => (
                <TableRow key={file.path}>
                  <TableCell className="font-mono text-xs">{file.path}</TableCell>
                  <TableCell className="text-right tabular text-pass">+{file.added}</TableCell>
                  <TableCell className="text-right tabular text-fail">−{file.removed}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : null}
      <CodeView value={diff.patch} language="diff" height={420} />
    </div>
  );
}
