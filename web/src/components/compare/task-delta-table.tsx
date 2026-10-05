import { Link } from "react-router-dom";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { DeltaPill } from "@/components/common/stat";
import { EmptyState } from "@/components/common/states";
import { Value } from "@/components/common/presence-value";
import { firstLine, formatScore } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { RunComparison, TaskMove } from "@/logic/compare";

/**
 * The per-task delta: the table the headline strip summarises.
 *
 * `test_rate` gets its own delta column because it is the only signal that resolves a task
 * whose binary reward did not move while its check tally did. Each side's verdict `detail`
 * is one truncated line (full text on hover) so a reader can see *why* a task flipped without
 * leaving the screen — the difference between "reward 0" and "the layout file hash is wrong".
 *
 * A task present in only one run is shown as `unmeasured` on the other side rather than
 * dropped: two runs sampled with different `--tasks` are not comparable task-for-task, and a
 * table that silently intersected them would hide that.
 */
export function TaskDeltaTable({
  comparison,
  onlyMoved,
}: {
  comparison: RunComparison;
  onlyMoved: boolean;
}) {
  const tasks = onlyMoved
    ? comparison.tasks.filter((t) => t.move === "gained" || t.move === "lost" || t.move === "partial-moved" || t.move === "unmeasured")
    : comparison.tasks;

  if (!tasks.length) {
    return (
      <EmptyState
        title={onlyMoved ? "No tasks moved" : "No per-task scoring on both sides"}
        description={
          onlyMoved
            ? "Every task present in both states has the same pass/fail outcome. Turn off “only moved” to see the full task set."
            : "At least one side records no per_task map for the selected round — absence, not an empty task set."
        }
      />
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <Table>
        <TableHeader className="bg-muted/40">
          <TableRow className="hover:bg-transparent">
            <TableHead>Task</TableHead>
            <TableHead className="w-16 text-right">{comparison.leftRunId}</TableHead>
            <TableHead className="w-16 text-right">{comparison.rightRunId}</TableHead>
            <TableHead className="w-24">Move</TableHead>
            <TableHead className="w-24 text-right">Δ test_rate</TableHead>
            <TableHead>Why it changed (each side's verdict)</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tasks.map((task) => (
            <TableRow key={task.taskId} className="group">
              <TableCell className="font-mono text-xs">
                {task.membership === "both" ? (
                  <Link
                    to={`/runs/${comparison.rightRunId}/tasks/${comparison.rightRound}/${task.taskId}`}
                    className="underline-offset-2 hover:underline"
                    title="open this task's verdict and trace in the right-hand run"
                  >
                    {task.taskId}
                  </Link>
                ) : (
                  <span title={`only present in the ${task.membership === "left-only" ? "left" : "right"} run`}>
                    {task.taskId}
                  </span>
                )}
              </TableCell>
              <ScoreCell value={task.leftScore} membership={task.membership === "right-only"} />
              <ScoreCell value={task.rightScore} membership={task.membership === "left-only"} />
              <TableCell>
                <MoveBadge move={task.move} />
              </TableCell>
              <TableCell className="text-right">
                {task.testRateDelta === null ? (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <span className="cursor-help text-muted-foreground/60">—</span>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs">
                      {`left test_rate: ${task.leftTestRate === undefined ? "absent" : task.leftTestRate ?? "null"}, ` +
                        `right test_rate: ${task.rightTestRate === undefined ? "absent" : task.rightTestRate ?? "null"}`}
                    </TooltipContent>
                  </Tooltip>
                ) : (
                  <DeltaPill value={task.testRateDelta} />
                )}
              </TableCell>
              <TableCell className="max-w-[420px]">
                <div className="space-y-0.5">
                  <DetailLine side="L" detail={task.leftDetail} />
                  <DetailLine side="R" detail={task.rightDetail} />
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <div className="border-t border-border px-3 py-1.5 text-2xs text-muted-foreground">
        Pass is `score ≥ 1`, fail is `score ≤ 0`; a value strictly between them is a partial and
        only occurs with <span className="font-mono">--trials &gt; 1</span>. An em dash is an
        absent or null value, never a zero.
      </div>
    </div>
  );
}

function ScoreCell({ value, membership }: { value: number | null; membership: boolean }) {
  if (membership) {
    return (
      <TableCell className="text-right">
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="cursor-help text-2xs text-muted-foreground">
              not in this run
            </span>
          </TooltipTrigger>
          <TooltipContent className="max-w-xs">
            the task is absent from this run&apos;s sampling, which is a different fact from a
            score of zero
          </TooltipContent>
        </Tooltip>
      </TableCell>
    );
  }
  if (value === null) {
    return (
      <TableCell className="text-right">
        <Value value={null} />
      </TableCell>
    );
  }
  return (
    <TableCell
      className={cn(
        "text-right tabular font-medium",
        value >= 1 ? "text-pass" : value > 0 ? "text-warn" : "text-fail",
      )}
    >
      {formatScore(value)}
    </TableCell>
  );
}

const MOVE_BADGE: Record<TaskMove, { label: string; className: string; icon: typeof Minus }> = {
  gained: { label: "gained", className: "border-pass/40 bg-pass/12 text-pass", icon: ArrowUpRight },
  lost: { label: "lost", className: "border-fail/40 bg-fail/12 text-fail", icon: ArrowDownRight },
  "still-pass": { label: "still pass", className: "border-border text-muted-foreground", icon: Minus },
  "still-fail": { label: "still fail", className: "border-border text-muted-foreground", icon: Minus },
  "partial-moved": { label: "partial", className: "border-warn/40 bg-warn/12 text-warn", icon: Minus },
  unchanged: { label: "unchanged", className: "border-border text-muted-foreground", icon: Minus },
  unmeasured: { label: "unmeasured", className: "border-dashed border-border text-muted-foreground", icon: Minus },
};

function MoveBadge({ move }: { move: TaskMove }) {
  const config = MOVE_BADGE[move];
  const Icon = config.icon;
  return (
    <Badge variant="outline" className={cn("gap-1", config.className)}>
      <Icon className="h-3 w-3" />
      {config.label}
    </Badge>
  );
}

function DetailLine({ side, detail }: { side: "L" | "R"; detail: string | null }) {
  return (
    <div className="flex items-start gap-1.5">
      <span className="mt-px w-3 shrink-0 font-mono text-2xs text-muted-foreground">{side}</span>
      <span
        className="truncate text-2xs text-muted-foreground"
        title={detail ?? "no verdict detail recorded for this side"}
      >
        {detail ? firstLine(detail, 130) : <Value value={undefined} />}
      </span>
    </div>
  );
}
