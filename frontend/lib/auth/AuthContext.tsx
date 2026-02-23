"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type Role = 'Admin' | 'User';

export interface User {
    email: string;
    role: Role;
}

interface AuthContextType {
    user: User | null;
    login: (email: string) => void;
    logout: () => void;
    toggleRole: () => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check local storage for existing session on mount
        const storedUser = localStorage.getItem('auth_user');
        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
            } catch (e) {
                console.error("Failed to parse stored user", e);
                localStorage.removeItem('auth_user');
            }
        }
        setIsLoading(false);
    }, []);

    const login = (email: string) => {
        const isAdmin = email.toLowerCase() === 'aki@onenew.ai';
        const newUser: User = {
            email,
            role: isAdmin ? 'Admin' : 'User'
        };
        setUser(newUser);
        localStorage.setItem('auth_user', JSON.stringify(newUser));
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('auth_user');
    };

    const toggleRole = () => {
        if (user && user.email.toLowerCase() === 'aki@onenew.ai') {
            const updatedUser: User = {
                ...user,
                role: user.role === 'Admin' ? 'User' : 'Admin'
            };
            setUser(updatedUser);
            localStorage.setItem('auth_user', JSON.stringify(updatedUser));
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, toggleRole, isLoading }}>
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
