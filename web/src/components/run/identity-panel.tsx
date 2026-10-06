import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Field, Value } from "@/components/common/presence-value";
import { formatDuration, formatTokens } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { CurvePoint, RunMeta } from "@/types";

/**
 * "Why is this number what it is."
 *
 * `docs/refactor_references.md` §6.3 asks the UI to show the fields that *explain* a score,
 * not only the score: the two model roles, the `score_kind` (a `training` score "must never
 * be quoted as a result"), the pinned image digest, and the three cost budgets. It also asks
 * the UI to distinguish **absence from null from zero** — so every field goes through
 * `Value`/`Field`, and the cost panel never sums the budgets, because one number cannot tell
 * a thrifty harness from a lazy method.
 */
export function RunIdentityPanel({
  meta,
  point,
}: {
  /**
   * **`Partial`, because a run directory need not have a readable `run_meta.json`** -- the
   * API answers `{}` and sets `load_problems` rather than 404. Every field below was
   * already rendered through a guard or a `<Value>` that prints absent as an em dash; the
   * narrow type was claiming a contract the API does not make.
   */
  meta: Partial<RunMeta>;
  point: CurvePoint | null;
}) {
  const identity = point?.identity;
  const improver = identity?.improver;
  const harnessConfig = identity?.harness_config;
  const platform = meta.platform;
  const runtime = point?.env?.harness_runtime;

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-3 lg:grid-cols-4">
        <Field label="Run">{meta.run_id}</Field>
        <Field label="Round">
          <Value value={point?.round} />
        </Field>
        <Field
          label="Score kind"
          hint="a training score is inflated by construction and must never be quoted"
        >
          {point?.score_kind === "training" ? (
            <Badge variant="warn">training</Badge>
          ) : point?.score_kind ? (
            <Badge variant="info">{point.score_kind}</Badge>
          ) : (
            <Value value={undefined} />
          )}
        </Field>
        <Field label="Side" hint="which half of the split this point measured">
          <Value value={point?.side} />
        </Field>
        <Field label="Harness (meta)">
          <span className="font-mono">{meta.harness}</span>
        </Field>
        <Field label="Dataset">
          <span className="font-mono">{meta.dataset}</span>
        </Field>
        <Field label="Mode">
          <Value value={meta.mode} />
        </Field>
        <Field label="Trials" hint="`--trials > 1` records n_trials and score_std">
          <Value value={meta.trials ?? undefined} fieldName="n_trials" />
        </Field>
        <Field label="Harness name / version">
          <span className="font-mono">
            {identity?.harness_name ?? "—"} {identity?.harness_version ?? ""}
          </span>
        </Field>
        <Field label="Harness sha" hint="identity.harness_sha — which artifact this score belongs to">
          <span className="font-mono">{identity?.harness_sha ?? "—"}</span>
        </Field>
        <Field label="Run mode">
          <Value value={identity?.run_mode} />
        </Field>
        <Field label="Framework version">
          <Value value={identity?.framework_version} />
        </Field>
        <Field
          label="Agent model"
          hint="the model that solved the tasks; separate from the improver's model"
        >
          <span className="font-mono">{identity?.agent_model ?? "—"}</span>
        </Field>
        <Field label="Agent backend">
          <Value value={identity?.agent_backend} />
        </Field>
        <Field label="Agent model source" hint="`harness` or the platform's environment">
          <Value value={identity?.agent_model_source} />
        </Field>
        <Field label="Method">
          <Value value={identity?.method} />
        </Field>
        <Field label="Improver" hint="what the platform resolved, not what was asked for">
          {improver ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="cursor-help font-mono">
                  {improver.name ?? "?"}
                  {improver.model ? ` · ${improver.model}` : ""}
                </span>
              </TooltipTrigger>
              <TooltipContent className="space-y-0.5">
                <div>kind: {improver.kind ?? "—"}</div>
                <div>version: {improver.version || "—"}</div>
                <div>endpoint: {improver.base_url ?? "—"}</div>
                <div>
                  declaration modified: {improver.modified === undefined ? "—" : String(improver.modified)}
                </div>
              </TooltipContent>
            </Tooltip>
          ) : (
            <Value value={improver === null ? null : undefined} />
          )}
        </Field>
        <Field label="Skill sha">
          <span className="font-mono">{identity?.skill_sha?.slice(0, 12) ?? "—"}</span>
        </Field>
      </div>

      <Separator />

      <div className="grid gap-3 lg:grid-cols-3">
        <div className="space-y-2">
          <h3 className="text-2xs font-semibold uppercase tracking-wide text-muted-foreground">
            Harness config
          </h3>
          <div className="space-y-1">
            {harnessConfig && Object.keys(harnessConfig).length ? (
              Object.entries(harnessConfig).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between gap-3 text-2xs">
                  <span className="font-mono text-muted-foreground">{key}</span>
                  <span className="font-mono tabular">{JSON.stringify(value)}</span>
                </div>
              ))
            ) : (
              <p className="text-2xs text-muted-foreground">
                no `identity.harness_config` on this point
              </p>
            )}
          </div>
        </div>

        <div className="space-y-2">
          <h3 className="text-2xs font-semibold uppercase tracking-wide text-muted-foreground">
            Environment
          </h3>
          <div className="space-y-1 text-2xs">
            <Row label="kind" value={point?.env?.kind} />
            <Row label="placement" value={point?.env?.placement} />
            <Row label="network" value={point?.env?.network} />
            <Row
              label="image digest"
              value={point?.env?.image_digest}
              mono
              hint="per point, not per run: two points from different environments are different quantities"
            />
            <Row
              label="harness runtime"
              value={
                Array.isArray(runtime) && runtime.length
                  ? runtime
                      .map((r) => {
                        const record = r as { source?: string; python?: string };
                        return `${record.source ?? "?"}/py${record.python ?? "?"}`;
                      })
                      .join(", ")
                  : undefined
              }
            />
            <Row
              label="variants"
              value={
                typeof point?.env?.variants_count === "number"
                  ? point.env.variants_count
                  : undefined
              }
            />
            <Row
              label="seed"
              value={point?.env?.seed === null || point?.env?.seed === undefined ? undefined : String(point.env.seed)}
            />
          </div>
        </div>

        <div className="space-y-2">
          <h3 className="text-2xs font-semibold uppercase tracking-wide text-muted-foreground">
            Cost — three budgets, never summed
          </h3>
          <div className="space-y-1 text-2xs">
            <Row label="harness tokens" value={formatTokens(point?.cost?.harness_tokens)} />
            <Row label="harness model calls" value={point?.cost?.harness_model_calls} />
            <Row
              label="method generation tokens"
              value={formatTokens(point?.cost?.method_generation_tokens)}
            />
            <Row label="env generation tokens" value={formatTokens(point?.cost?.env_generation_tokens)} />
            <Row label="evaluation trials" value={point?.cost?.evaluation_trials} />
            <Row label="wall clock" value={formatDuration(point?.cost?.wall_clock_s)} />
          </div>
          <p className="text-2xs leading-snug text-muted-foreground">
            They are not summed because one number cannot tell a thrifty harness from a lazy
            method, and a simulated user spends tokens whether or not the harness is any good.
          </p>
        </div>
      </div>

      <Separator />

      <div className="grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-4">
        <Field label="Sampling policy">
          <Value value={point?.sampling?.policy} />
        </Field>
        <Field label="Selected within">
          <Value value={point?.sampling?.selected_within} />
        </Field>
        <Field label="Tasks in sampling">
          <Value value={point?.sampling?.task_ids?.length} />
        </Field>
        <Field label="Selection basis round">
          <Value value={point?.sampling?.selection_basis_round} />
        </Field>
        <Field label="Platform content sha" hint="run_meta.platform.content_sha — required for certification">
          <span className="font-mono">{platform?.content_sha ?? "—"}</span>
        </Field>
        <Field label="Platform git sha">
          <span className="font-mono">{platform?.git_sha?.slice(0, 12) ?? "—"}</span>
        </Field>
        <Field label="Platform tree dirty">
          <Value value={platform?.dirty === undefined ? undefined : String(platform.dirty)} />
        </Field>
        <Field label="Sandbox">
          {meta.sandbox ? (
            <span>
              {meta.sandbox.active ? "active" : "inactive"}
              {meta.sandbox.plan_version ? ` · plan v${meta.sandbox.plan_version}` : ""}
            </span>
          ) : (
            <Value value={undefined} />
          )}
        </Field>
      </div>
      {meta.sandbox?.detail ? (
        <p className="text-2xs leading-snug text-muted-foreground">{meta.sandbox.detail}</p>
      ) : null}
      {(!platform?.content_sha) ? (
        <p className="text-2xs leading-snug text-warn">
          This run records no `platform.content_sha`. It can still be `valid`, but its numbers
          cannot be compared with a run made by different code — which is what `certified`
          means.
        </p>
      ) : null}
    </div>
  );
}

function Row({
  label,
  value,
  mono,
  hint,
}: {
  label: string;
  value: string | number | null | undefined;
  mono?: boolean;
  hint?: string;
}) {
  return (
    <div className="flex items-start justify-between gap-3">
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="cursor-help text-muted-foreground">{label}</span>
        </TooltipTrigger>
        {hint ? <TooltipContent className="max-w-xs">{hint}</TooltipContent> : null}
      </Tooltip>
      <span className={cn("text-right", mono && "break-all font-mono")}>
        <Value value={value} />
      </span>
    </div>
  );
}
