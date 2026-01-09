"use client";

import React from 'react';
import {
    Activity,
    Target,
    TrendingUp,
    Zap,
    ArrowUpRight,
    ArrowDownRight
} from 'lucide-react';

const StatCard = ({ label, value, subtext, icon: Icon, trend, colorClass }: {
    label: string,
    value: string,
    subtext: string,
    icon: any,
    trend?: 'up' | 'down',
    colorClass?: string
}) => (
    <div className="glass-card p-5 rounded-xl flex flex-col justify-between group hover:scale-[1.02] transition-all duration-300 relative overflow-hidden hover:shadow-2xl">
        {/* Animated Background Pulse */}
        <div className={`absolute -right-10 -top-10 w-32 h-32 blur-[60px] opacity-20 group-hover:opacity-40 transition-opacity rounded-full ${colorClass || 'bg-primary'}`} />
        <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

        <div className="flex items-start justify-between relative z-10 w-full mb-4">
            <div className="space-y-1.5">
                <span className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em]">{label}</span>
                <h3 className="text-3xl font-black tracking-tighter text-white drop-shadow-md">{value}</h3>
            </div>
            <div className={`p-2.5 rounded-lg bg-white/5 border border-white/10 ${colorClass?.replace('bg-', 'text-') || 'text-primary'}`}>
                <Icon className="w-5 h-5" />
            </div>
        </div>

        <div className="flex items-center justify-between relative z-10 w-full">
            <span className="text-[10px] text-muted-foreground font-mono">{subtext}</span>
            {trend && (
                <div className={`flex items-center gap-0.5 text-[10px] font-bold px-1.5 py-0.5 rounded-sm bg-black/20 ${trend === 'up' ? 'text-primary' : 'text-destructive'}`}>
                    {trend === 'up' ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {trend === 'up' ? '+12.5%' : '-3.2%'}
                </div>
            )}
        </div>
    </div>
);

export function StatCards() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
            <StatCard
                label="Active Exposure"
                value="$1.2M"
                subtext="Across 12 positions"
                icon={TrendingUp}
                trend="up"
            />
            <StatCard
                label="Prediction Accuracy"
                value="94.2%"
                subtext="Last 30 days"
                icon={Target}
                colorClass="bg-indigo"
                trend="up"
            />
            <StatCard
                label="Compute Health"
                value="98.5%"
                subtext="Latency < 15ms"
                icon={Activity}
                colorClass="bg-neon-blue"
            />
            <StatCard
                label="Alpha Signals"
                value="42"
                subtext="24h generation"
                icon={Zap}
                colorClass="bg-gold"
                trend="up"
            />
        </div>
    );
}
