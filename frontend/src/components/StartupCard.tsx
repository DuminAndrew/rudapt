"use client";
import { Sparkles, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export type Startup = {
  id: string;
  name: string;
  source: string;
  tagline?: string | null;
  description?: string | null;
  url?: string | null;
  logo_url?: string | null;
  categories?: string[] | null;
  votes?: number | null;
  launched_at?: string | null;
};

const SOURCE_BADGE: Record<string, "cyan" | "rose" | "violet"> = {
  producthunt: "rose",
  yc: "cyan",
  crunchbase: "violet",
};

export function StartupCard({ startup, onPick }: { startup: Startup; onPick: (s: Startup) => void }) {
  return (
    <div className="glass-card p-6 flex flex-col gap-4 hover:bg-white/[0.06] hover:ring-glow transition group">
      <div className="flex items-start gap-4">
        {startup.logo_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={startup.logo_url}
            alt={startup.name}
            className="h-12 w-12 rounded-xl object-cover bg-white/5"
          />
        ) : (
          <div className="h-12 w-12 rounded-xl bg-grad-violet flex items-center justify-center font-bold">
            {startup.name.slice(0, 1)}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <h3 className="font-display text-lg font-bold truncate">{startup.name}</h3>
          <p className="text-sm text-ink-muted line-clamp-2">{startup.tagline || startup.description}</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <Badge variant={SOURCE_BADGE[startup.source] || "default"}>{startup.source}</Badge>
        {(startup.categories || []).slice(0, 3).map((c) => (
          <Badge key={c}>{c}</Badge>
        ))}
        {startup.votes != null && <Badge>↑ {startup.votes}</Badge>}
      </div>

      <div className="flex items-center gap-2 mt-auto">
        <Button size="sm" className="flex-1" onClick={() => onPick(startup)}>
          <Sparkles className="h-4 w-4" /> Сгенерировать план
        </Button>
        {startup.url && (
          <a
            href={startup.url}
            target="_blank"
            rel="noreferrer"
            className="rounded-xl border border-white/10 p-2 text-ink-muted hover:text-ink hover:bg-white/5"
            title="Открыть источник"
          >
            <ExternalLink className="h-4 w-4" />
          </a>
        )}
      </div>
    </div>
  );
}
