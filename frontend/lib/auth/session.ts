// The backend's access token (POST /auth/token) and the one fetch wrapper that
// sends it. Every call to the backend should go through apiFetch.

/** localStorage key of the token; other tabs see changes to it as 'storage' events. */
export const TOKEN_KEY = 'token';

/** Fired on window when the backend rejects the token; AuthContext signs out. */
export const SESSION_EXPIRED_EVENT = 'auth:session-expired';

/** The token's claims (sub, role, exp), or null if it is not a readable JWT. */
export function tokenClaims(token: string): { sub?: string; role?: string; exp?: number } | null {
    try {
        const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
        const claims = JSON.parse(atob(payload));
        return claims && typeof claims === 'object' ? claims : null;
    } catch {
        return null;
    }
}

/**
 * The stored token, or null. Whether it is still valid is the backend's call
 * (a 401 ends the session): judging its expiry here would depend on the
 * browser's clock agreeing with the server's.
 */
export function getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
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
    // Also when no token was sent: it may have been cleared since sign-in.
    if (res.status === 401) {
        clearToken();
        window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
    }
    return res;
}
