import { Link, Navigate, Route, Routes } from "react-router-dom";
import { AppShell, PageContainer } from "@/components/layout/app-shell";
import { EmptyState } from "@/components/common/states";
import { ExperimentsPage } from "@/pages/experiments";
import { RunDetailPage } from "@/pages/run-detail";
import { ComparePage } from "@/pages/compare";
import { TaskDetailPage } from "@/pages/task-detail";
import { LaunchPage } from "@/pages/launch";
import { Button } from "@/components/ui/button";

/**
 * The five screens. `/compare` is a top-level destination rather than a mode of the run
 * detail because it is the question the platform exists to answer, and burying it one click
 * deeper would make the number the default view again.
 */
export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Navigate to="/experiments" replace />} />
        <Route path="experiments" element={<ExperimentsPage />} />
        <Route path="runs/:runId" element={<RunDetailPage />} />
        <Route path="runs/:runId/tasks/:round/:taskId" element={<TaskDetailPage />} />
        <Route path="compare" element={<ComparePage />} />
        <Route path="launch" element={<LaunchPage />} />
        <Route
          path="*"
          element={
            <PageContainer>
              <EmptyState
                title="No such screen"
                description="The five screens are Experiments, Run detail, Compare, Task detail and Launch."
                action={
                  <Button asChild size="sm" variant="outline">
                    <Link to="/experiments">Back to Experiments</Link>
                  </Button>
                }
              />
            </PageContainer>
          }
        />
      </Route>
    </Routes>
  );
}
