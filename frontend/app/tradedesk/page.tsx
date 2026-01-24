"use client"

// ... imports

import { useState, useEffect } from 'react';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { Sidebar } from '@/components/ui/sidebar';
import { SettingsModal } from '@/components/settings/settings-modal';
import { useAuth } from '@/components/providers/auth-context';
import { useRouter } from 'next/navigation';
import { ThreadList, TradeSignal } from '@/components/tradedesk/thread-list';
import { ProposedTradesList } from '@/components/tradedesk/proposed-trades-list';
import { ChatView } from '@/components/dashboard/chat-view';
import { Activity, Globe, ShieldCheck, Cpu, Zap, LayoutGrid, MessageSquare, Sparkles } from 'lucide-react';
import { MarketPulse } from '@/components/dashboard/market-pulse';

export default function Home() {
    const [currentView, setCurrentView] = useState('tradedesk'); // Default to the new AI desk
    const [activeTab, setActiveTab] = useState<'active' | 'proposed'>('active');
    const { user, isLoading, isAuthenticated } = useAuth();
    const router = useRouter();

    // State for the selected trade thread
    const [activeSignal, setActiveSignal] = useState<TradeSignal | null>(null);

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
            <Sidebar activeView={currentView} onNavigate={setCurrentView} userRole={user?.role} />

            <main className="flex-1 flex flex-col min-w-0 relative overflow-hidden bg-black/90">
                {/* Header */}
                <div className="w-full border-b border-white/5 bg-black/40 backdrop-blur-md p-4 flex justify-between items-center z-30">
                    <div className="flex items-center gap-4">
                        <h1 className="text-xl font-black tracking-tighter text-white flex items-center gap-2">
                            <span className="text-primary">AI</span>
                            <span>TRADEDESK</span>
                        </h1>
                        <div className="h-4 w-px bg-white/10" />
                        <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground">
                            <Activity className="w-3 h-3 text-emerald-500 animate-pulse" />
                            <span>NEURAL_LINK_ACTIVE</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <ConnectButton showBalance={false} chainStatus="icon" />
                        <SettingsModal />
                    </div>
                </div>

                {/* Market Pulse Ticker */}
                <MarketPulse />

                {/* Main Content Grid */}
                <div className="flex-1 grid grid-cols-12 gap-0 overflow-hidden relative z-10 h-full">

                    {/* LEFT PANEL: Trade Threads / Proposals */}
                    <div className="col-span-3 border-r border-white/5 bg-black/20 flex flex-col min-h-0 h-full overflow-hidden">
                        {/* Tab Switcher */}
                        <div className="flex border-b border-white/5 bg-white/[0.02] shrink-0 p-1 gap-1">
                            <button
                                onClick={() => setActiveTab('active')}
                                className={`flex-1 py-2 px-1 rounded flex items-center justify-center gap-1.5 transition-all
                                    ${activeTab === 'active'
                                        ? 'bg-white/10 text-white shadow-[0_0_10px_rgba(255,255,255,0.05)]'
                                        : 'text-muted-foreground hover:text-white/60 hover:bg-white/[0.05]'
                                    }`}
                            >
                                <MessageSquare className={`w-3 h-3 ${activeTab === 'active' ? 'text-primary' : ''}`} />
                                <span className="text-[10px] font-black tracking-widest uppercase truncate">Active Threads</span>
                            </button>
                            <button
                                onClick={() => setActiveTab('proposed')}
                                className={`flex-1 py-2 px-1 rounded flex items-center justify-center gap-1.5 transition-all
                                    ${activeTab === 'proposed'
                                        ? 'bg-white/10 text-white shadow-[0_0_10px_rgba(255,255,255,0.05)]'
                                        : 'text-muted-foreground hover:text-white/60 hover:bg-white/[0.05]'
                                    }`}
                            >
                                <Sparkles className={`w-3 h-3 ${activeTab === 'proposed' ? 'text-primary' : ''}`} />
                                <span className="text-[10px] font-black tracking-widest uppercase truncate">Proposals</span>
                            </button>
                        </div>

                        <div className="flex-1 min-h-0 overflow-hidden">
                            {activeTab === 'active' ? (
                                <div className="h-full flex flex-col">
                                    <div className="p-3 border-b border-white/5 flex items-center justify-between shrink-0 bg-white/[0.01]">
                                        <span className="text-[9px] font-mono text-muted-foreground uppercase opacity-50">THREAD_POOL_v4.2</span>
                                        <span className="text-[9px] bg-primary/20 text-primary px-1.5 rounded animate-pulse">LIVE</span>
                                    </div>
                                    <div className="flex-1 overflow-y-auto slice-scrollbar">
                                        <ThreadList
                                            onSelectThread={setActiveSignal}
                                            activeSignalId={activeSignal?.market_id}
                                        />
                                    </div>
                                </div>
                            ) : (
                                <ProposedTradesList />
                            )}
                        </div>
                    </div>

                    {/* RIGHT PANEL: Chat / Execution */}
                    <div className="col-span-9 flex flex-col bg-gradient-to-br from-black to-white/5 relative h-full min-h-0">
                        {/* Background ambience */}
                        <div className="absolute inset-0 pointer-events-none opacity-20 bg-[radial-gradient(circle_at_50%_50%,rgba(16,185,129,0.1),transparent_50%)]" />

                        <div className="flex-1 flex flex-col min-h-0 overflow-hidden z-20">
                            <ChatView
                                context={activeSignal?.market_question}
                                contextId={activeSignal?.market_id}
                            />
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
