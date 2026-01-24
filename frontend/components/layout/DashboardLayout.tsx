"use client";

import React from 'react';
import { LucideIcon, Activity, Zap } from 'lucide-react';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useAuth } from '@/components/providers/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Sidebar } from '@/components/ui/sidebar';
import { SettingsModal } from '@/components/settings/settings-modal';
import { MarketPulse } from '@/components/dashboard/market-pulse';
import { FloatingAgentPanel } from '@/components/agents/FloatingAgentPanel';

interface DashboardLayoutProps {
    children: React.ReactNode;
    title: string;
    subtitle?: string;
    icon?: LucideIcon;
    showMarketPulse?: boolean;
}

export function DashboardLayout({
    children,
    title,
    subtitle,
    icon: Icon,
    showMarketPulse = true
}: DashboardLayoutProps) {
    const { user, isLoading, isAuthenticated } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.push('/');
        }
    }, [isLoading, isAuthenticated, router]);

    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center bg-black text-white">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
                    <p className="text-sm font-mono text-muted-foreground animate-pulse">AUTHENTICATING...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) return null;

    return (
        <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans selection:bg-primary/30 selection:text-white">
            <Sidebar userRole={user?.role} />

            <main className="flex-1 flex flex-col min-w-0 relative overflow-hidden bg-black/90">
                {/* Header */}
                <div className="w-full border-b border-white/5 bg-black/40 backdrop-blur-md p-4 flex justify-between items-center z-30">
                    <div className="flex items-center gap-4">
                        <h1 className="text-xl font-black tracking-tighter text-white flex items-center gap-2">
                            {Icon && <Icon className="w-5 h-5 text-primary" />}
                            <span className="text-primary">{title.split(' ')[0]}</span>
                            <span>{title.split(' ').slice(1).join(' ')}</span>
                        </h1>
                        {subtitle && (
                            <>
                                <div className="h-4 w-px bg-white/10" />
                                <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground">
                                    <Activity className="w-3 h-3 text-emerald-500 animate-pulse" />
                                    <span>{subtitle}</span>
                                </div>
                            </>
                        )}
                    </div>
                    <div className="flex items-center gap-4">
                        <ConnectButton showBalance={false} chainStatus="icon" />
                        <SettingsModal />
                    </div>
                </div>

                {/* Market Pulse Ticker */}
                {showMarketPulse && <MarketPulse />}

                {/* Main Content Area */}
                <div className="flex-1 overflow-auto relative z-10">
                    {/* Background ambience */}
                    <div className="absolute inset-0 pointer-events-none opacity-20 bg-[radial-gradient(circle_at_50%_50%,rgba(16,185,129,0.1),transparent_50%)]" />

                    <div className="relative z-10 h-full">
                        {children}
                    </div>
                </div>
            </main>

            {/* Floating Agent Panel - available on all pages */}
            <FloatingAgentPanel />
        </div>
    );
}
