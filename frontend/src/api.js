const ACCESS_TOKEN_KEY = 'medtech_access_token';
const BASE_KEY = 'medtech_api_base';
/** Legacy key from old static bearer; cleared on logout. */
const LEGACY_BEARER_KEY = 'medtech_bearer_token';

export function getApiBase() {
  const fromEnv = import.meta.env.VITE_API_BASE_URL;
  const stored = localStorage.getItem(BASE_KEY);
  const raw = (stored || fromEnv || 'http://127.0.0.1:8001').trim();
  return raw.replace(/\/$/, '');
}

export function getSavedAccessToken() {
  const s = localStorage.getItem(ACCESS_TOKEN_KEY);
  return s ? s.trim() : '';
}

/**
 * JWT from login (localStorage) or optional `VITE_API_ACCESS_TOKEN` in `frontend/.env` for local dev.
 */
export function getAccessToken() {
  const saved = getSavedAccessToken();
  if (saved) return saved;
  const fromEnv = import.meta.env.VITE_API_ACCESS_TOKEN;
  if (typeof fromEnv === 'string' && fromEnv.trim()) return fromEnv.trim();
  return '';
}

/** @deprecated use getAccessToken */
export function getBearerToken() {
  return getAccessToken();
}

export function saveAccessToken(token) {
  if (token) localStorage.setItem(ACCESS_TOKEN_KEY, token);
  else localStorage.removeItem(ACCESS_TOKEN_KEY);
}

export function clearAuth() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(LEGACY_BEARER_KEY);
}

export function saveApiSettings({ baseUrl }) {
  if (baseUrl !== undefined) {
    const t = baseUrl.trim().replace(/\/$/, '');
    if (t) localStorage.setItem(BASE_KEY, t);
    else localStorage.removeItem(BASE_KEY);
  }
}

export async function apiFetch(path, options = {}) {
  const { method = 'GET', body, headers: extra = {}, skipAuth = false } = options;
  const headers = { ...extra };
  const token = getAccessToken();
  if (token && !skipAuth) headers.Authorization = `Bearer ${token}`;
  return fetch(`${getApiBase()}${path}`, { method, body, headers });
}

export async function authRegister(email, password) {
  return apiFetch('/auth/register', {
    method: 'POST',
    skipAuth: true,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email.trim(), password }),
  });
}

export async function authLogin(email, password) {
  const res = await apiFetch('/auth/login', {
    method: 'POST',
    skipAuth: true,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email.trim(), password }),
  });
  if (res.ok) {
    const data = await res.json();
    if (data.access_token) saveAccessToken(data.access_token);
  }
  return res;
}

export async function readErrorMessage(response) {
  try {
    const data = await response.json();
    if (data?.error?.detail) return data.error.detail;
    if (typeof data?.detail === 'string') return data.detail;
  } catch {
    /* ignore */
  }
  return response.statusText || `HTTP ${response.status}`;
}

export async function fetchBackendMeta() {
  try {
    const [h, v] = await Promise.all([
      apiFetch('/health', { skipAuth: true }),
      apiFetch('/version', { skipAuth: true }),
    ]);
    return {
      healthOk: h.ok,
      version: v.ok ? await v.json() : null,
    };
  } catch {
    return { healthOk: false, version: null };
  }
}

export async function fetchPrescriptionList() {
  if (!getAccessToken()) return [];
  try {
    const res = await apiFetch('/prescriptions');
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}
