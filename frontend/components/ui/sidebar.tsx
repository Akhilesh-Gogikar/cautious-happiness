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
    Cpu,
} from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from "@/lib/utils";
import { useAuth } from '@/components/providers/auth-context';
import { RoleSwitcher } from './role-switcher';

interface NavItemProps {
    icon: any;
    label: string;
    href: string;
    active?: boolean;
    badge?: string;
}

const NavLink = ({ icon: Icon, label, href, active, badge }: NavItemProps) => (
    <Link
        href={href}
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
    </Link>
);

interface SidebarProps {
    activeView?: string;
    onNavigate?: (view: string) => void;
    userRole?: string;
}

export function Sidebar({ userRole }: SidebarProps) {
    const { user, logout } = useAuth();
    const pathname = usePathname();
    const effectiveRole = userRole || user?.role;

    const isVisible = (allowedRoles: string[]) => {
        if (!effectiveRole) return false;
        if (effectiveRole === 'developer') return true;
        return allowedRoles.includes(effectiveRole);
    };

    const isActive = (path: string) => pathname === path;

    return (
        <aside className="w-64 h-full border-r border-white/10 bg-black/40 backdrop-blur-xl flex flex-col p-4 space-y-8 relative z-40">
            <div className="flex items-center gap-3 px-2 py-2">
                <div className="w-8 h-8 bg-primary rounded flex items-center justify-center shadow-[0_0_15px_rgba(16,185,129,0.5)] animate-pulse-glow">
                    <Zap className="w-5 h-5 text-black fill-current" />
                </div>
                <div>
                    <h2 className="text-sm font-bold tracking-tighter text-white">ALPHASIGNALS</h2>
                    <p className="text-[10px] text-muted-foreground font-mono leading-none tracking-wider">QUANT_SYSTEM / v4</p>
                </div>
            </div>

            <nav className="flex-1 space-y-6">
                <div className="space-y-1">
                    <p className="px-2 pb-2 text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em]">Mission Control</p>
                    {isVisible(['trader', 'risk_manager']) && (
                        <Link
                            href="/cockpit"
                            className={cn(
                                "flex items-center justify-between p-2 rounded-lg cursor-pointer transition-all group mb-4",
                                isActive('/cockpit')
                                    ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 shadow-[0_0_15px_rgba(99,102,241,0.2)]"
                                    : "bg-white/5 border border-white/5 text-muted-foreground hover:bg-white/10 hover:text-white hover:border-white/10"
                            )}>
                            <div className="flex items-center gap-3">
                                <TerminalIcon className={cn("w-4 h-4", isActive('/cockpit') ? "text-indigo-400" : "text-indigo-500/70 group-hover:text-indigo-400 transition-colors")} />
                                <span className="text-xs font-bold tracking-wide">AI Cockpit</span>
                            </div>
                            <span className="flex h-2 w-2 rounded-full bg-indigo-500 animate-pulse shadow-[0_0_8px_#6366f1]" />
                        </Link>
                    )}
                </div>

                <div className="space-y-1">
                    <p className="px-2 pb-2 text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em]">Dashboards</p>
                    {isVisible(['trader', 'pwd']) && <NavLink icon={TerminalIcon} label="Trade Desk" href="/tradedesk" active={isActive('/tradedesk')} badge="PRO" />}
                    {isVisible(['trader', 'risk_manager', 'auditor', 'pwd']) && <NavLink icon={LayoutDashboard} label="Institutional" href="/dashboard" active={isActive('/dashboard')} badge="LIVE" />}
                    {isVisible(['trader', 'risk_manager', 'auditor', 'pwd']) && <NavLink icon={PieChart} label="Portfolio" href="/portfolio" active={isActive('/portfolio')} />}
                    {isVisible(['trader', 'risk_manager', 'auditor', 'pwd']) && <NavLink icon={TrendingUp} label="P&L Analytics" href="/pnl" active={isActive('/pnl')} />}
                </div>

                <div className="space-y-1">
                    <p className="px-2 pb-2 text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em]">Analysis Tools</p>
                    {isVisible(['trader', 'risk_manager']) && <NavLink icon={BarChart3} label="Attribution" href="/attribution" active={isActive('/attribution')} badge="NEW" />}
                    {isVisible(['trader', 'risk_manager']) && <NavLink icon={Cpu} label="AI Hub" href="/ai-hub" active={isActive('/ai-hub')} badge="AI" />}
                </div>

                <div className="space-y-1">
                    <p className="px-2 pb-2 text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em]">Tax & Compliance</p>
                    {isVisible(['trader', 'risk_manager', 'auditor']) && <NavLink icon={Shield} label="Tax Center" href="/tax" active={isActive('/tax')} />}
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
                <div className="pt-2 space-y-4">
                    <RoleSwitcher />

                    <div className="w-full p-2 rounded-lg bg-white/5 border border-white/10 space-y-2">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary/20 to-indigo-500/20 border border-white/10 flex items-center justify-center">
                                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                            </div>
                            <div className="flex flex-col overflow-hidden">
                                <span className="text-xs font-bold text-white truncate" title={user?.full_name}>
                                    {user?.full_name || 'User'}
                                </span>
                                <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider truncate">
                                    <span className="text-emerald-500">●</span> {user?.role || 'Active'}
                                </span>
                            </div>
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
