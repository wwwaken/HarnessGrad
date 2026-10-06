import { Moon, Sun, MonitorCog } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useTheme, type Theme } from "@/lib/theme";
import { useT } from "@/i18n";
import type { TranslationKey } from "@/i18n/en";

const OPTIONS: Array<{ value: Theme; label: TranslationKey; icon: typeof Sun }> = [
  { value: "light", label: "nav.themeLight", icon: Sun },
  { value: "dark", label: "nav.themeDark", icon: Moon },
  { value: "system", label: "nav.themeSystem", icon: MonitorCog },
];

/** Light/dark/system, the whole theme surface in one control. */
export function ThemeToggle() {
  const t = useT();
  const { theme, resolved, setTheme } = useTheme();
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8" title={`${t("nav.theme")}: ${t(OPTIONS.find((o) => o.value === theme)?.label ?? "nav.theme")}`}>
          {resolved === "dark" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
          <span className="sr-only">{t("nav.changeTheme")}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>{t("nav.theme")}</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {OPTIONS.map(({ value, label, icon: Icon }) => (
          <DropdownMenuItem key={value} onSelect={() => setTheme(value)}>
            <Icon className="h-3.5 w-3.5" />
            <span className="flex-1">{t(label)}</span>
            {theme === value ? <span className="text-2xs text-muted-foreground">{t("nav.themeCurrent")}</span> : null}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
