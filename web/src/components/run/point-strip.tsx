import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Value } from "@/components/common/presence-value";
import { formatPercent, formatScore, shortSha } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { CurvePointView } from "@/logic/curve";

/**
 * One card per measured state.
 *
 * The strip exists to make the per-round *set* of passing tasks visible next to the score,
 * because that is where the platform's own history loses people: `runs/ds-dgm` reads
 * `0.1 → 0.1 → 0.1`, and only the passing-task count shows that round 1 lost
 * `cobol-modernization` and gained `fix-git`. A round with a point-level problem (a claimed
 * number, a startup failure, a tamper record) is marked here rather than buried in a JSON
 * blob.
 */
export function PointStrip({
  points,
  selectedRound,
  onSelect,
}: {
  points: CurvePointView[];
  selectedRound: number | null;
  onSelect: (round: number) => void;
}) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1">
      {points.map((point) => {
        const active = selectedRound === point.round;
        return (
          <button
            key={point.round}
            type="button"
            onClick={() => onSelect(point.round)}
            className={cn(
              "min-w-[168px] shrink-0 rounded-lg border bg-card p-2.5 text-left transition-colors",
              active ? "border-ring ring-1 ring-ring" : "border-border hover:border-muted-foreground/40",
            )}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
                Round {point.round}
              </span>
              <span className="flex items-center gap-1">
                {point.isKept ? (
                  <Badge variant="pass" title="the method kept this state">
                    kept
                  </Badge>
                ) : null}
                {point.problems.length ? (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Badge variant="fail">{point.problems.length} problem(s)</Badge>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-md">
                      <ul className="list-disc space-y-0.5 pl-4">
                        {point.problems.map((p) => (
                          <li key={p}>{p}</li>
                        ))}
                      </ul>
                    </TooltipContent>
                  </Tooltip>
                ) : null}
              </span>
            </div>
            <div className="mt-1.5 flex items-baseline gap-1.5">
              <span className="text-lg font-semibold tabular leading-none">
                {formatScore(point.score)}
              </span>
              <span className="text-2xs text-muted-foreground">score</span>
            </div>
            <div className="mt-1 space-y-0.5 text-2xs text-muted-foreground">
              <div className="flex items-center justify-between gap-2">
                <span>test_rate</span>
                <span className="tabular text-foreground">
                  {point.testRate === undefined ? (
                    <Value value={undefined} fieldName="test_rate" />
                  ) : point.testRate === null ? (
                    <Value value={null} fieldName="test_rate" />
                  ) : (
                    `${formatScore(point.testRate)} (${formatPercent(point.testRate)})`
                  )}
                </span>
              </div>
              <div className="flex items-center justify-between gap-2">
                <span>tasks passing</span>
                <span className="tabular text-foreground">
                  {point.passedCount ?? "—"}/{point.scoredCount}
                </span>
              </div>
              <div className="flex items-center justify-between gap-2">
                <span>harness</span>
                <span className="font-mono text-foreground">{shortSha(point.harnessSha)}</span>
              </div>
            </div>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-2xs text-muted-foreground">{point.scoreKind}</span>
              <span className="text-2xs text-muted-foreground">
                {point.timestampUtc ? point.timestampUtc.slice(0, 10) : ""}
              </span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
