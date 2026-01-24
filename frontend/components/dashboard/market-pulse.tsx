"use client"

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { TrendingUp, TrendingDown, Zap } from "lucide-react";

interface MarketSource {
    title: string;
    url: string;
    snippet: string;
}

export function MarketPulse() {
    const [data, setData] = useState<MarketSource[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const res = await api.get("/market-context");
            setData(res.data);
            setLoading(false);
        } catch (error) {
            console.error("Failed to fetch market pulse:", error);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000); // 30s refresh
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="w-full h-8 bg-white/5 animate-pulse flex items-center px-4">
                <div className="h-4 w-24 bg-white/10 rounded mr-8" />
                <div className="h-4 w-32 bg-white/10 rounded mr-8" />
                <div className="h-4 w-28 bg-white/10 rounded" />
            </div>
        );
    }

    return (
        <div className="w-full border-b border-white/5 bg-black/40 backdrop-blur-md overflow-hidden relative group">
            <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-black to-transparent z-10" />
            <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-black to-transparent z-10" />

            <div className="flex animate-ticker whitespace-nowrap py-2 items-center hover:pause">
                {/* Double the data for seamless loop */}
                {[...data, ...data].map((item, idx) => {
                    const isBullish = item.snippet.includes("+");
                    const priceMatch = item.snippet.match(/\$?\d{1,3}(,\d{3})*(\.\d+)?/);
                    const changeMatch = item.snippet.match(/([-+]\d+\.\d+%)?/);

                    return (
                        <div key={idx} className="flex items-center gap-3 px-8 border-r border-white/5 last:border-0 h-full">
                            <span className="text-[10px] font-black tracking-widest text-muted-foreground uppercase">{item.title.split(' ')[0]}</span>
                            <span className="text-xs font-mono font-bold text-white leading-none">
                                {priceMatch ? priceMatch[0] : ""}
                            </span>
                            <span className={`text-[10px] font-mono font-bold px-1 rounded flex items-center gap-0.5 ${isBullish ? 'text-emerald-400 bg-emerald-400/10' : 'text-rose-400 bg-rose-400/10'}`}>
                                {isBullish ? <TrendingUp className="w-2.5 h-2.5" /> : <TrendingDown className="w-2.5 h-2.5" />}
                                {changeMatch ? changeMatch[0] : ""}
                            </span>
                        </div>
                    );
                })}
            </div>

            {/* Visual Flare */}
            <div className="absolute left-4 top-1/2 -translate-y-1/2 z-20 flex items-center gap-2 pointer-events-none">
                <Zap className="w-3 h-3 text-primary fill-primary animate-pulse" />
                <span className="text-[9px] font-bold tracking-[0.2em] text-primary/80">PULSE_FEED</span>
            </div>
        </div>
    );
}
