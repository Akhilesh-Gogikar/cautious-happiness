"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, TrendingUp, TrendingDown, Eye, Zap, ArrowRight, Server, FileText, Crosshair, Cpu } from 'lucide-react';
import { cn } from "@/lib/utils";
import { toast } from "sonner";

// --- Types ---
type SortField = 'symbol' | 'price' | 'change' | 'volume' | 'category' | 'signal';
type SortOrder = 'asc' | 'desc';

interface MarketDataPoint {
    id: string;
    symbol: string;
    name: string;
    price: number;
    change: number;
    volume: number;
    category: 'EXTREME_NOISE' | 'PHYSICAL_DRIVEN' | 'MACRO_HEDGE' | 'FLOW_TOXIC' | 'NEUTRAL';
    signal: 'BUY' | 'SELL' | 'HOLD' | 'AVOID';
    oiHistory: number[];
}

export function DataMatrix() {
    const [data, setData] = useState<MarketDataPoint[]>([]);
    const [sortField, setSortField] = useState<SortField>('volume');
    const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
    
    // Context Menu State
    const [contextMenu, setContextMenu] = useState<{ x: number, y: number, item: MarketDataPoint | null } | null>(null);

    // Initial Data Generation
    useEffect(() => {
        const initialData: MarketDataPoint[] = [
            { id: '1', symbol: 'BRENT', name: 'Brent Crude Oil', price: 82.45, change: 1.2, volume: 154000, category: 'PHYSICAL_DRIVEN', signal: 'BUY', oiHistory: Array.from({ length: 20 }, () => 50 + Math.random() * 50) },
            { id: '2', symbol: 'WTI', name: 'WTI Crude Oil', price: 78.12, change: -0.5, volume: 142000, category: 'MACRO_HEDGE', signal: 'HOLD', oiHistory: Array.from({ length: 20 }, () => 40 + Math.random() * 60) },
            { id: '3', symbol: 'NGAS', name: 'Natural Gas', price: 2.85, change: -4.2, volume: 215000, category: 'EXTREME_NOISE', signal: 'AVOID', oiHistory: Array.from({ length: 20 }, () => 20 + Math.random() * 80) },
            { id: '4', symbol: 'GOLD', name: 'Gold (XAU)', price: 2045.60, change: 0.8, volume: 98000, category: 'MACRO_HEDGE', signal: 'BUY', oiHistory: Array.from({ length: 20 }, () => 70 + Math.random() * 30) },
            { id: '5', symbol: 'COPPER', name: 'Copper (HG)', price: 3.84, change: 2.1, volume: 65000, category: 'PHYSICAL_DRIVEN', signal: 'BUY', oiHistory: Array.from({ length: 20 }, () => 50 + Math.random() * 50) },
            { id: '6', symbol: 'SILVER', name: 'Silver (XAG)', price: 24.15, change: -1.1, volume: 82000, category: 'FLOW_TOXIC', signal: 'SELL', oiHistory: Array.from({ length: 20 }, () => 30 + Math.random() * 70) },
            { id: '7', symbol: 'ALUM', name: 'Aluminum', price: 2150.00, change: 0.4, volume: 45000, category: 'PHYSICAL_DRIVEN', signal: 'HOLD', oiHistory: Array.from({ length: 20 }, () => 50 + Math.random() * 30) },
            { id: '8', symbol: 'URANIUM', name: 'Uranium (U3O8)', price: 92.50, change: 5.4, volume: 12000, category: 'EXTREME_NOISE', signal: 'BUY', oiHistory: Array.from({ length: 20 }, () => 80 + Math.random() * 20) },
        ];
        setData(initialData);

        // Streaming Data Simulation
        const interval = setInterval(() => {
            setData(prev => prev.map(item => {
                const priceVolatility = item.price * 0.001; 
                const newPrice = item.price + (Math.random() * priceVolatility * 2 - priceVolatility);
                
                // Update sparkline history
                const newOiHistory = [...item.oiHistory.slice(1), item.oiHistory[item.oiHistory.length - 1] + (Math.random() * 10 - 5)];
                // clamp
                const clampedHistory = newOiHistory.map(v => Math.max(0, Math.min(100, v)));

                return {
                    ...item,
                    price: Number(newPrice.toFixed(2)),
                    change: Number((item.change + (Math.random() * 0.2 - 0.1)).toFixed(2)),
                    oiHistory: clampedHistory
                };
            }));
        }, 1000); // 1-second ticks

        return () => clearInterval(interval);
    }, []);

    // Close Context Menu on outside click
    useEffect(() => {
        const handleClick = () => setContextMenu(null);
        window.addEventListener('click', handleClick);
        return () => window.removeEventListener('click', handleClick);
    }, []);

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortOrder('desc'); // Default to desc on new field
        }
    };

    const sortedData = [...data].sort((a, b) => {
        let valA = a[sortField];
        let valB = b[sortField];
        
        if (typeof valA === 'string' && typeof valB === 'string') {
            return sortOrder === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
        }
        
        if (typeof valA === 'number' && typeof valB === 'number') {
            return sortOrder === 'asc' ? valA - valB : valB - valA;
        }
        return 0;
    });

    const getCategoryStyles = (category: string) => {
        switch (category) {
            case 'EXTREME_NOISE': return 'bg-red-500/10 text-red-500 border-red-500/30';
            case 'PHYSICAL_DRIVEN': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
            case 'MACRO_HEDGE': return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
            case 'FLOW_TOXIC': return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
            default: return 'bg-white/5 text-white/50 border-white/10';
        }
    };

    const getSignalStyles = (signal: string) => {
        switch (signal) {
            case 'BUY': return 'text-emerald-400 font-bold drop-shadow-[0_0_8px_rgba(52,211,153,0.5)]';
            case 'SELL': return 'text-red-400 font-bold drop-shadow-[0_0_8px_rgba(248,113,113,0.5)]';
            case 'AVOID': return 'text-orange-400 font-bold';
            default: return 'text-muted-foreground';
        }
    };

    // Render Sparkline SVG
    const Sparkline = ({ data }: { data: number[] }) => {
        const min = Math.min(...data);
        const max = Math.max(...data);
        const range = max - min || 1;
        
        const pathData = data.map((val, i) => {
            const x = (i / (data.length - 1)) * 100;
            const y = 100 - ((val - min) / range) * 100;
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
        }).join(' ');

        return (
            <div className="w-full h-8 flex items-center justify-center relative group-hover/row:scale-105 transition-transform duration-300">
                <svg viewBox="0 -10 100 120" className="w-[80%] h-full overflow-visible" preserveAspectRatio="none">
                    <defs>
                        <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="rgba(16, 185, 129, 0.4)" />
                            <stop offset="100%" stopColor="rgba(16, 185, 129, 1)" />
                        </linearGradient>
                        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                            <feGaussianBlur stdDeviation="2" result="blur" />
                            <feComposite in="SourceGraphic" in2="blur" operator="over" />
                        </filter>
                    </defs>
                    <path
                        d={pathData}
                        fill="none"
                        stroke="url(#lineGrad)"
                        strokeWidth="3"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        filter="url(#glow)"
                        className="transition-all duration-300"
                    />
                    {/* Live Dot at the end */}
                    <circle 
                        cx="100" 
                        cy={100 - ((data[data.length - 1] - min) / range) * 100} 
                        r="4" 
                        fill="#10B981" 
                        className="animate-pulse shadow-[0_0_10px_#10B981]"
                    />
                </svg>
            </div>
        );
    };

    return (
        <Card className="glass-panel border-white/10 bg-black/60 shadow-2xl overflow-hidden relative flex-1 flex flex-col group min-h-[600px]">
             {/* Scanline Effect */}
             <div className="absolute inset-0 pointer-events-none opacity-[0.03] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[size:100%_2px,3px_100%] z-20" />
            
            <CardHeader className="py-4 px-5 border-b border-white/10 bg-white/5 z-10 shrink-0 backdrop-blur-md flex flex-row items-center justify-between">
                <CardTitle className="text-[12px] font-black font-mono tracking-widest text-muted-foreground uppercase flex items-center gap-3 text-glow-primary">
                    <Server className="w-5 h-5 text-primary animate-pulse" />
                    Data Matrix (Commodity Intelligence)
                </CardTitle>
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                        </span>
                        <span className="text-[9px] font-mono text-emerald-400 tracking-widest uppercase">Streaming Grid Active</span>
                    </div>
                </div>
            </CardHeader>
            
            <CardContent className="p-0 flex-1 overflow-x-auto overflow-y-auto custom-scrollbar relative z-10">
                <table className="w-full text-left font-mono text-sm whitespace-nowrap">
                    <thead className="sticky top-0 bg-black/80 backdrop-blur-md z-20">
                        <tr className="border-b border-white/5">
                            {[
                                { key: 'symbol', label: 'TARGET_ASSET' },
                                { key: 'price', label: 'SPOT_PRICE' },
                                { key: 'change', label: '24H_DELTA' },
                                { key: 'volume', label: 'VWAP_VOLUME' },
                                { key: 'oiHistory', label: 'OI_LIQUIDITY', sortable: false },
                                { key: 'category', label: 'DOMINANT_NARRATIVE' },
                                { key: 'signal', label: 'SYSTEM_ACTION' },
                            ].map((col) => (
                                <th 
                                    key={col.key}
                                    className={cn(
                                        "py-4 px-6 text-[10px] font-black tracking-widest uppercase text-muted-foreground transition-colors",
                                        col.sortable !== false && "cursor-pointer hover:text-white"
                                    )}
                                    onClick={() => col.sortable !== false && handleSort(col.key as SortField)}
                                >
                                    <div className="flex items-center gap-1">
                                        {col.label}
                                        {sortField === col.key && (
                                            <span className="text-primary text-[8px]">{sortOrder === 'asc' ? '▲' : '▼'}</span>
                                        )}
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {sortedData.map((row) => (
                            <tr 
                                key={row.id} 
                                className="border-b border-white/5 hover:bg-white/[0.04] transition-all duration-200 group/row select-none"
                                onContextMenu={(e) => {
                                    e.preventDefault();
                                    setContextMenu({ x: e.clientX, y: e.clientY, item: row });
                                }}
                            >
                                <td className="py-4 px-6 relative">
                                    <div className="absolute left-0 top-0 bottom-0 w-[2px] bg-primary scale-y-0 group-hover/row:scale-y-100 transition-transform duration-300 origin-center" />
                                    <div className="flex flex-col">
                                        <span className="font-bold text-white group-hover/row:text-primary transition-colors">{row.symbol}</span>
                                        <span className="text-[10px] text-muted-foreground">{row.name}</span>
                                    </div>
                                </td>
                                <td className="py-4 px-6 font-medium text-white/90">
                                    ${row.price.toFixed(2)}
                                </td>
                                <td className="py-4 px-6">
                                    <span className={cn(
                                        "flex items-center gap-1",
                                        row.change > 0 ? "text-emerald-400" : row.change < 0 ? "text-red-400" : "text-white/50"
                                    )}>
                                        {row.change > 0 ? '+' : ''}{row.change}%
                                    </span>
                                </td>
                                <td className="py-4 px-6 text-muted-foreground">
                                    {(row.volume / 1000).toFixed(1)}k
                                </td>
                                <td className="py-4 px-6 min-w-[120px]">
                                    <Sparkline data={row.oiHistory} />
                                </td>
                                <td className="py-4 px-6">
                                    <Badge variant="outline" className={cn("text-[9px] uppercase tracking-wider", getCategoryStyles(row.category))}>
                                        {row.category}
                                    </Badge>
                                </td>
                                <td className="py-4 px-6">
                                    <div className="flex items-center gap-2">
                                        <span className={cn("text-[10px] uppercase tracking-widest", getSignalStyles(row.signal))}>
                                            {row.signal}
                                        </span>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {/* Simulated Empty Space filler */}
                {sortedData.length < 10 && (
                    <div className="flex-1 opacity-10 flex flex-col pointer-events-none">
                        {Array.from({ length: 10 - sortedData.length }).map((_, i) => (
                            <div key={i} className="h-16 border-b border-white/5 w-full bg-[linear-gradient(90deg,transparent_0%,rgba(255,255,255,0.02)_50%,transparent_100%)] bg-[length:200%_100%] animate-shimmer" />
                        ))}
                    </div>
                )}
            </CardContent>

            {/* Context Menu Absolute Portal-like Overlay */}
            {contextMenu && contextMenu.item && (
                <div 
                    className="fixed z-50 p-1 min-w-[200px] bg-black/90 backdrop-blur-xl border border-white/10 rounded-lg shadow-2xl animate-in fade-in zoom-in-95 duration-100"
                    style={{ top: contextMenu.y, left: contextMenu.x }}
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="px-3 py-2 border-b border-white/10 mb-1">
                        <div className="text-[10px] text-muted-foreground uppercase tracking-wider font-sans font-black">Target Selected</div>
                        <div className="font-bold text-white text-sm font-sans">{contextMenu.item.symbol} <span className="text-muted-foreground text-xs ml-1 font-mono">${contextMenu.item.price.toFixed(2)}</span></div>
                    </div>
                    <div className="space-y-1">
                        <button 
                            className="w-full text-left px-3 py-2 text-xs font-mono text-white hover:bg-white/10 rounded flex items-center gap-2 group transition-colors"
                            onClick={() => {
                                toast.success("Trade Execution Initialized", { description: `Routing ${contextMenu.item?.symbol} order to nearest dark pool.` });
                                setContextMenu(null);
                            }}
                        >
                            <Zap className="w-3.5 h-3.5 text-emerald-400 group-hover:scale-110 transition-transform" />
                            Trade Now
                        </button>
                        <button 
                            className="w-full text-left px-3 py-2 text-xs font-mono text-white hover:bg-white/10 rounded flex items-center gap-2 group transition-colors"
                            onClick={() => {
                                toast.info("Asset Marked", { description: `${contextMenu.item?.symbol} added to Priority Watchlist.` });
                                setContextMenu(null);
                            }}
                        >
                            <Eye className="w-3.5 h-3.5 text-blue-400 group-hover:scale-110 transition-transform" />
                            Add to Watchlist
                        </button>
                        <button 
                            className="w-full text-left px-3 py-2 text-xs font-mono text-white hover:bg-white/10 rounded flex items-center gap-2 group transition-colors"
                            onClick={() => {
                                toast.message("Agent Bound", { description: `${contextMenu.item?.symbol} parameters injected into Agent Builder.` });
                                setContextMenu(null);
                            }}
                        >
                            <Cpu className="w-3.5 h-3.5 text-purple-400 group-hover:scale-110 transition-transform" />
                            Send to Agent Builder
                        </button>
                    </div>
                </div>
            )}
        </Card>
    );
}
