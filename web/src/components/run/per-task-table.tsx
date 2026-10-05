import { Link } from "react-router-dom";
import { ArrowUpRight, CircleAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { EmptyState } from "@/components/common/states";
import { Value } from "@/components/common/presence-value";
import { firstLine, formatScore } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { CurvePoint, Verdict } from "@/types";

/**
 * Every task the round scored, with the two signals side by side.
 *
 * The `test_rate` column is the reason this table is not just a score list: a task showing
 * `0` with `0.80` beside it is a task where four of five checks passed and the all-or-nothing
 * reward said nothing happened. The verdict's `detail` — the check's own sentence — is shown
 * truncated, because "reward 0" and "the XSS bypass failed" are different kinds of fact.
 *
 * Tasks the platform could not measure are rendered as **unmeasured**, never as `0`:
 * `harness_failed` ("the harness failed this") and `invalid` ("the platform could not measure
 * this") are separate maps on the point, and both are different from a fail.
 */
export function PerTaskTable({
  runId,
  round,
  point,
  verdicts,
}: {
  runId: string;
  round: number;
  point: CurvePoint | null;
  verdicts: Record<string, Verdict>;
}) {
  const perTask = point?.per_task ?? {};
  const perTaskRate = point?.per_task_test_rate ?? {};
  const ids = [...new Set([...Object.keys(perTask), ...Object.keys(perTaskRate), ...Object.keys(verdicts)])].sort();

  if (!point) {
    return (
      <EmptyState
        title={`Round ${round} is not in this run's curve`}
        description="The run's curve.jsonl has no point for this round, so there is no per-task scoring to show."
      />
    );
  }
  if (!ids.length) {
    return (
      <EmptyState
        title="No per-task scoring recorded"
        description="The point carries an empty `per_task` map. On a run that predates the field this is absence, not ten failures."
      />
    );
  }

  const passed = ids.filter((id) => (perTask[id] ?? 0) >= 1).length;

  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <Table>
        <TableHeader className="bg-muted/40">
          <TableRow className="hover:bg-transparent">
            <TableHead>Task</TableHead>
            <TableHead className="w-20">Score</TableHead>
            <TableHead className="w-24">test_rate</TableHead>
            <TableHead className="w-24">tests</TableHead>
            <TableHead>Verdict detail</TableHead>
            <TableHead className="w-10" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {ids.map((taskId) => {
            const score = perTask[taskId];
            const rate = perTaskRate[taskId];
            const verdict = verdicts[taskId];
            const invalid = point.invalid?.[taskId];
            const harnessFailed = point.harness_failed?.[taskId];
            const measured = !invalid && !harnessFailed && typeof score === "number";
            const unmeasuredLabel = harnessFailed
              ? "harness failed"
              : invalid
                ? "not measured"
                : "unmeasured";
            return (
              <TableRow key={taskId} className="group">
                <TableCell className="font-mono text-xs">
                  <Link
                    to={`/runs/${runId}/tasks/${round}/${taskId}`}
                    className="inline-flex items-center gap-1 underline-offset-2 hover:underline"
                  >
                    {taskId}
                    <ArrowUpRight className="h-3 w-3 opacity-0 transition-opacity group-hover:opacity-60" />
                  </Link>
                </TableCell>
                <TableCell>
                  {measured ? (
                    <span
                      className={cn(
                        "tabular font-medium",
                        score >= 1 ? "text-pass" : score > 0 ? "text-warn" : "text-fail",
                      )}
                    >
                      {formatScore(score)}
                    </span>
                  ) : (
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Badge variant="warn" className="cursor-help">
                          {unmeasuredLabel}
                        </Badge>
                      </TooltipTrigger>
                      <TooltipContent className="max-w-md">
                        {harnessFailed
                          ? `harness_failed: ${harnessFailed}`
                          : invalid
                            ? `invalid: ${invalid}`
                            : "the point records no score for this task — absence, not zero"}
                      </TooltipContent>
                    </Tooltip>
                  )}
                </TableCell>
                <TableCell>
                  <TestRateCell rate={rate} present={taskId in perTaskRate} />
                </TableCell>
                <TableCell className="text-2xs text-muted-foreground">
                  {verdict?.tests ? (
                    <span className="tabular">
                      {verdict.tests.passed}
                      <span className="text-muted-foreground/60">
                        /{verdict.tests.passed + verdict.tests.failed}
                      </span>
                    </span>
                  ) : (
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <span className="cursor-help">—</span>
                      </TooltipTrigger>
                      <TooltipContent className="max-w-xs">
                        this check reported no machine-readable per-test tally; that is not the
                        same as zero tests passing
                      </TooltipContent>
                    </Tooltip>
                  )}
                </TableCell>
                <TableCell className="max-w-[520px]">
                  <span className="block truncate text-2xs text-muted-foreground" title={verdict?.detail}>
                    {verdict ? firstLine(verdict.detail, 160) : "no verdict file for this task"}
                  </span>
                </TableCell>
                <TableCell>
                  {verdict?.passed === false && !point.invalid?.[taskId] ? (
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <CircleAlert className="h-3.5 w-3.5 text-muted-foreground/60" />
                      </TooltipTrigger>
                      <TooltipContent>the verifier ran and the task did not pass</TooltipContent>
                    </Tooltip>
                  ) : null}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-border px-3 py-1.5 text-2xs text-muted-foreground">
        <span>
          {passed} of {point.n_scored} scored tasks passed this round (score is the mean over
          the scored tasks).
        </span>
        {point.n_invalid || point.n_harness_failed ? (
          <span className="text-warn">
            {point.n_invalid ?? 0} invalid · {point.n_harness_failed ?? 0} harness failures — a
            refusal is a record, not a zero.
          </span>
        ) : null}
      </div>
    </div>
  );
}

function TestRateCell({ rate, present }: { rate: number | null | undefined; present: boolean }) {
  if (!present) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="cursor-help text-muted-foreground/60">
            <Value value={undefined} fieldName="per_task_test_rate" />
          </span>
        </TooltipTrigger>
        <TooltipContent className="max-w-xs">
          no `per_task_test_rate` for this task — the field was added 2026-10-05, or this check
          reported no tally
        </TooltipContent>
      </Tooltip>
    );
  }
  if (rate === null) {
    return <Value value={null} fieldName="per_task_test_rate" />;
  }
  return (
    <span className="flex items-center gap-1.5">
      <span className="tabular">{formatScore(rate)}</span>
      <span className="h-1.5 w-10 overflow-hidden rounded-full bg-muted">
        <span
          className="block h-full rounded-full bg-chart-testrate"
          style={{ width: `${Math.round((rate ?? 0) * 100)}%` }}
        />
      </span>
    </span>
  );
}
