import { CheckCircle2, CircleSlash, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Field, Value } from "@/components/common/presence-value";
import { formatScore } from "@/lib/format";
import type { Verdict } from "@/types";

/**
 * One task's verdict: `passed`, `score`, the `tests` tally and the full `detail`.
 *
 * The `detail` is the check's own sentence and is shown whole — not truncated — because it is
 * the difference between `reward 0` and *"test_layout_file: File /app/resources/patch_files/
 * default.html is not in the correct state"*. `verdict["tests"]` is the machine-readable form
 * of the same fact and is displayed as a tally with its denominator made explicit
 * (`passed / (passed + failed)`), since a skipped test was not measured and must not be
 * counted as a failure.
 *
 * `harness` (the harness's own exit code and stderr) is separated from the verifier's verdict
 * on purpose: "the harness failed this task" and "the harness ran and the artifact did not
 * pass" are different claims, and only one of them is about the method.
 */
export function VerdictPanel({
  verdict,
  problems,
}: {
  verdict: Verdict | null;
  problems: string[];
}) {
  if (!verdict) {
    return (
      <div className="space-y-2 rounded-lg border border-dashed border-border p-3">
        <div className="flex items-center gap-2 text-xs font-medium text-warn">
          <CircleSlash className="h-3.5 w-3.5" />
          No verdict for this task
        </div>
        {problems.map((p) => (
          <p key={p} className="text-2xs text-muted-foreground">
            {p}
          </p>
        ))}
        <p className="text-2xs text-muted-foreground">
          A missing verdict is absence, not a failure: the task was not scored in this round, or
          it is not part of this run&apos;s sampling.
        </p>
      </div>
    );
  }

  const tally = verdict.tests ?? null;
  const ran = tally ? tally.passed + tally.failed : null;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        {verdict.passed ? (
          <Badge variant="pass" className="gap-1">
            <CheckCircle2 className="h-3 w-3" />
            passed
          </Badge>
        ) : (
          <Badge variant="fail" className="gap-1">
            <XCircle className="h-3 w-3" />
            failed
          </Badge>
        )}
        <Badge variant="muted">kind {verdict.kind}</Badge>
        <Badge variant="muted">round {verdict.round}</Badge>
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-4">
        <Field label="Task">
          <span className="font-mono">{verdict.task_id}</span>
        </Field>
        <Field label="Score">
          <span className="tabular">{formatScore(verdict.score)}</span>
        </Field>
        <Field
          label="Tests"
          hint="passed / (passed + failed) — skipped tests were not measured"
        >
          {tally ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="tabular cursor-help">
                  {tally.passed}
                  <span className="text-muted-foreground">/{ran}</span>
                  {tally.skipped ? (
                    <span className="text-muted-foreground"> (+{tally.skipped} skipped)</span>
                  ) : null}
                </span>
              </TooltipTrigger>
              <TooltipContent>
                <pre className="font-mono text-2xs">{JSON.stringify(tally, null, 2)}</pre>
              </TooltipContent>
            </Tooltip>
          ) : (
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="cursor-help text-muted-foreground/70">no tally</span>
              </TooltipTrigger>
              <TooltipContent className="max-w-xs">
                this check reported no machine-readable per-test tally. That is not the same as
                zero tests passing — `eval/runner.py:test_rate_of` returns `None` here, not 0.
              </TooltipContent>
            </Tooltip>
          )}
        </Field>
        <Field label="Harness exit code" hint="the harness's own exit, separate from the verifier's verdict">
          {verdict.harness ? (
            <Value value={verdict.harness.exit_code ?? null} />
          ) : (
            <Value value={undefined} />
          )}
        </Field>
      </div>

      {tally ? (
        <div className="space-y-1">
          <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
            <span
              className="block h-full bg-pass"
              style={{ width: `${ran ? (tally.passed / ran) * 100 : 0}%` }}
            />
          </div>
          <p className="text-2xs text-muted-foreground">
            {tally.passed} passed, {tally.failed} failed
            {tally.skipped ? `, ${tally.skipped} skipped (not counted in the denominator)` : ""}.
            A binary `score` of {formatScore(verdict.score)} and a test rate of{" "}
            {ran ? (tally.passed / ran).toFixed(3) : "—"} are different facts about the same
            artifact.
          </p>
        </div>
      ) : null}

      <Separator />

      <div className="space-y-1">
        <div className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
          detail — the check&apos;s own sentence
        </div>
        <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap break-words rounded-md border border-border bg-muted/30 px-2.5 py-2 font-mono text-2xs leading-relaxed">
          {verdict.detail || "(empty)"}
        </pre>
      </div>

      {verdict.harness?.stderr ? (
        <div className="space-y-1">
          <div className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
            harness stderr
          </div>
          <pre className="max-h-[240px] overflow-auto whitespace-pre-wrap break-words rounded-md border border-fail/30 bg-fail/5 px-2.5 py-2 font-mono text-2xs">
            {verdict.harness.stderr}
          </pre>
        </div>
      ) : null}
    </div>
  );
}
