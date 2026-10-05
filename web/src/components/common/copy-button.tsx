import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { Button, type ButtonProps } from "@/components/ui/button";

/** Copy-to-clipboard for a run id, an argv line, or a patch. */
export function CopyButton({
  value,
  label = "Copy",
  size = "xs",
  variant = "ghost",
  className,
}: {
  value: string;
  label?: string;
  size?: ButtonProps["size"];
  variant?: ButtonProps["variant"];
  className?: string;
}) {
  const [copied, setCopied] = useState(false);
  return (
    <Button
      type="button"
      size={size}
      variant={variant}
      className={className}
      title={label}
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(value);
          setCopied(true);
          window.setTimeout(() => setCopied(false), 1500);
        } catch {
          /* clipboard denied (insecure origin): leave the button as it was */
        }
      }}
    >
      {copied ? <Check className="h-3 w-3 text-pass" /> : <Copy className="h-3 w-3" />}
      <span className="sr-only">{label}</span>
    </Button>
  );
}
