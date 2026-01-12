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
    TrendingUp,
    ChevronDown,
} from 'lucide-react';
import Link from 'next/link';
import { cn } from "@/lib/utils";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { useAuth } from '@/components/providers/auth-context';

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
    userRole?: string;
}

export function Sidebar({ activeView, onNavigate, userRole }: SidebarProps) {
    const { switchRole, logout } = useAuth();

    const isVisible = (allowedRoles: string[]) => {
        if (!userRole) return false;
        if (userRole === 'developer') return true;
        return allowedRoles.includes(userRole);
    };

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
                    {isVisible(['trader', 'pwd']) && <NavItem icon={TerminalIcon} label="Terminal" active={activeView === 'dashboard'} onClick={() => onNavigate('dashboard')} badge="PRO" />}
                    {isVisible(['trader', 'risk_manager', 'auditor', 'pwd']) && <NavItem icon={LayoutDashboard} label="Live Markets" active={activeView === 'markets'} onClick={() => onNavigate('markets')} badge="LIVE" />}
                    {isVisible(['trader', 'risk_manager', 'auditor', 'pwd']) && <NavItem icon={PieChart} label="Portfolio" active={activeView === 'portfolio'} onClick={() => onNavigate('portfolio')} />}
                    {isVisible(['trader']) && <NavItem icon={Layers} label="Strategies" active={activeView === 'strategies'} onClick={() => onNavigate('strategies')} />}
                </div>

                <div className="space-y-1">
                    <p className="px-2 pb-2 text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em]">Analysis Tools</p>
                    {isVisible(['trader', 'risk_manager']) && <NavItem icon={TrendingUp} label="Probability Heatmap" active={activeView === 'heatmap'} onClick={() => onNavigate('heatmap')} badge="NEW" />}
                    {isVisible(['trader', 'risk_manager']) && <NavItem icon={BarChart3} label="Correlations" active={activeView === 'correlations'} onClick={() => onNavigate('correlations')} />}
                    {isVisible(['trader']) && <NavItem icon={TerminalIcon} label="Quant Engine" active={activeView === 'quant'} onClick={() => onNavigate('quant')} />}
                    {isVisible(['trader', 'risk_manager', 'pwd']) && <NavItem icon={MessageSquare} label="Analyst Chat" active={activeView === 'chat'} onClick={() => onNavigate('chat')} badge="AI" />}
                    {isVisible(['trader']) && <NavItem icon={Zap} label="Alpha Scanner" active={activeView === 'alpha'} onClick={() => onNavigate('alpha')} />}
                </div>

                <div className="space-y-1">
                    <p className="px-2 pb-2 text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em]">System</p>
                    {isVisible(['risk_manager', 'auditor']) && <NavItem icon={Shield} label="Security" active={activeView === 'security'} onClick={() => onNavigate('security')} />}
                    {isVisible(['risk_manager']) && <NavItem icon={Settings} label="Config" active={activeView === 'config'} onClick={() => onNavigate('config')} />}
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

                {/* USER PROFILE SECTION */}
                <div className="pt-2 space-y-2">
                    <div className="w-full p-2 rounded-lg bg-white/5 border border-white/10 space-y-2">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary/20 to-indigo-500/20 border border-white/10 flex items-center justify-center">
                                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                            </div>
                            <div className="flex flex-col">
                                <span className="text-xs font-bold text-white">
                                    DEMO MODE
                                </span>
                                <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">
                                    <span className="text-emerald-500">●</span> ACTIVE
                                </span>
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-[9px] font-mono text-muted-foreground uppercase tracking-wider pl-1">Switch Role</label>
                            <Select
                                value={userRole || 'trader'}
                                onValueChange={(role) => switchRole(role)}
                            >
                                <SelectTrigger className="h-8 bg-black/20 border-white/10 text-xs">
                                    <SelectValue placeholder="Select role" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="trader">Trader</SelectItem>
                                    <SelectItem value="risk_manager">Risk Manager</SelectItem>
                                    <SelectItem value="auditor">Auditor</SelectItem>
                                    <SelectItem value="developer">Developer</SelectItem>
                                    <SelectItem value="pwd">Private Wealth</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div
                        onClick={logout}
                        className="flex items-center gap-2 px-2 text-[10px] text-red-400 hover:text-red-300 cursor-pointer transition-colors group"
                    >
                        <span className="uppercase tracking-wider font-mono">Logout</span>
                        <ExternalLink className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                    </div>
                </div>

                <Link href="/docs" className="flex items-center gap-2 px-2 text-[10px] text-muted-foreground hover:text-white cursor-pointer transition-colors group">
                    <ExternalLink className="w-3 h-3 group-hover:text-primary transition-colors" />
                    <span>Documentation</span>
                </Link>
            </div>
        </aside>
    );
}
