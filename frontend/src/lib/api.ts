import Cookies from "js-cookie";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const ACCESS = "rudapt_access";
const REFRESH = "rudapt_refresh";

export const tokens = {
  get access() { return Cookies.get(ACCESS); },
  get refresh() { return Cookies.get(REFRESH); },
  set(access: string, refresh: string) {
    Cookies.set(ACCESS, access, { sameSite: "lax", secure: location.protocol === "https:" });
    Cookies.set(REFRESH, refresh, { sameSite: "lax", secure: location.protocol === "https:" });
  },
  clear() { Cookies.remove(ACCESS); Cookies.remove(REFRESH); },
};

async function refreshAccess(): Promise<boolean> {
  const r = tokens.refresh;
  if (!r) return false;
  const res = await fetch(`${API_URL}/api/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: r }),
  });
  if (!res.ok) return false;
  const data = await res.json();
  tokens.set(data.access_token, data.refresh_token);
  return true;
}

export async function api<T = unknown>(
  path: string,
  init: RequestInit & { json?: unknown; auth?: boolean } = {}
): Promise<T> {
  const { json, auth = true, headers, ...rest } = init;
  const doFetch = async (): Promise<Response> => {
    const h: Record<string, string> = { ...(headers as Record<string, string>) };
    if (json !== undefined) h["Content-Type"] = "application/json";
    if (auth && tokens.access) h["Authorization"] = `Bearer ${tokens.access}`;
    return fetch(`${API_URL}${path}`, { ...rest, headers: h, body: json !== undefined ? JSON.stringify(json) : rest.body });
  };

  let res = await doFetch();
  if (res.status === 401 && auth && (await refreshAccess())) res = await doFetch();
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${text || res.statusText}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
