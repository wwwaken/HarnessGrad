import { Languages } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useI18n } from "@/i18n";
import { LANGS, LANG_LABEL } from "@/lib/lang";
/**
 * The language control, shaped like `ThemeToggle` because it is the same kind of thing: one
 * preference with a detected default and a remembered override.
 *
 * **"Automatic" is a real third state, and it is the default.** A reader who has never
 * touched this menu has no stored preference, so the app follows the browser — including
 * when they move to a machine set to another language. Once they choose explicitly, the
 * choice wins and keeps winning. Dropping the automatic entry would make the first click
 * irreversible, which is a small thing to get wrong and an annoying one to live with.
 *
 * The automatic entry reports what it currently resolves to, so a reader can tell what the
 * app thinks their browser asked for without having to reason about `navigator.languages`.
 */
export function LanguageToggle() {
  const { lang, choice, setLang, setAuto, t } = useI18n();
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8" title={t("nav.changeLanguage")}>
          <Languages className="h-4 w-4" />
          <span className="sr-only">{t("nav.changeLanguage")}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>{t("nav.language")}</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem onSelect={setAuto}>
          <span className="flex-1">{t("nav.languageAuto")}</span>
          <span className="text-2xs text-muted-foreground">
            {choice === "auto" ? `${LANG_LABEL[lang]} · ${t("nav.themeCurrent")}` : t("nav.languageAutoHint")}
          </span>
        </DropdownMenuItem>
        {LANGS.map((value) => (
          <DropdownMenuItem key={value} onSelect={() => setLang(value)}>
            <span className="flex-1">{LANG_LABEL[value]}</span>
            {choice === value ? (
              <span className="text-2xs text-muted-foreground">{t("nav.themeCurrent")}</span>
            ) : null}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
