"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { API_URL } from '@/lib/api';
import { SESSION_EXPIRED_EVENT, apiFetch, clearToken, getToken, setToken } from './session';

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

/** The signed-in user according to the backend (GET /auth/me), or null. */
async function fetchCurrentUser(): Promise<User | null> {
    const res = await apiFetch(`${API_URL}/auth/me`);
    if (!res.ok) return null;
    const me = await res.json();
    return {
        username: me.username,
        email: me.email ?? '',
        serverRole: me.role,
        role: me.role === 'admin' ? 'Admin' : 'User',
    };
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

        // Restore the session only if the backend still accepts the stored token.
        const restore = getToken() ? fetchCurrentUser().catch(() => null) : Promise.resolve(null);
        restore.then((current) => {
            if (!current) clearToken();
            setUser(current);
            setIsLoading(false);
        });

        // apiFetch fires this when the backend rejects the token (expired or revoked).
        window.addEventListener(SESSION_EXPIRED_EVENT, logout);
        return () => window.removeEventListener(SESSION_EXPIRED_EVENT, logout);
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
        if (!res.ok) throw new Error(`Sign-in failed (status ${res.status}).`);

        const { access_token } = await res.json();
        setToken(access_token);
        const current = await fetchCurrentUser();
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
