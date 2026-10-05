import { useSyncExternalStore } from "react";
import { getBackendState, subscribeBackend, type BackendState } from "@/lib/api";

/**
 * The backend mode, as a React value.
 *
 * `resolveBackend()` performs the one-time `/api/health` probe; this hook only reads the
 * result, so the banner flips from "Checking…" to "Live API" or "Fixtures" without any
 * screen re-fetching. `getBackendState` is passed as the server snapshot too, so the
 * server-render smoke test sees the initial state rather than throwing.
 */
export function useBackend(): BackendState {
  return useSyncExternalStore(subscribeBackend, getBackendState, getBackendState);
}
