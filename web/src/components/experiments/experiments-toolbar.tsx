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
import { useT } from "@/i18n";
import type { TranslationKey } from "@/i18n/en";
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

/**
 * The validity choices, named by translation key rather than by label: the key is a constant
 * and the label is not, so this map can stay at module scope and be read through `t` at render.
 */
const VALIDITY_LABELS: Record<ValidityFilter, TranslationKey> = {
  all: "experiments.validityAll",
  quotable: "experiments.validityQuotable",
  certified: "experiments.validityCertified",
  valid: "experiments.validityValid",
  invalid: "experiments.validityInvalid",
  "no-points": "experiments.validityNoPoints",
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
  const t = useT();
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
        <Label htmlFor="run-search">{t("experiments.searchLabel")}</Label>
        <div className="relative">
          <Search className="pointer-events-none absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            id="run-search"
            value={filters.search}
            onChange={(e) => onChange({ ...filters, search: e.target.value })}
            placeholder={t("experiments.searchPlaceholder")}
            className="h-8 pl-7 text-xs"
          />
        </div>
      </div>
      <div className="w-[220px] space-y-1">
        <Label>{t("experiments.validityLabel")}</Label>
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
                {t(VALIDITY_LABELS[key])}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="w-[150px] space-y-1">
        <Label>{t("experiments.harnessLabel")}</Label>
        <Select
          value={filters.harness}
          onValueChange={(value) => onChange({ ...filters, harness: value })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t("experiments.allHarnesses")}</SelectItem>
            {harnesses.map((h) => (
              <SelectItem key={h} value={h}>
                {h}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="w-[170px] space-y-1">
        <Label>{t("experiments.datasetLabel")}</Label>
        <Select
          value={filters.dataset}
          onValueChange={(value) => onChange({ ...filters, dataset: value })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t("experiments.allDatasets")}</SelectItem>
            {datasets.map((d) => (
              <SelectItem key={d} value={d}>
                {d}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="w-[190px] space-y-1">
        <Label>{t("experiments.agentModelLabel")}</Label>
        <Select
          value={filters.agentModel}
          onValueChange={(value) => onChange({ ...filters, agentModel: value })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t("experiments.allModels")}</SelectItem>
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
          {t(matched === 1 ? "experiments.matchOne" : "experiments.matchMany", { n: matched })}
        </span>
        {dirty ? (
          <Button variant="ghost" size="xs" onClick={() => onChange(DEFAULT_FILTERS)}>
            <X className="h-3 w-3" />
            {t("experiments.reset")}
          </Button>
        ) : null}
      </div>
    </div>
  );
}
