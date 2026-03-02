"use client";

import React from 'react';
import {
    Activity,
    Target,
    TrendingUp,
    Zap,
    ArrowUpRight,
    ArrowDownRight,
    BrainCircuit // New Icon
} from 'lucide-react';

const StatCard = ({ label, value, subtext, icon: Icon, trend, colorClass, showChartTooltip }: {
    label: string,
    value: string,
    subtext: string,
    icon: any,
    trend?: 'up' | 'down',
    colorClass?: string,
    showChartTooltip?: boolean
}) => {
    // Determine if we need the danger state for Compute Health
    const numericValue = parseFloat(value.replace(/[^0-9.-]+/g, ""));
    const isComputeHealth = label === "Compute Health";
    const isDanger = isComputeHealth && numericValue < 90;

    return (
        <div className={`glass-card p-5 rounded-xl flex flex-col justify-between group hover:scale-[1.02] transition-all duration-300 relative overflow-visible hover:shadow-2xl ${isDanger ? 'border border-red-500/50 bg-red-500/5 shadow-[0_0_30px_rgba(239,68,68,0.2)] animate-pulse' : ''}`}>
            {/* Animated Background Pulse */}
            <div className={`absolute -right-10 -top-10 w-32 h-32 blur-[60px] opacity-20 group-hover:opacity-40 transition-opacity rounded-full ${isDanger ? 'bg-red-500' : (colorClass || 'bg-primary')}`} />
            <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

            {/* Line Chart Tooltip for Mirror Accuracy */}
            {showChartTooltip && (
                <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-48 bg-black/90 backdrop-blur-md border border-white/10 rounded-lg p-3 opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none z-50 transform group-hover:-translate-y-2">
                    <div className="text-[10px] text-muted-foreground mb-2 flex justify-between">
                        <span>24h Performance</span>
                        <span className="text-indigo-400">+2.4%</span>
                    </div>
                    <div className="h-12 w-full flex items-end gap-1">
                        <svg viewBox="0 0 100 40" className="w-full h-full preserve-3d">
                            <path d="M0,35 L10,32 L20,38 L30,25 L40,28 L50,15 L60,20 L70,8 L80,12 L90,5 L100,0" fill="none" stroke="currentColor" strokeWidth="2" className="text-indigo-500" />
                            <path d="M0,35 L10,32 L20,38 L30,25 L40,28 L50,15 L60,20 L70,8 L80,12 L90,5 L100,0 L100,40 L0,40 Z" fill="currentColor" className="text-indigo-500/20" />
                        </svg>
                    </div>
                    <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-black/90 backdrop-blur-md border-b border-r border-white/10 transform rotate-45" />
                </div>
            )}

            <div className="flex items-start justify-between relative z-10 w-full mb-4">
                <div className="space-y-1.5">
                    <span className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
                        {label}
                        <BrainCircuit className={`w-3 h-3 transition-opacity ${isDanger ? 'text-red-500 animate-pulse opacity-100' : 'text-primary/50 group-hover:text-primary animate-pulse opacity-0 group-hover:opacity-100'}`} />
                    </span>
                    <h3 className={`text-3xl font-black tracking-tighter drop-shadow-md ${isDanger ? 'text-red-500' : 'text-white'}`}>{value}</h3>
                </div>
                <div className={`p-2.5 rounded-lg border transition-colors ${isDanger ? 'bg-red-500/10 border-red-500/30 text-red-500' : `bg-white/5 border-white/10 ${colorClass?.replace('bg-', 'text-') || 'text-primary'}`}`}>
                    <Icon className="w-5 h-5" />
                </div>
            </div>

            <div className="flex items-center justify-between relative z-10 w-full">
                <span className={`text-[10px] font-mono ${isDanger ? 'text-red-400/80 font-bold' : 'text-muted-foreground'}`}>
                    {isDanger ? 'CRITICAL LAG DETECTED' : subtext}
                </span>
                {trend && !isDanger && (
                    <div className={`flex items-center gap-0.5 text-[10px] font-bold px-1.5 py-0.5 rounded-sm bg-black/20 ${trend === 'up' ? 'text-primary' : 'text-destructive'}`}>
                        {trend === 'up' ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                        {trend === 'up' ? '+12.5%' : '-3.2%'}
                    </div>
                )}
            </div>
        </div>
    );
};

export function StatCards() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 w-full mt-6">
            <StatCard
                label="Physical Premium"
                value="+$4.20"
                subtext="Brent vs Paper"
                icon={TrendingUp}
                trend="up"
            />
            <StatCard
                label="Mirror Accuracy"
                value="89.1%"
                subtext="Sentiment Tracking"
                icon={Target}
                colorClass="bg-indigo-500"
                trend="up"
                showChartTooltip
            />
            <StatCard
                label="Compute Health"
                value="88.5%"
                subtext="Latency < 15ms"
                icon={Activity}
                colorClass="bg-neon-blue"
            />
            <StatCard
                label="Algo Noise Level"
                value="HIGH"
                subtext="Systemic Volatility"
                icon={Zap}
                colorClass="bg-yellow-500"
                trend="up"
            />
        </div>
    );
}
