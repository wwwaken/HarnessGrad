import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { EmptyState } from "@/components/common/states";
import { cn } from "@/lib/utils";
import type { FieldDiff } from "@/logic/compare";

/**
 * The two records compared field by field.
 *
 * `docs/refactor_references.md` §6.3 is explicit that comparing two runs means comparing two
 * *records* — "with the fields that differ and the fields that are absent on one side" — not
 * two metrics. So every field is a row, differing rows are highlighted, and `null` (absent,
 * or present-and-null) is printed as such rather than left blank. A field that is present on
 * one side and absent on the other is a difference; hiding it would report the two records
 * as more alike than they are.
 */
export function FieldDiffTable({
  fields,
  leftLabel,
  rightLabel,
  onlyDifferent = true,
}: {
  fields: FieldDiff[];
  leftLabel: string;
  rightLabel: string;
  onlyDifferent?: boolean;
}) {
  const rows = onlyDifferent ? fields.filter((f) => !f.same) : fields;
  if (!fields.length) {
    return (
      <EmptyState
        title="No comparable fields"
        description="Neither run's meta or selected point could be read, so there is nothing to diff field by field."
      />
    );
  }
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <Table>
        <TableHeader className="bg-muted/40">
          <TableRow className="hover:bg-transparent">
            <TableHead className="w-44">Field</TableHead>
            <TableHead>{leftLabel}</TableHead>
            <TableHead>{rightLabel}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.length ? (
            rows.map((row) => (
              <TableRow key={row.path} className={cn(!row.same && "bg-warn/5")}>
                <TableCell className="align-top">
                  <div className="text-xs font-medium">{row.label}</div>
                  <div className="font-mono text-2xs text-muted-foreground">{row.path}</div>
                </TableCell>
                <TableCell className="align-top">
                  <FieldCell value={row.left} differs={!row.same} />
                </TableCell>
                <TableCell className="align-top">
                  <FieldCell value={row.right} differs={!row.same} />
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={3} className="py-4 text-center text-xs text-muted-foreground">
                every recorded field is identical between these two states
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}

function FieldCell({ value, differs }: { value: string | null; differs: boolean }) {
  if (value === null) {
    return (
      <span
        className="text-2xs italic text-muted-foreground/80"
        title="absent — the recording code path did not set it"
      >
        absent
      </span>
    );
  }
  return (
    <span
      className={cn(
        "break-all font-mono text-2xs",
        differs ? "text-foreground" : "text-muted-foreground",
      )}
    >
      {value}
    </span>
  );
}
