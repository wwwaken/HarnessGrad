import type { ReactNode } from "react";
import { AlertTriangle, ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Stat } from "@/components/common/stat";
import { useT } from "@/i18n";
import type { TranslationKey } from "@/i18n/en";
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
  const t = useT();
  const { summary, left, right } = comparison;
  return (
    <div className="space-y-3">
      {summary.maskedByScore ? (
        <Alert variant="warn">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>{t("compare.flatScoreTitle")}</AlertTitle>
          <AlertDescription>
            {t("compare.flatScoreBody", {
              score: left?.score?.toFixed(3) ?? "—",
              gained: summary.gained,
              lost: summary.lost,
            })}
          </AlertDescription>
        </Alert>
      ) : null}

      <div className="grid grid-cols-2 gap-2 md:grid-cols-4 xl:grid-cols-6">
        <Stat
          label={t("compare.scoreStat")}
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
          label={t("compare.testRate")}
          value={`${left?.testRate?.toFixed(3) ?? "—"} → ${right?.testRate?.toFixed(3) ?? "—"}`}
          tone="info"
          hint={
            summary.testRateDelta === null
              ? t("compare.testRateUnmeasurable")
              : t("compare.testRateHint", { delta: formatDelta(summary.testRateDelta) })
          }
        />
        <Stat
          label={t("compare.gained")}
          value={summary.gained}
          tone={summary.gained ? "pass" : "neutral"}
          hint={t("compare.failToPass")}
        />
        <Stat
          label={t("compare.lost")}
          value={summary.lost}
          tone={summary.lost ? "fail" : "neutral"}
          hint={t("compare.passToFail")}
        />
        <Stat
          label={t("compare.stillPassing")}
          value={summary.stillPass}
          hint={t("compare.passInBothStates")}
        />
        <Stat
          label={t("compare.unmeasured")}
          value={summary.unmeasured}
          tone={summary.unmeasured ? "warn" : "neutral"}
          hint={t("compare.unmeasuredHint")}
        />
      </div>

      <div className="space-y-1.5">
        <div className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
          {t("compare.movementByTask")}
        </div>
        <div className="flex flex-wrap gap-1">
          {comparison.tasks.map((task) => (
            <MoveChip key={task.taskId} task={task} />
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-3 pt-1 text-2xs text-muted-foreground">
          <Legend tone="gain" icon={<ArrowUpRight className="h-3 w-3" />} label={t("compare.legendGained")} />
          <Legend tone="loss" icon={<ArrowDownRight className="h-3 w-3" />} label={t("compare.legendLost")} />
          <Legend tone="same" icon={<Minus className="h-3 w-3" />} label={t("compare.legendUnchanged")} />
          <Legend tone="unmeasured" icon={<Minus className="h-3 w-3" />} label={t("compare.legendUnmeasured")} />
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

const MOVE_STYLE: Record<TaskMove, { className: string; title: TranslationKey }> = {
  gained: { className: "border-pass/40 bg-pass/12 text-pass", title: "compare.failToPass" },
  lost: { className: "border-fail/40 bg-fail/12 text-fail", title: "compare.passToFail" },
  "still-pass": { className: "border-border bg-muted/60 text-foreground", title: "compare.passInBoth" },
  "still-fail": { className: "border-border bg-transparent text-muted-foreground", title: "compare.failInBoth" },
  "partial-moved": { className: "border-warn/40 bg-warn/12 text-warn", title: "compare.partialMoved" },
  unchanged: { className: "border-border bg-transparent text-muted-foreground", title: "compare.unchanged" },
  unmeasured: {
    className: "border-dashed border-border bg-transparent text-muted-foreground",
    title: "compare.unmeasuredOneSide",
  },
};

function MoveChip({ task }: { task: TaskComparison }) {
  const t = useT();
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
        <div>{t(style.title)}</div>
        <div className="tabular">
          {t("compare.tooltipScore", { left: task.leftScore ?? "—", right: task.rightScore ?? "—" })}
        </div>
        <div className="tabular">
          {t("compare.tooltipTestRate", {
            left: task.leftTestRate ?? "—",
            right: task.rightTestRate ?? "—",
          })}
        </div>
      </TooltipContent>
    </Tooltip>
  );
}
