import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Field, Value } from "@/components/common/presence-value";
import { formatDuration, formatTokens } from "@/lib/format";
import { useT } from "@/i18n";
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
  const t = useT();
  const identity = point?.identity;
  const improver = identity?.improver;
  const harnessConfig = identity?.harness_config;
  const platform = meta.platform;
  const runtime = point?.env?.harness_runtime;

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-3 lg:grid-cols-4">
        <Field label={t("run.identity.run")}>{meta.run_id}</Field>
        <Field label={t("run.identity.round")}>
          <Value value={point?.round} />
        </Field>
        <Field
          label={t("run.identity.scoreKind")}
          hint={t("run.identity.scoreKindHint")}
        >
          {point?.score_kind === "training" ? (
            <Badge variant="warn">training</Badge>
          ) : point?.score_kind ? (
            <Badge variant="info">{point.score_kind}</Badge>
          ) : (
            <Value value={undefined} />
          )}
        </Field>
        <Field label={t("run.identity.side")} hint={t("run.identity.sideHint")}>
          <Value value={point?.side} />
        </Field>
        <Field label={t("run.identity.harnessMeta")}>
          <span className="font-mono">{meta.harness}</span>
        </Field>
        <Field label={t("run.identity.dataset")}>
          <span className="font-mono">{meta.dataset}</span>
        </Field>
        <Field label={t("run.identity.mode")}>
          <Value value={meta.mode} />
        </Field>
        <Field label={t("run.identity.trials")} hint={t("run.identity.trialsHint")}>
          <Value value={meta.trials ?? undefined} fieldName="n_trials" />
        </Field>
        <Field label={t("run.identity.harnessNameVersion")}>
          <span className="font-mono">
            {identity?.harness_name ?? "—"} {identity?.harness_version ?? ""}
          </span>
        </Field>
        <Field label={t("run.identity.harnessSha")} hint={t("run.identity.harnessShaHint")}>
          <span className="font-mono">{identity?.harness_sha ?? "—"}</span>
        </Field>
        <Field label={t("run.identity.runMode")}>
          <Value value={identity?.run_mode} />
        </Field>
        <Field label={t("run.identity.frameworkVersion")}>
          <Value value={identity?.framework_version} />
        </Field>
        <Field
          label={t("run.identity.agentModel")}
          hint={t("run.identity.agentModelHint")}
        >
          <span className="font-mono">{identity?.agent_model ?? "—"}</span>
        </Field>
        <Field label={t("run.identity.agentBackend")}>
          <Value value={identity?.agent_backend} />
        </Field>
        <Field label={t("run.identity.agentModelSource")} hint={t("run.identity.agentModelSourceHint")}>
          <Value value={identity?.agent_model_source} />
        </Field>
        <Field label={t("run.identity.method")}>
          <Value value={identity?.method} />
        </Field>
        <Field label={t("run.identity.improver")} hint={t("run.identity.improverHint")}>
          {improver ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="cursor-help font-mono">
                  {improver.name ?? "?"}
                  {improver.model ? ` · ${improver.model}` : ""}
                </span>
              </TooltipTrigger>
              <TooltipContent className="space-y-0.5">
                <div>{t("run.identity.improverKind", { value: improver.kind ?? "—" })}</div>
                <div>{t("run.identity.improverVersion", { value: improver.version || "—" })}</div>
                <div>{t("run.identity.improverEndpoint", { value: improver.base_url ?? "—" })}</div>
                <div>
                  {t("run.identity.improverModified", {
                    value: improver.modified === undefined ? "—" : String(improver.modified),
                  })}
                </div>
              </TooltipContent>
            </Tooltip>
          ) : (
            <Value value={improver === null ? null : undefined} />
          )}
        </Field>
        <Field label={t("run.identity.skillSha")}>
          <span className="font-mono">{identity?.skill_sha?.slice(0, 12) ?? "—"}</span>
        </Field>
      </div>

      <Separator />

      <div className="grid gap-3 lg:grid-cols-3">
        <div className="space-y-2">
          <h3 className="text-2xs font-semibold uppercase tracking-wide text-muted-foreground">
            {t("run.identity.harnessConfig")}
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
                {t("run.identity.noHarnessConfig")}
              </p>
            )}
          </div>
        </div>

        <div className="space-y-2">
          <h3 className="text-2xs font-semibold uppercase tracking-wide text-muted-foreground">
            {t("run.identity.environment")}
          </h3>
          <div className="space-y-1 text-2xs">
            <Row label={t("run.identity.envKind")} value={point?.env?.kind} />
            <Row label={t("run.identity.envPlacement")} value={point?.env?.placement} />
            <Row label={t("run.identity.envNetwork")} value={point?.env?.network} />
            <Row
              label={t("run.identity.envImageDigest")}
              value={point?.env?.image_digest}
              mono
              hint={t("run.identity.envImageDigestHint")}
            />
            <Row
              label={t("run.identity.envHarnessRuntime")}
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
              label={t("run.identity.envVariants")}
              value={
                typeof point?.env?.variants_count === "number"
                  ? point.env.variants_count
                  : undefined
              }
            />
            <Row
              label={t("run.identity.envSeed")}
              value={point?.env?.seed === null || point?.env?.seed === undefined ? undefined : String(point.env.seed)}
            />
          </div>
        </div>

        <div className="space-y-2">
          <h3 className="text-2xs font-semibold uppercase tracking-wide text-muted-foreground">
            {t("run.identity.cost")}
          </h3>
          <div className="space-y-1 text-2xs">
            <Row label={t("run.identity.costHarnessTokens")} value={formatTokens(point?.cost?.harness_tokens)} />
            <Row label={t("run.identity.costHarnessModelCalls")} value={point?.cost?.harness_model_calls} />
            <Row
              label={t("run.identity.costMethodTokens")}
              value={formatTokens(point?.cost?.method_generation_tokens)}
            />
            <Row label={t("run.identity.costEnvTokens")} value={formatTokens(point?.cost?.env_generation_tokens)} />
            <Row label={t("run.identity.costEvalTrials")} value={point?.cost?.evaluation_trials} />
            <Row label={t("run.identity.costWallClock")} value={formatDuration(point?.cost?.wall_clock_s)} />
          </div>
          <p className="text-2xs leading-snug text-muted-foreground">
            {t("run.identity.costNote")}
          </p>
        </div>
      </div>

      <Separator />

      <div className="grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-4">
        <Field label={t("run.identity.samplingPolicy")}>
          <Value value={point?.sampling?.policy} />
        </Field>
        <Field label={t("run.identity.selectedWithin")}>
          <Value value={point?.sampling?.selected_within} />
        </Field>
        <Field label={t("run.identity.tasksInSampling")}>
          <Value value={point?.sampling?.task_ids?.length} />
        </Field>
        <Field label={t("run.identity.selectionBasisRound")}>
          <Value value={point?.sampling?.selection_basis_round} />
        </Field>
        <Field label={t("run.identity.platformContentSha")} hint={t("run.identity.platformContentShaHint")}>
          <span className="font-mono">{platform?.content_sha ?? "—"}</span>
        </Field>
        <Field label={t("run.identity.platformGitSha")}>
          <span className="font-mono">{platform?.git_sha?.slice(0, 12) ?? "—"}</span>
        </Field>
        <Field label={t("run.identity.platformTreeDirty")}>
          <Value value={platform?.dirty === undefined ? undefined : String(platform.dirty)} />
        </Field>
        <Field label={t("run.identity.sandbox")}>
          {meta.sandbox ? (
            <span>
              {meta.sandbox.active
                ? t("run.identity.sandboxActive")
                : t("run.identity.sandboxInactive")}
              {meta.sandbox.plan_version
                ? ` · ${t("run.identity.sandboxPlan", { version: meta.sandbox.plan_version })}`
                : ""}
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
          {t("run.identity.noContentSha")}
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
