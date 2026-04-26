import Link from "next/link";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, Zap, Target, ShieldCheck } from "lucide-react";

export default function Landing() {
  return (
    <div className="min-h-screen">
      <header className="container mx-auto flex items-center justify-between px-6 py-6">
        <Logo />
        <nav className="flex items-center gap-3">
          <Link href="/login" className="text-sm text-ink-muted hover:text-ink">Войти</Link>
          <Button asChild size="sm"><Link href="/register">Начать бесплатно</Link></Button>
        </nav>
      </header>

      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grad-hero pointer-events-none" />
        <div className="container mx-auto px-6 pt-20 pb-32 text-center relative">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-ink-muted">
            <Sparkles className="h-3 w-3 text-violet-brand" /> Powered by Claude Opus 4.7 & GPT-4o
          </span>
          <h1 className="mt-6 font-display text-5xl md:text-7xl font-black leading-[1.05]">
            Бери стартапы из США.<br />
            Запускай <span className="text-gradient">локально в РФ.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-ink-muted">
            RuDapt подтягивает свежие проекты с Product Hunt и Y Combinator, и за минуту собирает
            production-ready план локализации в нужный регион РФ — с MVP, юнит-экономикой и каналами.
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Button size="lg" asChild>
              <Link href="/register">Сгенерировать первый план <ArrowRight className="h-4 w-4" /></Link>
            </Button>
            <Button size="lg" variant="ghost" asChild>
              <Link href="/login">Войти</Link>
            </Button>
          </div>
        </div>
      </section>

      <section className="container mx-auto px-6 pb-24">
        <div className="grid gap-6 md:grid-cols-3">
          {[
            { icon: Zap, color: "from-cyan-brand to-blue-brand",
              title: "Свежие стартапы каждый день",
              text: "Парсим Product Hunt и YC, кладём в ленту с фильтрами по категориям и источнику." },
            { icon: Target, color: "from-violet-brand to-magenta-brand",
              title: "Локализация в любой регион",
              text: "85 субъектов РФ — учитываем покупательную способность и каналы продвижения." },
            { icon: ShieldCheck, color: "from-rose-brand to-orange-brand",
              title: "Готовый бизнес-план",
              text: "MVP, конкуренты, юнит-экономика, регуляторика, 90-дневный roadmap. JSON + Markdown." },
          ].map((f, i) => (
            <div key={i} className="glass-card p-6 hover:bg-white/[0.06] transition">
              <div className={`mb-4 inline-flex rounded-xl bg-gradient-to-br ${f.color} p-3`}>
                <f.icon className="h-5 w-5 text-white" />
              </div>
              <h3 className="font-display text-xl font-bold">{f.title}</h3>
              <p className="mt-2 text-sm text-ink-muted">{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-white/5 py-8 text-center text-sm text-ink-dim">
        © {new Date().getFullYear()} RuDapt. Startup Localization AI.
      </footer>
    </div>
  );
}
