"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Zap, Crosshair, BarChart, Clock, Filter, AlertTriangle } from 'lucide-react';
import { Button } from "@/components/ui/button";

export function AlphaScanner() {
    const signals = [
        { market: "Trump/Biden Spread", type: "ARBITRAGE", conf: 98, profit: "12%", risk: "LOW", time: "2m ago" },
        { market: "SpaceX Launch Success", type: "NEWS_EVENT", conf: 85, profit: "45%", risk: "MED", time: "5m ago" },
        { market: "CPI Data > 3.2%", type: "MACRO_SIGNAL", conf: 72, profit: "15%", risk: "HIGH", time: "12m ago" },
        { market: "Taylor Swift Engagement", type: "SENTIMENT", conf: 64, profit: "8%", risk: "LOW", time: "45m ago" },
        { market: "BTC > 50k", type: "MOMENTUM", conf: 91, profit: "22%", risk: "MED", time: "1h ago" },
    ];

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex justify-between items-center">
                <div className="space-y-1">
                    <h2 className="text-xl font-black tracking-tighter text-white flex items-center gap-2">
                        <Zap className="w-5 h-5 text-gold animate-pulse" /> ALPHA_SCANNER_V1
                    </h2>
                    <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">Real-time Opportunity Feed</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="h-8 text-[10px] font-mono border-white/10 hover:bg-white/5 uppercase">
                        <Filter className="w-3 h-3 mr-2" /> Filter: High_Conf
                    </Button>
                    <Button variant="outline" size="sm" className="h-8 text-[10px] font-mono border-white/10 hover:bg-white/5 uppercase">
                        <Clock className="w-3 h-3 mr-2" /> Time: 1H
                    </Button>
                </div>
            </div>

            <Card className="glass-panel border-white/10 bg-black/40">
                <div className="relative overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead className="bg-white/[0.02] text-[9px] font-black font-mono uppercase text-muted-foreground/60 tracking-wider">
                            <tr>
                                <th className="px-6 py-4">Signal_ID</th>
                                <th className="px-6 py-4">Market_Context</th>
                                <th className="px-6 py-4">Type</th>
                                <th className="px-6 py-4">Confidence</th>
                                <th className="px-6 py-4">Proj_Alpha</th>
                                <th className="px-6 py-4">Risk_Profile</th>
                                <th className="px-6 py-4 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {signals.map((s, i) => (
                                <tr key={i} className="hover:bg-white/5 transition-colors border-b border-white/5 bg-gradient-to-r from-transparent via-transparent to-transparent hover:from-primary/5 hover:to-transparent group">
                                    <td className="px-6 py-4 font-mono text-[10px] text-muted-foreground group-hover:text-white">
                                        #{Math.floor(Math.random() * 9000) + 1000}
                                    </td>
                                    <td className="px-6 py-4 font-bold text-xs text-white">
                                        {s.market}
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="px-2 py-1 bg-white/5 rounded text-[9px] font-mono font-bold border border-white/10 text-cyber-blue">
                                            {s.type}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full ${s.conf > 90 ? 'bg-primary shadow-[0_0_10px_#10B981]' : s.conf > 70 ? 'bg-indigo' : 'bg-gold'}`}
                                                style={{ width: `${s.conf}%` }}
                                            />
                                        </div>
                                        <span className="text-[9px] font-mono text-muted-foreground mt-1 block">{s.conf}%</span>
                                    </td>
                                    <td className="px-6 py-4 font-mono text-xs text-primary text-glow-primary font-bold">
                                        +{s.profit}
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`text-[9px] font-mono font-bold ${s.risk === 'LOW' ? 'text-primary' : s.risk === 'MED' ? 'text-gold' : 'text-red-500'}`}>
                                            {s.risk}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <Button size="sm" className="h-7 text-[9px] font-mono bg-white/5 hover:bg-primary hover:text-black border border-white/10 transition-all uppercase tracking-wider">
                                            <Crosshair className="w-3 h-3 mr-1" /> SNIPE
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="glass-panel border-white/10 bg-black/40 p-4 flex items-center gap-4 group cursor-pointer hover:border-primary/50 transition-colors">
                    <div className="p-3 rounded-full bg-red-500/10 border border-red-500/20 text-red-500 group-hover:bg-red-500 group-hover:text-black transition-colors">
                        <AlertTriangle className="w-5 h-5" />
                    </div>
                    <div>
                        <h4 className="text-sm font-bold text-white group-hover:text-red-400 transition-colors">Risk Alert: Volatility Spike</h4>
                        <p className="text-[10px] font-mono text-muted-foreground mt-1">Detected abnormal volume in 2024 Election markets.</p>
                    </div>
                </Card>
                <Card className="glass-panel border-white/10 bg-black/40 p-4 flex items-center gap-4 group cursor-pointer hover:border-gold/50 transition-colors">
                    <div className="p-3 rounded-full bg-gold/10 border border-gold/20 text-gold group-hover:bg-gold group-hover:text-black transition-colors">
                        <BarChart className="w-5 h-5" />
                    </div>
                    <div>
                        <h4 className="text-sm font-bold text-white group-hover:text-gold transition-colors">Market Report Ready</h4>
                        <p className="text-[10px] font-mono text-muted-foreground mt-1">Daily alpha summary generated by model.</p>
                    </div>
                </Card>
            </div>
        </div>
    );
}
