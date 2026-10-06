import { useMemo } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { EmptyState } from "@/components/common/states";
import { formatPercent, formatScore } from "@/lib/format";
import { useT } from "@/i18n";
import { cn } from "@/lib/utils";
import type { CurveView } from "@/logic/curve";

/**
 * The run's curve: **two series**, because one cannot resolve the effect.
 *
 * `docs/refactor_plan.md` stage 0 records why. A `command` check reports "4 passed 1 failed"
 * and the reward file collapses that to 0.0; a harness edit took `large-scale-text-editing`
 * to 3 of 5 — also 0.0. On the score axis alone the edit did nothing. `test_rate` is the
 * finer signal: the check's own test tally, averaged over the tasks that reported one.
 *
 * Three rendering decisions follow from that, and none is cosmetic:
 *
 * * the two series have **separate axes**, so "score 0.1" and "test_rate 0.48" are each
 *   read on their own scale rather than one flattening the other;
 * * a round whose `test_rate` is **absent or null** leaves a **gap**. `connectNulls` is
 *   false on purpose: joining across a gap would draw a measurement that was never taken;
 * * the score's 95% interval is drawn as a band, because a single point estimate over ten
 *   binary tasks has a noise band of roughly ±0.1 — the same size as the effects being
 *   looked for.
 *
 * The chart library is Recharts. See `web/README.md` for why, and why not ECharts.
 */
export function CurveChart({
  view,
  height = 260,
  onSelectRound,
  selectedRound,
}: {
  view: CurveView;
  height?: number;
  onSelectRound?: (round: number) => void;
  selectedRound?: number | null;
}) {
  const t = useT();
  const data = useMemo(
    () =>
      view.points.map((point) => ({
        round: `R${point.round}`,
        roundNumber: point.round,
        score: point.score ?? null,
        testRate: point.testRate === undefined || point.testRate === null ? null : point.testRate,
        band:
          point.scoreLow !== null && point.scoreHigh !== null
            ? [point.scoreLow, point.scoreHigh]
            : null,
      })),
    [view.points],
  );

  if (!data.length) {
    return (
      <EmptyState
        title={t("run.chart.empty")}
        description={t("run.chart.emptyHint")}
      />
    );
  }

  return (
    <div className="space-y-2">
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={data}
            margin={{ top: 8, right: 12, bottom: 4, left: -12 }}
            onClick={(state) => {
              const label = (state as { activeLabel?: string } | null)?.activeLabel;
              if (!label || !onSelectRound) return;
              const round = Number(label.replace("R", ""));
              if (Number.isFinite(round)) onSelectRound(round);
            }}
          >
            <CartesianGrid stroke="hsl(var(--chart-grid))" strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="round"
              stroke="hsl(var(--chart-axis))"
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "hsl(var(--chart-grid))" }}
            />
            <YAxis
              yAxisId="score"
              domain={[0, 1]}
              stroke="hsl(var(--chart-score))"
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: number) => v.toFixed(1)}
            />
            <YAxis
              yAxisId="rate"
              orientation="right"
              domain={[0, 1]}
              stroke="hsl(var(--chart-testrate))"
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: number) => v.toFixed(1)}
            />
            <Tooltip content={<CurveTooltip />} cursor={{ stroke: "hsl(var(--chart-axis))", strokeDasharray: "3 3" }} />
            <Legend
              verticalAlign="top"
              height={24}
              formatter={(value: string) => (
                <span className="text-2xs text-muted-foreground">{value}</span>
              )}
            />
            <Area
              yAxisId="score"
              type="monotone"
              dataKey="band"
              name={t("run.chart.seriesBand")}
              stroke="none"
              fill="hsl(var(--chart-band))"
              fillOpacity={0.7}
              isAnimationActive={false}
            />
            <Line
              yAxisId="score"
              type="monotone"
              dataKey="score"
              name={t("run.chart.seriesScore")}
              stroke="hsl(var(--chart-score))"
              strokeWidth={2}
              dot={{ r: 3, strokeWidth: 0, fill: "hsl(var(--chart-score))" }}
              activeDot={{ r: 4 }}
              isAnimationActive={false}
            />
            <Line
              yAxisId="rate"
              type="monotone"
              dataKey="testRate"
              name={t("run.chart.seriesTestRate")}
              stroke="hsl(var(--chart-testrate))"
              strokeWidth={2}
              strokeDasharray="4 3"
              connectNulls={false}
              dot={{ r: 3, strokeWidth: 0, fill: "hsl(var(--chart-testrate))" }}
              activeDot={{ r: 4 }}
              isAnimationActive={false}
            />
            {view.keptRound !== null ? (
              <ReferenceLine
                yAxisId="score"
                x={`R${view.keptRound}`}
                stroke="hsl(var(--chart-axis))"
                strokeDasharray="2 2"
                label={{ value: t("run.chart.kept"), position: "insideTopRight", fontSize: 10, fill: "hsl(var(--chart-axis))" }}
              />
            ) : null}
            {selectedRound !== undefined && selectedRound !== null ? (
              <ReferenceLine
                yAxisId="score"
                x={`R${selectedRound}`}
                stroke="hsl(var(--chart-axis))"
                strokeOpacity={0.5}
              />
            ) : null}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <CoverageNotes view={view} />
    </div>
  );
}

