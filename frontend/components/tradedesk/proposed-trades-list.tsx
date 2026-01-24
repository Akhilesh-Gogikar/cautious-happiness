"use client"

import { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ExternalLink, Check, X, Loader2, Sparkles, Clock, Newspaper } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export interface ProposedTrade {
    id: number;
    title: str;
    description: str;
    link: str;
    pub_date: string;
    ai_analysis: string;
    status: string;
    created_at: string;
}

export function ProposedTradesList() {
    const [trades, setTrades] = useState<ProposedTrade[]>([]);
    const [loading, setLoading] = useState(true);
    const [actioningId, setActioningId] = useState<number | null>(null);

    const fetchTrades = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/proposed-trades/`);
            const data = await res.json();
            setTrades(data);
        } catch (error) {
            console.error('Failed to fetch proposed trades:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTrades();
        const interval = setInterval(fetchTrades, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    const handleAction = async (id: number, action: 'accept' | 'dismiss') => {
        try {
            setActioningId(id);
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/proposed-trades/${id}/${action}`, {
                method: 'POST'
            });
            if (res.ok) {
                setTrades(trades.filter(t => t.id !== id));
            }
        } catch (error) {
            console.error(`Failed to ${action} trade:`, error);
        } finally {
            setActioningId(null);
        }
    };

    if (loading && trades.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-64 gap-4 text-muted-foreground">
                <Loader2 className="w-8 h-8 animate-spin" />
                <p className="text-xs font-mono">SCANNING NEWS FEEDS...</p>
            </div>
        );
    }

    if (trades.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-64 gap-2 text-muted-foreground p-8 text-center">
                <Newspaper className="w-12 h-12 opacity-20 mb-4" />
                <p className="text-sm font-bold text-white">No New Proposals</p>
                <p className="text-xs">AI is monitoring RSS feeds for high-impact trading catalysts.</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full">
            <ScrollArea className="flex-1">
                <div className="p-4 space-y-4">
                    {trades.map((trade) => (
                        <div
                            key={trade.id}
                            className="group relative bg-white/5 border border-white/10 rounded-lg p-4 transition-all hover:bg-white/[0.07] hover:border-primary/30"
                        >
                            <div className="flex justify-between items-start mb-2">
                                <Badge variant="outline" className="text-[9px] bg-primary/10 text-primary border-primary/20 flex gap-1 items-center">
                                    <Sparkles className="w-2.4 h-2.4" />
                                    AI_PROPOSAL
                                </Badge>
                                <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                                    <Clock className="w-2.5 h-2.5" />
                                    {formatDistanceToNow(new Date(trade.pub_date))} ago
                                </span>
                            </div>

                            <h3 className="text-sm font-bold text-white mb-2 line-clamp-2 leading-tight">
                                {trade.title}
                            </h3>

                            <p className="text-xs text-muted-foreground mb-4 line-clamp-3 leading-relaxed italic">
                                "{trade.description}"
                            </p>

                            <div className="bg-black/40 border border-white/5 rounded p-3 mb-4">
                                <div className="flex items-center gap-2 mb-1.5">
                                    <div className="w-1 h-1 bg-primary rounded-full" />
                                    <span className="text-[10px] font-black tracking-widest text-primary uppercase">Rationale</span>
                                </div>
                                <p className="text-[11px] text-white/80 leading-snug">
                                    {trade.ai_analysis}
                                </p>
                            </div>

                            <div className="flex gap-2">
                                <Button
                                    size="sm"
                                    className="flex-1 h-8 text-[11px] bg-emerald-500/20 text-emerald-500 hover:bg-emerald-500/30 border border-emerald-500/30"
                                    onClick={() => handleAction(trade.id, 'accept')}
                                    disabled={actioningId === trade.id}
                                >
                                    <Check className="w-3 h-3 mr-1.5" />
                                    Accept
                                </Button>
                                <Button
                                    size="sm"
                                    variant="ghost"
                                    className="flex-1 h-8 text-[11px] text-muted-foreground hover:text-white hover:bg-white/5 border border-white/5"
                                    onClick={() => handleAction(trade.id, 'dismiss')}
                                    disabled={actioningId === trade.id}
                                >
                                    <X className="w-3 h-3 mr-1.5" />
                                    Dismiss
                                </Button>
                                <Button
                                    size="sm"
                                    variant="outline"
                                    className="w-8 h-8 p-0 border-white/5"
                                    asChild
                                >
                                    <a href={trade.link} target="_blank" rel="noopener noreferrer">
                                        <ExternalLink className="w-3 h-3" />
                                    </a>
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            </ScrollArea>
        </div>
    );
}
