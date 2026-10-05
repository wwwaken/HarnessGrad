import { Link } from "react-router-dom";
import { GitCompareArrows, ShieldQuestion } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { CopyButton } from "@/components/common/copy-button";
import { PageHeader } from "@/components/common/section";
import { Stat } from "@/components/common/stat";
import { Value } from "@/components/common/presence-value";
import { formatDuration, formatScore } from "@/lib/format";
import { badgeFor, type BadgeTone } from "@/logic/certify";
import type { CurveView } from "@/logic/curve";
import type { CertifyResult, RunBundle } from "@/types";

const TONE_VARIANT: Record<BadgeTone, "pass" | "info" | "warn" | "fail" | "muted"> = {
  pass: "pass",
  info: "info",
  warn: "warn",
  fail: "fail",
  muted: "muted",
};

/**
 * The Run detail header: identity first, then the four numbers, then the certification
 * badge with its reasons attached.
 *
 * The badge sits in the header rather than at the bottom because it qualifies every number
 * below it. "certified" and "valid, not certified" are both quotable; "invalid" is not, and
 * the header says which one this is before a reader has read a single score.
 */
export function RunHeader({
  bundle,
  view,
  certify,
}: {
  bundle: RunBundle;
  view: CurveView;
  /**
   * The run's `certify()` result. Passed in from the runs index, which is the only place
   * that reads the whole run directory the way `certify()` does; the bundle alone cannot
   * tell "valid" from "not certified" without re-implementing that read.
   */
  certify: CertifyResult | null;
}) {
  const badge = badgeFor(certify);
  const last = view.points[view.points.length - 1] ?? null;
  const meta = bundle.meta;

  return (
    <div className="space-y-3">
      <PageHeader
        title={
          <span className="flex items-center gap-2">
            <span className="font-mono text-base">{bundle.run_id}</span>
            <CopyButton value={bundle.run_id} label="Copy run id" />
          </span>
        }
        description={
          meta.dataset ? (
            <>
              <span className="font-mono">{meta.harness}</span> on{" "}
              <span className="font-mono">{meta.dataset}</span>
              {meta.method_entrypoint ? (
                <>
                  {" · method "}
                  <span className="font-mono">{shortenPath(meta.method_entrypoint)}</span>
                </>
              ) : null}
            </>
          ) : (
            "run_meta.json is missing or unreadable"
          )
        }
        meta={
          <>
            <Tooltip>
              <TooltipTrigger asChild>
                <Badge variant={TONE_VARIANT[badge.tone]} className="cursor-help">
                  {badge.label}
                </Badge>
              </TooltipTrigger>
              <TooltipContent className="max-w-md space-y-1">
                <p>{badge.explanation}</p>
                {badge.problems.slice(0, 4).map((p) => (
                  <p key={p} className="text-2xs text-fail">
                    {p}
                  </p>
                ))}
                {badge.certificationNote ? (
                  <p className="text-2xs text-muted-foreground">{badge.certificationNote}</p>
                ) : null}
              </TooltipContent>
            </Tooltip>
            <Badge variant="muted">
              <Value value={meta.agent_model} fieldName="agent_model" />
            </Badge>
            {meta.improver ? (
              <Badge variant="muted">
                improver {typeof meta.improver === "string" ? meta.improver : meta.improver.name}
              </Badge>
            ) : (
              <Badge variant="muted">
                <ShieldQuestion className="h-3 w-3" />
                no improver recorded
              </Badge>
            )}
          </>
        }
        actions={
          <Button variant="outline" size="sm" asChild>
            <Link to={`/compare?left=${encodeURIComponent(bundle.run_id)}`}>
              <GitCompareArrows className="h-3.5 w-3.5" />
              Compare
            </Link>
          </Button>
        }
      />

      <div className="grid grid-cols-2 gap-2 md:grid-cols-4 xl:grid-cols-6">
        <Stat
          label="Last score"
          value={formatScore(last?.score ?? null)}
          tone={badge.level === "invalid" || badge.level === "tampered" ? "fail" : "neutral"}
          hint={
            last
              ? `round ${last.round} · ${last.passedCount ?? "—"}/${last.scoredCount} tasks passing`
              : "no points"
          }
        />
        <Stat
          label="test_rate"
          value={
            last?.testRate === undefined ? (
              <Value value={undefined} fieldName="test_rate" />
            ) : (
              formatScore(last.testRate)
            )
          }
          tone="info"
          hint={
            last?.testRate === undefined
              ? "absent — every point predates stage 0 (2026-10-05)"
              : last.testRate === null
                ? "null — the checks reported no per-test tally"
                : `mean over ${last.testRateNTasks ?? "?"} task(s) that reported a tally`
          }
        />
        <Stat
          label="Rounds"
          value={view.points.length}
          hint={view.points.length ? `0 – ${view.points[view.points.length - 1]?.round}` : "—"}
        />
        <Stat
          label="Score lift"
          value={view.scoreLift === null ? "—" : formatScore(view.scoreLift)}
          tone={view.scoreLift === null ? "neutral" : view.scoreLift > 0 ? "pass" : view.scoreLift < 0 ? "fail" : "neutral"}
          hint="last − first, over the rounds that carry a number"
        />
        <Stat
          label="test_rate lift"
          value={view.testRateLift === null ? "—" : formatScore(view.testRateLift)}
          tone={
            view.testRateLift === null
              ? "neutral"
              : view.testRateLift > 0
                ? "pass"
                : view.testRateLift < 0
                  ? "fail"
                  : "neutral"
          }
          hint="the finer signal: it can move while score does not"
        />
        <Stat
          label="Wall clock"
          value={formatDuration(meta.wall_clock_s ?? null)}
          hint={meta.jobs ? `${meta.jobs} job(s)` : undefined}
        />
      </div>
    </div>
  );
}

function shortenPath(path: string): string {
  const parts = path.split("/");
  return parts.length > 3 ? `…/${parts.slice(-2).join("/")}` : path;
}
