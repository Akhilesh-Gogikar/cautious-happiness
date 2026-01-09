"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUpRight, ArrowDownRight, Wallet, PieChart, TrendingUp, DollarSign } from 'lucide-react';

export function PortfolioView() {
    return (
        <div className="space-y-6 animate-fade-in">
            {/* Top Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="glass-card border-white/10 bg-black/40 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <CardHeader className="pb-2">
                        <CardTitle className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
                            <Wallet className="w-4 h-4 text-primary" /> Total Equity
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white tracking-tight">$124,592.42</div>
                        <div className="flex items-center gap-2 mt-2 text-xs font-mono">
                            <span className="text-primary flex items-center bg-primary/10 px-1.5 py-0.5 rounded border border-primary/20">
                                <ArrowUpRight className="w-3 h-3 mr-1" /> +$4,291.00 (3.5%)
                            </span>
                            <span className="text-muted-foreground">Today</span>
                        </div>
                    </CardContent>
                </Card>

                <Card className="glass-card border-white/10 bg-black/40 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-indigo/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <CardHeader className="pb-2">
                        <CardTitle className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-indigo" /> Sharpe Ratio
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white tracking-tight">2.84</div>
                        <div className="flex items-center gap-2 mt-2 text-xs font-mono">
                            <span className="text-indigo flex items-center bg-indigo/10 px-1.5 py-0.5 rounded border border-indigo/20">
                                Top 5% Global
                            </span>
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
                        <div className="text-3xl font-black text-white tracking-tight">$12,840.50</div>
                        <div className="flex items-center gap-2 mt-2 text-xs font-mono">
                            <span className="text-gold flex items-center bg-gold/10 px-1.5 py-0.5 rounded border border-gold/20">
                                4 Active Positions
                            </span>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Equity Curve Chart (Mock SVG) */}
                <Card className="lg:col-span-2 glass-panel border-white/10 bg-black/40 p-0 overflow-hidden flex flex-col">
                    <CardHeader className="border-b border-white/5 bg-white/[0.02] py-3">
                        <CardTitle className="text-xs font-black font-mono text-muted-foreground uppercase tracking-widest flex justify-between items-center">
                            <span>Performance_History // YTD</span>
                            <div className="flex gap-2">
                                <span className="px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/20 text-[9px] cursor-pointer">1D</span>
                                <span className="px-2 py-0.5 rounded bg-white/5 text-muted-foreground hover:text-white border border-transparent hover:border-white/10 text-[9px] cursor-pointer">1W</span>
                                <span className="px-2 py-0.5 rounded bg-white/5 text-muted-foreground hover:text-white border border-transparent hover:border-white/10 text-[9px] cursor-pointer">1M</span>
                                <span className="px-2 py-0.5 rounded bg-white/5 text-muted-foreground hover:text-white border border-transparent hover:border-white/10 text-[9px] cursor-pointer">YTD</span>
                            </div>
                        </CardTitle>
                    </CardHeader>
                    <div className="flex-1 min-h-[300px] relative">
                        {/* Grid */}
                        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px]" />

                        {/* Chart Line */}
                        <svg className="absolute inset-0 w-full h-full p-4" viewBox="0 0 100 50" preserveAspectRatio="none">
                            <defs>
                                <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#10B981" stopOpacity="0.2" />
                                    <stop offset="100%" stopColor="#10B981" stopOpacity="0" />
                                </linearGradient>
                            </defs>
                            <path d="M0 45 L 5 44 L 10 46 L 15 42 L 20 40 L 25 41 L 30 35 L 35 36 L 40 30 L 45 28 L 50 25 L 55 26 L 60 20 L 65 18 L 70 22 L 75 15 L 80 12 L 85 10 L 90 8 L 95 5 L 100 2"
                                fill="url(#chartGradient)"
                                stroke="#10B981"
                                strokeWidth="0.5"
                                vectorEffect="non-scaling-stroke" />
                        </svg>

                        {/* Hover Overlay Line (Mock) */}
                        <div className="absolute top-0 bottom-0 left-[60%] w-[1px] bg-white/20 border-r border-dashed border-white/20 pointer-events-none">
                            <div className="absolute top-[20%] -right-1 w-2 h-2 bg-primary rounded-full shadow-[0_0_10px_#10B981]" />
                            <div className="absolute top-[5%] left-2 bg-black/80 border border-white/10 p-2 rounded backdrop-blur-md">
                                <div className="text-[9px] text-muted-foreground font-mono">VALUATION</div>
                                <div className="text-xs font-bold text-white font-mono">$118,240.00</div>
                            </div>
                        </div>
                    </div>
                </Card>

                {/* Asset Allocation */}
                <Card className="glass-panel border-white/10 bg-black/40">
                    <CardHeader className="border-b border-white/5 bg-white/[0.02] py-3">
                        <CardTitle className="text-xs font-black font-mono text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                            <PieChart className="w-3 h-3 text-cyber-blue" /> Exposure_Proflie
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-6 flex flex-col items-center justify-center space-y-6">
                        <div className="relative w-40 h-40">
                            <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
                                {/* Circle Segments - Mocking a Donut Chart */}
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#10B981" strokeWidth="12" strokeDasharray="180 251" /> {/* 70% Primary */}
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#3b82f6" strokeWidth="12" strokeDasharray="50 251" strokeDashoffset="-185" /> {/* 20% Blue */}
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#f59e0b" strokeWidth="12" strokeDasharray="20 251" strokeDashoffset="-235" /> {/* 10% Gold */}
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className="text-2xl font-black text-white">4</span>
                                <span className="text-[9px] font-mono text-muted-foreground uppercase">Assets</span>
                            </div>
                        </div>
                        <div className="w-full space-y-2">
                            <div className="flex justify-between items-center text-[10px] font-mono">
                                <div className="flex items-center gap-2"><div className="w-2 h-2 bg-primary rounded-sm" /> POLY_MARKETS</div>
                                <span className="text-white">72%</span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] font-mono">
                                <div className="flex items-center gap-2"><div className="w-2 h-2 bg-indigo rounded-sm" /> USDC_YIELD</div>
                                <span className="text-white">18%</span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] font-mono">
                                <div className="flex items-center gap-2"><div className="w-2 h-2 bg-gold rounded-sm" /> PENDING_ARB</div>
                                <span className="text-white">10%</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Active Positions Table */}
            <Card className="glass-panel border-white/10 bg-black/40">
                <CardHeader className="border-b border-white/5 bg-white/[0.02] py-3">
                    <CardTitle className="text-xs font-black font-mono text-muted-foreground uppercase tracking-widest">
                        Active_Order_Flow
                    </CardTitle>
                </CardHeader>
                <div className="relative overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-white/[0.02] text-[9px] font-black font-mono uppercase text-muted-foreground/60 tracking-wider">
                            <tr>
                                <th className="px-6 py-3">Instrument</th>
                                <th className="px-6 py-3">Side</th>
                                <th className="px-6 py-3 text-right">Entry</th>
                                <th className="px-6 py-3 text-right">Current</th>
                                <th className="px-6 py-3 text-right">PnL</th>
                                <th className="px-6 py-3 text-right">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {[
                                { name: "Will BTC hit 100k in Q1?", side: "YES", entry: 0.12, current: 0.45, pnl: 275, status: "OPEN" },
                                { name: "Fed Rate Cut March", side: "NO", entry: 0.65, current: 0.62, pnl: -4.5, status: "HEDGED" },
                                { name: "ETH Flippening 2026", side: "YES", entry: 0.08, current: 0.15, pnl: 87.5, status: "OPEN" },
                                { name: "US Election Result Certified", side: "YES", entry: 0.98, current: 0.99, pnl: 1.2, status: "CLOSING" },
                            ].map((pos, i) => (
                                <tr key={i} className="hover:bg-white/5 transition-colors group">
                                    <td className="px-6 py-3 text-xs font-medium text-white">{pos.name}</td>
                                    <td className="px-6 py-3">
                                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${pos.side === 'YES' ? 'bg-primary/10 text-primary border border-primary/20' : 'bg-destructive/10 text-destructive border border-destructive/20'}`}>
                                            {pos.side}
                                        </span>
                                    </td>
                                    <td className="px-6 py-3 text-right font-mono text-xs text-muted-foreground">${pos.entry}</td>
                                    <td className="px-6 py-3 text-right font-mono text-xs text-white">${pos.current}</td>
                                    <td className={`px-6 py-3 text-right font-mono text-xs font-bold ${pos.pnl >= 0 ? 'text-primary' : 'text-red-400'}`}>
                                        {pos.pnl >= 0 ? '+' : ''}{pos.pnl}%
                                    </td>
                                    <td className="px-6 py-3 text-right">
                                        <span className="text-[9px] font-mono text-muted-foreground/60 group-hover:text-white transition-colors">{pos.status}</span>
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
