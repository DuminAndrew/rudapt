"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Send, Trash2, Copy, Check, Bot, ExternalLink } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

type Sub = {
  id: string;
  chat_id: number;
  username: string | null;
  categories: string[] | null;
  created_at: string;
};

type Link = {
  code: string;
  expires_at: string;
  bot_username: string | null;
  deep_link: string | null;
};

export default function TelegramPage() {
  const qc = useQueryClient();
  const [link, setLink] = useState<Link | null>(null);
  const [copied, setCopied] = useState(false);
  const [editing, setEditing] = useState<string | null>(null);
  const [cats, setCats] = useState("");

  const { data: subs, isLoading } = useQuery({
    queryKey: ["tg-subs"],
    queryFn: () => api<Sub[]>("/api/telegram/subscriptions"),
    refetchInterval: 5000,
  });

  const linkMut = useMutation({
    mutationFn: () => api<Link>("/api/telegram/link-code", { method: "POST" }),
    onSuccess: (l) => setLink(l),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, categories }: { id: string; categories: string[] }) =>
      api(`/api/telegram/subscriptions/${id}`, { method: "PATCH", json: { categories } }),
    onSuccess: () => {
      setEditing(null);
      qc.invalidateQueries({ queryKey: ["tg-subs"] });
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => api(`/api/telegram/subscriptions/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tg-subs"] }),
  });

  return (
    <div className="container mx-auto px-6 py-10 max-w-3xl">
      <h1 className="font-display text-4xl font-black mb-2">
        <span className="text-gradient">Telegram</span> бот
      </h1>
      <p className="text-ink-muted">
        Привяжи Telegram-чат к аккаунту и подпишись на категории — бот ответит на{" "}
        <code className="text-ink">/digest</code> свежими стартапами.
      </p>

      <div className="glass-card p-6 mt-8">
        <h2 className="font-display text-xl font-bold mb-2 flex items-center gap-2">
          <Bot className="h-5 w-5" /> Привязка чата
        </h2>
        <p className="text-sm text-ink-muted">
          Получи одноразовый код, открой бота и отправь ему{" "}
          <code className="text-ink">/start КОД</code>.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Button onClick={() => linkMut.mutate()} disabled={linkMut.isPending}>
            <Send className="h-4 w-4" />
            {linkMut.isPending ? "..." : "Получить код"}
          </Button>
          {link?.deep_link && (
            <a href={link.deep_link} target="_blank" rel="noreferrer">
              <Button variant="ghost">
                <ExternalLink className="h-4 w-4" /> Открыть бота
              </Button>
            </a>
          )}
        </div>
        {link && (
          <div className="mt-4 rounded-xl border border-violet-brand/40 bg-violet-brand/10 p-4">
            <div className="text-xs text-ink-muted">Код (действует 10 минут):</div>
            <div className="mt-1 flex items-center gap-3">
              <code className="text-xl font-mono font-bold tracking-widest text-ink select-all">
                {link.code}
              </code>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  navigator.clipboard.writeText(link.code);
                  setCopied(true);
                  setTimeout(() => setCopied(false), 1500);
                }}
              >
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>
            <div className="text-xs text-ink-dim mt-2">
              Команды бота: <code>/subscribe ai, fintech</code> · <code>/list</code> ·{" "}
              <code>/digest</code> · <code>/unsubscribe</code>
            </div>
          </div>
        )}
      </div>

      <div className="mt-8">
        <h2 className="font-display text-xl font-bold mb-4">Привязанные чаты</h2>
        {isLoading ? (
          <div className="glass-card h-24 animate-pulse" />
        ) : !subs?.length ? (
          <div className="glass-card p-6 text-ink-muted">
            Пока ни одного чата. Получи код выше и отправь его боту.
          </div>
        ) : (
          <div className="space-y-3">
            {subs.map((s) => (
              <div key={s.id} className="glass-card p-4">
                <div className="flex items-center justify-between flex-wrap gap-3">
                  <div className="min-w-0">
                    <div className="font-display font-bold">
                      {s.username ? `@${s.username}` : `chat ${s.chat_id}`}
                    </div>
                    <div className="text-xs text-ink-dim mt-1">
                      {new Date(s.created_at).toLocaleString("ru-RU")}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteMut.mutate(s.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
                <div className="mt-3 flex items-center gap-2 flex-wrap">
                  {(s.categories || []).map((c) => (
                    <Badge key={c} variant="violet">
                      {c}
                    </Badge>
                  ))}
                  {(!s.categories || s.categories.length === 0) && (
                    <span className="text-xs text-ink-dim">без категорий</span>
                  )}
                </div>
                {editing === s.id ? (
                  <div className="mt-3 flex gap-2">
                    <Input
                      placeholder="ai, fintech, b2b"
                      value={cats}
                      onChange={(e) => setCats(e.target.value)}
                    />
                    <Button
                      size="sm"
                      onClick={() =>
                        updateMut.mutate({
                          id: s.id,
                          categories: cats
                            .split(",")
                            .map((c) => c.trim().toLowerCase())
                            .filter(Boolean),
                        })
                      }
                      disabled={updateMut.isPending}
                    >
                      Сохранить
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => setEditing(null)}>
                      Отмена
                    </Button>
                  </div>
                ) : (
                  <Button
                    size="sm"
                    variant="ghost"
                    className="mt-3"
                    onClick={() => {
                      setEditing(s.id);
                      setCats((s.categories || []).join(", "));
                    }}
                  >
                    Изменить категории
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
