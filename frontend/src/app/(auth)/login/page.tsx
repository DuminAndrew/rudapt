"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, tokens } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const r = await api<{ access_token: string; refresh_token: string }>("/api/auth/login", {
        method: "POST",
        json: { email, password },
        auth: false,
      });
      tokens.set(r.access_token, r.refresh_token);
      router.push("/feed");
    } catch (e: any) {
      setErr(e.message || "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <div className="mb-8 flex justify-center"><Logo /></div>
        <div className="glass-card p-8 ring-glow">
          <h1 className="font-display text-3xl font-bold">Вход</h1>
          <p className="mt-1 text-sm text-ink-muted">С возвращением в RuDapt.</p>
          <form onSubmit={submit} className="mt-6 space-y-4">
            <Input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <Input type="password" placeholder="Пароль" value={password} onChange={(e) => setPassword(e.target.value)} required />
            {err && <div className="text-sm text-rose-brand">{err}</div>}
            <Button type="submit" size="lg" className="w-full" disabled={loading}>
              {loading ? "..." : "Войти"}
            </Button>
          </form>
          <div className="mt-6 text-sm text-ink-muted text-center">
            Нет аккаунта? <Link href="/register" className="text-violet-brand hover:underline">Регистрация</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
