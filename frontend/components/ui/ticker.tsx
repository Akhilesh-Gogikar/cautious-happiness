"use client";

import React from 'react';
import { cn } from '@/lib/utils';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

const TickerItem = ({ symbol, price, change }: { symbol: string, price: string, change: number }) => (
    <div className="flex items-center space-x-3 mx-4 min-w-max group cursor-pointer hover:bg-white/5 py-1.5 px-3 rounded-md transition-all duration-300 border border-transparent hover:border-white/5">
        <span className="font-mono text-[10px] font-black text-muted-foreground group-hover:text-primary transition-colors uppercase tracking-widest">{symbol}</span>
        <span className="font-mono text-xs text-white font-bold tracking-tight">{price}</span>
        <div className={cn(
            "flex items-center gap-0.5 font-mono text-[9px] font-black px-1.5 py-0.5 rounded shadow-sm backdrop-blur-sm",
            change >= 0 ? "text-primary bg-primary/10 border border-primary/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]" : "text-destructive bg-destructive/10 border border-destructive/20"
        )}>
            {change >= 0 ? <ArrowUpRight className="w-2.5 h-2.5" /> : <ArrowDownRight className="w-2.5 h-2.5" />}
            {Math.abs(change)}%
        </div>
    </div>
);

export function Ticker() {
    // Hardcoded for now, could fetch from API in future
    const items = [
        { symbol: "BTC/USD", price: "$42,105.20", change: 2.5 },
        { symbol: "ETH/USD", price: "$2,251.10", change: 1.8 },
        { symbol: "SOL/USD", price: "$105.15", change: -0.5 },
        { symbol: "POLY/ALPHA", price: "$0.8521", change: 3.2 },
        { symbol: "S&P 500", price: "4,783.45", change: 0.12 },
        { symbol: "DXY", price: "102.45", change: -0.21 },
        { symbol: "TRUMP/YES", price: "52¢", change: 1.1 },
    ];

    return (
        <div className="flex items-center overflow-hidden h-9 relative select-none">
            <div className="animate-ticker flex whitespace-nowrap will-change-transform hover:[animation-play-state:paused]">
                {items.map((item, i) => (
                    <TickerItem key={i} {...item} />
                ))}
                {items.map((item, i) => (
                    <TickerItem key={`dup-${i}`} {...item} />
                ))}
                {items.map((item, i) => (
                    <TickerItem key={`trip-${i}`} {...item} />
                ))}
            </div>
            {/* Glossy overlay */}
            <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-white/5 to-transparent h-[1px]" />
        </div>
    );
}
