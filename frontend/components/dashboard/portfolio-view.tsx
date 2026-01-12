"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUpRight, ArrowDownRight, Wallet, PieChart, TrendingUp, DollarSign, Loader2, Activity } from 'lucide-react';

interface Position {
    asset_id: string;
    condition_id: string;
    question: string;
    outcome: string;
    price: number;
    size: number;
    svalue: number;
    pnl: number;
}

interface PortfolioData {
    balance: number;
    exposure: number;
    positions: Position[];
}

export function PortfolioView() {
    const [data, setData] = useState<PortfolioData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPortfolio = async () => {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api';
                const res = await fetch(`${apiUrl}/portfolio`);
                if (res.ok) {
                    const json = await res.json();
                    setData(json);
                }
            } catch (e) {
                console.error("Failed to fetch portfolio", e);
            } finally {
                setLoading(false);
            }
        };

        fetchPortfolio();
    }, []);

    if (loading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
            </div>
        );
    }

    const balance = data?.balance || 0;
    const exposure = data?.exposure || 0;
    const positions = data?.positions || [];

    // Calculate total PnL from positions
    const totalPnL = positions.reduce((acc, p) => acc + p.pnl, 0);
    const totalEquity = balance + exposure;

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
                        <div className="text-3xl font-black text-white tracking-tight">
                            ${totalEquity.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </div>
                        <div className="flex items-center gap-2 mt-2 text-xs font-mono">
                            <span className={`flex items-center px-1.5 py-0.5 rounded border ${totalPnL >= 0 ? 'bg-primary/10 text-primary border-primary/20' : 'bg-destructive/10 text-destructive border-destructive/20'}`}>
                                {totalPnL >= 0 ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                                ${Math.abs(totalPnL).toFixed(2)}
                            </span>
                            <span className="text-muted-foreground">Unrealized PnL</span>
                        </div>
                    </CardContent>
                </Card>

                <Card className="glass-card border-white/10 bg-black/40 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-indigo/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <CardHeader className="pb-2">
                        <CardTitle className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-indigo" /> Cash Balance
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white tracking-tight">
                            ${balance.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </div>
                        <div className="flex items-center gap-2 mt-2 text-xs font-mono">
                            <span className="text-indigo flex items-center bg-indigo/10 px-1.5 py-0.5 rounded border border-indigo/20">
                                Available
                            </span>
                        </div>
                    </CardContent>
                </Card>

                <Card className="glass-card border-white/10 bg-black/40 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gold/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <CardHeader className="pb-2">
                        <CardTitle className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
                            <DollarSign className="w-4 h-4 text-gold" /> Exposure
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-black text-white tracking-tight">
                            ${exposure.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </div>
                        <div className="flex items-center gap-2 mt-2 text-xs font-mono">
                            <span className="text-gold flex items-center bg-gold/10 px-1.5 py-0.5 rounded border border-gold/20">
                                {positions.length} Active Positions
                            </span>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Equity Curve Chart (Mock SVG - Kept for aesthetics) */}
                <Card className="lg:col-span-2 glass-panel border-white/10 bg-black/40 p-0 overflow-hidden flex flex-col">
                    <CardHeader className="border-b border-white/5 bg-white/[0.02] py-3">
                        <CardTitle className="text-xs font-black font-mono text-muted-foreground uppercase tracking-widest flex justify-between items-center">
                            <span>Performance_History // YTD</span>
                            <div className="flex gap-2">
                                <span className="px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/20 text-[9px] cursor-pointer">1D</span>
                                <span className="px-2 py-0.5 rounded bg-white/5 text-muted-foreground hover:text-white border border-transparent hover:border-white/10 text-[9px] cursor-pointer">1W</span>
                            </div>
                        </CardTitle>
                    </CardHeader>
                    <div className="flex-1 min-h-[300px] relative">
                        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px]" />
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
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#10B981" strokeWidth="12" strokeDasharray="180 251" />
                                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#3b82f6" strokeWidth="12" strokeDasharray="50 251" strokeDashoffset="-185" />
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className="text-2xl font-black text-white">{positions.length}</span>
                                <span className="text-[9px] font-mono text-muted-foreground uppercase">Assets</span>
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
                    {positions.length === 0 ? (
                        <div className="p-8 text-center text-muted-foreground font-mono text-sm flex flex-col items-center gap-3">
                            <Activity className="w-8 h-8 opacity-20" />
                            <span>No active positions. The AI Agent is scanning for alpha...</span>
                        </div>
                    ) : (
                        <table className="w-full text-left">
                            <thead className="bg-white/[0.02] text-[9px] font-black font-mono uppercase text-muted-foreground/60 tracking-wider">
                                <tr>
                                    <th className="px-6 py-3">Instrument</th>
                                    <th className="px-6 py-3">Side</th>
                                    <th className="px-6 py-3 text-right">Size</th>
                                    <th className="px-6 py-3 text-right">Value</th>
                                    <th className="px-6 py-3 text-right">PnL</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {positions.map((pos, i) => (
                                    <tr key={i} className="hover:bg-white/5 transition-colors group">
                                        <td className="px-6 py-3 text-xs font-medium text-white">{pos.question}</td>
                                        <td className="px-6 py-3">
                                            <span className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${pos.outcome === 'Yes' ? 'bg-primary/10 text-primary border border-primary/20' : 'bg-destructive/10 text-destructive border border-destructive/20'}`}>
                                                {pos.outcome}
                                            </span>
                                        </td>
                                        <td className="px-6 py-3 text-right font-mono text-xs text-muted-foreground">{pos.size}</td>
                                        <td className="px-6 py-3 text-right font-mono text-xs text-white">${pos.svalue.toFixed(2)}</td>
                                        <td className={`px-6 py-3 text-right font-mono text-xs font-bold ${pos.pnl >= 0 ? 'text-primary' : 'text-red-400'}`}>
                                            {pos.pnl >= 0 ? '+' : ''}{pos.pnl.toFixed(2)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </Card>
        </div>
    );
}
