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
        <PageHeader title="Launch" description="Reading the harnesses, datasets and improvers on this machine…" />
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
        title="Launch"
        description="Configure a run and read the argv a future API would take. The options are read from disk (base_harness/, data/, improvers/), never hard-coded."
        meta={
          <Badge variant="warn">
            <Info className="h-3 w-3" />
            not submitted anywhere — the write API does not exist yet
          </Badge>
        }
      />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,520px)]">
        <div className="space-y-4">
          <Section title="Run identity" description="`--run-id` names the directory under runs/. The driver refuses a name that is not a safe path segment.">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Run id" required>
                <Input
                  value={config.runId}
                  onChange={(e) => set("runId", e.target.value)}
                  placeholder="ds-dgm-r3"
                  className="h-8 font-mono text-xs"
                />
              </Field>
              <Field label="Seed" hint="drawn at random when omitted; re-supplyable so a recorded run can be reproduced">
                <Input
                  value={config.seed}
                  onChange={(e) => set("seed", e.target.value)}
                  placeholder="(random)"
                  className="h-8 font-mono text-xs"
                />
              </Field>
            </div>
          </Section>

          <Section title="Harness and task set" description="The base harness to start from, the task set, and which half of the split this run is about.">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Harness" required hint="a directory under base_harness/ with a harness.json">
                <Select value={config.harness} onValueChange={(v) => set("harness", v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="pick one" />
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
              <Field label="Dataset" required>
                <Select value={config.dataset} onValueChange={(v) => set("dataset", v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="pick one" />
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
              <Field label="Side" hint="a run evaluates ONE side; the exam's traces are a separate run, not a withheld field">
                <Select value={config.side} onValueChange={(v) => set("side", v as "train" | "eval")}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="train">train — the harness evolves here</SelectItem>
                    <SelectItem value="eval">eval — measure one state of a train run</SelectItem>
                  </SelectContent>
                </Select>
              </Field>
              <Field label="Sampling" hint="chosen on H0; `all` measures the whole side">
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
                  <Field label="From run" required hint="the train run whose harness state to measure">
                    <Input
                      value={config.fromRun}
                      onChange={(e) => set("fromRun", e.target.value)}
                      placeholder="ds-dgm"
                      className="h-8 font-mono text-xs"
                    />
                  </Field>
                  <Field label="From round" hint="default: that run's last measured round">
                    <Input
                      value={config.fromRound}
                      onChange={(e) => set("fromRound", e.target.value)}
                      placeholder="last"
                      className="h-8 font-mono text-xs"
                    />
                  </Field>
                </>
              ) : null}
              <Field label="Tasks (subset)" hint="comma-separated; refused if any id is not in the dataset">
                <Input
                  value={config.tasks}
                  onChange={(e) => set("tasks", e.target.value)}
                  placeholder="(the whole side)"
                  className="h-8 font-mono text-xs"
                />
              </Field>
            </div>
          </Section>

          <Section title="Budget and measurement" description="How many states, how many trials per state, and how much concurrency. These change what the numbers mean, so each is echoed in the warnings.">
            <div className="grid gap-3 sm:grid-cols-3">
              <Field label="Rounds" required>
                <Input
                  type="number"
                  min={1}
                  value={config.rounds}
                  onChange={(e) => set("rounds", Number(e.target.value))}
                  className="h-8 text-xs"
                />
              </Field>
              <Field label="Trials" hint="each point then carries n_trials and score_std">
                <Input
                  type="number"
                  min={1}
                  value={config.trials}
                  onChange={(e) => set("trials", Number(e.target.value))}
                  className="h-8 text-xs"
                />
              </Field>
              <Field label="Jobs" hint="tasks share one endpoint and one host">
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

          <Section title="Improver and method" description="The improver is resolved from improvers/improvers.json; what was resolved is recorded on identity.improver, not what was asked for.">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Improver" hint="a name from improvers.json, or a path to an executable">
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
              <Field label="Improver model" hint="overrides the improver's own model; forbidden models are refused by the driver">
                <Input
                  value={config.improverModel}
                  onChange={(e) => set("improverModel", e.target.value)}
                  placeholder="(the improver's own)"
                  className="h-8 font-mono text-xs"
                />
              </Field>
              <Field
                label="Method entrypoint"
                hint="argv for the method's own runner; defaults to harness.json's improve_entrypoint"
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

          <Section title="Isolation" description="A sandboxed harness cannot see the platform at all. Numbers are not comparable across the two modes, and run_meta records which one produced a run.">
            <div className="space-y-3">
              <div className="flex items-center justify-between gap-3 rounded-md border border-border px-3 py-2">
                <div className="space-y-0.5">
                  <Label htmlFor="no-sandbox" className="text-xs">
                    Run without a mount namespace (`--no-sandbox`)
                  </Label>
                  <p className="text-2xs text-muted-foreground">
                    Debugging only. The harness can then read driver.py and .env; only the
                    integrity hash check stands between it and the scorer.
                  </p>
                </div>
                <Switch
                  id="no-sandbox"
                  checked={config.noSandbox}
                  onCheckedChange={(v) => set("noSandbox", v)}
                />
              </div>
              <Field label="Work root" hint="where harness working trees live; must be OUTSIDE the platform tree">
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
            title="Read from the environment, not from this form"
            description="These values reach a run through .env / HG_* variables and are recorded on the curve points. A form that presented them as free choices would misstate where the number came from. Values for secret-looking variables are never returned — only whether they are set."
          >
            <div className="space-y-1">
              {envFields.map((field) => (
                <div
                  key={`${field.flag}-${field.env_var}`}
                  className="flex flex-wrap items-center gap-2 rounded-md border border-border/70 px-2 py-1.5"
                >
                  <Badge variant="warn">env</Badge>
                  <span className="font-mono text-2xs">{field.env_var}</span>
                  <span className="text-2xs text-muted-foreground">{field.flag}</span>
                  <span className="ml-auto flex items-center gap-2">
                    {field.value ? (
                      <span className="font-mono text-2xs text-foreground">{field.value}</span>
                    ) : field.set ? (
                      <span className="text-2xs text-muted-foreground">
                        {field.secret ? "set (value hidden)" : "set"}
                      </span>
                    ) : (
                      <span className="text-2xs text-muted-foreground/60">unset</span>
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
            title="argv"
            description="Exactly the line a future API would run. Defaults are omitted rather than spelled out, so the line reads like the one a person would have typed."
            actions={<Badge variant="muted">python3 driver.py</Badge>}
          >
            <pre className="overflow-x-auto whitespace-pre-wrap break-all rounded-md border border-border bg-muted/30 px-2.5 py-2 font-mono text-2xs">
              {plan.command}
            </pre>
            {plan.errors.length ? (
              <Alert variant="destructive" className="mt-2">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>The driver would refuse this</AlertTitle>
                <AlertDescription>
                  <ul className="list-disc space-y-0.5 pl-4">
                    {plan.errors.map((e) => (
                      <li key={e}>{e}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            ) : null}
            {plan.warnings.length ? (
              <div className="mt-2 space-y-1.5">
                {plan.warnings.map((w) => (
                  <Alert key={w} variant="warn">
                    <Terminal className="h-4 w-4" />
                    <AlertDescription>{w}</AlertDescription>
                  </Alert>
                ))}
              </div>
            ) : null}
          </Section>

          <Section
            title="JSON request body"
            description="The same configuration as the body POST /api/runs should take. Inferred: the write API does not exist yet."
          >
            <pre className="max-h-[360px] overflow-auto rounded-md border border-border bg-muted/30 px-2.5 py-2 font-mono text-2xs">
              {JSON.stringify(plan.request, null, 2)}
            </pre>
          </Section>

          <Section title="Actions" description="Disabled by design: there is no endpoint to submit to.">
            <div className="flex items-center gap-2">
              <Button disabled={plan.errors.length > 0} title="no write API yet">
                <Play className="h-3.5 w-3.5" />
                Start run
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
                Fill from a real run
              </Button>
            </div>
            <p className="mt-2 text-2xs leading-relaxed text-muted-foreground">
              The write API contract this form implies is in{" "}
              <span className="font-mono">web/README.md</span>: accept this JSON, refuse a request
              that the driver would refuse, and return the run id plus a stream of the run&apos;s
              events. Until then the form is a specification, not a control.
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
  return (
    <div className={cn("space-y-1", className)}>
      <div className="flex items-center gap-1">
        <Label>{label}</Label>
        {required ? <span className="text-2xs text-fail">required</span> : null}
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
