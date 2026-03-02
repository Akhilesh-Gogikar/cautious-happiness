"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, X, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

// Mock available assets
const AVAILABLE_ASSETS = [
    "SPY", "QQQ", "IWM", "BTC", "ETH", "GLD", "SLV", "USO", "TLT", "VIX",
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN"
];

// Helper to generate a deterministically random correlation between -1.0 and 1.0
// using a simple seed based calculation for demo
const getCorrelation = (assetA: string, assetB: string, period: string) => {
    if (assetA === assetB) return 1.0;

    // Simple deterministic hash
    const hash = (assetA.charCodeAt(0) + assetB.charCodeAt(0) + (period === '30D' ? 1 : 2)) * 17;
    const value = ((hash % 200) - 100) / 100; // -1.0 to 1.0
    return Number(value.toFixed(2));
};

const getColorClass = (value: number) => {
    if (value === 1) return "bg-primary/80 text-white font-bold";
    if (value > 0.7) return "bg-primary/60 text-white";
    if (value > 0.4) return "bg-primary/40 text-primary-foreground";
    if (value > 0.1) return "bg-primary/20 text-muted-foreground";
    if (value > -0.1) return "bg-white/5 text-muted-foreground";
    if (value > -0.4) return "bg-rose-500/20 text-rose-300";
    if (value > -0.7) return "bg-rose-500/40 text-rose-200";
    if (value >= -1.0) return "bg-rose-500/60 text-rose-100";
    return "bg-black text-transparent";
};

export function CorrelationHeatmap() {
    const [selectedAssets, setSelectedAssets] = useState<string[]>(["SPY", "QQQ", "TLT", "GLD", "BTC"]);
    const [period, setPeriod] = useState<"30D" | "90D">("30D");

    const toggleAsset = (asset: string) => {
        if (selectedAssets.includes(asset)) {
            setSelectedAssets(prev => prev.filter(a => a !== asset));
        } else {
            if (selectedAssets.length < 10) {
                setSelectedAssets(prev => [...prev, asset]);
            }
        }
    };

    return (
        <Card className="glass-panel border-white/10 bg-black/40 overflow-hidden relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-rose-500/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
            <CardHeader className="border-b border-white/5 bg-white/[0.02] py-4">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <CardTitle className="text-xs font-black font-mono text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                        <Activity className="w-4 h-4 text-primary" /> FACTOR_ANALYSIS // CORRELATION_MATRIX
                    </CardTitle>

                    <div className="flex gap-2 bg-black/50 p-1 rounded-md border border-white/5">
                        <button
                            onClick={() => setPeriod("30D")}
                            className={cn(
                                "px-3 py-1 rounded text-[10px] font-mono font-bold transition-all cursor-pointer",
                                period === "30D"
                                    ? "bg-primary/20 text-primary border border-primary/30 shadow-[0_0_10px_rgba(16,185,129,0.2)]"
                                    : "bg-white/5 text-muted-foreground hover:text-white border border-transparent hover:border-white/10"
                            )}>
                            30-DAY
                        </button>
                        <button
                            onClick={() => setPeriod("90D")}
                            className={cn(
                                "px-3 py-1 rounded text-[10px] font-mono font-bold transition-all cursor-pointer",
                                period === "90D"
                                    ? "bg-primary/20 text-primary border border-primary/30 shadow-[0_0_10px_rgba(16,185,129,0.2)]"
                                    : "bg-white/5 text-muted-foreground hover:text-white border border-transparent hover:border-white/10"
                            )}>
                            90-DAY
                        </button>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="p-6 space-y-6">

                {/* Asset Selector */}
                <div className="space-y-3 relative z-10">
                    <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest flex justify-between">
                        <span>Selected Assets ({selectedAssets.length}/10)</span>
                        {selectedAssets.length >= 10 && <span className="text-rose-400">MAX LIMIT REACHED</span>}
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {selectedAssets.map(asset => (
                            <button
                                key={asset}
                                onClick={() => toggleAsset(asset)}
                                className="flex items-center gap-1.5 px-2.5 py-1 rounded border border-white/20 bg-white/10 hover:bg-white/15 hover:border-white/30 text-white text-[11px] font-mono transition-colors group"
                            >
                                {asset}
                                <X className="w-3 h-3 text-muted-foreground group-hover:text-rose-400 transition-colors" />
                            </button>
                        ))}
                    </div>
                    <div className="flex flex-wrap gap-1.5 pt-2 border-t border-white/5">
                        {AVAILABLE_ASSETS.filter(a => !selectedAssets.includes(a)).map(asset => (
                            <button
                                key={asset}
                                onClick={() => toggleAsset(asset)}
                                disabled={selectedAssets.length >= 10}
                                className="flex items-center gap-1 px-2 py-0.5 rounded border border-white/5 bg-transparent hover:bg-white/5 text-muted-foreground hover:text-white text-[10px] font-mono transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                            >
                                <Plus className="w-3 h-3" /> {asset}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Heatmap Grid */}
                <div className="relative z-10 overflow-x-auto pb-4">
                    {selectedAssets.length > 0 ? (
                        <div className="min-w-max">
                            <div className="grid" style={{ gridTemplateColumns: `auto repeat(${selectedAssets.length}, minmax(40px, 1fr))` }}>
                                {/* Header Row */}
                                <div className="p-2"></div>
                                {selectedAssets.map(asset => (
                                    <div key={`header-${asset}`} className="p-2 text-center text-[10px] font-bold font-mono text-muted-foreground">
                                        {asset}
                                    </div>
                                ))}

                                {/* Matrix Rows */}
                                {selectedAssets.map(assetRow => (
                                    <div key={`row-${assetRow}`} className="contents">
                                        <div className="p-2 text-right text-[10px] font-bold font-mono text-muted-foreground self-center pr-4">
                                            {assetRow}
                                        </div>
                                        {selectedAssets.map(assetCol => {
                                            const val = getCorrelation(assetRow, assetCol, period);
                                            return (
                                                <div
                                                    key={`${assetRow}-${assetCol}`}
                                                    className="p-1"
                                                >
                                                    <div
                                                        className={cn(
                                                            "w-full h-10 flex items-center justify-center rounded text-[10px] font-mono border border-white/5 transition-colors cursor-default hover:ring-1 hover:ring-white/30",
                                                            getColorClass(val)
                                                        )}
                                                        title={`${assetRow} vs ${assetCol}: ${val.toFixed(2)}`}
                                                    >
                                                        {val.toFixed(2)}
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="h-40 flex items-center justify-center text-xs font-mono text-muted-foreground border border-dashed border-white/10 rounded-lg bg-white/[0.01]">
                            SELECT ASSETS TO GENERATE MATRIX
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
