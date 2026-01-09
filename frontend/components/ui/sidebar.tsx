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
    MessageSquare
} from 'lucide-react';
import { cn } from "@/lib/utils";

const NavItem = ({ icon: Icon, label, active, badge, onClick }: { icon: any, label: string, active?: boolean, badge?: string, onClick?: () => void }) => (
    <div
        onClick={onClick}
        className={cn(
            "flex items-center justify-between p-2 rounded-lg cursor-pointer transition-all group",
            active
                ? "bg-primary/10 text-primary border border-primary/20 text-glow-primary shadow-[0_0_15px_rgba(16,185,129,0.1)]"
                : "text-muted-foreground hover:bg-white/5 hover:text-white"
        )}>
        <div className="flex items-center gap-3">
            <Icon className={cn("w-4 h-4", active ? "text-primary" : "group-hover:text-primary transition-colors")} />
            <span className="text-xs font-medium tracking-wide">{label}</span>
        </div>
        {badge && (
            <span className="text-[10px] font-mono bg-primary/20 text-primary px-1.5 py-0.5 rounded border border-primary/20">
                {badge}
            </span>
        )}
    </div>
);

interface SidebarProps {
    activeView: string;
    onNavigate: (view: string) => void;
}

export function Sidebar({ activeView, onNavigate }: SidebarProps) {
    return (
        <aside className="w-64 h-full border-r border-white/10 bg-black/40 backdrop-blur-xl flex flex-col p-4 space-y-8 relative z-40">
            <div className="flex items-center gap-3 px-2 py-2">
                <div className="w-8 h-8 bg-primary rounded flex items-center justify-center shadow-[0_0_15px_rgba(16,185,129,0.5)] animate-pulse-glow">
                    <Zap className="w-5 h-5 text-black fill-current" />
                </div>
                <div>
                    <h2 className="text-sm font-bold tracking-tighter text-white">POLYMARKET</h2>
                    <p className="text-[10px] text-muted-foreground font-mono leading-none tracking-wider">QUANT_SYSTEM / v4</p>
                </div>
            </div>

            <nav className="flex-1 space-y-6">
                <div className="space-y-1">
                    <p className="px-2 pb-2 text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em]">Dashboards</p>
                    <NavItem icon={LayoutDashboard} label="Live Markets" active={activeView === 'markets'} onClick={() => onNavigate('markets')} badge="LIVE" />
                    <NavItem icon={PieChart} label="Portfolio" active={activeView === 'portfolio'} onClick={() => onNavigate('portfolio')} />
                    <NavItem icon={Layers} label="Strategies" active={activeView === 'strategies'} onClick={() => onNavigate('strategies')} />
                </div>

                <div className="space-y-1">
                    <p className="px-2 pb-2 text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em]">Analysis Tools</p>
                    <NavItem icon={BarChart3} label="Correlations" active={activeView === 'correlations'} onClick={() => onNavigate('correlations')} />
                    <NavItem icon={TerminalIcon} label="Quant Engine" active={activeView === 'quant'} onClick={() => onNavigate('quant')} />
                    <NavItem icon={MessageSquare} label="Analyst Chat" active={activeView === 'chat'} onClick={() => onNavigate('chat')} badge="AI" />
                    <NavItem icon={Zap} label="Alpha Scanner" active={activeView === 'alpha'} onClick={() => onNavigate('alpha')} />
                </div>

                <div className="space-y-1">
                    <p className="px-2 pb-2 text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em]">System</p>
                    <NavItem icon={Shield} label="Security" active={activeView === 'security'} onClick={() => onNavigate('security')} />
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
