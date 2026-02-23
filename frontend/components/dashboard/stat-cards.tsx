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
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";

const StatCard = ({ label, value, subtext, icon: Icon, trend, colorClass }: {
    label: string,
    value: string,
    subtext: string,
    icon: any,
    trend?: 'up' | 'down',
    colorClass?: string
}) => (
    <TooltipProvider>
        <Tooltip>
            <TooltipTrigger asChild>
                <div className="glass-card p-5 rounded-xl flex flex-col justify-between group hover:scale-[1.02] transition-all duration-300 relative overflow-hidden hover:shadow-2xl cursor-help">
                    {/* Animated Background Pulse */}
                    <div className={`absolute -right-10 -top-10 w-32 h-32 blur-[60px] opacity-20 group-hover:opacity-40 transition-opacity rounded-full ${colorClass || 'bg-primary'}`} />
                    <div className="absolute inset-0 bg-gradient-to-br from-white/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

                    <div className="flex items-start justify-between relative z-10 w-full mb-4">
                        <div className="space-y-1.5">
                            <span className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
                                {label}
                                <BrainCircuit className="w-3 h-3 text-primary/50 group-hover:text-primary animate-pulse opacity-0 group-hover:opacity-100 transition-opacity" />
                            </span>
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
            </TooltipTrigger>
            <TooltipContent className="bg-black/90 border-white/10 text-xs font-mono p-3 max-w-[200px]">
                <div className="flex items-center gap-2 mb-1 text-primary">
                    <BrainCircuit className="w-3 h-3" />
                    <span className="font-bold">AI_INSIGHT</span>
                </div>
                <p className="text-gray-300">
                    Neural detection: 3-sigma deviation in {label.toLowerCase()} correlating with generic algo flows.
                </p>
            </TooltipContent>
        </Tooltip>
    </TooltipProvider>
);

export function StatCards() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
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
                label="Algo Noise Level"
                value="HIGH"
                subtext="Systemic Volatility"
                icon={Zap}
                colorClass="bg-gold"
                trend="up"
            />
        </div>
    );
}
