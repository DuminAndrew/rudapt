import { cn } from "@/lib/utils";

export function Badge({
  className,
  variant = "default",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { variant?: "default" | "cyan" | "rose" | "violet" }) {
  const v = {
    default: "bg-white/10 text-ink",
    cyan: "bg-cyan-brand/15 text-cyan-brand border border-cyan-brand/30",
    rose: "bg-rose-brand/15 text-rose-brand border border-rose-brand/30",
    violet: "bg-violet-brand/15 text-violet-brand border border-violet-brand/30",
  }[variant];
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        v,
        className
      )}
      {...props}
    />
  );
}
