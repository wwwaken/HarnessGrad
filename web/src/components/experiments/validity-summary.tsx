import { ShieldCheck, ShieldHalf, ShieldX, CircleSlash, CircleHelp } from "lucide-react";
import { Stat } from "@/components/common/stat";
import { quotableSummary, type ValidityFilter } from "@/logic/certify";
import { useT } from "@/i18n";
import { cn } from "@/lib/utils";
import type { RunSummary } from "@/types";

/**
 * The four numbers a reader needs before quoting anything, each of which is also a filter.
 *
 * `Quotable` is the headline because it is the actual question; `Certified` is the stricter
 * property and is deliberately shown *beside* it, not instead of it. The difference between
 * the two is the number of runs whose numbers cannot be compared with a run made by
 * different code — which is a real cost, not a formality.
 */
export function ValiditySummary({
  rows,
  activeFilter,
  onFilter,
}: {
  rows: RunSummary[];
  activeFilter: ValidityFilter;
  onFilter: (filter: ValidityFilter) => void;
}) {
  const t = useT();
  const summary = quotableSummary(rows);

  const tiles = [
    {
      label: t("experiments.tileRuns"),
      value: summary.total,
      hint: t("experiments.tileRunsHint"),
      filter: "all" as ValidityFilter,
      icon: null,
      tone: "neutral" as const,
    },
    {
      label: t("experiments.tileQuotable"),
      value: summary.quotable,
      hint: t("experiments.tileQuotableHint", {
        valid: summary.valid,
        certified: summary.certified,
      }),
      filter: "quotable" as ValidityFilter,
      icon: ShieldCheck,
      tone: "info" as const,
    },
    {
      label: t("experiments.tileCertified"),
      value: summary.certified,
      hint: t("experiments.tileCertifiedHint"),
      filter: "certified" as ValidityFilter,
      icon: ShieldHalf,
      tone: "pass" as const,
    },
    {
      label: t("experiments.tileInvalid"),
      value: summary.invalid,
      hint: t("experiments.tileInvalidHint"),
      filter: "invalid" as ValidityFilter,
      icon: ShieldX,
      tone: "fail" as const,
    },
    {
      label: t("experiments.tileNoPoints"),
      value: summary.noPoints,
      hint: t("experiments.tileNoPointsHint"),
      filter: "no-points" as ValidityFilter,
      icon: CircleSlash,
      tone: "neutral" as const,
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-2 md:grid-cols-5">
      {tiles.map((tile) => {
        const Icon = tile.icon;
        const active = activeFilter === tile.filter;
        return (
          <button
            key={tile.filter}
            type="button"
            onClick={() => onFilter(active ? "all" : tile.filter)}
            className={cn(
              "rounded-lg text-left transition-colors",
              active ? "ring-1 ring-ring" : "hover:bg-accent/40",
            )}
            title={
              active
                ? t("experiments.clearFilter")
                : t("experiments.filterBy", { label: tile.label })
            }
          >
            <Stat
              label={
                <span className="inline-flex items-center gap-1">
                  {Icon ? <Icon className="h-3 w-3" /> : <CircleHelp className="h-3 w-3" />}
                  {tile.label}
                </span>
              }
              value={tile.value}
              hint={tile.hint}
              tone={tile.tone}
              className={cn("h-full", active && "border-ring")}
            />
          </button>
        );
      })}
    </div>
  );
}
