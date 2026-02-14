import React from 'react';
import { TrendingUp, TrendingDown, Divide, AlertTriangle } from 'lucide-react';

interface NarrativeDivergenceProps {
    market: string;
    sentimentScore: number; // 0-100
    physicalScore: number; // 0-100
    divergenceReason: string;
}

export function NarrativeDivergence({ market, sentimentScore, physicalScore, divergenceReason }: NarrativeDivergenceProps) {
    const divergence = Math.abs(sentimentScore - physicalScore);
    const isOverhyped = sentimentScore > physicalScore;

    return (
        <div className="glass-panel p-6 bg-black/40 border border-white/10 rounded-xl space-y-4">
            <div className="flex justify-between items-start">
                <div>
                    <h3 className="text-sm font-black font-mono text-muted-foreground uppercase tracking-widest">Narrative_Divergence</h3>
                    <div className="text-xl font-bold text-white mt-1">{market}</div>
                </div>
                {divergence > 20 && (
                    <div className="px-2 py-1 bg-amber-500/10 border border-amber-500/20 text-amber-500 text-xs font-mono font-bold rounded flex items-center gap-1 animate-pulse">
                        <AlertTriangle className="w-3 h-3" />
                        HIGH_DIVERGENCE
                    </div>
                )}
            </div>

            <div className="grid grid-cols-2 gap-4">
                {/* Sentiment Meter */}
                <div className="space-y-2">
                    <div className="flex justify-between text-xs font-mono">
                        <span className="text-muted-foreground">MEDIA_SENTIMENT</span>
                        <span className={sentimentScore > 50 ? "text-emerald-400" : "text-red-400"}>{sentimentScore}%</span>
                    </div>
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                        <div
                            className={`h-full ${sentimentScore > 50 ? "bg-emerald-500" : "bg-red-500"}`}
                            style={{ width: `${sentimentScore}%` }}
                        />
                    </div>
                </div>

                {/* Physical Meter */}
                <div className="space-y-2">
                    <div className="flex justify-between text-xs font-mono">
                        <span className="text-muted-foreground">PHYSICAL_REALITY</span>
                        <span className={physicalScore > 50 ? "text-emerald-400" : "text-red-400"}>{physicalScore}%</span>
                    </div>
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                        <div
                            className={`h-full ${physicalScore > 50 ? "bg-blue-500" : "bg-orange-500"}`}
                            style={{ width: `${physicalScore}%` }}
                        />
                    </div>
                </div>
            </div>

            {/* Analysis Box */}
            <div className="p-3 bg-white/5 rounded border border-white/5">
                <div className="flex items-center gap-2 mb-2">
                    <Divide className="w-4 h-4 text-primary" />
                    <span className="text-xs font-bold text-primary font-mono">INTELLIGENCE_LAYER_OUTPUT</span>
                </div>
                <p className="text-sm text-gray-300 leading-snug">
                    {divergenceReason}
                </p>
                <div className="mt-3 pt-3 border-t border-white/5 flex gap-4 text-xs font-mono text-muted-foreground">
                    <div className="flex items-center gap-1">
                        <span>GAP:</span>
                        <span className="text-white">{divergence.toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <span>VERDICT:</span>
                        <span className={isOverhyped ? "text-red-400" : "text-emerald-400"}>
                            {isOverhyped ? "OVERHYPED (SHORT)" : "UNDERVALUED (LONG)"}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
