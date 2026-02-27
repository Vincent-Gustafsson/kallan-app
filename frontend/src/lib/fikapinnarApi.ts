import { ensureCsrfCookie, csrfHeader } from "@/lib/csrf";

export type FikapinneStats = {
  target_id: number;
  total_amount: number;
  month_amount: number;
};

async function errorFrom(res: Response, fallback: string) {
  try {
    const data = await res.json();
    if (data?.detail) return String(data.detail);
  } catch {}
  return fallback;
}

export async function apiGiveFikapinne(target_id: number): Promise<void> {
  await ensureCsrfCookie();

  const res = await fetch("/api/punishments/fikapinnar/give", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...csrfHeader(),
    },
    body: JSON.stringify({ target_id }),
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Kunde inte ge fikapinne"));
}

export async function apiTakeFikapinnar(target_id: number, amount: 3 | 5): Promise<void> {
  await ensureCsrfCookie();

  const res = await fetch("/api/punishments/fikapinnar/take", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...csrfHeader(),
    },
    body: JSON.stringify({ target_id, amount }),
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Kunde inte stryka fikapinnar"));
}

export async function apiFikapinneStats(params?: { target_id?: number }): Promise<FikapinneStats> {
  const qs = params?.target_id ? `?target_id=${params.target_id}` : "";
  const res = await fetch(`/api/punishments/fikapinnar/stats${qs}`, {
    method: "GET",
    credentials: "include",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(await errorFrom(res, "Kunde inte ladda fikapinne-statistik"));
  return await res.json();
}
