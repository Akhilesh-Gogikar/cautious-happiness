"use client";

import React, { useEffect, useState, useMemo } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';

interface OrderBookLevel {
    price: number;
    amount: number;
}

interface OrderBook {
    asks: OrderBookLevel[];
    bids: OrderBookLevel[];
}

interface DepthChartProps {
    marketId?: string;
}

export function DepthChart({ marketId }: DepthChartProps) {
    const [data, setData] = useState<OrderBook | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(false);
    const [hoverPrice, setHoverPrice] = useState<number | null>(null);

    useEffect(() => {
        if (!marketId) return;

        const fetchData = async () => {
            setLoading(true);
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api";
                const res = await fetch(`${apiUrl}/markets/${marketId}/orderbook`);
                if (res.ok) {
                    const json = await res.json();
                    setData(json);
                    setError(false);
                } else {
                    setError(true);
                }
            } catch (e) {
                console.error("Failed to fetch order book", e);
                setError(true);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        // Poll every 5 seconds
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, [marketId]);

    const { bidPath, askPath, minPrice, maxPrice, maxVolume } = useMemo(() => {
        if (!data || (!data.bids.length && !data.asks.length)) {
            return { bidPath: "", askPath: "", minPrice: 0, maxPrice: 1, maxVolume: 100 };
        }

        // Combine to find ranges
        const allLevels = [...data.bids, ...data.asks];
        // Sort for safety
        const bids = [...data.bids].sort((a, b) => b.price - a.price); // Descending
        const asks = [...data.asks].sort((a, b) => a.price - b.price); // Ascending

        // We want a cumulative volume for depth chart
        let cumVol = 0;
        const bidPoints: { x: number, y: number }[] = [];
        for (const b of bids) {
            cumVol += b.amount;
            bidPoints.push({ x: b.price, y: cumVol });
        }
        const maxBidVol = cumVol;

        cumVol = 0;
        const askPoints: { x: number, y: number }[] = [];
        for (const a of asks) {
            cumVol += a.amount;
            askPoints.push({ x: a.price, y: cumVol });
        }
        const maxAskVol = cumVol;

        const maxVol = Math.max(maxBidVol, maxAskVol) || 100;

        // Price range (local visual focus)
        // If empty, default 0-1
        const prices = allLevels.map(l => l.price);
        const minP = prices.length ? Math.min(...prices) * 0.95 : 0;
        const maxP = prices.length ? Math.max(...prices) * 1.05 : 1;

        // Scaling functions
        // X = Price, Y = Volume (usually depth charts show Price on X, Volume on Y)
        // Or strictly: Price on X (horz), Cumulative Vol on Y (vert)
        const scaleX = (price: number) => {
            return ((price - minP) / (maxP - minP)) * 100;
        }
        const scaleY = (vol: number) => {
            // Invert Y for SVG (0 is top)
            return 100 - ((vol / maxVol) * 90); // Use 90% height
        }

        // Build Paths
        // Bids: From low price to high price, but they are sorted desc.
        // Usually Depth Chart:
        // Left Side: Bids (Green). Right Side: Asks (Red).
        // Mid is the spread.
        // So Bids should go from minP to bestBid.
        // Asks should go from bestAsk to maxP.

        // Re-process for drawing
        // We want to draw from left (minP) to right (maxP).

        // Bids: Start from left (minP), go to bestBid.
        // But our sorted bids list starts at bestBid and goes down.
        // So reverse it for plotting left-to-right.
        const sortedBidsAsc = [...bids].reverse();

        let dBid = `M 0 100 `; // Start bottom-left
        let currentCumVol = 0; // But we need total cum vol at lowest price? No, usually cum vol accumulates AWAY from the spread.
        // Standard Depth Chart: X-axis is price. Y-axis is Total Quantity available at that price or better.
        // So at Best Bid, volume is small. At Low Bid, volume is high (sum of all better bids).
        // Wait, "At that price or better".
        // If I want to sell, I look at Bids. I can sell X amount at Best Bid.
        // If I need to sell MORE, I eat into lower bids.
        // So visual:
        // Center (Spread) -> Outwards.
        // Volume grows as we move away from center.

        // Bids (Left side):
        // X: Price. Y: Cumulative Volume.
        // Iterating Bids (Best -> Worst / High -> Low).
        // Point (BestBidPrice, Vol1)
        // Point (NextBidPrice, Vol1+Vol2) ...

        let pathPointsBids: string[] = [];
        let cv = 0;

        // Start from Best Bid (Rightmost of the green side)
        // We need to draw the filled area.
        // Let's collect points (x, y)
        const bidPoly: [number, number][] = [];

        bids.forEach(b => {
            cv += b.amount;
            bidPoly.push([scaleX(b.price), scaleY(cv)]);
        });

        // Construct SVG Path
        // Start from bottom-right of bid side (Best Bid Price, 0 volume -> which is bottom)
        // Actually, usually we fill UNDER the line.
        // Point 0: (BestBid.X, 100) (Bottom)
        // Then line to (BestBid.X, BestBid.Y)
        // Then ... (WorstBid.X, WorstBid.Y)
        // Then line to (WorstBid.X, 100) (Bottom)

        if (bids.length > 0) {
            const bestX = scaleX(bids[0].price);
            dBid = `M ${bestX} 100 L ${bestX} ${scaleY(bids[0].amount)} `;

            let cVol = 0;
            bids.forEach(b => {
                cVol += b.amount;
                // Step logic for crisp edges? Or smooth?
                // Smooth for now
                dBid += `L ${scaleX(b.price)} ${scaleY(cVol)} `;
            });

            // Close shape at bottom left
            const lastX = scaleX(bids[bids.length - 1].price);
            dBid += `L ${lastX} 100 Z`;
        } else {
            dBid = "";
        }

        // Asks (Right Side)
        // Start Best Ask -> High Ask
        let dAsk = "";
        if (asks.length > 0) {
            const bestAskX = scaleX(asks[0].price);
            dAsk = `M ${bestAskX} 100 L ${bestAskX} ${scaleY(asks[0].amount)} `;

            let cVol = 0;
            asks.forEach(a => {
                cVol += a.amount;
                dAsk += `L ${scaleX(a.price)} ${scaleY(cVol)} `;
            });

            // Close shape at bottom right
            const lastX = scaleX(asks[asks.length - 1].price);
            dAsk += `L ${lastX} 100 Z`;
        }

        return { bidPath: dBid, askPath: dAsk, minPrice: minP, maxPrice: maxP, maxVolume: maxVol };

    }, [data]);

    if (loading && !data) {
        return (
            <div className="w-full h-full min-h-[120px] bg-black/20 border border-white/5 rounded flex items-center justify-center">
                <Loader2 className="w-4 h-4 text-emerald-500 animate-spin" />
            </div>
        );
    }

    if (error && !data) {
        return (
            <div className="w-full h-full min-h-[120px] bg-black/20 border border-white/5 rounded flex items-center justify-center flex-col gap-2">
                <AlertCircle className="w-4 h-4 text-red-500/50" />
                <span className="text-[10px] text-zinc-600">NO DATA</span>
            </div>
        );
    }

    if (!marketId) {
        return (
            <div className="w-full h-full min-h-[120px] bg-black/20 border border-white/5 rounded flex items-center justify-center">
                <span className="text-[10px] text-zinc-600 font-mono tracking-widest">SELECT MARKET</span>
            </div>
        );
    }

    return (
        <div className="w-full h-full min-h-[120px] bg-black/20 border border-white/5 relative overflow-hidden rounded flex items-end group">
            {/* Grid Background */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px] pointer-events-none" />

            <div className="absolute top-2 left-2 text-[8px] font-mono text-muted-foreground z-10 flex gap-2">
                <span>DEPTH // {marketId.substring(0, 6)}...</span>
                {hoverPrice && <span className="text-white bg-black/50 px-1 rounded">Price: {hoverPrice.toFixed(2)}</span>}
            </div>

            {/* Dynamic Depth Visualization - SVG */}
            <svg
                className="w-full h-full absolute inset-0 z-0"
                preserveAspectRatio="none"
                onMouseMove={(e) => {
                    const rect = e.currentTarget.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const percent = x / rect.width;
                    const price = minPrice + (percent * (maxPrice - minPrice));
                    setHoverPrice(price);
                }}
                onMouseLeave={() => setHoverPrice(null)}
            >
                <defs>
                    <linearGradient id="bidGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#10B981" stopOpacity="0.4" />
                        <stop offset="100%" stopColor="#10B981" stopOpacity="0.05" />
                    </linearGradient>
                    <linearGradient id="askGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#ef4444" stopOpacity="0.4" />
                        <stop offset="100%" stopColor="#ef4444" stopOpacity="0.05" />
                    </linearGradient>
                </defs>

                {/* Bids (Left - Green) */}
                <path
                    d={bidPath}
                    fill="url(#bidGradient)"
                    stroke="#10B981"
                    strokeWidth="1.5"
                    strokeOpacity="0.8"
                    vectorEffect="non-scaling-stroke"
                />

                {/* Asks (Right - Red/Orange) */}
                <path
                    d={askPath}
                    fill="url(#askGradient)"
                    stroke="#ef4444"
                    strokeWidth="1.5"
                    strokeOpacity="0.8"
                    vectorEffect="non-scaling-stroke"
                />

                {/* Mid Price Line */}
                {/* Calculate Mid X */}
                {data && data.asks.length > 0 && data.bids.length > 0 && (
                    <line
                        x1={`${(((data.asks[0].price + data.bids[0].price) / 2 - minPrice) / (maxPrice - minPrice)) * 100}%`}
                        y1="0"
                        x2={`${(((data.asks[0].price + data.bids[0].price) / 2 - minPrice) / (maxPrice - minPrice)) * 100}%`}
                        y2="100%"
                        stroke="rgba(255,255,255,0.2)"
                        strokeDasharray="2 2"
                    />
                )}

                {/* Hover Line */}
                {hoverPrice && (
                    <line
                        x1={`${((hoverPrice - minPrice) / (maxPrice - minPrice)) * 100}%`}
                        y1="0"
                        x2={`${((hoverPrice - minPrice) / (maxPrice - minPrice)) * 100}%`}
                        y2="100%"
                        stroke="rgba(255,255,255,0.5)"
                        strokeWidth="1"
                    />
                )}
            </svg>

            {/* Price Labels */}
            <div className="w-full flex justify-between px-2 text-[8px] font-mono text-muted-foreground absolute bottom-1 z-10 pointer-events-none">
                <span>{minPrice.toFixed(2)}</span>
                {data && data.bids.length > 0 && data.asks.length > 0 && (
                    <span className="text-white">{((data.bids[0].price + data.asks[0].price) / 2).toFixed(3)}</span>
                )}
                <span>{maxPrice.toFixed(2)}</span>
            </div>
        </div>
    );
}
