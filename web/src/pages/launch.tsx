import { useMemo, useState, type ReactNode } from "react";
import { AlertTriangle, Info, Play, Terminal } from "lucide-react";
import { PageContainer } from "@/components/layout/app-shell";
import { PageHeader, Section } from "@/components/common/section";
import { ErrorState } from "@/components/common/states";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { useLaunchOptions } from "@/hooks/queries";
import { useT } from "@/i18n";
import { DEFAULT_LAUNCH_CONFIG, buildLaunchPlan, type LaunchConfig } from "@/logic/launch";
import { cn } from "@/lib/utils";

/**
 * Launch — configure a run and *read the argv it would produce*.
 *
 * There is no write API yet, and this session must not invent one, so the form does not
 * submit. What it does instead is more useful at this stage: it shows the exact
 * `python3 driver.py …` line and the JSON body a `POST /api/runs` would take, validated
 * against the real driver's refusals (a bad `--run-id`, `--side eval` without `--from-run`).
 *
 * The fields that the driver would take from the **environment** are separated into their own
 * panel and marked `env`, because a form that presents them as free choices would misrepresent
 * where the value comes from: `agent_model` is recorded on every point and comes from `.env`,
 * not from argv. Secrets are never rendered — only whether they are set.
 */
export function LaunchPage() {
  const t = useT();
  const options = useLaunchOptions();
  const [config, setConfig] = useState<LaunchConfig>({
    ...DEFAULT_LAUNCH_CONFIG,
    harness: "loop",
    dataset: "demo",
    improver: "default",
  });

  const plan = useMemo(() => buildLaunchPlan(config, options.data), [config, options.data]);
  const set = <K extends keyof LaunchConfig>(key: K, value: LaunchConfig[K]) =>
    setConfig((c) => ({ ...c, [key]: value }));

  if (options.isLoading) {
    return (
      <PageContainer>
        <PageHeader title={t("launch.title")} description={t("launch.loading")} />
        <div className="grid gap-3 lg:grid-cols-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-14 animate-pulse rounded-lg bg-muted" />
          ))}
        </div>
      </PageContainer>
    );
  }
  if (options.error) {
    return (
      <PageContainer>
        <ErrorState error={options.error} onRetry={() => void options.refetch()} />
      </PageContainer>
    );
  }

  const harnesses = options.data?.harnesses ?? [];
  const datasets = options.data?.datasets ?? [];
  const samplings = options.data?.samplings ?? [];
  const improvers = options.data?.improver_names ?? [];
  const envFields = options.data?.env_derived ?? [];

  return (
    <PageContainer>
      <PageHeader
        title={t("launch.title")}
        description={t("launch.description")}
        meta={
          <Badge variant="warn">
            <Info className="h-3 w-3" />
            {t("launch.notSubmitted")}
          </Badge>
        }
      />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,520px)]">
        <div className="space-y-4">
          <Section title={t("launch.identity.title")} description={t("launch.identity.description")}>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label={t("launch.runId.label")} required>
                <Input
                  value={config.runId}
                  onChange={(e) => set("runId", e.target.value)}
                  placeholder="ds-dgm-r3"
                  className="h-8 font-mono text-xs"
                />
              </Field>
              <Field label={t("launch.seed.label")} hint={t("launch.seed.hint")}>
                <Input
                  value={config.seed}
                  onChange={(e) => set("seed", e.target.value)}
                  placeholder={t("launch.seed.placeholder")}
                  className="h-8 font-mono text-xs"
                />
              </Field>
            </div>
          </Section>

          <Section title={t("launch.harness.title")} description={t("launch.harness.description")}>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label={t("launch.harness.label")} required hint={t("launch.harness.hint")}>
                <Select value={config.harness} onValueChange={(v) => set("harness", v)}>
                  <SelectTrigger>
                    <SelectValue placeholder={t("launch.pickOne")} />
                  </SelectTrigger>
                  <SelectContent>
                    {harnesses.map((h) => (
                      <SelectItem key={h} value={h}>
                        {h}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Field>
              <Field label={t("launch.dataset.label")} required>
                <Select value={config.dataset} onValueChange={(v) => set("dataset", v)}>
                  <SelectTrigger>
                    <SelectValue placeholder={t("launch.pickOne")} />
                  </SelectTrigger>
                  <SelectContent>
                    {datasets.map((d) => (
                      <SelectItem key={d} value={d}>
                        {d}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Field>
              <Field label={t("launch.side.label")} hint={t("launch.side.hint")}>
                <Select value={config.side} onValueChange={(v) => set("side", v as "train" | "eval")}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="train">{t("launch.side.train")}</SelectItem>
                    <SelectItem value="eval">{t("launch.side.eval")}</SelectItem>
                  </SelectContent>
                </Select>
              </Field>
              <Field label={t("launch.sampling.label")} hint={t("launch.sampling.hint")}>
                <Select value={config.sampling} onValueChange={(v) => set("sampling", v)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {(samplings.length ? samplings : ["all"]).map((s) => (
                      <SelectItem key={s} value={s}>
                        {s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Field>
              {config.side === "eval" ? (
                <>
                  <Field label={t("launch.fromRun.label")} required hint={t("launch.fromRun.hint")}>
                    <Input
                      value={config.fromRun}
                      onChange={(e) => set("fromRun", e.target.value)}
                      placeholder="ds-dgm"
                      className="h-8 font-mono text-xs"
                    />
                  </Field>
                  <Field label={t("launch.fromRound.label")} hint={t("launch.fromRound.hint")}>
                    <Input
                      value={config.fromRound}
                      onChange={(e) => set("fromRound", e.target.value)}
                      placeholder={t("launch.fromRound.placeholder")}
                      className="h-8 font-mono text-xs"
                    />
                  </Field>
                </>
              ) : null}
              <Field label={t("launch.tasks.label")} hint={t("launch.tasks.hint")}>
                <Input
                  value={config.tasks}
                  onChange={(e) => set("tasks", e.target.value)}
                  placeholder={t("launch.tasks.placeholder")}
                  className="h-8 font-mono text-xs"
                />
              </Field>
            </div>
          </Section>

          <Section title={t("launch.budget.title")} description={t("launch.budget.description")}>
            <div className="grid gap-3 sm:grid-cols-3">
              <Field label={t("launch.rounds.label")} required>
                <Input
                  type="number"
                  min={1}
                  value={config.rounds}
                  onChange={(e) => set("rounds", Number(e.target.value))}
                  className="h-8 text-xs"
                />
              </Field>
              <Field label={t("launch.trials.label")} hint={t("launch.trials.hint")}>
                <Input
                  type="number"
                  min={1}
                  value={config.trials}
                  onChange={(e) => set("trials", Number(e.target.value))}
                  className="h-8 text-xs"
                />
              </Field>
              <Field label={t("launch.jobs.label")} hint={t("launch.jobs.hint")}>
                <Input
                  type="number"
                  min={1}
                  value={config.jobs}
                  onChange={(e) => set("jobs", Number(e.target.value))}
                  className="h-8 text-xs"
                />
              </Field>
            </div>
          </Section>

          <Section title={t("launch.improver.title")} description={t("launch.improver.description")}>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label={t("launch.improver.label")} hint={t("launch.improver.hint")}>
                <Select value={config.improver} onValueChange={(v) => set("improver", v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="default" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">resolve the default</SelectItem>
                    {improvers.map((name) => (
                      <SelectItem key={name} value={name}>
                        {name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Field>
              <Field label={t("launch.improverModel.label")} hint={t("launch.improverModel.hint")}>
                <Input
                  value={config.improverModel}
                  onChange={(e) => set("improverModel", e.target.value)}
                  placeholder={t("launch.improverModel.placeholder")}
                  className="h-8 font-mono text-xs"
                />
              </Field>
              <Field
                label={t("launch.methodEntrypoint.label")}
                hint={t("launch.methodEntrypoint.hint")}
                className="sm:col-span-2"
              >
                <Input
                  value={config.methodEntrypoint}
                  onChange={(e) => set("methodEntrypoint", e.target.value)}
                  placeholder={`python ${"$"}PWD/methods/noop/run.py`}
                  className="h-8 font-mono text-xs"
                />
              </Field>
            </div>
          </Section>

          <Section title={t("launch.isolation.title")} description={t("launch.isolation.description")}>
            <div className="space-y-3">
              <div className="flex items-center justify-between gap-3 rounded-md border border-border px-3 py-2">
                <div className="space-y-0.5">
                  <Label htmlFor="no-sandbox" className="text-xs">
                    {t("launch.noSandbox.label")}
                  </Label>
                  <p className="text-2xs text-muted-foreground">{t("launch.noSandbox.body")}</p>
                </div>
                <Switch
                  id="no-sandbox"
                  checked={config.noSandbox}
                  onCheckedChange={(v) => set("noSandbox", v)}
                />
              </div>
              <Field label={t("launch.workRoot.label")} hint={t("launch.workRoot.hint")}>
                <Input
                  value={config.workRoot}
                  onChange={(e) => set("workRoot", e.target.value)}
                  placeholder="../harnessgrad_work"
                  className="h-8 font-mono text-xs"
                />
              </Field>
            </div>
          </Section>

          <Section
            title={t("launch.env.title")}
            description={t("launch.env.description")}
          >
            <div className="space-y-1">
              {envFields.map((field) => (
                <div
                  key={`${field.flag}-${field.env_var}`}
                  className="flex flex-wrap items-center gap-2 rounded-md border border-border/70 px-2 py-1.5"
                >
                  <Badge variant="warn">{t("launch.env.badge")}</Badge>
                  <span className="font-mono text-2xs">{field.env_var}</span>
                  <span className="text-2xs text-muted-foreground">{field.flag}</span>
                  <span className="ml-auto flex items-center gap-2">
                    {field.value ? (
                      <span className="font-mono text-2xs text-foreground">{field.value}</span>
                    ) : field.set ? (
                      <span className="text-2xs text-muted-foreground">
                        {field.secret ? t("launch.env.setHidden") : t("launch.env.set")}
                      </span>
                    ) : (
                      <span className="text-2xs text-muted-foreground/60">
                        {t("launch.env.unset")}
                      </span>
                    )}
                  </span>
                  <p className="w-full text-2xs leading-snug text-muted-foreground">{field.note}</p>
                </div>
              ))}
            </div>
          </Section>
        </div>

        <div className="space-y-4 xl:sticky xl:top-14 xl:self-start">
          <Section
            title={t("launch.argv.title")}
            description={t("launch.argv.description")}
            actions={<Badge variant="muted">python3 driver.py</Badge>}
          >
            <pre className="overflow-x-auto whitespace-pre-wrap break-all rounded-md border border-border bg-muted/30 px-2.5 py-2 font-mono text-2xs">
              {plan.command}
            </pre>
            {plan.errors.length ? (
              <Alert variant="destructive" className="mt-2">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>{t("launch.errors.title")}</AlertTitle>
                <AlertDescription>
                  <ul className="list-disc space-y-0.5 pl-4">
                    {plan.errors.map((e) => (
                      <li key={e.key}>{t(e.key, e.params)}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            ) : null}
            {plan.warnings.length ? (
              <div className="mt-2 space-y-1.5">
                {plan.warnings.map((w) => (
                  <Alert key={w.key} variant="warn">
                    <Terminal className="h-4 w-4" />
                    <AlertDescription>{t(w.key, w.params)}</AlertDescription>
                  </Alert>
                ))}
              </div>
            ) : null}
          </Section>

          <Section
            title={t("launch.json.title")}
            description={t("launch.json.description")}
          >
            <pre className="max-h-[360px] overflow-auto rounded-md border border-border bg-muted/30 px-2.5 py-2 font-mono text-2xs">
              {JSON.stringify(plan.request, null, 2)}
            </pre>
          </Section>

          <Section title={t("launch.actions.title")} description={t("launch.actions.description")}>
            <div className="flex items-center gap-2">
              <Button disabled={plan.errors.length > 0} title={t("launch.startRunTitle")}>
                <Play className="h-3.5 w-3.5" />
                {t("launch.startRun")}
              </Button>
              <Button
                variant="outline"
                onClick={() =>
                  setConfig({
                    runId: "ds-dgm-r3",
                    harness: "loop",
                    dataset: "terminal_bench",
                    sampling: "all",
                    rounds: 2,
                    trials: 1,
                    jobs: 4,
                    improver: "deepseek",
                    improverModel: "",
                    methodEntrypoint: `python ${"$"}PWD/methods/dgm/run.py`,
                    tasks: "",
                    side: "train",
                    fromRun: "",
                    fromRound: "",
                    seed: "",
                    noSandbox: false,
                    workRoot: "",
                    mode: "A",
                  })
                }
              >
                {t("launch.fillFromRealRun")}
              </Button>
            </div>
            <p className="mt-2 text-2xs leading-relaxed text-muted-foreground">
              {t("launch.contractBefore")}
              <span className="font-mono">web/README.md</span>
              {t("launch.contractAfter")}
            </p>
          </Section>
        </div>
      </div>
    </PageContainer>
  );
}

function Field({
  label,
  children,
  hint,
  required,
  className,
}: {
  label: string;
  children: ReactNode;
  hint?: string;
  required?: boolean;
  className?: string;
}) {
  const t = useT();
  return (
    <div className={cn("space-y-1", className)}>
      <div className="flex items-center gap-1">
        <Label>{label}</Label>
        {required ? <span className="text-2xs text-fail">{t("launch.required")}</span> : null}
        {hint ? (
          <Tooltip>
            <TooltipTrigger asChild>
              <Info className="h-3 w-3 cursor-help text-muted-foreground" />
            </TooltipTrigger>
            <TooltipContent className="max-w-xs">{hint}</TooltipContent>
          </Tooltip>
        ) : null}
      </div>
      {children}
    </div>
  );
}
