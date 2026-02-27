export function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()!.split(";").shift() ?? null;
  return null;
}

export async function ensureCsrfCookie(): Promise<void> {
  await fetch("/api/users/csrf", {
    method: "POST",
    credentials: "include",
  });
}

export function csrfHeader(): Record<string, string> {
  const token = getCookie("csrftoken");
  return token ? { "X-CSRFToken": token } : {};
}
