"use client";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Check, Sparkles, Crown, Zap, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

type Status = {
  plan: string;
  is_pro: boolean;
  expires_at: string | null;
  provider_configured: boolean;
};

const FREE = [
  "5 генераций бизнес-плана / месяц",
  "Лента стартапов с фильтрами",
  "Telegram-бот · /digest",
  "1 API ключ · 60 запросов/мин",
];

const PRO = [
  "Безлимит генераций",
  "Сравнение до 5 регионов в одном плане",
  "Экспорт в PDF",
  "10 API ключей · до 1000 запросов/мин",
  "Приоритет в очереди генерации",
  "Email-поддержка",
];

export default function BillingPage() {
  const { data, refetch } = useQuery({
    queryKey: ["billing-status"],
    queryFn: () => api<Status>("/api/billing/status"),
  });

  const checkoutMut = useMutation({
    mutationFn: () =>
      api<{ payment_url: string }>("/api/billing/checkout", { method: "POST" }),
    onSuccess: ({ payment_url }) => {
      window.location.href = payment_url;
    },
  });

  return (
    <div className="container mx-auto px-6 py-10 max-w-5xl">
      <h1 className="font-display text-4xl font-black mb-2 text-center">
        Подписка <span className="text-gradient">RuDapt</span>
      </h1>
      <p className="text-ink-muted text-center max-w-xl mx-auto">
        Платежи через <strong className="text-ink">Platega</strong>. Российские карты, СБП и
        электронные кошельки.
      </p>

      {data?.is_pro && (
        <div className="glass-card mt-6 p-5 border border-cyan-brand/40 flex items-center gap-3">
          <Crown className="h-6 w-6 text-cyan-brand" />
          <div className="flex-1">
            <div className="font-display font-bold">Pro активен</div>
            <div className="text-xs text-ink-muted">
              {data.expires_at &&
                `до ${new Date(data.expires_at).toLocaleDateString("ru-RU")}`}
            </div>
          </div>
          <Badge variant="cyan">Pro</Badge>
        </div>
      )}

      {data && !data.provider_configured && (
        <div className="glass-card mt-6 p-4 border border-rose-brand/40 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-rose-brand mt-0.5 shrink-0" />
          <div className="text-sm text-ink-muted">
            Платежный провайдер не настроен (нет{" "}
            <code className="text-ink">PLATEGA_MERCHANT_ID</code> и{" "}
            <code className="text-ink">PLATEGA_SECRET</code> в env). Бесплатный план доступен
            без ограничений в dev-режиме.
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6 mt-8">
        <div className="glass-card p-8 flex flex-col">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-grad-cyan flex items-center justify-center">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <h3 className="font-display text-2xl font-bold">Free</h3>
          </div>
          <div className="mt-4">
            <span className="text-4xl font-display font-black">0 ₽</span>
            <span className="text-ink-muted">/мес</span>
          </div>
          <ul className="mt-6 space-y-3 flex-1">
            {FREE.map((f) => (
              <li key={f} className="flex items-start gap-2 text-sm">
                <Check className="h-4 w-4 mt-0.5 text-cyan-brand shrink-0" />
                <span>{f}</span>
              </li>
            ))}
          </ul>
          <Button variant="outline" className="mt-6" disabled>
            {data && !data.is_pro ? "Текущий план" : "Базовый план"}
          </Button>
        </div>

        <div className="glass-card p-8 flex flex-col ring-glow border border-violet-brand/30 relative overflow-hidden">
          <div className="absolute top-3 right-3">
            <Badge variant="violet">популярный</Badge>
          </div>
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-grad-brand flex items-center justify-center">
              <Crown className="h-5 w-5 text-white" />
            </div>
            <h3 className="font-display text-2xl font-bold">Pro</h3>
          </div>
          <div className="mt-4">
            <span className="text-4xl font-display font-black text-gradient">1 490 ₽</span>
            <span className="text-ink-muted">/мес</span>
          </div>
          <ul className="mt-6 space-y-3 flex-1">
            {PRO.map((f) => (
              <li key={f} className="flex items-start gap-2 text-sm">
                <Check className="h-4 w-4 mt-0.5 text-violet-brand shrink-0" />
                <span>{f}</span>
              </li>
            ))}
          </ul>
          <Button
            size="lg"
            className="mt-6"
            disabled={
              data?.is_pro || !data?.provider_configured || checkoutMut.isPending
            }
            onClick={() => checkoutMut.mutate()}
          >
            <Sparkles className="h-4 w-4" />
            {data?.is_pro
              ? "Активен"
              : checkoutMut.isPending
              ? "Создаю платёж…"
              : "Оформить Pro"}
          </Button>
          {checkoutMut.isError && (
            <div className="mt-3 text-xs text-rose-brand">
              {(checkoutMut.error as Error).message}
            </div>
          )}
        </div>
      </div>

      <p className="text-center text-xs text-ink-dim mt-8">
        Оплачивая подписку, вы соглашаетесь с условиями оферты. Возврат средств — в течение
        14 дней при отсутствии использования сверх квоты Free плана.
      </p>
    </div>
  );
}
