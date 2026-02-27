export type UserMini = {
  id: number;
  username: string;
  avatar_url: string | null;
  tier: "vest" | "hat" | "bandana";
};

async function errorFrom(res: Response, fallback: string) {
  try {
    const data = await res.json();
    if (data?.detail) return String(data.detail);
  } catch {}
  return fallback;
}

export async function apiUsers(params?: {
  q?: string;
  excludeMe?: boolean;
  limit?: number;
}): Promise<UserMini[]> {
  const qs = new URLSearchParams();

  const q = params?.q?.trim();
  if (q) qs.set("q", q);

  const excludeMe = params?.excludeMe ?? true;
  qs.set("exclude_me", excludeMe ? "1" : "0");

  const limit = params?.limit ?? 20;
  qs.set("limit", String(limit));

  const url = qs.toString() ? `/api/users?${qs}` : "/api/users";

  const res = await fetch(url, {
    method: "GET",
    credentials: "include",
    headers: { Accept: "application/json" },
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Failed to load users"));
  return await res.json();
}

export async function apiUser(userId: number): Promise<UserMini> {
  const res = await fetch(`/api/users/${userId}`, {
    method: "GET",
    credentials: "include",
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    let msg = "Failed to load user";
    try {
      const data = await res.json();
      if (data?.detail) msg = String(data.detail);
    } catch {}
    throw new Error(msg);
  }

  return await res.json();
}
