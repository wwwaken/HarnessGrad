import { useState, type ReactNode } from "react";
import {
  Ban,
  CheckCircle2,
  ClipboardCopy,
  Copy,
  Repeat,
  Scissors,
  Send,
  Terminal,
  TriangleAlert,
  User,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { EmptyState } from "@/components/common/states";
import { useT } from "@/i18n";
import { formatDuration } from "@/lib/format";
import { buildTimeline, traceSummary, type TimelineItem } from "@/logic/trace";
import { cn } from "@/lib/utils";
import type { JsonValue, TraceEvent } from "@/types";

/**
 * A task's trace, as a timeline of steps rather than raw JSONL.
 *
 * The reader's question is "why is this number what it is", and the trace is the only place
 * that can answer it: whether the harness kept re-issuing the same command, whether it was
 * nudged to finish, whether a submit was rejected, or whether a command failed with output
 * the model then ignored. Each of those is a distinct event kind in the JSONL and a distinct
 * mark here.
 *
 * Long text is collapsed rather than truncated: the model's reply and a command's output are
 * the evidence, so they are one click away and never silently cut. An `output_clipped` event
 * is shown as the harness's own decision to bound the output, with both counts.
 */
export function TraceTimeline({ events }: { events: TraceEvent[] }) {
  const t = useT();
  const timeline = buildTimeline(events);
  const summary = traceSummary(timeline);

  if (!events.length) {
    return (
      <EmptyState
        title={t("task.noTrace")}
        description={t("task.noTraceHint")}
      />
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 rounded-md border border-border bg-card px-3 py-2 text-2xs">
        <span className="font-medium">{t("task.summarySteps", { n: summary.steps })}</span>
        <span className="text-muted-foreground">
          {t("task.summaryCommands", { n: summary.commands })}
        </span>
        {summary.failedCommands ? (
          <span className="text-fail">
            {t("task.summaryFailedExits", { n: summary.failedCommands })}
          </span>
        ) : null}
        {summary.nudges ? (
          <span className="text-warn">{t("task.summaryNudges", { n: summary.nudges })}</span>
        ) : null}
        <span className="text-muted-foreground">
          {t("task.summaryModel", { time: formatDuration(summary.modelMs / 1000) })}
        </span>
        <span className="text-muted-foreground">
          {t("task.summaryExec", { time: formatDuration(summary.commandMs / 1000) })}
        </span>
        {timeline.wallClockS !== null ? (
          <span className="text-muted-foreground">
            {t("task.summaryWall", { time: formatDuration(timeline.wallClockS) })}
          </span>
        ) : null}
        <span className="ml-auto text-muted-foreground">
          {t("task.summaryEvents", { n: events.length })}
        </span>
      </div>

      {timeline.harnessConfig ? (
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-2xs text-muted-foreground">{t("task.harnessConfig")}</span>
          {Object.entries(timeline.harnessConfig).map(([key, value]) => (
            <Badge key={key} variant="muted" className="font-mono">
              {key}={JSON.stringify(value)}
            </Badge>
          ))}
        </div>
      ) : null}

      <ol className="relative space-y-3 border-l border-border pl-4">
        {timeline.steps.map((step) => (
          <li key={step.step} className="relative">
            <span
              className={cn(
                "absolute -left-[1.4rem] top-0.5 flex h-5 w-5 items-center justify-center rounded-full border text-2xs font-medium tabular",
                step.flagged
                  ? "border-fail/50 bg-fail/10 text-fail"
                  : "border-border bg-card text-muted-foreground",
              )}
            >
              {step.step}
            </span>
            <div className="space-y-1.5">
              <div className="flex flex-wrap items-center gap-2 text-2xs text-muted-foreground">
                <span className="font-medium text-foreground">
                  {t("task.stepLabel", { n: step.step })}
                </span>
                {step.modelMs ? (
                  <span>{t("task.summaryModel", { time: formatDuration(step.modelMs / 1000) })}</span>
                ) : null}
                {step.commandMs ? (
                  <span>{t("task.summaryExec", { time: formatDuration(step.commandMs / 1000) })}</span>
                ) : null}
                {step.exitCodes.some((code) => code !== 0) ? (
                  <span className="text-fail">
                    {t("task.exitsLabel", { codes: step.exitCodes.join(", ") })}
                  </span>
                ) : null}
              </div>
              {step.items.map((item, index) => (
                <TimelineItemView key={index} item={item} />
              ))}
            </div>
          </li>
        ))}
      </ol>

      {timeline.unpaced.length ? (
        <div className="space-y-1">
          <Separator />
          <p className="text-2xs text-muted-foreground">
            {t("task.unpacedEvents", { n: timeline.unpaced.length })}
          </p>
          <JsonBlock value={timeline.unpaced} />
        </div>
      ) : null}

      {timeline.usage ? (
        <div className="space-y-1">
          <Separator />
          <div className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
            {t("task.tokenUsage")}
          </div>
          <JsonBlock value={timeline.usage} />
        </div>
      ) : null}
    </div>
  );
}

function TimelineItemView({ item }: { item: TimelineItem }) {
  const t = useT();
  switch (item.kind) {
    case "model":
      return (
        <div className="rounded-md border border-border bg-card">
          <ItemHeader
            icon={<User className="h-3 w-3" />}
            label={t("task.modelReply")}
            right={item.modelMs ? formatDuration(item.modelMs / 1000) : undefined}
          />
          <ExpandableText text={item.reply} className="font-mono text-2xs" collapsedLines={6} />
        </div>
      );
    case "command":
      return (
        <div className="rounded-md border border-border bg-card">
          <ItemHeader
            icon={<Terminal className="h-3 w-3" />}
            label={t("task.commandLabel")}
            right={
              <span className="flex items-center gap-2">
                {item.commandMs ? <span>{formatDuration(item.commandMs / 1000)}</span> : null}
                <Badge variant={item.exit === 0 ? "pass" : item.exit === null ? "muted" : "fail"}>
                  {t("task.exitBadge", { code: item.exit ?? "?" })}
                </Badge>
              </span>
            }
          />
          <pre className="overflow-x-auto whitespace-pre-wrap break-all border-t border-border bg-muted/30 px-2 py-1.5 font-mono text-2xs">
            {item.command}
          </pre>
          {item.output ? (
            <ExpandableText text={item.output} className="border-t border-border font-mono text-2xs" collapsedLines={10} />
          ) : (
            <div className="border-t border-border px-2 py-1 text-2xs text-muted-foreground">
              {t("task.noOutput")}
            </div>
          )}
        </div>
      );
    case "clipped":
      return (
        <div className="flex items-center gap-2 rounded-md border border-warn/30 bg-warn/5 px-2 py-1 text-2xs">
          <Scissors className="h-3 w-3 text-warn" />
          <span>
            {t("task.clipped", {
              shown: describeCount(item.shown),
              original: describeCount(item.original),
            })}
          </span>
        </div>
      );
    case "nudge":
      return (
        <div className="flex items-start gap-2 rounded-md border border-info/30 bg-info/5 px-2 py-1 text-2xs">
          {item.nudge === "finish" ? (
            <CheckCircle2 className="mt-0.5 h-3 w-3 shrink-0 text-info" />
          ) : (
            <Repeat className="mt-0.5 h-3 w-3 shrink-0 text-info" />
          )}
          <span>
            <span className="font-medium">{t("task.nudgeLabel", { kind: item.nudge })}</span>{" "}
            <span className="text-muted-foreground">{stringify(item.value)}</span>
          </span>
        </div>
      );
    case "submit":
      return (
        <div
          className={cn(
            "flex items-start gap-2 rounded-md border px-2 py-1 text-2xs",
            item.event === "submitted"
              ? "border-pass/30 bg-pass/5"
              : item.event === "rejected"
                ? "border-fail/30 bg-fail/5"
                : "border-warn/30 bg-warn/5",
          )}
        >
          {item.event === "submitted" ? (
            <Send className="mt-0.5 h-3 w-3 shrink-0 text-pass" />
          ) : item.event === "rejected" ? (
            <Ban className="mt-0.5 h-3 w-3 shrink-0 text-fail" />
          ) : (
            <TriangleAlert className="mt-0.5 h-3 w-3 shrink-0 text-warn" />
          )}
          <span>
            <span className="font-medium">
              {item.event === "submitted"
                ? t("task.submitted")
                : item.event === "rejected"
                  ? t("task.submitRejected")
                  : t("task.submittedMissing")}
            </span>{" "}
            <span className="text-muted-foreground">{stringify(item.value)}</span>
          </span>
        </div>
      );
    case "duplicate":
      return (
        <div className="flex items-start gap-2 rounded-md border border-warn/30 bg-warn/5 px-2 py-1 text-2xs">
          <Copy className="mt-0.5 h-3 w-3 shrink-0 text-warn" />
          <span>
            <span className="font-medium">{t("task.duplicateKeys")}</span>{" "}
            <span className="text-muted-foreground">{stringify(item.keys)}</span>
          </span>
        </div>
      );
    case "unknown":
      return (
        <div className="rounded-md border border-dashed border-border px-2 py-1">
          <div className="flex items-center gap-1.5 text-2xs text-muted-foreground">
            <ClipboardCopy className="h-3 w-3" />
            {t("task.unrecognisedEvent")}
          </div>
          <JsonBlock value={item.event} />
        </div>
      );
  }
}

function ItemHeader({
  icon,
  label,
  right,
}: {
  icon: ReactNode;
  label: string;
  right?: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between gap-2 px-2 py-1">
      <span className="flex items-center gap-1.5 text-2xs font-medium">
        {icon}
        {label}
      </span>
      {right ? <span className="text-2xs text-muted-foreground">{right}</span> : null}
    </div>
  );
}

/** Collapsed, never truncated: the evidence stays one click away. */
function ExpandableText({
  text,
  className,
  collapsedLines = 8,
}: {
  text: string;
  className?: string;
  collapsedLines?: number;
}) {
  const t = useT();
  const [expanded, setExpanded] = useState(false);
  const lines = text.split("\n");
  const long = lines.length > collapsedLines || text.length > 2000;
  const shown = expanded ? text : lines.slice(0, collapsedLines).join("\n");
  return (
    <div>
      <pre
        className={cn(
          "overflow-x-auto whitespace-pre-wrap break-words px-2 py-1.5",
          !expanded && long && "max-h-[220px] overflow-hidden",
          className,
        )}
      >
        {shown}
        {!expanded && long ? "\n…" : ""}
      </pre>
      {long ? (
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="border-t border-border px-2 py-0.5 text-2xs text-muted-foreground underline-offset-2 hover:underline"
        >
          {expanded
            ? t("task.collapse")
            : t("task.showAll", { lines: lines.length, chars: text.length })}
        </button>
      ) : null}
    </div>
  );
}

function JsonBlock({ value }: { value: unknown }) {
  return (
    <pre className="overflow-x-auto whitespace-pre-wrap break-all rounded-md border border-border bg-muted/30 px-2 py-1.5 font-mono text-2xs">
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}

function stringify(value: JsonValue): string {
  if (typeof value === "string") return value;
  return JSON.stringify(value);
}

function describeCount(value: JsonValue): string {
  if (typeof value === "number") return `${value}`;
  if (typeof value === "string") return value;
  return JSON.stringify(value);
}
