'use client';

import React from 'react';
import { Check, X, Clock, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PendingTrade {
    id: string;
    market: string;
    action: 'BUY' | 'SELL';
    amount: number;
    reason: string;
    confidence: number;
}

export function ApprovalQueue() {
    // Mock pending trades
    const pendingTrades: PendingTrade[] = [
        {
            id: '1',
            market: 'Taiwan Election: YES',
            action: 'BUY',
            amount: 5000,
            reason: 'Detected high social sentiment + betting volume spike.',
            confidence: 85
        },
        {
            id: '2',
            market: 'Bitcoin > 45k: NO',
            action: 'SELL',
            amount: 2500,
            reason: 'Technical resistance level + macro headwinds.',
            confidence: 72
        }
    ];

    return (
        <div className="rounded-xl border border-yellow-500/30 bg-yellow-500/5 backdrop-blur-sm p-4 relative overflow-hidden animate-fade-in">
            {/* Header */}
            <div className="flex items-center gap-2 text-yellow-500 mb-3 border-b border-yellow-500/20 pb-2">
                <Clock className="w-4 h-4 animate-pulse" />
                <span className="font-bold text-sm tracking-widest uppercase">Pending Approval ({pendingTrades.length})</span>
            </div>

            {/* Trades List */}
            <div className="space-y-3">
                {pendingTrades.map((trade) => (
                    <div key={trade.id} className="p-3 rounded bg-yellow-500/10 border border-yellow-500/20 group hover:bg-yellow-500/20 transition-colors">
                        <div className="flex justify-between items-start mb-2">
                            <div>
                                <span className={cn(
                                    "text-[10px] font-bold px-1.5 py-0.5 rounded ",
                                    trade.action === 'BUY' ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
                                )}>
                                    {trade.action}
                                </span>
                                <span className="ml-2 text-xs text-white font-bold">{trade.market}</span>
                            </div>
                            <span className="text-xs text-white/50">${trade.amount.toLocaleString()}</span>
                        </div>

                        <p className="text-[10px] text-white/60 mb-3 italic">
                            &quot;{trade.reason}&quot; <span className="not-italic text-blue-400 font-bold ml-1">(Conf: {trade.confidence}%)</span>
                        </p>

                        <div className="flex gap-2">
                            <button className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded bg-white/5 hover:bg-emerald-500/20 text-white/50 hover:text-emerald-400 border border-white/5 hover:border-emerald-500/30 transition-all text-xs">
                                <Check className="w-3 h-3" /> Approve
                            </button>
                            <button className="flex-1 flex items-center justify-center gap-1 py-1.5 rounded bg-white/5 hover:bg-red-500/20 text-white/50 hover:text-red-400 border border-white/5 hover:border-red-500/30 transition-all text-xs">
                                <X className="w-3 h-3" /> Reject
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
