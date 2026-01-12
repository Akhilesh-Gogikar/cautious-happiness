"use client"

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

interface User {
    email: string;
    full_name: string;
    role: string;
}

interface AuthContextType {
    user: User | null;
    login: (role?: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
    isLoading: boolean;
    switchRole: (role: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const DEMO_USERS: Record<string, User> = {
    'trader': { email: 'trader@alphasignals.io', full_name: 'Active Trader', role: 'trader' },
    'risk_manager': { email: 'risk@alphasignals.io', full_name: 'Risk Officer', role: 'risk_manager' },
    'auditor': { email: 'audit@alphasignals.io', full_name: 'Compliance Auditor', role: 'auditor' },
    'developer': { email: 'dev@alphasignals.io', full_name: 'System Dev', role: 'developer' },
    'pwd': { email: 'vip@alphasignals.io', full_name: 'Private Wealth', role: 'pwd' },
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        // Hydrate from local storage
        const storedRole = localStorage.getItem('demo_role');
        const token = localStorage.getItem('token');

        if (token && storedRole && DEMO_USERS[storedRole]) {
            setUser(DEMO_USERS[storedRole]);
        }
        setIsLoading(false);
    }, []);

    const login = (role: string = 'trader') => {
        const demoUser = DEMO_USERS[role] || DEMO_USERS['trader'];
        localStorage.setItem('token', 'demo-token');
        localStorage.setItem('demo_role', demoUser.role);
        setUser(demoUser);
        toast.success(`Welcome back, ${demoUser.full_name}`);
        router.push('/tradedesk');
    };

    const switchRole = (role: string) => {
        const demoUser = DEMO_USERS[role];
        if (demoUser) {
            localStorage.setItem('demo_role', role);
            setUser(demoUser);
            toast.info(`Switched view to ${demoUser.full_name} (${role})`);
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('demo_role');
        setUser(null);
        router.push('/');
        toast.info('Logged out');
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user, isLoading, switchRole }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
