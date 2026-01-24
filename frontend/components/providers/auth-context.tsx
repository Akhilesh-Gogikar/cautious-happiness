"use client"

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { login as apiLogin, getMe as apiGetMe, User, LoginRequest, api } from '@/lib/api';

interface AuthContextType {
    user: User | null;
    login: (credentials: LoginRequest) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
    isLoading: boolean;
    switchRole: (role: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    const userData = await apiGetMe();
                    setUser(userData);
                } catch (error) {
                    console.error('Failed to restore session:', error);
                    localStorage.removeItem('token');
                }
            }
            setIsLoading(false);
        };
        initAuth();
    }, []);

    const login = async (credentials: LoginRequest) => {
        try {
            const response = await apiLogin(credentials);
            localStorage.setItem('token', response.access_token);

            const userData = await apiGetMe();
            setUser(userData);

            toast.success(`Welcome back, ${userData.full_name}`);
            router.push('/tradedesk');
        } catch (error: any) {
            console.error('Login error:', error);
            throw error; // Let the component handle the specific error message
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
        toast.success('Logged out successfully');
        router.push('/');
    };

    const switchRole = async (role: string) => {
        try {
            await api.updateUserRole(role);
            const userData = await apiGetMe();
            setUser(userData);
            toast.success(`Role switched to ${role}`);
        } catch (error: any) {
            console.error('Failed to switch role:', error);
            toast.error('Failed to switch role');
        }
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
