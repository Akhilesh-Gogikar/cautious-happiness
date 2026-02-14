"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Play, Pause, Settings2, BrainCircuit, LineChart } from 'lucide-react';
import { useState } from 'react';

export function StrategyView() {
    const [kellyFraction, setKellyFraction] = useState([0.5]);
    const [slippage, setSlippage] = useState([0.5]);

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex justify-between items-center">
                <div className="space-y-1">
                    <h2 className="text-xl font-black tracking-tighter text-white flex items-center gap-2">
                        <BrainCircuit className="w-5 h-5 text-indigo animate-pulse" /> STRATEGY_ENGINE
                    </h2>
                    <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">Automated Execution Rules</p>
                </div>
                <div className="flex gap-2">
                    <Button size="sm" className="h-8 text-[10px] font-mono bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 uppercase tracking-wider">
                        <Play className="w-3 h-3 mr-1" /> Deploy_Active
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Kelly Engine Control Panel */}
                <Card className="glass-panel border-white/10 bg-black/40 lg:col-span-1">
                    <CardHeader className="border-b border-white/5 bg-white/[0.02] py-3">
                        <CardTitle className="text-xs font-black font-mono text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                            <Settings2 className="w-3 h-3" /> Kelly_Criterion_Config
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-6 space-y-8">
                        {/* Fractional Kelly */}
                        <div className="space-y-4">
                            <div className="flex justify-between items-center">
                                <label className="text-[10px] font-mono text-white font-bold uppercase">Exposure_Fraction (Kelly)</label>
                                <span className="text-xs font-black text-primary font-mono">{kellyFraction[0]}x</span>
                            </div>
                            <Slider
                                defaultValue={[0.5]}
                                max={1}
                                step={0.1}
                                onValueChange={setKellyFraction}
                                className="[&_.bg-primary]:bg-primary [&_.border-primary]:border-primary"
                            />
                            <p className="text-[9px] text-muted-foreground">Adjusts bet sizing based on model confidence. Lower values reduce volatility.</p>
                        </div>

                        {/* Slippage Tolerance */}
                        <div className="space-y-4">
                            <div className="flex justify-between items-center">
                                <label className="text-[10px] font-mono text-white font-bold uppercase">Max_Slippage_Tolerance</label>
                                <span className="text-xs font-black text-indigo font-mono">{slippage[0]}%</span>
                            </div>
                            <Slider
                                defaultValue={[0.5]}
                                max={5}
                                step={0.1}
                                onValueChange={setSlippage}
                                className="[&_.bg-primary]:bg-indigo [&_.border-primary]:border-indigo"
                            />
                            <p className="text-[9px] text-muted-foreground">Maximum price deviation accepted during atomic execution.</p>
                        </div>

                        {/* AI Critic Toggle */}
                        <div className="flex items-center justify-between border-t border-white/5 pt-4">
                            <div className="space-y-0.5">
                                <label className="text-[10px] font-mono text-white font-bold uppercase">Reasoning_Critic</label>
                                <p className="text-[9px] text-muted-foreground">Require &quot;Step-by-Step&quot; verify before trade</p>
                            </div>
                            <Switch />
                        </div>
                    </CardContent>
                </Card>

                {/* Active Strategies Grid */}
                <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                        { name: "Mean Reversion", desc: "Bet against >2 sigma moves on low volume.", active: true, pnl: "+12.4%", color: "primary" },
                        { name: "News Momentum", desc: "Follow trend on high-confidence API signals.", active: true, pnl: "+45.2%", color: "indigo" },
                        { name: "Polymarket Arb", desc: "Exploit discrepancies between related markets.", active: false, pnl: "0.0%", color: "gold" },
                        { name: "Gamma Scalping", desc: "Dynamic hedging of binary option delta.", active: false, pnl: "-2.1%", color: "fuchsia" },
                    ].map((strat, i) => (
                        <Card key={i} className={`glass-panel border-white/10 bg-black/40 relative overflow-hidden group transition-all duration-300 ${strat.active ? 'border-l-4 border-l-' + (strat.color === 'primary' ? 'primary' : strat.color) : 'opacity-60 grayscale'}`}>
                            <CardHeader className="pb-2">
                                <div className="flex justify-between items-start">
                                    <CardTitle className="text-sm font-black text-white">{strat.name}</CardTitle>
                                    <Switch checked={strat.active} />
                                </div>
                                <p className="text-[10px] text-muted-foreground font-mono h-8">{strat.desc}</p>
                            </CardHeader>
                            <CardContent>
                                <div className="mt-4 flex items-end justify-between">
                                    <div className="space-y-1">
                                        <div className="text-[9px] font-mono text-muted-foreground uppercase">Performance (30d)</div>
                                        <div className={`text-xl font-black ${strat.pnl.startsWith('-') ? 'text-destructive' : 'text-white'}`}>{strat.pnl}</div>
                                    </div>
                                    {strat.active && <LineChart className={`w-12 h-8 text-${strat.color} opacity-50`} />}
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
}
