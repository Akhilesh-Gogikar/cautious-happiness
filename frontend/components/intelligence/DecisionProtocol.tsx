"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Zap, ShieldAlert, TrendingUp, TrendingDown, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { AnalysisResult } from "./types";

interface DecisionProtocolProps {
    analysis: AnalysisResult;
    symbol?: string;
}

export function DecisionProtocol({ analysis, symbol = "BRENT" }: DecisionProtocolProps) {
    const [quantity, setQuantity] = useState<number>(1.0);
    const [isExecuting, setIsExecuting] = useState(false);

    const recommendation = analysis.sentiment_score > 0.2 ? 'BUY' :
        analysis.sentiment_score < -0.2 ? 'SELL' : 'HOLD';

    const convictionLevel = analysis.crowd_conviction > 0.7 ? 'HIGH' :
        analysis.crowd_conviction > 0.4 ? 'MEDIUM' : 'LOW';

    const handleExecute = async (side: 'buy' | 'sell') => {
        setIsExecuting(true);
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${API_URL}/trade/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Assuming auth is handled via cookies or common middleware
                },
                body: JSON.stringify({
                    symbol,
                    side,
                    quantity,
                    target_id: analysis.target_id,
                    provider: 'polymarket'
                })
            });

            if (!response.ok) throw new Error("Execution Failed");

            const result = await response.json();
            toast.success("Mirror Trade Initialized", {
                description: `Routing ${side.toUpperCase()} order for ${quantity} ${symbol} via ${result.provider}.`
            });
        } catch (error) {
            console.error(error);
            toast.error("Execution Interrupted", {
                description: "Check neural core synchronization."
            });
        } finally {
            setIsExecuting(false);
        }
    };

    return (
        <Card className="border-primary/20 bg-black/60 backdrop-blur-md shadow-[0_0_20px_rgba(16,185,129,0.1)]">
            <CardHeader className="pb-2 border-b border-primary/10">
                <CardTitle className="text-sm font-mono flex items-center gap-2 text-primary">
                    <ShieldAlert className="w-4 h-4" />
                    DECISION_PROTOCOL // v1.0
                </CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
                <div className="flex items-center justify-between">
                    <div className="space-y-1">
                        <p className="text-[10px] font-mono text-muted-foreground uppercase">AI_RECOMMENDATION</p>
                        <div className="flex items-center gap-2">
                            <Badge className={
                                recommendation === 'BUY' ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" :
                                    recommendation === 'SELL' ? "bg-red-500/20 text-red-400 border-red-500/30" :
                                        "bg-blue-500/20 text-blue-400 border-blue-500/30"
                            }>
                                {recommendation}
                            </Badge>
                            <span className="text-[10px] font-mono text-muted-foreground">
                                CONVICTION: {convictionLevel}
                            </span>
                        </div>
                    </div>
                    <div className="text-right">
                        <p className="text-[10px] font-mono text-muted-foreground uppercase">TARGET_ASSET</p>
                        <p className="text-sm font-bold font-mono text-white">{symbol}</p>
                    </div>
                </div>

                <div className="space-y-2">
                    <label className="text-[10px] font-mono text-muted-foreground uppercase">EXECUTION_QUANTITY</label>
                    <div className="flex gap-2">
                        <Input
                            type="number"
                            value={quantity}
                            onChange={(e) => setQuantity(Number(e.target.value))}
                            className="bg-black/40 border-primary/20 font-mono text-sm"
                        />
                        <div className="flex gap-1">
                            {[0.5, 1, 5].map(v => (
                                <Button
                                    key={v}
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setQuantity(v)}
                                    className="h-9 px-2 text-[10px] font-mono border-primary/10 hover:bg-primary/5"
                                >
                                    {v}x
                                </Button>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2">
                    <Button
                        disabled={isExecuting}
                        onClick={() => handleExecute('buy')}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs gap-2 shadow-[0_0_15px_rgba(16,185,129,0.3)]"
                    >
                        {isExecuting ? <Loader2 className="w-3 h-3 animate-spin" /> : <TrendingUp className="w-3 h-3" />}
                        INITIATE_BUY
                    </Button>
                    <Button
                        disabled={isExecuting}
                        onClick={() => handleExecute('sell')}
                        className="bg-red-600 hover:bg-red-500 text-white font-mono text-xs gap-2 shadow-[0_0_15px_rgba(239,68,68,0.3)]"
                    >
                        {isExecuting ? <Loader2 className="w-3 h-3 animate-spin" /> : <TrendingDown className="w-3 h-3" />}
                        INITIATE_SELL
                    </Button>
                </div>

                <div className="pt-2 border-t border-white/5">
                    <p className="text-[9px] font-mono text-muted-foreground leading-tight italic">
                        Caution: Decisions are mirrored from crowd-sentiment data. Slippage and liquidity risks not fully mitigated by Mirror Hub.
                    </p>
                </div>
            </CardContent>
        </Card>
    );
}
