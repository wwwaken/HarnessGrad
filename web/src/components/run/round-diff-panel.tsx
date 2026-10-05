import { CodeView } from "@/components/common/code-view";
import { EmptyState } from "@/components/common/states";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { shortSha } from "@/lib/format";
import type { RunBundle } from "@/types";

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
 * Round 0 is the unmodified base harness, so it has no diff; that is an absence, not an
 * empty edit.
 */
export function RoundDiffPanel({ bundle, round }: { bundle: RunBundle; round: number | null }) {
  if (round === null) {
    return <EmptyState title="No round selected" description="Pick a round to see its candidate diff." />;
  }
  const diff = bundle.diffs[String(round)];
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
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-2 text-2xs">
        <Badge variant="muted" className="font-mono">
          {shortSha(diff.from)} → {shortSha(diff.to)}
        </Badge>
        <span className="tabular text-pass">+{diff.added}</span>
        <span className="tabular text-fail">−{diff.removed}</span>
        <span className="text-muted-foreground">
          {diff.files.length} file{diff.files.length === 1 ? "" : "s"} changed
        </span>
        {diff.added === 0 && diff.removed === 0 ? (
          <Badge variant="warn">no textual change — a score here is not evidence about the edit</Badge>
        ) : null}
      </div>
      {diff.files.length ? (
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
