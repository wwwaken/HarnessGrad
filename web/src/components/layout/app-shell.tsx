import type { ReactNode } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { FlaskConical, GitCompareArrows, Info, Rocket, Sigma } from "lucide-react";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { TooltipProvider } from "@/components/ui/tooltip";
import { availableRunIds } from "@/lib/api";
import { useBackend } from "@/hooks/use-backend";
import { cn } from "@/lib/utils";

const NAV = [
  {
    to: "/experiments",
    label: "Experiments",
    icon: FlaskConical,
    hint: "Every run, and whether its numbers can be quoted",
  },
  {
    to: "/compare",
    label: "Compare",
    icon: GitCompareArrows,
    hint: "Two runs side by side: which tasks moved",
  },
  {
    to: "/launch",
    label: "Launch",
    icon: Rocket,
    hint: "Configure a run and read the argv it would produce",
  },
];

function NavItem({ to, label, icon: Icon, hint }: (typeof NAV)[number]) {
  return (
    <NavLink
      to={to}
      title={hint}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-2 rounded-md px-2 py-1.5 text-xs font-medium transition-colors",
          isActive
            ? "bg-accent text-accent-foreground"
            : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
        )
      }
    >
      <Icon className="h-3.5 w-3.5" />
      {label}
    </NavLink>
  );
}

/**
 * The shell: a fixed rail, a content column, and one honesty banner.
 *
 * The banner is not removable while the fixtures stand in for the API, and it says which
 * source is live rather than only whether fixtures are. `useBackend()` re-renders it the
 * moment the startup `/api/health` probe resolves; a screenshot of this UI will outlive the
 * session that produced it, and a fixture number that reaches a slide without that banner is
 * the exact class of error the platform exists to prevent.
 */
export function AppShell() {
  const backend = useBackend();
  const live = backend.mode === "live";
  return (
    <TooltipProvider delayDuration={200}>
      <div className="flex min-h-screen">
        <aside className="sticky top-0 hidden h-screen w-56 shrink-0 flex-col border-r border-border bg-card/40 md:flex">
          <div className="flex items-center gap-2 px-3 py-3">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <Sigma className="h-4 w-4" />
            </div>
            <div className="leading-tight">
              <div className="text-xs font-semibold tracking-tight">HarnessGrad</div>
              <div className="text-2xs text-muted-foreground">harness self-improvement</div>
            </div>
          </div>
          <nav className="flex flex-col gap-0.5 px-2 pt-1">
            {NAV.map((item) => (
              <NavItem key={item.to} {...item} />
            ))}
          </nav>
          <div className="mt-3 px-3">
            <div className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
              {live ? "Shortcuts" : "Fixture runs"}
            </div>
            <div className="mt-1 space-y-0.5">
              {availableRunIds().map((id) => (
                <NavLink
                  key={id}
                  to={`/runs/${id}`}
                  className={({ isActive }) =>
                    cn(
                      "block truncate rounded px-1.5 py-1 font-mono text-2xs transition-colors",
                      isActive
                        ? "bg-accent text-accent-foreground"
                        : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
                    )
                  }
                >
                  {id}
                </NavLink>
              ))}
            </div>
          </div>
          <div className="mt-auto space-y-2 border-t border-border p-3">
            <div className="flex items-start gap-1.5 text-2xs leading-snug text-muted-foreground">
              <Info className="mt-0.5 h-3 w-3 shrink-0" />
              <span>
                <span
                  className={cn(
                    "font-medium",
                    backend.status === "unreachable"
                      ? "text-fail"
                      : live
                        ? "text-pass"
                        : "text-foreground",
                  )}
                >
                  {backend.label}.
                </span>{" "}
                {live
                  ? `Serving ${backend.runs ?? "?"} run row(s) from the read API.`
                  : "Reading the curated fixture subset; the read API is not in use."}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-2xs text-muted-foreground">v0.1 scaffold</span>
              <ThemeToggle />
            </div>
          </div>
        </aside>
        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-30 border-b border-border bg-background/90 backdrop-blur">
            <div className="flex items-center justify-between gap-3 px-4 py-2">
              <div className="flex items-center gap-2 md:hidden">
                <Sigma className="h-4 w-4" />
                <span className="text-xs font-semibold">HarnessGrad</span>
              </div>
              <nav className="flex items-center gap-1 md:hidden">
                {NAV.map(({ to, label }) => (
                  <NavLink
                    key={to}
                    to={to}
                    className={({ isActive }) =>
                      cn(
                        "rounded px-1.5 py-1 text-2xs font-medium",
                        isActive ? "bg-accent" : "text-muted-foreground",
                      )
                    }
                  >
                    {label}
                  </NavLink>
                ))}
              </nav>
              <div className="hidden min-w-0 flex-1 items-center gap-2 text-2xs text-muted-foreground md:flex">
                <span
                  className={cn(
                    "shrink-0 rounded px-1 py-0.5 font-medium",
                    backend.status === "unreachable"
                      ? "bg-fail/15 text-fail"
                      : live
                        ? "bg-pass/15 text-pass"
                        : "bg-muted text-foreground",
                  )}
                >
                  {backend.label}
                </span>
                <span className="truncate">{backend.note}</span>
              </div>
              <div className="md:hidden">
                <ThemeToggle />
              </div>
            </div>
          </header>
          <main className="min-w-0 flex-1 px-4 py-4 lg:px-6">
            <Outlet />
          </main>
        </div>
      </div>
    </TooltipProvider>
  );
}

export function PageContainer({ children }: { children: ReactNode }) {
  return <div className="mx-auto w-full max-w-[1500px] space-y-4">{children}</div>;
}
