import { useMemo, useState } from "react";
import { PageContainer } from "@/components/layout/app-shell";
import { PageHeader, Section } from "@/components/common/section";
import { ErrorState, TableSkeleton } from "@/components/common/states";
import { ExperimentsToolbar, DEFAULT_FILTERS, type ExperimentsFilters } from "@/components/experiments/experiments-toolbar";
import { RunsTable } from "@/components/experiments/runs-table";
import { ValiditySummary } from "@/components/experiments/validity-summary";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { useRuns } from "@/hooks/queries";
import { badgeFor, matchesSearch, matchesValidity } from "@/logic/certify";
import { Info } from "lucide-react";

/**
 * Experiments — every run, and whether its numbers can be quoted.
 *
 * The order of the page is the order of the question:
 *
 * 1. the four counts, each of which is also a filter;
 * 2. the filters (search, validity, harness, dataset, model);
 * 3. the dense table, with the certification badge as the second column.
 *
 * The table is sorted by run id by default rather than by score. Sorting by score first
 * would put unquotable numbers at the top of the screen, which is exactly the misreading this
 * screen exists to prevent.
 */
export function ExperimentsPage() {
  const { data, isLoading, error, refetch } = useRuns();
  const [filters, setFilters] = useState<ExperimentsFilters>(DEFAULT_FILTERS);

  const rows = data ?? [];
  const attributeFiltered = useMemo(
    () =>
      rows.filter(
        (row) =>
          (filters.harness === "all" || row.harness === filters.harness) &&
          (filters.dataset === "all" || row.dataset === filters.dataset) &&
          (filters.agentModel === "all" || row.agent_model === filters.agentModel),
      ),
    [rows, filters.harness, filters.dataset, filters.agentModel],
  );

  const matched = useMemo(
    () =>
      attributeFiltered.filter(
        (row) =>
          matchesValidity(badgeFor(row.certify), filters.validity) &&
          matchesSearch(row, filters.search),
      ).length,
    [attributeFiltered, filters.validity, filters.search],
  );

  return (
    <PageContainer>
      <PageHeader
        title="Experiments"
        description="Every run the platform has recorded, and the question a reader asks before quoting any number: is this run a measurement? `valid` means every point can be read and was measured by the platform; `certified` additionally means the record names the platform that produced it."
      />

      {isLoading ? (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2 md:grid-cols-5">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-[74px] animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
          <TableSkeleton rows={10} columns={8} />
        </div>
      ) : error ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <>
          <ValiditySummary
            rows={rows}
            activeFilter={filters.validity}
            onFilter={(validity) => setFilters((f) => ({ ...f, validity }))}
          />

          {filters.validity === "certified" || filters.validity === "quotable" ? (
            <Alert variant="info">
              <Info className="h-4 w-4" />
              <AlertDescription>
                {filters.validity === "certified"
                  ? "Certified runs name their platform content hash, so they are comparable with any other run made by the same code. The fixture set carries the certified runs from the platform's own validation pass."
                  : "Quotable = valid or certified. A valid run is still a measurement; it simply cannot be compared with a run made by different code, because the record does not name the platform that produced it."}
              </AlertDescription>
            </Alert>
          ) : null}

          <Section
            title="Runs"
            description="Sortable on every column. The status badge names the problems when a run is not quotable, and the reason when it is only valid."
            actions={
              <Button variant="outline" size="xs" onClick={() => void refetch()}>
                Reload
              </Button>
            }
          >
            <div className="space-y-3">
              <ExperimentsToolbar
                rows={rows}
                filters={filters}
                onChange={setFilters}
                matched={matched}
              />
              <RunsTable rows={attributeFiltered} validity={filters.validity} search={filters.search} />
            </div>
          </Section>
        </>
      )}
    </PageContainer>
  );
}
