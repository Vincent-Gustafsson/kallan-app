import type { UserMini } from "@/lib/usersApi";
import { ensureCsrfCookie, csrfHeader } from "@/lib/csrf";

async function errorFrom(res: Response, fallback: string) {
  try {
    const data = await res.json();
    if (data?.detail) return String(data.detail);
  } catch {}
  return fallback;
}

export type PunishmentEvent = {
  id: number;
  target: UserMini;
  initiator: UserMini;
  confirmer: UserMini | null;

  reason: string;
  amount: number;

  created_at: string; // ISO
  confirmed_at: string | null; // ISO
  stage: "pending" | "confirmed";
};

type ListEventsOpts = {
  target_id?: number;
  limit?: number;
};

export type PunishmentStats = {
  target_id: number;
  total_amount: number;
  week_amount: number;
};

export type TakePunishmentEvent = {
  id: number;
  target: UserMini;
  judge: UserMini;
  amount: number;
  created_at: string;
};

function buildQs(base: Record<string, string>, opts?: ListEventsOpts) {
  const qs = new URLSearchParams(base);
  if (opts?.target_id != null) qs.set("target_id", String(opts.target_id));
  if (opts?.limit != null) qs.set("limit", String(opts.limit));
  return qs.toString();
}

export async function apiCreatePunishmentEvent(input: {
  target_id: number;
  amount: number; // 1..10
  reason?: string; // optional, can be ""
}): Promise<PunishmentEvent> {
  await ensureCsrfCookie();

  const res = await fetch("/api/punishments/events", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...csrfHeader(),
    },
    body: JSON.stringify({
      target_id: input.target_id,
      amount: input.amount,
      reason: input.reason ?? "",
    }),
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Kunde inte ge straff"));
  return await res.json();
}

export async function apiListPendingPunishmentEvents(
  opts?: ListEventsOpts,
): Promise<PunishmentEvent[]> {
  const q = buildQs({ pending: "1" }, opts);

  const res = await fetch(`/api/punishments/events?${q}`, {
    method: "GET",
    credentials: "include",
    headers: { Accept: "application/json" },
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Kunde inte ladda straff"));
  return await res.json();
}

export async function apiListConfirmedPunishmentEvents(
  opts?: ListEventsOpts,
): Promise<PunishmentEvent[]> {
  const q = buildQs({ confirmed: "1" }, opts);

  const res = await fetch(`/api/punishments/events?${q}`, {
    method: "GET",
    credentials: "include",
    headers: { Accept: "application/json" },
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Kunde inte ladda bekräftade straff"));
  return await res.json();
}

export async function apiConfirmPunishmentEvent(eventId: number): Promise<PunishmentEvent> {
  await ensureCsrfCookie();

  const res = await fetch(`/api/punishments/events/${eventId}/confirm`, {
    method: "POST",
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...csrfHeader(),
    },
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Kunde inte bekräfta straff"));
  return await res.json();
}

export async function apiDeletePunishmentEvent(eventId: number): Promise<void> {
  await ensureCsrfCookie();

  const res = await fetch(`/api/punishments/events/${eventId}`, {
    method: "DELETE",
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...csrfHeader(),
    },
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Kunde inte ångra straff"));
}

export async function apiPunishmentStats(opts?: { target_id?: number }): Promise<PunishmentStats> {
  const qs = new URLSearchParams();
  if (opts?.target_id != null) qs.set("target_id", String(opts.target_id));

  const res = await fetch(`/api/punishments/stats?${qs.toString()}`, {
    method: "GET",
    credentials: "include",
    headers: { Accept: "application/json" },
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Kunde inte ladda statistik"));
  return await res.json();
}

export async function apiTakePunishmentEvent(input: {
  target_id: number;
  amount: number;
}): Promise<TakePunishmentEvent> {
  await ensureCsrfCookie();

  const res = await fetch("/api/punishments/take", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...csrfHeader(),
    },
    body: JSON.stringify(input),
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Kunde inte stryka straff"));
  return await res.json();
}
