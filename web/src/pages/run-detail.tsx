import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { PageContainer } from "@/components/layout/app-shell";
import { Section } from "@/components/common/section";
import { ChartSkeleton, DetailSkeleton, ErrorState } from "@/components/common/states";
import { CurveChart } from "@/components/run/curve-chart";
import { RunIdentityPanel } from "@/components/run/identity-panel";
import { PointStrip } from "@/components/run/point-strip";
import { PerTaskTable } from "@/components/run/per-task-table";
import { RoundDiffPanel } from "@/components/run/round-diff-panel";
import { RunHeader } from "@/components/run/run-header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useRun, useRuns } from "@/hooks/queries";
import { buildCurveView } from "@/logic/curve";
import { badgeFor } from "@/logic/certify";

/**
 * Run detail — the curve, the per-task table, and the run's own account of itself.
 *
 * The curve comes first because the platform's unit of evidence is a curve, not a final
 * score: a method that improves once and then loses it reads as a single number otherwise.
 * Score and `test_rate` are drawn as two series on two axes, and the round selector under the
 * chart drives the per-task table and the candidate diff, so "what happened in round 1" is
 * one click from the curve point that says round 1 did something.
 */
export function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>();
  const bundle = useRun(runId);
  const runs = useRuns();
  const [pickedRound, setPickedRound] = useState<number | null>(null);

  const view = useMemo(
    () => (bundle.data ? buildCurveView(bundle.data.points) : null),
    [bundle.data],
  );

  // The default selection is derived rather than written by an effect: an effect would render
  // one frame with no round selected, and that frame would claim "round 0 is not in this run's
  // curve" for a run whose curve is right there.
  const selectedRound = pickedRound ?? view?.points[view.points.length - 1]?.round ?? null;
  const setSelectedRound = setPickedRound;

  const certify = useMemo(() => {
    const row = runs.data?.find((r) => r.run_id === runId);
    return row ? row.certify : null;
  }, [runs.data, runId]);

  if (bundle.isLoading) {
    return (
      <PageContainer>
        <DetailSkeleton />
      </PageContainer>
    );
  }
  if (bundle.error) {
    return (
      <PageContainer>
        <ErrorState error={bundle.error} onRetry={() => void bundle.refetch()} />
      </PageContainer>
    );
  }
  if (!bundle.data || !view) return null;

  const point = bundle.data.points.find((p) => p.round === selectedRound) ?? null;
  const verdicts = selectedRound === null ? {} : bundle.data.verdicts[String(selectedRound)] ?? {};
  const badge = badgeFor(certify);

  return (
    <PageContainer>
      <RunHeader bundle={bundle.data} view={view} certify={certify} />

      {bundle.data.load_problems.length ? (
        <Section
          title="Problems reading this run"
          description="The read API reported these while loading the run directory. A run that is being written right now can be caught mid-write; the response is still a page, not a 500."
          className="border-warn/30"
        >
          <ul className="list-disc space-y-1 pl-4 text-2xs text-warn">
            {bundle.data.load_problems.map((problem) => (
              <li key={problem}>{problem}</li>
            ))}
          </ul>
        </Section>
      ) : null}

      {badge.problems.length ? (
        <Section
          title="Why this run is not quotable"
          description="Problems reported by certify() — a point that cannot be read as a measurement."
          className="border-fail/30"
        >
          <ul className="list-disc space-y-1 pl-4 text-2xs text-fail">
            {badge.problems.map((problem) => (
              <li key={problem}>{problem}</li>
            ))}
          </ul>
        </Section>
      ) : null}

      {badge.certificationNote && badge.level === "valid" ? (
        <Section
          title="Valid, but not certified"
          description="Both are quotable; only certified runs can be compared with a run made by different code."
        >
          <p className="text-2xs text-muted-foreground">{badge.certificationNote}</p>
        </Section>
      ) : null}

      <Section
        title="Curve"
        description="score and test_rate are two different measurements of the same artifact. The score is the mean over the round's scored tasks; test_rate is the check's own test tally, averaged over the tasks whose check reported one."
      >
        <CurveChart
          view={view}
          selectedRound={selectedRound}
          onSelectRound={setSelectedRound}
        />
      </Section>

      <Section
        title="Measured states"
        description="One card per curve point. Click a card to drive the per-task table and the candidate diff below."
      >
        <PointStrip
          points={view.points}
          selectedRound={selectedRound}
          onSelect={setSelectedRound}
        />
      </Section>

      <Tabs defaultValue="tasks" className="space-y-1">
        <TabsList>
          <TabsTrigger value="tasks">Per-task {selectedRound !== null ? `· round ${selectedRound}` : ""}</TabsTrigger>
          <TabsTrigger value="diff">Candidate diff {selectedRound !== null ? `· round ${selectedRound}` : ""}</TabsTrigger>
          <TabsTrigger value="identity">Identity &amp; config</TabsTrigger>
        </TabsList>
        <TabsContent value="tasks">
          <Section
            title={`Per-task scoring · round ${selectedRound ?? "—"}`}
            description="Every task the round scored, with its verdict detail. A `test_rate` of 0.80 beside a score of 0.000 is a task where four of five checks passed and the all-or-nothing reward said nothing happened."
          >
            <PerTaskTable
              runId={bundle.data.run_id}
              round={selectedRound ?? 0}
              point={point}
              verdicts={verdicts}
            />
          </Section>
        </TabsContent>
        <TabsContent value="diff">
          <Section
            title={`Candidate diff · round ${selectedRound ?? "—"}`}
            description="The git diff the platform saved beside this point, so the record still shows what changed after the workspace's dangling commits are collected."
          >
            {selectedRound === null ? (
              <ChartSkeleton />
            ) : (
              <RoundDiffPanel runId={bundle.data.run_id} round={selectedRound} />
            )}
          </Section>
        </TabsContent>
        <TabsContent value="identity">
          <Section
            title="Identity, environment and cost"
            description="The fields that explain the score: which harness sha, which two models, which pinned image, and the three cost budgets — which are never summed."
          >
            <RunIdentityPanel meta={bundle.data.meta} point={point} />
          </Section>
        </TabsContent>
      </Tabs>
    </PageContainer>
  );
}
