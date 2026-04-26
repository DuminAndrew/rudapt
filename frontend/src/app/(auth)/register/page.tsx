"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, tokens } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const r = await api<{ access_token: string; refresh_token: string }>("/api/auth/register", {
        method: "POST",
        json: { email, password, full_name: name || null },
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
          <h1 className="font-display text-3xl font-bold">Создать аккаунт</h1>
          <p className="mt-1 text-sm text-ink-muted">Free план — 5 генераций в месяц.</p>
          <form onSubmit={submit} className="mt-6 space-y-4">
            <Input placeholder="Имя (необязательно)" value={name} onChange={(e) => setName(e.target.value)} />
            <Input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <Input type="password" placeholder="Пароль (мин. 8 символов)" value={password} onChange={(e) => setPassword(e.target.value)} minLength={8} required />
            {err && <div className="text-sm text-rose-brand">{err}</div>}
            <Button type="submit" size="lg" className="w-full" disabled={loading}>
              {loading ? "..." : "Зарегистрироваться"}
            </Button>
          </form>
          <div className="mt-6 text-sm text-ink-muted text-center">
            Уже есть аккаунт? <Link href="/login" className="text-violet-brand hover:underline">Войти</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
