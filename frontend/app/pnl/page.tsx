"use client";

import { DashboardLayout } from "@/components/layout";
import { PnLVelocityChart } from "@/components/PnLVelocityChart";
import { BarChart3, TrendingUp, Activity, Zap } from "lucide-react";

function PnLContent() {
    return (
        <div className="p-6 space-y-6">
            {/* Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white/5 border border-white/10 rounded-xl p-5 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                    <div className="relative z-10">
                        <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">Session P&L</div>
                        <div className="text-3xl font-black text-primary">+$2,847.32</div>
                        <div className="text-xs text-white/40 mt-1">Since 09:30 EST</div>
                    </div>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-5">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">Max Drawdown</div>
                    <div className="text-2xl font-black text-red-400">-$420.69</div>
                    <div className="text-xs text-white/40 mt-1">Peak to trough</div>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-5">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">Sharpe Ratio</div>
                    <div className="text-2xl font-black text-white">3.14</div>
                    <div className="text-xs text-primary mt-1">Excellent</div>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-5">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">Alpha Source</div>
                    <div className="text-2xl font-black text-blue-400">LLM-W3</div>
                    <div className="text-xs text-white/40 mt-1">AI-adjusted model</div>
                </div>
            </div>

            {/* Main Chart */}
            <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                <div className="p-4 border-b border-white/10 flex items-center justify-between">
                    <h2 className="text-xs font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                        <Activity className="w-4 h-4 text-primary animate-pulse" />
                        P&L Velocity Stream
                    </h2>
                    <div className="flex items-center gap-4 text-[10px] font-mono text-muted-foreground">
                        <span className="flex items-center gap-1">
                            <Zap className="w-3 h-3 text-amber-500" />
                            VOLATILITY: HIGH
                        </span>
                        <span className="text-primary">LIVE</span>
                    </div>
                </div>
                <div className="p-4 h-[400px]">
                    <PnLVelocityChart marketId="simulated-election-2024" />
                </div>
            </div>

            {/* Secondary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white/5 border border-white/10 rounded-xl p-5 hover:border-primary/30 transition-colors">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">Win Rate</div>
                    <div className="text-3xl font-black text-white">67.3%</div>
                    <div className="w-full h-2 bg-white/10 rounded-full mt-3 overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-primary to-emerald-400 rounded-full" style={{ width: '67.3%' }} />
                    </div>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-5 hover:border-primary/30 transition-colors">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">Avg Trade Duration</div>
                    <div className="text-3xl font-black text-white">4.2h</div>
                    <div className="text-xs text-white/40 mt-1">Fast execution cycle</div>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-5 hover:border-primary/30 transition-colors">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">Trades Today</div>
                    <div className="text-3xl font-black text-white">23</div>
                    <div className="text-xs text-primary mt-1">+8 vs avg</div>
                </div>
            </div>
        </div>
    );
}

export default function PnLPage() {
    return (
        <DashboardLayout title="P&L ANALYTICS" subtitle="EXECUTION_STREAM" icon={BarChart3}>
            <PnLContent />
        </DashboardLayout>
    );
}
