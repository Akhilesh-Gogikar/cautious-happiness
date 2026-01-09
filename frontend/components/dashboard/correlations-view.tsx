"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Network } from 'lucide-react';

export function CorrelationsView() {
    const assets = ["BTC", "ETH", "SOL", "TRUMP", "BIDEN", "FED", "CPI"];

    // Mock Correlation Matrix (-1 to 1)
    const correlations = [
        [1.00, 0.85, 0.72, 0.45, -0.42, -0.65, -0.30], // BTC
        [0.85, 1.00, 0.78, 0.40, -0.38, -0.60, -0.25], // ETH
        [0.72, 0.78, 1.00, 0.35, -0.30, -0.55, -0.20], // SOL
        [0.45, 0.40, 0.35, 1.00, -0.92, 0.15, 0.10],   // TRUMP
        [-0.42, -0.38, -0.30, -0.92, 1.00, -0.10, -0.05], // BIDEN
        [-0.65, -0.60, -0.55, 0.15, -0.10, 1.00, 0.45],  // FED
        [-0.30, -0.25, -0.20, 0.10, -0.05, 0.45, 1.00],  // CPI
    ];

    const getColor = (val: number) => {
        if (val === 1) return "bg-white/10 text-white";
        // Green for positive, Red for negative
        if (val > 0) {
            const intensity = Math.round(val * 100);
            // Using tailwind arbitrary values for dynamic opacity
            return `bg-emerald-500/${intensity > 20 ? intensity : 20} text-white`;
        } else {
            const intensity = Math.round(Math.abs(val) * 100);
            return `bg-red-500/${intensity > 20 ? intensity : 20} text-white`;
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="space-y-1">
                <h2 className="text-xl font-black tracking-tighter text-white flex items-center gap-2">
                    <Network className="w-5 h-5 text-cyber-blue animate-pulse" /> MARKET_CORRELATIONS
                </h2>
                <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">Cross-Asset Dependency Matrix</p>
            </div>

            <Card className="glass-panel border-white/10 bg-black/40 overflow-hidden">
                <div className="p-6 overflow-x-auto">
                    <div className="min-w-[600px]">
                        {/* Header Row */}
                        <div className="flex mb-2">
                            <div className="w-24 shrink-0"></div>
                            {assets.map(asset => (
                                <div key={asset} className="w-24 text-center text-xs font-black font-mono text-muted-foreground uppercase">{asset}</div>
                            ))}
                        </div>

                        {/* Rows */}
                        {assets.map((rowAsset, i) => (
                            <div key={rowAsset} className="flex mb-2 items-center">
                                {/* Row Label */}
                                <div className="w-24 shrink-0 text-xs font-black font-mono text-white uppercase text-right pr-4">{rowAsset}</div>

                                {/* Cells */}
                                {correlations[i].map((val, j) => (
                                    <div key={j} className="w-24 h-12 p-1">
                                        <div className={`w-full h-full rounded flex items-center justify-center text-xs font-mono font-bold transition-all hover:scale-105 cursor-default ${getColor(val)}`}>
                                            {val > 0 ? '+' : ''}{val.toFixed(2)}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="glass-panel border-white/10 p-4 flex flex-col justify-center items-center text-center">
                    <h4 className="text-xs font-black text-white uppercase mb-2">Highest Correlation</h4>
                    <div className="text-2xl font-black text-primary">TRUMP / BTC (+0.45)</div>
                    <p className="text-[10px] text-muted-foreground mt-2">Strong signal alignment detected.</p>
                </Card>
                <Card className="glass-panel border-white/10 p-4 flex flex-col justify-center items-center text-center">
                    <h4 className="text-xs font-black text-white uppercase mb-2">Inverse Correlation</h4>
                    <div className="text-2xl font-black text-destructive">TRUMP / BIDEN (-0.92)</div>
                    <p className="text-[10px] text-muted-foreground mt-2">Prediction markets mirroring.</p>
                </Card>
                <Card className="glass-panel border-white/10 p-4 flex flex-col justify-center items-center text-center">
                    <h4 className="text-xs font-black text-white uppercase mb-2">Macro Sensitivity</h4>
                    <div className="text-2xl font-black text-indigo">FED / BTC (-0.65)</div>
                    <p className="text-[10px] text-muted-foreground mt-2">High sensitivity to rate cuts.</p>
                </Card>
            </div>
        </div>
    );
}
