import { useQuery } from "@tanstack/react-query";
import {
  getLaunchOptions,
  getRoundDiff,
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
  /**
   * The patch, keyed by round. Kept apart from `run(id)` because the bundle carries the
   * stat only: a patch is tens of kilobytes and is fetched by the panel that shows it.
   */
  roundDiff: (runId: string, round: number) => ["round-diff", runId, round] as const,
  task: (runId: string, round: number, taskId: string) =>
    ["task", runId, round, taskId] as const,
  launchOptions: ["launch", "options"] as const,
};

export function useRuns() {
  return useQuery({
    queryKey: queryKeys.runs,
    queryFn: listRuns,
    // A live `runs/` tree changes under the reader (a run is being written right now), but a
    // 30 s window keeps a click on Reload meaningful rather than a race with every render.
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

/**
 * One round's patch. `round === null` disables the query: the screens render "no round
 * selected" without asking for a diff of nothing.
 *
 * The 404 that means "no saved patch" is resolved to `null` inside `getRoundDiff`, so the
 * query never enters its error state for an absence — only for a real API failure.
 */
export function useRoundDiff(runId: string | undefined, round: number | null) {
  return useQuery({
    queryKey: queryKeys.roundDiff(runId ?? "", round ?? -1),
    queryFn: () => getRoundDiff(runId as string, round as number),
    enabled: Boolean(runId) && round !== null,
    staleTime: 5 * 60_000,
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
