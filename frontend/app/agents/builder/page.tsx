"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { Sidebar } from '@/components/ui/sidebar';
import { SettingsModal } from '@/components/settings/settings-modal';
import { NotificationCenter } from '@/components/layout/notification-center';
import { SystemStatusDropdown } from '@/components/dashboard/system-status-dropdown';
import { Globe, ShieldCheck, Play, Save } from 'lucide-react';
import { AgentBuilderCanvas } from '@/components/agent-builder/AgentBuilderCanvas';

export default function AgentBuilderPage() {
    const { user, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !user) {
            router.push('/login');
        } else if (!isLoading && user?.role !== 'Admin') {
            router.push('/dashboard');
        }
    }, [user, isLoading, router]);

    if (isLoading || !user) {
        return <div className="min-h-screen bg-background flex items-center justify-center">
            <div className="w-8 h-8 rounded-full border-t-2 border-primary animate-spin" />
        </div>;
    }

    return (
        <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans selection:bg-primary/30 selection:text-white">
            <Sidebar activeView="builder" onNavigate={(view) => router.push(view === 'builder' ? '/agents/builder' : '/dashboard')} userRole={user?.role} />

            <main className="flex-1 flex flex-col min-w-0 relative overflow-hidden">
                {/* Visual Background Elements */}
                <div className="absolute inset-0 pointer-events-none z-0">
                    <div className="absolute -top-[20%] -right-[10%] w-[800px] h-[800px] bg-emerald-500/10 blur-[120px] rounded-full opacity-40 mix-blend-screen" />
                </div>

                {/* Header Section */}
                <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 px-6 py-4 border-b border-white/5 bg-black/40 backdrop-blur-md relative z-30">
                    <div className="space-y-1">
                        <div className="flex items-center gap-3">
                            <h1 className="text-2xl font-black tracking-tighter text-white flex items-center gap-2 drop-shadow-lg">
                                <span className="text-emerald-400">AGENT</span>
                                <span className="text-white">BUILDER</span>
                            </h1>
                            <div className="px-2 py-0.5 rounded-sm text-[10px] font-mono bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 uppercase tracking-widest font-bold">
                                BETA
                            </div>
                        </div>
                        <SystemStatusDropdown />
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-3">
                            <button className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-mono text-white transition-colors">
                                <Save className="w-3 h-3" /> Save Draft
                            </button>
                            <button className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/50 text-emerald-400 text-xs font-mono font-bold transition-colors">
                                <Play className="w-3 h-3" /> Deploy Agent
                            </button>
                        </div>

                        <div className="hidden lg:flex flex-col items-end gap-1 px-4 border-l border-white/10">
                            <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground group">
                                <Globe className="w-3 h-3 group-hover:text-cyber-blue transition-colors" />
                                <span>NETWORK: <span className="text-white">GLOBAL_MESH</span></span>
                            </div>
                            <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground group">
                                <ShieldCheck className="w-3 h-3 group-hover:text-primary transition-colors" />
                                <span>SECURITY: <span className="text-primary">MAXIMUM</span></span>
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            <ConnectButton
                                accountStatus={{ smallScreen: 'avatar', largeScreen: 'full' }}
                                showBalance={false}
                                chainStatus="icon"
                            />
                            <NotificationCenter />
                            <SettingsModal />
                        </div>
                    </div>
                </header>

                {/* Canvas Area */}
                <div className="flex-1 relative z-10 p-0 overflow-hidden">
                    <AgentBuilderCanvas />
                </div>
            </main>
        </div>
    );
}
