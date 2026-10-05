import { useQuery } from "@tanstack/react-query";
import {
  getLaunchOptions,
  getRun,
  getTaskPage,
  listRuns,
} from "@/lib/api";

/**
 * Query keys and hooks. One place, so a later `POST /api/runs` invalidates exactly the
 * right cache entries (`queryKeys.runs` and the affected `queryKeys.run(id)`).
 */
export const queryKeys = {
  runs: ["runs"] as const,
  run: (runId: string) => ["run", runId] as const,
  task: (runId: string, round: number, taskId: string) =>
    ["task", runId, round, taskId] as const,
  launchOptions: ["launch", "options"] as const,
};

export function useRuns() {
  return useQuery({
    queryKey: queryKeys.runs,
    queryFn: listRuns,
    // Fixtures never change; a real API would use a shorter staleTime. Kept short enough
    // that a page refresh always re-reads, which is what a debugging tool should do.
    staleTime: 30_000,
  });
}

export function useRun(runId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.run(runId ?? ""),
    queryFn: () => getRun(runId as string),
    enabled: Boolean(runId),
    staleTime: 30_000,
  });
}

export function useTaskPage(
  runId: string | undefined,
  round: number | undefined,
  taskId: string | undefined,
) {
  return useQuery({
    queryKey: queryKeys.task(runId ?? "", round ?? -1, taskId ?? ""),
    queryFn: () => getTaskPage(runId as string, round as number, taskId as string),
    enabled: Boolean(runId && taskId) && round !== undefined,
    staleTime: 30_000,
  });
}

export function useLaunchOptions() {
  return useQuery({
    queryKey: queryKeys.launchOptions,
    queryFn: getLaunchOptions,
    staleTime: 5 * 60_000,
  });
}
