import type { ReactNode } from "react";
import { AlertTriangle, ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Stat } from "@/components/common/stat";
import { formatDelta } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { RunComparison, TaskComparison, TaskMove } from "@/logic/compare";

/**
 * The headline: what moved between the two selected states.
 *
 * This panel is deliberately above the chart on the Compare screen, because the chart is
 * where a flat score hides a changed task set. Three things are stated in order:
 *
 * 1. the sentence — `score unchanged, but 2 task(s) moved`;
 * 2. the four counts, so absent movement is as visible as movement;
 * 3. the movement strip — one chip per task in task-id order, so "which tasks moved" is
 *    answerable without reading a table.
 *
 * When the score is flat and tasks moved, the alert says so in words. That is the platform's
 * own recurring case (`runs/ds-dgm`: `0.1 → 0.1` while `cobol-modernization` stopped passing
 * and `fix-git` started), and a UI that only drew the score would have hidden it.
 */
export function FlipSummary({ comparison }: { comparison: RunComparison }) {
  const { summary, left, right } = comparison;
  return (
    <div className="space-y-3">
      {summary.maskedByScore ? (
        <Alert variant="warn">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Total score unchanged — the passing set is not</AlertTitle>
          <AlertDescription>
            Both states score {left?.score?.toFixed(3) ?? "—"}, but {summary.gained} task(s)
            started passing and {summary.lost} stopped. Quoting the total would report no
            change and lose both facts.
          </AlertDescription>
        </Alert>
      ) : null}

      <div className="grid grid-cols-2 gap-2 md:grid-cols-4 xl:grid-cols-6">
        <Stat
          label="Score"
          value={`${left?.score?.toFixed(3) ?? "—"} → ${right?.score?.toFixed(3) ?? "—"}`}
          tone={
            summary.scoreDelta === null
              ? "neutral"
              : summary.scoreDelta > 0
                ? "pass"
                : summary.scoreDelta < 0
                  ? "fail"
                  : "neutral"
          }
          hint={`Δ ${formatDelta(summary.scoreDelta)}`}
        />
        <Stat
          label="test_rate"
          value={`${left?.testRate?.toFixed(3) ?? "—"} → ${right?.testRate?.toFixed(3) ?? "—"}`}
          tone="info"
          hint={
            summary.testRateDelta === null
              ? "not measurable on both sides"
              : `Δ ${formatDelta(summary.testRateDelta)} — the finer check tally`
          }
        />
        <Stat
          label="Gained"
          value={summary.gained}
          tone={summary.gained ? "pass" : "neutral"}
          hint="fail → pass"
        />
        <Stat
          label="Lost"
          value={summary.lost}
          tone={summary.lost ? "fail" : "neutral"}
          hint="pass → fail"
        />
        <Stat
          label="Still passing"
          value={summary.stillPass}
          hint="pass in both states"
        />
        <Stat
          label="Unmeasured"
          value={summary.unmeasured}
          tone={summary.unmeasured ? "warn" : "neutral"}
          hint="absent or unscored on one side — not a failure"
        />
      </div>

      <div className="space-y-1.5">
        <div className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
          Movement by task
        </div>
        <div className="flex flex-wrap gap-1">
          {comparison.tasks.map((task) => (
            <MoveChip key={task.taskId} task={task} />
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-3 pt-1 text-2xs text-muted-foreground">
          <Legend tone="gain" icon={<ArrowUpRight className="h-3 w-3" />} label="gained (fail → pass)" />
          <Legend tone="loss" icon={<ArrowDownRight className="h-3 w-3" />} label="lost (pass → fail)" />
          <Legend tone="same" icon={<Minus className="h-3 w-3" />} label="unchanged" />
          <Legend tone="unmeasured" icon={<Minus className="h-3 w-3" />} label="unmeasured" />
        </div>
      </div>
    </div>
  );
}

function Legend({ tone, icon, label }: { tone: string; icon: ReactNode; label: string }) {
  return (
    <span className="inline-flex items-center gap-1">
      <span className={cn("inline-flex", tone === "gain" && "text-pass", tone === "loss" && "text-fail")}>
        {icon}
      </span>
      {label}
    </span>
  );
}

const MOVE_STYLE: Record<TaskMove, { className: string; title: string }> = {
  gained: { className: "border-pass/40 bg-pass/12 text-pass", title: "fail → pass" },
  lost: { className: "border-fail/40 bg-fail/12 text-fail", title: "pass → fail" },
  "still-pass": { className: "border-border bg-muted/60 text-foreground", title: "pass in both" },
  "still-fail": { className: "border-border bg-transparent text-muted-foreground", title: "fail in both" },
  "partial-moved": { className: "border-warn/40 bg-warn/12 text-warn", title: "partial score moved" },
  unchanged: { className: "border-border bg-transparent text-muted-foreground", title: "unchanged" },
  unmeasured: {
    className: "border-dashed border-border bg-transparent text-muted-foreground",
    title: "unmeasured on one side",
  },
};

function MoveChip({ task }: { task: TaskComparison }) {
  const style = MOVE_STYLE[task.move];
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span
          className={cn(
            "inline-flex max-w-[220px] items-center gap-1 truncate rounded border px-1.5 py-0.5 font-mono text-2xs",
            style.className,
          )}
        >
          {task.move === "gained" ? <ArrowUpRight className="h-3 w-3 shrink-0" /> : null}
          {task.move === "lost" ? <ArrowDownRight className="h-3 w-3 shrink-0" /> : null}
          <span className="truncate">{task.taskId}</span>
        </span>
      </TooltipTrigger>
      <TooltipContent className="space-y-0.5">
        <div>{style.title}</div>
        <div className="tabular">
          score {task.leftScore ?? "—"} → {task.rightScore ?? "—"}
        </div>
        <div className="tabular">
          test_rate {task.leftTestRate ?? "—"} → {task.rightTestRate ?? "—"}
        </div>
      </TooltipContent>
    </Tooltip>
  );
}
