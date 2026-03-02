"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Network, Sparkles, Clock, Settings2 } from 'lucide-react';

const ALL_ASSETS = ["BTC", "ETH", "SOL", "TRUMP", "BIDEN", "FED", "CPI"];

// Mock Correlation Matrix (-1 to 1) converted to map
const CORRELATION_DATA: Record<string, Record<string, number>> = {
    "BTC": { "BTC": 1.00, "ETH": 0.85, "SOL": 0.72, "TRUMP": 0.45, "BIDEN": -0.42, "FED": -0.65, "CPI": -0.30 },
    "ETH": { "BTC": 0.85, "ETH": 1.00, "SOL": 0.78, "TRUMP": 0.40, "BIDEN": -0.38, "FED": -0.60, "CPI": -0.25 },
    "SOL": { "BTC": 0.72, "ETH": 0.78, "SOL": 1.00, "TRUMP": 0.35, "BIDEN": -0.30, "FED": -0.55, "CPI": -0.20 },
    "TRUMP": { "BTC": 0.45, "ETH": 0.40, "SOL": 0.35, "TRUMP": 1.00, "BIDEN": -0.92, "FED": 0.15, "CPI": 0.10 },
    "BIDEN": { "BTC": -0.42, "ETH": -0.38, "SOL": -0.30, "TRUMP": -0.92, "BIDEN": 1.00, "FED": -0.10, "CPI": -0.05 },
    "FED": { "BTC": -0.65, "ETH": -0.60, "SOL": -0.55, "TRUMP": 0.15, "BIDEN": -0.10, "FED": 1.00, "CPI": 0.45 },
    "CPI": { "BTC": -0.30, "ETH": -0.25, "SOL": -0.20, "TRUMP": 0.10, "BIDEN": -0.05, "FED": 0.45, "CPI": 1.00 },
};

const AI_RECOMMENDED_ASSETS = ["BTC", "TRUMP", "BIDEN", "FED"];

