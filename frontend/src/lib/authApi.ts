export type Me = {
  id: number;
  username: string;
  avatar_url: string | null;
  force_password_reset: boolean;
  tier: "vest" | "hat" | "bandana";
  permissions: string[];
};

async function errorFrom(res: Response, fallback: string) {
  try {
    const data = await res.json();
    if (data?.detail) return String(data.detail);
  } catch {}
  return fallback;
}

function getCookie(name: string) {
  const m = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return m ? decodeURIComponent(m[1]) : null;
}

function csrfHeader() {
  const token = getCookie("csrftoken");
  return token ? { "X-CSRFToken": token } : {};
}

export async function apiCsrf(): Promise<void> {
  // Your backend uses POST /api/users/csrf
  await fetch("/api/users/csrf", {
    method: "POST",
    credentials: "include",
    headers: { Accept: "application/json" },
  });
}

export async function apiLogin(
  username: string,
  password: string,
): Promise<{ ok: true; force_password_reset: boolean }> {
  await apiCsrf();

  const res = await fetch("/api/users/login", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...csrfHeader(),
    },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Login failed"));
  return await res.json();
}

export async function apiLogout(): Promise<void> {
  await apiCsrf();

  const res = await fetch("/api/users/logout", {
    method: "POST",
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...csrfHeader(),
    },
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Logout failed"));
}

export async function apiMe(): Promise<Me> {
  const res = await fetch("/api/users/me", {
    method: "GET",
    credentials: "include",
    headers: { Accept: "application/json" },
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Not authenticated"));
  return await res.json();
}

export async function apiSetPassword(newPassword: string): Promise<void> {
  await apiCsrf();

  const res = await fetch("/api/users/set-password", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...csrfHeader(),
    },
    body: JSON.stringify({ new_password: newPassword }),
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Failed to set password"));
}

export async function apiSetAvatar(file: File): Promise<Me> {
  await apiCsrf();

  const fd = new FormData();
  fd.append("avatar", file);

  const res = await fetch("/api/users/me/avatar", {
    method: "POST",
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...csrfHeader(),
    },
    body: fd,
  });

  if (!res.ok) throw new Error(await errorFrom(res, "Failed to upload avatar"));
  return await res.json();
}
