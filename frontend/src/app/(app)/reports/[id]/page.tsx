"use client";
import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Loader2, Download, ExternalLink } from "lucide-react";
import Link from "next/link";

type ReportDetail = {
  id: string;
  region: string;
  status: "pending" | "running" | "done" | "failed";
  model: string | null;
  content: any;
  content_md: string | null;
  error: string | null;
  created_at: string;
  finished_at: string | null;
  startup?: {
    id: string;
    name: string;
    tagline?: string | null;
    url?: string | null;
    logo_url?: string | null;
    source: string;
  } | null;
};

export default function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data, error } = useQuery({
    queryKey: ["report", id],
    queryFn: () => api<ReportDetail>(`/api/reports/${id}`),
    refetchInterval: (q) => {
      const s = q.state.data?.status;
      return s === "pending" || s === "running" ? 3000 : false;
    },
  });

  if (error) {
    return (
      <div className="container mx-auto px-6 py-10">
        <div className="glass-card p-6 text-rose-brand">{(error as Error).message}</div>
      </div>
    );
  }
  if (!data) return null;

  const inProgress = data.status === "pending" || data.status === "running";

  function downloadMd() {
    if (!data?.content_md) return;
    const blob = new Blob([data.content_md], { type: "text/markdown;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `rudapt-${data.startup?.name || "plan"}-${data.region}.md`;
    a.click();
  }

  return (
    <div className="container mx-auto px-6 py-10 max-w-4xl">
      <Link href="/reports" className="text-sm text-ink-muted hover:text-ink">← К моим планам</Link>

      <div className="glass-card p-6 mt-4 ring-glow">
        <div className="flex items-start gap-4 flex-wrap">
          {data.startup?.logo_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={data.startup.logo_url} alt="" className="h-14 w-14 rounded-xl bg-white/5 object-cover" />
          ) : (
            <div className="h-14 w-14 rounded-xl bg-grad-violet flex items-center justify-center font-bold">
              {data.startup?.name?.slice(0, 1) || "?"}
            </div>
          )}
          <div className="flex-1 min-w-0">
            <h1 className="font-display text-3xl font-black">
              {data.startup?.name || "—"} <span className="text-ink-muted text-xl">→</span>{" "}
              <span className="text-gradient">{data.region}</span>
            </h1>
            <p className="text-sm text-ink-muted mt-1">{data.startup?.tagline}</p>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <Badge variant={data.status === "done" ? "cyan" : data.status === "failed" ? "rose" : "violet"}>
                {data.status}
              </Badge>
              {data.model && <Badge>{data.model}</Badge>}
              {data.startup?.url && (
                <a
                  href={data.startup.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-ink-muted hover:text-ink inline-flex items-center gap-1"
                >
                  <ExternalLink className="h-3 w-3" /> источник
                </a>
              )}
            </div>
          </div>
          {data.status === "done" && (
            <Button size="sm" variant="ghost" onClick={downloadMd}>
              <Download className="h-4 w-4" /> .md
            </Button>
          )}
        </div>
      </div>

      {inProgress && (
        <div className="glass-card p-10 mt-6 text-center">
          <Loader2 className="h-10 w-10 animate-spin mx-auto text-violet-brand" />
          <p className="mt-4 text-ink-muted">
            Нейросеть собирает план локализации. Обычно занимает 20–60 секунд.
          </p>
        </div>
      )}

      {data.status === "failed" && (
        <div className="glass-card p-6 mt-6 text-rose-brand">
          Ошибка генерации: {data.error || "—"}
        </div>
      )}

      {data.status === "done" && data.content_md && (
        <article className="glass-card p-8 mt-6 prose prose-invert max-w-none
                            prose-headings:font-display prose-headings:text-ink
                            prose-h1:text-3xl prose-h2:text-2xl prose-h2:text-gradient
                            prose-strong:text-ink prose-a:text-violet-brand">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.content_md}</ReactMarkdown>
        </article>
      )}
    </div>
  );
}
