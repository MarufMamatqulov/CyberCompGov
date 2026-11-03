const TOKEN_KEY = "ccg_token";

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string | null) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* brauzer xotirasi mavjud emas */
  }
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

function errorText(body: unknown, status: number): string {
  if (body && typeof body === "object" && "detail" in body) {
    const d = (body as { detail: unknown }).detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) return d.map((x) => (x as { msg?: string }).msg ?? "").join("; ");
  }
  return `Server xatosi (${status})`;
}

export async function api<T>(path: string, options: RequestInit & { json?: unknown } = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let body = options.body;
  if (options.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(options.json);
  }
  const res = await fetch(path, { ...options, headers, body });
  if (res.status === 401 && token) {
    setToken(null);
    window.dispatchEvent(new Event("ccg-logout"));
  }
  if (!res.ok) {
    let parsed: unknown = null;
    try {
      parsed = await res.json();
    } catch {
      /* JSON emas */
    }
    throw new ApiError(res.status, errorText(parsed, res.status));
  }
  return (await res.json()) as T;
}

export async function downloadFile(path: string, filename: string) {
  const token = getToken();
  const res = await fetch(path, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
  if (!res.ok) throw new ApiError(res.status, "Faylni yuklab bo‘lmadi");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
