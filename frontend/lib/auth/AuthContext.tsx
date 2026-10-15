"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { API_URL } from '@/lib/api';
import { SESSION_EXPIRED_EVENT, TOKEN_KEY, apiFetch, clearToken, getToken, setToken, tokenClaims } from './session';

/** What the UI gates on: admin-only views need 'Admin'. */
export type Role = 'Admin' | 'User';

export interface User {
    username: string;
    email: string;
    /** The backend role: admin, trader, analyst or risk_manager. */
    serverRole: string;
    role: Role;
}

interface AuthContextType {
    user: User | null;
    /** Signs in with the backend; throws an Error with a message to show on failure. */
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function toUser(username: string, email: string | null | undefined, serverRole: string): User {
    return { username, email: email ?? '', serverRole, role: serverRole === 'admin' ? 'Admin' : 'User' };
}

/**
 * The signed-in user according to the backend (GET /auth/me); null when the
 * backend rejects the token. Throws when the backend cannot answer, which
 * says nothing about the token.
 */
async function fetchCurrentUser(): Promise<User | null> {
    const res = await apiFetch(`${API_URL}/auth/me`);
    if (res.status === 401) return null;
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const me = await res.json();
    return toUser(me.username, me.email, me.role);
}

/** The user named in the token itself, for when the backend is unreachable. */
function userFromToken(token: string): User | null {
    const claims = tokenClaims(token);
    return claims?.sub ? toUser(claims.sub, '', claims.role ?? '') : null;
}

/** Resolve the session for `token`: the backend's answer, or the token's claims if it is unreachable. */
async function resolveUser(token: string | null): Promise<User | null> {
    if (!token) return null;
    try {
        return await fetchCurrentUser();
    } catch {
        // The backend still decides on every call; a 401 later signs the user out.
        return userFromToken(token);
    }
}

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const logout = useCallback(() => {
        clearToken();
        setUser(null);
    }, []);

    useEffect(() => {
        // Earlier versions kept a client-side "session" here with no token behind it.
        localStorage.removeItem('auth_user');

        resolveUser(getToken()).then((current) => {
            setUser(current);
            setIsLoading(false);
        });

        // Another tab signed in, switched user or signed out: follow it, so the
        // user shown here is the one the shared token acts as.
        const onStorage = (e: StorageEvent) => {
            if (e.key === TOKEN_KEY || e.key === null) resolveUser(e.newValue ?? getToken()).then(setUser);
        };

        // apiFetch fires this when the backend rejects the token (expired or revoked).
        window.addEventListener(SESSION_EXPIRED_EVENT, logout);
        window.addEventListener('storage', onStorage);
        return () => {
            window.removeEventListener(SESSION_EXPIRED_EVENT, logout);
            window.removeEventListener('storage', onStorage);
        };
    }, [logout]);

    const login = async (username: string, password: string) => {
        let res: Response;
        try {
            res = await fetch(`${API_URL}/auth/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ username, password }),
            });
        } catch {
            throw new Error('Cannot reach the server. Is the backend running?');
        }
        if (res.status === 401) throw new Error('Incorrect username or password.');
        // The /api proxy answers 500/502 when the backend is down.
        if (res.status >= 500) throw new Error(`The server is not responding (status ${res.status}). Is the backend running?`);
        if (!res.ok) throw new Error(`Sign-in failed (status ${res.status}).`);

        const { access_token } = await res.json();
        setToken(access_token);
        const current = await resolveUser(access_token);
        if (!current) {
            clearToken();
            throw new Error('Signed in, but the server did not return your account.');
        }
        setUser(current);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