function CoverageNotes({ view }: { view: CurveView }) {
  const t = useT();
  const notes = [view.scoreCoverage.caveat, view.testRateCoverage.caveat].filter(
    (n): n is NonNullable<typeof n> => Boolean(n),
  );
  if (!notes.length && !view.scoreFlatButTasksMoved) {
    return (
      <p className="text-2xs text-muted-foreground">
        {t("run.chart.coverageAll", { n: view.points.length })}
      </p>
    );
  }
  return (
    <div className="space-y-1">
      {notes.map((note) => (
        <p key={note.key + String(note.params.series)} className="text-2xs text-warn">
          {t(note.key, note.params)}
          {note.extra ? ` — ${t(note.extra)}` : ""}
        </p>
      ))}
      {view.scoreFlatButTasksMoved ? (
        <p className="text-2xs font-medium text-warn">{t("run.chart.flatScore")}</p>
      ) : null}
    </div>
  );
}

interface TooltipDatum {
  payload?: ChartDatum;
}

interface ChartDatum {
  round: string;
  roundNumber: number;
  score: number | null;
  testRate: number | null;
  band: [number, number] | null;
}

/** A tooltip that reports absence explicitly instead of printing `0`. */
function CurveTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: ReadonlyArray<TooltipDatum>;
}) {
  const t = useT();
  if (!active || !payload?.length) return null;
  const datum = payload[0]?.payload;
  if (!datum) return null;
  return (
    <div className="rounded-md border border-border bg-popover px-2.5 py-2 text-2xs shadow-md">
      <div className="font-medium">{t("run.chart.tooltipRound", { round: datum.roundNumber })}</div>
      <div className="mt-1 grid grid-cols-[auto_auto] gap-x-3 gap-y-0.5">
        <span className="text-muted-foreground">score</span>
        <span className="tabular text-right">{formatScore(datum.score)}</span>
        <span className="text-muted-foreground">{t("run.chart.tooltipInterval")}</span>
        <span className={cn("tabular text-right", !datum.band && "text-muted-foreground/60")}>
          {datum.band ? `${formatScore(datum.band[0])} … ${formatScore(datum.band[1])}` : "—"}
        </span>
        <span className="text-muted-foreground">test_rate</span>
        <span className={cn("tabular text-right", datum.testRate === null && "text-muted-foreground/60")}>
          {datum.testRate === null
            ? t("run.chart.tooltipNotRecorded")
            : `${formatScore(datum.testRate)} (${formatPercent(datum.testRate)})`}
        </span>
      </div>
    </div>
  );
}