export function CorrelationsView() {
    const [selectedAssets, setSelectedAssets] = useState<string[]>(AI_RECOMMENDED_ASSETS);

    const toggleAsset = (asset: string) => {
        if (selectedAssets.includes(asset)) {
            // Ensure at least 2 assets are selected
            if (selectedAssets.length > 2) {
                setSelectedAssets(selectedAssets.filter(a => a !== asset));
            }
        } else {
            // Maintain original order
            setSelectedAssets(ALL_ASSETS.filter(a => a === asset || selectedAssets.includes(a)));
        }
    };

    const setAIDefaults = () => {
        setSelectedAssets(AI_RECOMMENDED_ASSETS);
    };

    const getColor = (val: number) => {
        if (val === 1) return "bg-white/10 text-white";
        // Green for positive, Red for negative
        if (val > 0) {
            const intensity = Math.round(val * 100);
            return `bg-emerald-500/${intensity > 20 ? intensity : 20} text-white`;
        } else {
            const intensity = Math.round(Math.abs(val) * 100);
            return `bg-red-500/${intensity > 20 ? intensity : 20} text-white`;
        }
    };

    // Calculate dynamic insights based on current selection
    let maxCorr = { pair: "", val: -2 };
    let minCorr = { pair: "", val: 2 };

    for (let i = 0; i < selectedAssets.length; i++) {
        for (let j = i + 1; j < selectedAssets.length; j++) {
            const a = selectedAssets[i];
            const b = selectedAssets[j];
            const val = CORRELATION_DATA[a][b];

            if (val > maxCorr.val) maxCorr = { pair: `${a} / ${b}`, val };
            if (val < minCorr.val) minCorr = { pair: `${a} / ${b}`, val };
        }
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b border-white/10 pb-4">
                <div className="space-y-1">
                    <h2 className="text-xl font-black tracking-tighter text-white flex items-center gap-2">
                        <Network className="w-5 h-5 text-cyber-blue animate-pulse" /> MARKET_CORRELATIONS
                    </h2>
                    <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">Cross-Asset Dependency Matrix</p>
                </div>

                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1.5 text-[10px] font-mono text-cyber-blue bg-cyber-blue/10 px-2 py-1 rounded border border-cyber-blue/20">
                        <Sparkles className="w-3 h-3" />
                        AI TARGETED
                    </div>
                    <div className="flex items-center gap-1.5 text-[10px] font-mono text-muted-foreground">
                        <Clock className="w-3 h-3" />
                        UPDATED HOURLY
                    </div>
                </div>
            </div>

            <Card className="glass-panel border-white/10 bg-black/40 overflow-hidden">
                <div className="p-4 flex flex-col gap-4">
                    <div className="flex flex-wrap items-center gap-2">
                        <div className="text-xs font-mono text-muted-foreground mr-2 flex items-center gap-1.5">
                            <Settings2 className="w-4 h-4" /> ASSETS:
                        </div>
                        {ALL_ASSETS.map(asset => {
                            const isSelected = selectedAssets.includes(asset);
                            const isAIRecommended = AI_RECOMMENDED_ASSETS.includes(asset);

                            return (
                                <button
                                    key={asset}
                                    onClick={() => toggleAsset(asset)}
                                    className={`px-3 py-1.5 rounded text-[10px] sm:text-xs font-mono font-bold transition-all ${isSelected
                                            ? "bg-white/10 text-white border border-white/20"
                                            : "bg-transparent text-muted-foreground border border-white/5 hover:border-white/20 hover:text-white/80"
                                        }`}
                                >
                                    {asset}
                                    {isAIRecommended && !isSelected && <span className="ml-1.5 text-cyber-blue opacity-50">*</span>}
                                </button>
                            );
                        })}

                        {JSON.stringify(selectedAssets) !== JSON.stringify(AI_RECOMMENDED_ASSETS) && (
                            <button
                                onClick={setAIDefaults}
                                className="ml-auto px-3 py-1.5 rounded text-[10px] font-mono text-cyber-blue hover:bg-cyber-blue/10 transition-colors flex items-center gap-1"
                            >
                                <Sparkles className="w-3 h-3" />
                                RESET TO AI DEFAULTS
                            </button>
                        )}
                    </div>

                    <div className="overflow-x-auto mt-2 pb-2">
                        <div className="min-w-fit">
                            {/* Header Row */}
                            <div className="flex mb-2">
                                <div className="w-24 shrink-0"></div>
                                {selectedAssets.map(asset => (
                                    <div key={asset} className="w-24 text-center text-xs font-black font-mono text-muted-foreground uppercase">{asset}</div>
                                ))}
                            </div>

                            {/* Rows */}
                            {selectedAssets.map((rowAsset) => (
                                <div key={rowAsset} className="flex mb-2 items-center">
                                    {/* Row Label */}
                                    <div className="w-24 shrink-0 text-xs font-black font-mono text-white uppercase text-right pr-4">{rowAsset}</div>

                                    {/* Cells */}
                                    {selectedAssets.map((colAsset) => {
                                        const val = CORRELATION_DATA[rowAsset][colAsset];
                                        return (
                                            <div key={colAsset} className="w-24 h-12 p-1">
                                                <div className={`w-full h-full rounded flex items-center justify-center text-xs font-mono font-bold transition-all hover:scale-105 cursor-default ${getColor(val)}`}>
                                                    {val > 0 && val !== 1 ? '+' : ''}{val.toFixed(2)}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="glass-panel border-white/10 p-4 flex flex-col justify-center items-center text-center">
                    <h4 className="text-xs font-black text-white uppercase mb-2">Highest Selected Correlation</h4>
                    <div className="text-2xl font-black text-primary">
                        {maxCorr.pair ? `${maxCorr.pair} (+${maxCorr.val.toFixed(2)})` : "N/A"}
                    </div>
                    <p className="text-[10px] text-muted-foreground mt-2">Strong signal alignment detected.</p>
                </Card>
                <Card className="glass-panel border-white/10 p-4 flex flex-col justify-center items-center text-center">
                    <h4 className="text-xs font-black text-white uppercase mb-2">Inverse Selected Correlation</h4>
                    <div className="text-2xl font-black text-destructive">
                        {minCorr.pair ? `${minCorr.pair} ${minCorr.val.toFixed(2)}` : "N/A"}
                    </div>
                    <p className="text-[10px] text-muted-foreground mt-2">Prediction markets mirroring.</p>
                </Card>
                <Card className="glass-panel border-white/10 p-4 flex flex-col justify-center items-center text-center">
                    <h4 className="text-xs font-black text-white uppercase mb-2">Dynamic Selection Mode</h4>
                    <div className="text-xl font-black text-indigo mt-1">
                        {JSON.stringify(selectedAssets) === JSON.stringify(AI_RECOMMENDED_ASSETS) ? "AI DEFAULTS" : "USER CUSTOM"}
                    </div>
                    <p className="text-[10px] text-muted-foreground mt-2">
                        {JSON.stringify(selectedAssets) === JSON.stringify(AI_RECOMMENDED_ASSETS)
                            ? "Currently viewing AI optimized signal matrix."
                            : "Custom view active. Click reset for AI optimized view."}
                    </p>
                </Card>
            </div>
        </div>
    );
}
