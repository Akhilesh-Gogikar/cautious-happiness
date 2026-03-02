"use client";

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { ArrowUpRight, ArrowDownRight, Settings2 } from 'lucide-react';
import { ChartModal } from '@/components/ui/chart-modal';

interface TickerData {
    symbol: string;
    price: string;
    change: number;
}

const TickerItem = ({ item, onClick }: { item: TickerData, onClick: (item: TickerData) => void }) => (
    <div onClick={() => onClick(item)} className="flex items-center space-x-3 mx-4 min-w-max group cursor-pointer hover:bg-white/5 py-1.5 px-3 rounded-md transition-all duration-300 border border-transparent hover:border-white/10 relative z-10">
        <span className="font-mono text-[10px] font-black text-muted-foreground group-hover:text-primary transition-colors uppercase tracking-widest">{item.symbol}</span>
        <span className="font-mono text-xs text-white font-bold tracking-tight">{item.price}</span>
        <div className={cn(
            "flex items-center gap-0.5 font-mono text-[9px] font-black px-1.5 py-0.5 rounded shadow-sm backdrop-blur-sm transition-colors",
            item.change >= 0 ? "text-primary bg-primary/10 border border-primary/20 shadow-[0_0_10px_rgba(16,185,129,0.1)] group-hover:bg-primary/20" : "text-destructive bg-destructive/10 border border-destructive/20 group-hover:bg-destructive/20"
        )}>
            {item.change >= 0 ? <ArrowUpRight className="w-2.5 h-2.5" /> : <ArrowDownRight className="w-2.5 h-2.5" />}
            {Math.abs(item.change)}%
        </div>
    </div>
);

const CATEGORIES = {
    'Overview': [
        { symbol: "BTC/USD", price: "$42,105.20", change: 2.5 },
        { symbol: "ETH/USD", price: "$2,251.10", change: 1.8 },
        { symbol: "S&P 500", price: "4,783.45", change: 0.12 },
        { symbol: "DXY", price: "102.45", change: -0.21 },
        { symbol: "USDT/USD", price: "$1.00", change: 0.01 },
    ],
    'Crypto': [
        { symbol: "BTC/USD", price: "$42,105.20", change: 2.5 },
        { symbol: "ETH/USD", price: "$2,251.10", change: 1.8 },
        { symbol: "SOL/USD", price: "$105.15", change: -0.5 },
        { symbol: "POLY/ALPHA", price: "$0.8521", change: 3.2 },
        { symbol: "LINK/USD", price: "$15.42", change: 5.1 },
    ],
    'Energy': [
        { symbol: "BRENT", price: "$82.45", change: 1.2 },
        { symbol: "WTI", price: "$78.15", change: 1.5 },
        { symbol: "NATGAS", price: "$2.15", change: -3.4 },
        { symbol: "USD/NOK", price: "10.45", change: -0.2 },
        { symbol: "USD/CAD", price: "1.35", change: 0.1 },
    ],
    'PolitiFi': [
        { symbol: "TRUMP/YES", price: "52¢", change: 1.1 },
        { symbol: "BIDEN/YES", price: "45¢", change: -2.3 },
        { symbol: "RFK/YES", price: "3¢", change: 0.0 },
    ]
};

export function Ticker() {
    const [activeCategory, setActiveCategory] = useState<keyof typeof CATEGORIES>('Overview');
    const [selectedTicker, setSelectedTicker] = useState<TickerData | null>(null);
    const [showCategories, setShowCategories] = useState(false);

    const items = CATEGORIES[activeCategory];

    return (
        <div className="flex items-center overflow-visible h-9 relative select-none bg-black/40 border-b border-white/5">
            {/* Category Selector Menu Trigger */}
            <div className="relative h-full flex items-center z-40 border-r border-white/10 bg-black/80 px-4 group cursor-pointer" onClick={() => setShowCategories(!showCategories)}>
                <div className="flex items-center gap-2">
                    <Settings2 className="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary transition-colors" />
                    <span className="text-[10px] font-mono font-bold text-muted-foreground group-hover:text-white transition-colors uppercase">{activeCategory}</span>
                </div>

                {/* Category Dropdown */}
                {showCategories && (
                    <div className="absolute top-full left-0 mt-1 w-40 bg-black/95 border border-white/10 rounded-md shadow-2xl backdrop-blur-xl overflow-hidden py-1">
                        {Object.keys(CATEGORIES).map((cat) => (
                            <div
                                key={cat}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setActiveCategory(cat as keyof typeof CATEGORIES);
                                    setShowCategories(false);
                                }}
                                className={cn(
                                    "px-4 py-2 text-[10px] font-mono cursor-pointer transition-colors hover:bg-white/10 uppercase tracking-wider",
                                    activeCategory === cat ? "text-primary font-bold bg-primary/5" : "text-muted-foreground"
                                )}
                            >
                                {cat}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Ticker Tape */}
            <div className="flex-1 overflow-hidden relative h-full">
                <div className="animate-ticker flex h-full items-center whitespace-nowrap will-change-transform hover:[animation-play-state:paused]">
                    {items.map((item, i) => (
                        <TickerItem key={i} item={item} onClick={setSelectedTicker} />
                    ))}
                    {items.map((item, i) => (
                        <TickerItem key={`dup-${i}`} item={item} onClick={setSelectedTicker} />
                    ))}
                    {items.map((item, i) => (
                        <TickerItem key={`trip-${i}`} item={item} onClick={setSelectedTicker} />
                    ))}
                    {items.map((item, i) => (
                        <TickerItem key={`quad-${i}`} item={item} onClick={setSelectedTicker} />
                    ))}
                </div>

                {/* Glossy overlay */}
                <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-white/5 to-transparent h-[1px]" />
                <div className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-black to-transparent pointer-events-none z-10" />
                <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-black to-transparent pointer-events-none z-10" />
            </div>

            {/* Chart Modal */}
            <ChartModal isOpen={!!selectedTicker} onClose={() => setSelectedTicker(null)} ticker={selectedTicker} />
        </div>
    );
}
