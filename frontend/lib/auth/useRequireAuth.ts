"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth, type Role, type User } from './AuthContext';

/**
 * The signed-in user once they may see the page, null until then. Sends a
 * signed-out visitor to /login, and a user without `role` to /dashboard,
 * replacing the history entry so Back doesn't return to the guarded page.
 */
export function useRequireAuth(role?: Role): User | null {
    const { user, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (isLoading) return;
        if (!user) {
            router.replace('/login');
        } else if (role && user.role !== role) {
            router.replace('/dashboard');
        }
    }, [isLoading, user, role, router]);

    if (isLoading || !user || (role && user.role !== role)) return null;
    return user;
}
