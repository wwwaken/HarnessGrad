import { ShieldCheck, ShieldHalf, ShieldX, CircleSlash, CircleHelp } from "lucide-react";
import { Stat } from "@/components/common/stat";
import { quotableSummary, type ValidityFilter } from "@/logic/certify";
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
  const summary = quotableSummary(rows);

  const tiles = [
    {
      label: "Runs",
      value: summary.total,
      hint: "every run directory in the fixture index",
      filter: "all" as ValidityFilter,
      icon: null,
      tone: "neutral" as const,
    },
    {
      label: "Quotable",
      value: summary.quotable,
      hint: `valid or certified — ${summary.valid} valid, ${summary.certified} certified`,
      filter: "quotable" as ValidityFilter,
      icon: ShieldCheck,
      tone: "info" as const,
    },
    {
      label: "Certified",
      value: summary.certified,
      hint: "the record names the platform that produced it",
      filter: "certified" as ValidityFilter,
      icon: ShieldHalf,
      tone: "pass" as const,
    },
    {
      label: "Invalid",
      value: summary.invalid,
      hint: "a point cannot be read as a measurement, or the platform was touched",
      filter: "invalid" as ValidityFilter,
      icon: ShieldX,
      tone: "fail" as const,
    },
    {
      label: "Not measured",
      value: summary.noPoints,
      hint: "no curve.jsonl: there is no number to be wrong about",
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
            key={tile.label}
            type="button"
            onClick={() => onFilter(active ? "all" : tile.filter)}
            className={cn(
              "rounded-lg text-left transition-colors",
              active ? "ring-1 ring-ring" : "hover:bg-accent/40",
            )}
            title={active ? "Clear this filter" : `Filter: ${tile.label}`}
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
