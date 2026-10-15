// The backend's access token (POST /auth/token) and the one fetch wrapper that
// sends it. Every call to the backend should go through apiFetch.

const TOKEN_KEY = 'token';

/** Fired on window when the backend rejects the token; AuthContext signs out. */
export const SESSION_EXPIRED_EVENT = 'auth:session-expired';

/** Seconds since the epoch at which the JWT expires, or null if unreadable. */
function tokenExpiry(token: string): number | null {
    try {
        const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
        const { exp } = JSON.parse(atob(payload));
        return typeof exp === 'number' ? exp : null;
    } catch {
        return null;
    }
}

/** The stored token, or null when there is none or it has expired. */
export function getToken(): string | null {
    if (typeof window === 'undefined') return null;
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) return null;
    const exp = tokenExpiry(token);
    if (exp === null || exp * 1000 <= Date.now()) {
        localStorage.removeItem(TOKEN_KEY);
        return null;
    }
    return token;
}

export function setToken(token: string) {
    localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

/** fetch() with the session token attached; a 401 ends the session. */
export async function apiFetch(input: string, init: RequestInit = {}): Promise<Response> {
    const token = getToken();
    const headers = new Headers(init.headers);
    if (token) headers.set('Authorization', `Bearer ${token}`);
    const res = await fetch(input, { ...init, headers });
    // Also when no token was sent: it may have expired since sign-in.
    if (res.status === 401) {
        clearToken();
        window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
    }
    return res;
}
