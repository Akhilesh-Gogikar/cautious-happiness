"use client";

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MessageSquare, TrendingUp, Clock, ArrowRight } from 'lucide-react';
import { cn } from "@/lib/utils";
import { api } from '@/lib/api';

export interface TradeSignal {
    market_id: string;
    market_question: string;
    signal_side: string;
    price_estimate: number;
    expected_value: number;
    status: string;
    timestamp: number;
}

interface ThreadListProps {
    onSelectThread: (signal: TradeSignal) => void;
    activeSignalId?: string;
}

export function ThreadList({ onSelectThread, activeSignalId }: ThreadListProps) {
    const [signals, setSignals] = useState<TradeSignal[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const loadSignals = async () => {
            try {
                const res = await api.get('/signals');
                if (res.data) {
                    setSignals(res.data);
                }
            } catch (error) {
                console.error("Failed to load signals:", error);
            } finally {
                setIsLoading(false);
            }
        };
        loadSignals();
    }, []);

    if (isLoading) {
        return <div className="p-4 text-xs font-mono text-muted-foreground animate-pulse">LOADING_THREADS...</div>;
    }

    return (
        <div className="space-y-3 h-full overflow-y-auto custom-scrollbar p-1">
            {signals.length === 0 ? (
                <div className="text-center p-8 border border-dashed border-white/10 rounded-lg">
                    <MessageSquare className="w-8 h-8 text-muted-foreground/50 mx-auto mb-2" />
                    <p className="text-xs text-muted-foreground">NO_ACTIVE_THREADS</p>
                </div>
            ) : (
                signals.map((signal) => (
                    <div
                        key={signal.market_id}
                        onClick={() => onSelectThread(signal)}
                        className={cn(
                            "cursor-pointer group relative overflow-hidden rounded-lg border p-4 transition-all duration-300",
                            activeSignalId === signal.market_id
                                ? "bg-primary/5 border-primary/50 shadow-[0_0_20px_rgba(16,185,129,0.1)]"
                                : "bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20"
                        )}
                    >
                        <div className="flex justify-between items-start mb-2">
                            <Badge variant="outline" className={cn(
                                "text-[10px] tracking-wider font-mono",
                                signal.signal_side === 'BUY_YES' ? "text-emerald-400 border-emerald-400/30" : "text-rose-400 border-rose-400/30"
                            )}>
                                {signal.signal_side}
                            </Badge>
                            <span className="text-[10px] text-muted-foreground font-mono flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {new Date(signal.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>

                        <h4 className="text-sm font-medium leading-relaxed mb-3 text-gray-200 line-clamp-2 group-hover:text-white transition-colors">
                            {signal.market_question}
                        </h4>

                        <div className="flex items-center justify-between text-xs font-mono text-muted-foreground">
                            <div className="flex gap-3">
                                <span className="flex items-center gap-1 text-emerald-400">
                                    <TrendingUp className="w-3 h-3" />
                                    EV: +{signal.expected_value}
                                </span>
                                <span>Est: {signal.price_estimate}¢</span>
                            </div>
                            <ArrowRight className={cn(
                                "w-4 h-4 transition-transform duration-300",
                                activeSignalId === signal.market_id ? "translate-x-0 text-primary" : "-translate-x-2 opacity-0 group-hover:translate-x-0 group-hover:opacity-100"
                            )} />
                        </div>

                        {activeSignalId === signal.market_id && (
                            <div className="absolute inset-0 bg-gradient-to-r from-primary/0 via-primary/5 to-primary/0 animate-shimmer pointer-events-none" />
                        )}
                    </div>
                ))
            )}
        </div>
    );
}
