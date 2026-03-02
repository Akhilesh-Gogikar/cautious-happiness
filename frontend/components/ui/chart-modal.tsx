"use client";

import React, { useState, useEffect } from "react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { ArrowUpRight, ArrowDownRight, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChartModalProps {
    isOpen: boolean;
    onClose: () => void;
    ticker: { symbol: string; price: string; change: number } | null;
}

export function ChartModal({ isOpen, onClose, ticker }: ChartModalProps) {
    const [dataPoints, setDataPoints] = useState<number[]>([]);

    useEffect(() => {
        if (isOpen && ticker) {
            // Generate some mock data based on the current price/change
            const points = [];
            let currentVal = parseFloat(ticker.price.replace(/[^0-9.-]+/g, ""));
            for (let i = 0; i < 50; i++) {
                points.push(currentVal);
                currentVal += (Math.random() - 0.5) * (currentVal * 0.05);
            }
            setDataPoints(points);
        }
    }, [isOpen, ticker]);

    if (!ticker) return null;

    const isPositive = ticker.change >= 0;
    const strokeColor = isPositive ? "#10B981" : "#ef4444";
    const gradientId = isPositive ? "positiveGradient" : "negativeGradient";

    const min = Math.min(...dataPoints);
    const max = Math.max(...dataPoints);
    const range = max - min || 1;

    // Generate SVG path for the line chart
    const pathData = dataPoints.map((val, i) => {
        const x = (i / (dataPoints.length - 1)) * 100;
        const y = 100 - ((val - min) / range) * 80 - 10; // keep it within vertically
        return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
    }).join(' ');

    // Add final points to close the area
    const areaPath = `${pathData} L 100 100 L 0 100 Z`;

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[600px] border-white/10 bg-black/90 backdrop-blur-xl">
                <DialogHeader>
                    <div className="flex items-center justify-between">
                        <DialogTitle className="flex items-center gap-3">
                            <span className="text-2xl font-black text-white">{ticker.symbol}</span>
                            <span className="text-xl font-mono text-white/80">{ticker.price}</span>
                            <div
                                className={cn(
                                    "flex items-center gap-1 font-mono text-sm font-black px-2 py-1 rounded",
                                    isPositive
                                        ? "text-primary bg-primary/10"
                                        : "text-destructive bg-destructive/10"
                                )}
                            >
                                {isPositive ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                                {Math.abs(ticker.change)}%
                            </div>
                        </DialogTitle>
                    </div>
                </DialogHeader>

                <div className="mt-4 w-full h-[300px] bg-black/20 border border-white/5 relative overflow-hidden rounded-md flex items-end">
                    {/* Grid Background */}
                    <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px] pointer-events-none" />

                    <div className="absolute top-4 left-4 text-xs font-mono text-muted-foreground z-10 flex items-center gap-2">
                        <Activity className="w-4 h-4 text-primary animate-pulse" />
                        LIVE_CHART // SYMBOL: {ticker.symbol.split('/')[0]}
                    </div>

                    {/* Chart Visualization - SVG */}
                    {dataPoints.length > 0 && (
                        <svg className="w-full h-full absolute inset-0 z-0" preserveAspectRatio="none" viewBox="0 0 100 100">
                            <defs>
                                <linearGradient id="positiveGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#10B981" stopOpacity="0.4" />
                                    <stop offset="100%" stopColor="#10B981" stopOpacity="0.05" />
                                </linearGradient>
                                <linearGradient id="negativeGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#ef4444" stopOpacity="0.4" />
                                    <stop offset="100%" stopColor="#ef4444" stopOpacity="0.05" />
                                </linearGradient>
                            </defs>

                            {/* Area filled */}
                            <path d={areaPath} fill={`url(#${gradientId})`} />

                            {/* Line */}
                            <path d={pathData} fill="none" stroke={strokeColor} strokeWidth="1.5" vectorEffect="non-scaling-stroke" />

                        </svg>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
