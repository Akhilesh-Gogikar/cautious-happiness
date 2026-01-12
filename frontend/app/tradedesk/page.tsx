"use client";

import { useState } from 'react';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { MarketTable } from '@/components/dashboard/market-table';
import { StatCards } from '@/components/dashboard/stat-cards';
import { Ticker } from '@/components/ui/ticker';
import { Sidebar } from '@/components/ui/sidebar';
import { SettingsModal } from '@/components/settings/settings-modal';
import { useAuth } from '@/components/providers/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { PortfolioView } from '@/components/dashboard/portfolio-view';
import { AlphaScanner } from '@/components/dashboard/alpha-scanner';
import { StrategyView } from '@/components/dashboard/strategy-view';
import { CorrelationsView } from '@/components/dashboard/correlations-view';
import { SecurityView } from '@/components/dashboard/security-view';
import { ChatView } from '@/components/dashboard/chat-view';
import { HeatmapView } from '@/components/dashboard/heatmap-view';
import InstitutionalDashboard from '@/components/institutional/Dashboard';
import { Activity, Globe, ShieldCheck, Cpu, Zap } from 'lucide-react';

// Basic Placeholder Component for WIP Views
function ViewPlaceholder({ title }: { title: string }) {
    return (
        <div className="flex flex-col items-center justify-center h-[60vh] space-y-4 animate-fade-in text-center">
            <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                <ShieldCheck className="w-8 h-8 text-muted-foreground/40" />
            </div>
            <div>
                <h3 className="text-lg font-black tracking-widest text-white uppercase">{title}</h3>
                <p className="text-xs font-mono text-muted-foreground mt-2">MODULE_UNDER_CONSTRUCTION // ACCESS_DENIED</p>
            </div>
        </div>
    );
}

export default function Home() {
    const [currentView, setCurrentView] = useState('dashboard');
    const { user, isLoading, isAuthenticated } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.push('/login');
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

    if (!isAuthenticated) return null; // Prevent flash of content

    return (
        <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans selection:bg-primary/30 selection:text-white">
            {/* Sidebar with Navigation Logic */}
            <Sidebar activeView={currentView} onNavigate={setCurrentView} userRole={user?.role} />

            <main className="flex-1 flex flex-col min-w-0 relative overflow-hidden">
                {/* Visual Background Elements - ENHANCED */}
                <div className="absolute inset-0 pointer-events-none z-0">
                    <div className="absolute -top-[20%] -right-[10%] w-[800px] h-[800px] bg-primary/20 blur-[120px] rounded-full opacity-40 mix-blend-screen animate-pulse-glow" />
                    <div className="absolute -bottom-[20%] -left-[10%] w-[600px] h-[600px] bg-indigo/20 blur-[120px] rounded-full opacity-40 mix-blend-screen" />
                    <div className="absolute top-[20%] left-[20%] w-[400px] h-[400px] bg-cyber-blue/10 blur-[100px] rounded-full opacity-30" />
                </div>

                {/* Ticker Bar - Top of main content */}
                <div className="w-full border-b border-white/5 bg-black/40 backdrop-blur-md relative z-30">
                    <Ticker />
                </div>

                {/* Scrollable Content Area */}
                <div className="flex-1 overflow-y-auto custom-scrollbar relative z-10 px-6 py-6 space-y-8">

                    {/* Header Section - Staggered Entry */}
                    <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 animate-fade-in [animation-delay:100ms] opacity-0 fill-mode-forwards">
                        <div className="space-y-1">
                            <div className="flex items-center gap-3">
                                <h1 className="text-3xl font-black tracking-tighter text-white flex items-center gap-2 drop-shadow-lg">
                                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-white to-primary animate-pulse-glow">ALPHA</span>
                                    <span className="text-white">TERMINAL</span>
                                </h1>
                                <div className="px-2 py-0.5 rounded-sm text-[10px] font-mono bg-primary/10 border border-primary/20 text-primary uppercase tracking-widest font-bold shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                                    v4.2.0_STABLE
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <p className="text-[10px] text-muted-foreground font-mono flex items-center gap-1.5 leading-none">
                                    <Activity className="w-3 h-3 text-primary animate-pulse" />
                                    SYSTEM_OPTIMAL
                                </p>
                                <p className="text-[10px] text-muted-foreground font-mono flex items-center gap-1.5 leading-none">
                                    <Cpu className="w-3 h-3 text-indigo" />
                                    NEURAL_ENGINE_ACTIVE
                                </p>
                                <p className="text-[10px] text-muted-foreground font-mono flex items-center gap-1.5 leading-none">
                                    <Zap className="w-3 h-3 text-gold" />
                                    LOW_LATENCY
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-6">
                            <div className="hidden lg:flex flex-col items-end gap-1 px-4 border-r border-white/10">
                                <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground group">
                                    <Globe className="w-3 h-3 group-hover:text-cyber-blue transition-colors" />
                                    <span>NETWORK: <span className="text-white group-hover:text-cyber-blue transition-colors">GLOBAL_MESH</span></span>
                                </div>
                                <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground group">
                                    <ShieldCheck className="w-3 h-3 group-hover:text-primary transition-colors" />
                                    <span>SECURITY: <span className="text-primary group-hover:text-emerald-400 transition-colors">MAXIMUM</span></span>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <ConnectButton
                                    accountStatus={{
                                        smallScreen: 'avatar',
                                        largeScreen: 'full',
                                    }}
                                    showBalance={false}
                                    chainStatus="icon"
                                />
                                <SettingsModal />
                            </div>
                        </div>
                    </header>

                    {/* MAIN CONTENT SWITCH */}
                    <div className="grid gap-6 animate-fade-in [animation-delay:500ms] opacity-0 fill-mode-forwards pb-10">
                        {currentView === 'dashboard' && <InstitutionalDashboard />}
                        {currentView === 'markets' && <MarketTable />}
                        {currentView === 'portfolio' && <PortfolioView />}
                        {currentView === 'strategies' && <StrategyView />}
                        {currentView === 'heatmap' && <HeatmapView />}
                        {currentView === 'correlations' && <CorrelationsView />}
                        {currentView === 'quant' && <MarketTable />}
                        {currentView === 'chat' && <ChatView />}
                        {currentView === 'alpha' && <AlphaScanner />}
                        {currentView === 'security' && <SecurityView />}
                        {currentView === 'config' && <ViewPlaceholder title="GLOBAL_CONFIG" />}
                    </div>
                </div>

                {/* Overlay Scanline Effect - Subtle Retro Feel */}
                <div className="fixed inset-0 pointer-events-none z-50 opacity-[0.02] bg-[size:100%_3px] bg-repeat-y bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.5)_50%)]" />
                <div className="fixed inset-0 pointer-events-none z-50 opacity-[0.03] animate-scanline bg-gradient-to-b from-transparent via-white to-transparent h-24 blur-sm" />
            </main>
        </div>
    );
}
