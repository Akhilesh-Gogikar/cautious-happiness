"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUpRight, ArrowDownRight, Wallet, PieChart, TrendingUp, DollarSign, Activity, Target, Zap, ShieldAlert, BarChart3, Layers } from 'lucide-react';
import { useEffect, useState } from "react";
import { AlpacaDashboard } from "./alpaca-dashboard";

export function PortfolioView() {
    const [mounted, setMounted] = useState(false);
    const [hasAlpacaAuth, setHasAlpacaAuth] = useState(false);

    useEffect(() => {
        setMounted(true);
        if (localStorage.getItem("ALPACA_API_KEY")) {
            setHasAlpacaAuth(true);
        }
    }, []);

    if (!mounted) return null;

    if (hasAlpacaAuth) {
        return <AlpacaDashboard />;
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Top Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="glass-card border-white/10 bg-black/40 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <CardHeader className="pb-2">
                        <CardTitle className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
                            <Wallet className="w-4 h-4 text-primary" /> Total Equity
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white tracking-tight drop-shadow-[0_0_15px_rgba(16,185,129,0.3)]">
                            $2,124,592.42
                        </div>
                        <div className="flex items-center gap-2 mt-2 text-xs font-mono">
                            <span className="text-primary flex items-center bg-primary/10 px-1.5 py-0.5 rounded border border-primary/20 shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                                <ArrowUpRight className="w-3 h-3 mr-1" /> +$14,291.50 (0.67%)
                            </span>
                            <span className="text-muted-foreground">Live PnL</span>
                        </div>
                    </CardContent>
                </Card>

                <Card className="glass-card border-white/10 bg-black/40 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-rose-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <CardHeader className="pb-2">
                        <CardTitle className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
                            <ShieldAlert className="w-4 h-4 text-rose-500" /> Margin Utilization
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex justify-between items-end mb-2">
                            <div className="text-3xl font-black text-white tracking-tight">68.4%</div>
                            <div className="text-xs font-mono text-rose-400 mb-1">HIGH</div>
                        </div>
                        <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
                            <div className="h-full bg-gradient-to-r from-rose-500/50 to-rose-500 w-[68.4%] rounded-full shadow-[0_0_10px_rgba(244,63,94,0.5)]" />
                        </div>
                        <div className="flex justify-between mt-2 text-[10px] text-muted-foreground font-mono">
                            <span>$1.2M Used</span>
                            <span>$1.75M Limit</span>
                        </div>
                    </CardContent>
                </Card>

                <Card className="glass-card border-white/10 bg-black/40 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-indigo/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <CardHeader className="pb-2">
                        <CardTitle className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
                            <Activity className="w-4 h-4 text-indigo-400" /> Options Greeks
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 pt-1">
                        <div className="flex justify-between items-center text-xs font-mono">
                            <span className="text-muted-foreground flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" /> Net Delta
                            </span>
                            <span className="text-indigo-400 font-bold">+450,210 $</span>
                        </div>
                        <div className="flex justify-between items-center text-xs font-mono">
                            <span className="text-muted-foreground flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-purple-400" /> Net Gamma
                            </span>
                            <span className="text-purple-400 font-bold">-12,450 $</span>
                        </div>
                        <div className="flex justify-between items-center text-xs font-mono">
                            <span className="text-muted-foreground flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-amber-400" /> Net Theta
                            </span>
                            <span className="text-amber-400 font-bold">+2,150 $/d</span>
                        </div>
                    </CardContent>
                </Card>

                <Card className="glass-card border-white/10 bg-black/40 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gold/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <CardHeader className="pb-2">
                        <CardTitle className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
                            <DollarSign className="w-4 h-4 text-gold" /> Unsettled PnL
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white tracking-tight">$32,840.50</div>
                        <div className="flex items-center gap-2 mt-2 text-xs font-mono">
                            <span className="text-gold flex items-center bg-gold/10 px-1.5 py-0.5 rounded border border-gold/20">
                                <Layers className="w-3 h-3 mr-1" /> 12 Active Pos
                            </span>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Equity Curve Chart */}
                <Card className="lg:col-span-2 glass-panel border-white/10 bg-black/40 p-0 overflow-hidden flex flex-col relative group">
                    <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                    <CardHeader className="border-b border-white/5 bg-white/[0.02] py-3 relative z-10">
                        <CardTitle className="text-xs font-black font-mono text-muted-foreground uppercase tracking-widest flex justify-between items-center">
                            <span className="flex items-center gap-2"><TrendingUp className="w-4 h-4 text-primary" /> Performance_History // YTD</span>
                            <div className="flex gap-2 bg-black/50 p-1 rounded-md border border-white/5">
                                <span className="px-2 py-0.5 rounded bg-white/5 text-muted-foreground hover:text-white border border-transparent hover:border-white/10 text-[9px] cursor-pointer transition-colors">1D</span>
                                <span className="px-2 py-0.5 rounded bg-white/5 text-muted-foreground hover:text-white border border-transparent hover:border-white/10 text-[9px] cursor-pointer transition-colors">1W</span>
                                <span className="px-2 py-0.5 rounded bg-white/5 text-muted-foreground hover:text-white border border-transparent hover:border-white/10 text-[9px] cursor-pointer transition-colors">1M</span>
                                <span className="px-2 py-0.5 rounded bg-primary/20 text-primary border border-primary/30 text-[9px] cursor-pointer shadow-[0_0_10px_rgba(16,185,129,0.2)]">YTD</span>
                            </div>
                        </CardTitle>
                    </CardHeader>
                    <div className="flex-1 min-h-[300px] relative">
                        {/* Grid */}
                        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:linear-gradient(to_bottom,white,transparent)]" />

                        {/* Chart Line */}
                        <svg className="absolute inset-0 w-full h-full p-4 drop-shadow-[0_0_15px_rgba(16,185,129,0.4)]" viewBox="0 0 100 50" preserveAspectRatio="none">
                            <defs>
                                <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#10B981" stopOpacity="0.4" />
                                    <stop offset="100%" stopColor="#10B981" stopOpacity="0" />
                                </linearGradient>
                            </defs>
                            <path d="M0 45 L 5 44 L 10 46 L 15 42 L 20 40 L 25 41 L 30 35 L 35 36 L 40 30 L 45 28 L 50 25 L 55 26 L 60 20 L 65 18 L 70 22 L 75 15 L 80 12 L 85 10 L 90 8 L 95 5 L 100 2"
                                fill="url(#chartGradient)"
                                stroke="#10B981"
                                strokeWidth="0.8"
                                vectorEffect="non-scaling-stroke" />
                        </svg>

                        {/* Hover Overlay Line (Mock) */}
                        <div className="absolute top-0 bottom-0 left-[60%] w-[1px] bg-white/20 border-r border-dashed border-white/20 pointer-events-none group-hover:opacity-100 opacity-50 transition-opacity">
                            <div className="absolute top-[20%] -right-1.5 w-3 h-3 bg-primary rounded-full shadow-[0_0_15px_#10B981] ring-2 ring-black" />
                            <div className="absolute top-[5%] left-3 bg-black/90 border border-primary/30 p-2.5 rounded-lg backdrop-blur-xl shadow-xl shadow-black/50">
                                <div className="text-[10px] text-muted-foreground font-mono mb-0.5">MAR 14, 2026</div>
                                <div className="text-sm font-bold text-white font-mono">$1,988,240.00</div>
                                <div className="text-[10px] text-primary font-mono mt-0.5">+1.2% Day</div>
                            </div>
                        </div>
                    </div>
                </Card>

                {/* Asset Allocation */}
                <Card className="glass-panel border-white/10 bg-black/40 relative overflow-hidden">
                    <div className="absolute -top-20 -right-20 w-40 h-40 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
                    <CardHeader className="border-b border-white/5 bg-white/[0.02] py-3">
                        <CardTitle className="text-xs font-black font-mono text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                            <PieChart className="w-4 h-4 text-blue-400" /> Asset_Allocation
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-6 flex flex-col items-center justify-center space-y-8 relative z-10">
                        <div className="relative w-48 h-48 drop-shadow-[0_0_20px_rgba(59,130,246,0.15)]">
                            <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
                                {/* Background Ring */}
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="rgba(255,255,255,0.05)" strokeWidth="12" />
                                {/* Segments */}
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#3b82f6" strokeWidth="12" strokeDasharray="130 251" className="hover:opacity-80 transition-opacity cursor-pointer delay-100" style={{ strokeLinecap: 'butt' }} /> {/* 50% Blue - Equities */}
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#10b981" strokeWidth="12" strokeDasharray="75 251" strokeDashoffset="-133" className="hover:opacity-80 transition-opacity cursor-pointer delay-200" style={{ strokeLinecap: 'butt' }} /> {/* 30% Green - Derivatives */}
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#f59e0b" strokeWidth="12" strokeDasharray="38 251" strokeDashoffset="-210" className="hover:opacity-80 transition-opacity cursor-pointer delay-300" style={{ strokeLinecap: 'butt' }} /> {/* 15% Gold - Cash */}
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#8b5cf6" strokeWidth="12" strokeDasharray="12 251" strokeDashoffset="-250" className="hover:opacity-80 transition-opacity cursor-pointer delay-300" style={{ strokeLinecap: 'butt' }} /> {/* 5% Purple - Crypto */}
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                                <span className="text-3xl font-black text-white tracking-tighter">4</span>
                                <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mt-1">Sectors</span>
                            </div>
                        </div>

                        <div className="w-full space-y-3 bg-white/[0.02] p-4 rounded-xl border border-white/5">
                            <div className="flex justify-between items-center text-xs font-mono group cursor-pointer hover:bg-white/5 p-1 -mx-1 rounded transition-colors">
                                <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 bg-blue-500 rounded-sm shadow-[0_0_8px_rgba(59,130,246,0.5)]" /> EQUITIES</div>
                                <div className="flex gap-4"><span className="text-muted-foreground">$1.06M</span><span className="text-white font-bold w-10 text-right">52%</span></div>
                            </div>
                            <div className="flex justify-between items-center text-xs font-mono group cursor-pointer hover:bg-white/5 p-1 -mx-1 rounded transition-colors">
                                <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 bg-green-500 rounded-sm shadow-[0_0_8px_rgba(16,185,129,0.5)]" /> DERIVATIVES</div>
                                <div className="flex gap-4"><span className="text-muted-foreground">$637k</span><span className="text-white font-bold w-10 text-right">30%</span></div>
                            </div>
                            <div className="flex justify-between items-center text-xs font-mono group cursor-pointer hover:bg-white/5 p-1 -mx-1 rounded transition-colors">
                                <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 bg-amber-500 rounded-sm shadow-[0_0_8px_rgba(245,158,11,0.5)]" /> CASH_EQ</div>
                                <div className="flex gap-4"><span className="text-muted-foreground">$318k</span><span className="text-white font-bold w-10 text-right">15%</span></div>
                            </div>
                            <div className="flex justify-between items-center text-xs font-mono group cursor-pointer hover:bg-white/5 p-1 -mx-1 rounded transition-colors">
                                <div className="flex items-center gap-2"><div className="w-2.5 h-2.5 bg-purple-500 rounded-sm shadow-[0_0_8px_rgba(139,92,246,0.5)]" /> CRYPTO_STRAT</div>
                                <div className="flex gap-4"><span className="text-muted-foreground">$106k</span><span className="text-white font-bold w-10 text-right">3%</span></div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Cross-Account Exposures Table */}
            <Card className="glass-panel border-white/10 bg-black/40 overflow-hidden">
                <CardHeader className="border-b border-white/5 bg-white/[0.02] py-4 flex flex-row items-center justify-between">
                    <CardTitle className="text-xs font-black font-mono text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                        <BarChart3 className="w-4 h-4 text-white" /> Brokerage_Allocations_&_Greeks
                    </CardTitle>
                    <div className="flex gap-2">
                        <span className="text-[10px] font-mono px-2 py-1 rounded bg-white/5 text-white border border-white/10 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" /> 3 Connected
                        </span>
                    </div>
                </CardHeader>
                <div className="relative overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-black/20 text-[10px] font-black font-mono uppercase text-muted-foreground/80 tracking-widest border-b border-white/5">
                            <tr>
                                <th className="px-6 py-4">Account / Broker</th>
                                <th className="px-6 py-4 text-right">Net Liquidity</th>
                                <th className="px-6 py-4 text-right">Margin Util</th>
                                <th className="px-6 py-4 text-right">Delta ($)</th>
                                <th className="px-6 py-4 text-right">Gamma ($)</th>
                                <th className="px-6 py-4 text-right">Day PnL</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {[
                                { broker: "IBKR_PRO_01", liq: 1250400, margin: 72, delta: 310500, gamma: -8200, pnl: 12400 },
                                { broker: "ALPACA_ALG_01", liq: 540320, margin: 45, delta: 85400, gamma: 1200, pnl: 3250 },
                                { broker: "KRAKEN_INST", liq: 333872, margin: 85, delta: 54310, gamma: -5450, pnl: -1358.50 },
                            ].map((acc, i) => (
                                <tr key={i} className="hover:bg-white/[0.02] transition-colors group">
                                    <td className="px-6 py-4 text-xs font-bold text-white font-mono flex items-center gap-2">
                                        <div className="w-6 h-6 rounded bg-white/10 flex items-center justify-center text-[10px]">
                                            {acc.broker.substring(0, 2)}
                                        </div>
                                        {acc.broker}
                                    </td>
                                    <td className="px-6 py-4 text-right font-mono text-xs text-white">
                                        ${acc.liq.toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <div className="flex items-center justify-end gap-2">
                                            <span className={`text-[10px] font-mono ${acc.margin > 80 ? 'text-rose-400' : 'text-muted-foreground'}`}>{acc.margin}%</span>
                                            <div className="w-16 h-1.5 bg-white/5 rounded-full overflow-hidden">
                                                <div className={`h-full rounded-full ${acc.margin > 80 ? 'bg-rose-500' : acc.margin > 60 ? 'bg-amber-500' : 'bg-green-500'}`} style={{ width: `${acc.margin}%` }} />
                                            </div>
                                        </div>
                                    </td>
                                    <td className={`px-6 py-4 text-right font-mono text-xs ${acc.delta >= 0 ? 'text-green-400' : 'text-rose-400'}`}>
                                        {acc.delta >= 0 ? '+' : ''}{acc.delta.toLocaleString()}
                                    </td>
                                    <td className={`px-6 py-4 text-right font-mono text-xs ${acc.gamma >= 0 ? 'text-green-400' : 'text-rose-400'}`}>
                                        {acc.gamma >= 0 ? '+' : ''}{acc.gamma.toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold ${acc.pnl >= 0 ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                                            {acc.pnl >= 0 ? '+' : ''}{acc.pnl.toLocaleString()}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}
