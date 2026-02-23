"use client";

import React from 'react';
import {
    LayoutDashboard,
    BarChart3,
    Zap,
    Shield,
    Settings,
    ExternalLink,
    PieChart,
    Layers,
    Terminal as TerminalIcon,
    MessageSquare,
    Workflow, // New Icon
    TrendingUp,
    Lock
} from 'lucide-react';
import { cn } from "@/lib/utils";
import { useRouter } from 'next/navigation';

const NavItem = ({ icon: Icon, label, active, badge, onClick, locked }: { icon: any, label: string, active?: boolean, badge?: string, onClick?: () => void, locked?: boolean }) => (
    <div
        onClick={onClick}
        className={cn(
            "flex items-center justify-between p-2 rounded-lg cursor-pointer transition-all group",
            active
                ? "bg-primary/10 text-primary border border-primary/20 text-glow-primary shadow-[0_0_15px_rgba(16,185,129,0.1)]"
                : "text-muted-foreground hover:bg-white/5 hover:text-white",
            locked && "opacity-60 cursor-not-allowed hover:bg-transparent"
        )}>
        <div className="flex items-center gap-3">
            <Icon className={cn("w-4 h-4", active ? "text-primary" : "group-hover:text-primary transition-colors")} />
            <span className="text-xs font-medium tracking-wide flex items-center gap-2">
                {label}
                {locked && <Lock className="w-3 h-3 text-red-500/50" />}
            </span>
        </div>
        {badge && !locked && (
            <span className="text-[10px] font-mono bg-primary/20 text-primary px-1.5 py-0.5 rounded border border-primary/20">
                {badge}
            </span>
        )}
    </div>
);

interface SidebarProps {
    activeView: string;
    onNavigate: (view: string) => void;
    userRole?: 'Admin' | 'User';
}

export function Sidebar({ activeView, onNavigate, userRole = 'User' }: SidebarProps) {
    const router = useRouter();

    const isAdmin = userRole === 'Admin';

    return (
        <aside className="w-64 h-full border-r border-white/10 bg-black/40 backdrop-blur-xl flex flex-col p-4 space-y-8 relative z-40">
            <div className="flex items-center gap-3 px-2 py-4 group cursor-default">
                <div className="w-10 h-10 bg-primary rounded-sm flex items-center justify-center shadow-[0_0_20px_rgba(16,185,129,0.3)] group-hover:shadow-[0_0_30px_rgba(16,185,129,0.6)] transition-all duration-500 animate-pulse-glow">
                    <Zap className="w-6 h-6 text-black fill-current" />
                </div>
                <div className="flex flex-col">
                    <h2 className="text-lg font-black tracking-tighter text-white leading-none">
                        <span className="text-primary text-glow-primary">ALPHA</span>
                        <span className="ml-1">INSIGHTS</span>
                    </h2>
                    <p className="text-[9px] text-muted-foreground/60 font-mono mt-1 tracking-[0.2em] font-bold uppercase transition-colors group-hover:text-primary/60">NEURAL_DOMAIN_v4.2</p>
                </div>
            </div>

            <nav className="flex-1 space-y-6">
                <div className="space-y-1">
                    <p className="px-2 pb-2 text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em]">Dashboards</p>
                    <NavItem icon={LayoutDashboard} label="Live Markets" active={activeView === 'markets'} onClick={() => onNavigate('markets')} badge="LIVE" />
                    <NavItem icon={PieChart} label="Portfolio" active={activeView === 'portfolio'} onClick={() => onNavigate('portfolio')} />
                    <NavItem icon={TrendingUp} label="Alpaca Markets" active={activeView === 'alpaca_markets'} onClick={() => onNavigate('alpaca_markets')} badge="ALPACA" />
                    <NavItem icon={Layers} label="Strategies" active={activeView === 'strategies'} onClick={() => onNavigate('strategies')} locked={!isAdmin} />
                </div>

                <div className="space-y-1">
                    <p className="px-2 pb-2 text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em]">Analysis Tools</p>
                    <NavItem icon={BarChart3} label="Correlations" active={activeView === 'correlations'} onClick={() => onNavigate('correlations')} locked={!isAdmin} />
                    <NavItem icon={TerminalIcon} label="Quant Engine" active={activeView === 'quant'} onClick={() => onNavigate('quant')} locked={!isAdmin} />
                    <NavItem icon={Zap} label="Intelligence Mirror" active={activeView === 'intelligence'} onClick={() => onNavigate('intelligence')} badge="NEW" locked={!isAdmin} />
                    <NavItem icon={MessageSquare} label="Analyst Chat" active={activeView === 'chat'} onClick={() => onNavigate('chat')} badge="AI" />
                    <NavItem icon={Workflow} label="Agent Builder" active={activeView === 'builder'} onClick={() => { if (isAdmin) router.push('/agents/builder') }} badge="BETA" locked={!isAdmin} />
                    <NavItem icon={Zap} label="Alpha Scanner" active={activeView === 'alpha'} onClick={() => onNavigate('alpha')} locked={!isAdmin} />
                </div>

                <div className="space-y-1">
                    <p className="px-2 pb-2 text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em]">System</p>
                    <NavItem icon={Shield} label="Security" active={activeView === 'security'} onClick={() => onNavigate('security')} locked={!isAdmin} />
                    <NavItem icon={Settings} label="Config" active={activeView === 'config'} onClick={() => onNavigate('config')} />
                </div>
            </nav>

            <div className="mt-auto pt-6 border-t border-white/5 space-y-4">
                <div className="bg-primary/5 border border-primary/10 rounded-lg p-3 space-y-2 relative overflow-hidden group">
                    {/* Subtle Scanline in status box */}
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                    <div className="flex items-center justify-between relative z-10">
                        <span className="text-[10px] font-mono text-muted-foreground">API_LATENCY</span>
                        <span className="text-[10px] font-mono text-primary font-bold">12ms</span>
                    </div>
                    <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden relative z-10">
                        <div className="w-[85%] h-full bg-gradient-to-r from-primary to-emerald-300 shadow-[0_0_10px_#10B981]" />
                    </div>
                </div>

                <div className="flex items-center gap-2 px-2 text-[10px] text-muted-foreground hover:text-white cursor-pointer transition-colors group">
                    <ExternalLink className="w-3 h-3 group-hover:text-primary transition-colors" />
                    <span>Documentation</span>
                </div>
            </div>
        </aside>
    );
}
