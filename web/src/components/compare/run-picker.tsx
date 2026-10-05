import { ArrowLeftRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { RunSummary } from "@/types";

/**
 * Pick the two runs and the two rounds.
 *
 * A comparison is between two *states*, not two run directories: `ds-dgm` at round 2 against
 * `ds-rrsi` at round 2 is a different question from each run's first vs last round. The
 * round selectors are therefore always visible, and default to each run's last measured
 * round.
 */
export function RunPicker({
  runs,
  leftId,
  rightId,
  leftRound,
  rightRound,
  onLeft,
  onRight,
  onLeftRound,
  onRightRound,
  onSwap,
  roundsFor,
}: {
  runs: RunSummary[];
  leftId: string;
  rightId: string;
  leftRound: number | null;
  rightRound: number | null;
  onLeft: (runId: string) => void;
  onRight: (runId: string) => void;
  onLeftRound: (round: number) => void;
  onRightRound: (round: number) => void;
  onSwap: () => void;
  roundsFor: (runId: string) => number[];
}) {
  return (
    <div className="flex flex-wrap items-end gap-3">
      <div className="min-w-[200px] flex-1 space-y-1">
        <Label>Left run</Label>
        <Select value={leftId} onValueChange={onLeft}>
          <SelectTrigger>
            <SelectValue placeholder="pick a run" />
          </SelectTrigger>
          <SelectContent>
            {runs.map((run) => (
              <SelectItem key={run.run_id} value={run.run_id}>
                {run.run_id}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="w-[110px] space-y-1">
        <Label>Round</Label>
        <Select
          value={leftRound === null ? "" : String(leftRound)}
          onValueChange={(v) => onLeftRound(Number(v))}
        >
          <SelectTrigger>
            <SelectValue placeholder="last" />
          </SelectTrigger>
          <SelectContent>
            {roundsFor(leftId).map((round) => (
              <SelectItem key={round} value={String(round)}>
                round {round}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <Button variant="ghost" size="icon" onClick={onSwap} title="Swap sides" className="mb-0.5">
        <ArrowLeftRight className="h-4 w-4" />
      </Button>
      <div className="min-w-[200px] flex-1 space-y-1">
        <Label>Right run</Label>
        <Select value={rightId} onValueChange={onRight}>
          <SelectTrigger>
            <SelectValue placeholder="pick a run" />
          </SelectTrigger>
          <SelectContent>
            {runs.map((run) => (
              <SelectItem key={run.run_id} value={run.run_id}>
                {run.run_id}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="w-[110px] space-y-1">
        <Label>Round</Label>
        <Select
          value={rightRound === null ? "" : String(rightRound)}
          onValueChange={(v) => onRightRound(Number(v))}
        >
          <SelectTrigger>
            <SelectValue placeholder="last" />
          </SelectTrigger>
          <SelectContent>
            {roundsFor(rightId).map((round) => (
              <SelectItem key={round} value={String(round)}>
                round {round}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
