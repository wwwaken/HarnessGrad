import { Search, X } from "lucide-react";
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
import type { ValidityFilter } from "@/logic/certify";
import type { RunSummary } from "@/types";

export interface ExperimentsFilters {
  search: string;
  validity: ValidityFilter;
  harness: string;
  dataset: string;
  agentModel: string;
}

export const DEFAULT_FILTERS: ExperimentsFilters = {
  search: "",
  validity: "all",
  harness: "all",
  dataset: "all",
  agentModel: "all",
};

const VALIDITY_LABELS: Record<ValidityFilter, string> = {
  all: "All runs",
  quotable: "Quotable (valid or certified)",
  certified: "Certified only",
  valid: "Valid, not certified",
  invalid: "Invalid or tampered",
  "no-points": "Nothing measured",
};

function unique(values: Array<string | null>): string[] {
  return [...new Set(values.filter((v): v is string => Boolean(v)))].sort();
}

/**
 * Filters as a single row above the table. The validity filter is first because it is the
 * question the screen answers; the rest are narrowing tools.
 */
export function ExperimentsToolbar({
  rows,
  filters,
  onChange,
  matched,
}: {
  rows: RunSummary[];
  filters: ExperimentsFilters;
  onChange: (next: ExperimentsFilters) => void;
  matched: number;
}) {
  const harnesses = unique(rows.map((r) => r.harness));
  const datasets = unique(rows.map((r) => r.dataset));
  const models = unique(rows.map((r) => r.agent_model));
  const dirty =
    filters.search !== DEFAULT_FILTERS.search ||
    filters.validity !== DEFAULT_FILTERS.validity ||
    filters.harness !== "all" ||
    filters.dataset !== "all" ||
    filters.agentModel !== "all";

  return (
    <div className="flex flex-wrap items-end gap-3">
      <div className="min-w-[220px] flex-1 space-y-1">
        <Label htmlFor="run-search">Search</Label>
        <div className="relative">
          <Search className="pointer-events-none absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            id="run-search"
            value={filters.search}
            onChange={(e) => onChange({ ...filters, search: e.target.value })}
            placeholder="run id, model, harness, dataset, improver"
            className="h-8 pl-7 text-xs"
          />
        </div>
      </div>
      <div className="w-[220px] space-y-1">
        <Label>Validity</Label>
        <Select
          value={filters.validity}
          onValueChange={(value) => onChange({ ...filters, validity: value as ValidityFilter })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {(Object.keys(VALIDITY_LABELS) as ValidityFilter[]).map((key) => (
              <SelectItem key={key} value={key}>
                {VALIDITY_LABELS[key]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="w-[150px] space-y-1">
        <Label>Harness</Label>
        <Select
          value={filters.harness}
          onValueChange={(value) => onChange({ ...filters, harness: value })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All harnesses</SelectItem>
            {harnesses.map((h) => (
              <SelectItem key={h} value={h}>
                {h}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="w-[170px] space-y-1">
        <Label>Dataset</Label>
        <Select
          value={filters.dataset}
          onValueChange={(value) => onChange({ ...filters, dataset: value })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All datasets</SelectItem>
            {datasets.map((d) => (
              <SelectItem key={d} value={d}>
                {d}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="w-[190px] space-y-1">
        <Label>Agent model</Label>
        <Select
          value={filters.agentModel}
          onValueChange={(value) => onChange({ ...filters, agentModel: value })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All models</SelectItem>
            {models.map((m) => (
              <SelectItem key={m} value={m}>
                {m}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex items-center gap-2 pb-0.5">
        <span className="text-2xs text-muted-foreground">
          {matched} match{matched === 1 ? "" : "es"}
        </span>
        {dirty ? (
          <Button variant="ghost" size="xs" onClick={() => onChange(DEFAULT_FILTERS)}>
            <X className="h-3 w-3" />
            Reset
          </Button>
        ) : null}
      </div>
    </div>
  );
}
