"use client";

import React from 'react';

export function DepthChart() {
    return (
        <div className="w-full h-full min-h-[120px] bg-black/20 border border-white/5 relative overflow-hidden rounded flex items-end">
            {/* Grid Background */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px] pointer-events-none" />

            <div className="absolute top-2 left-2 text-[8px] font-mono text-muted-foreground z-10">
                ORDER_BOOK_DEPTH // SYMBOL: POLY
            </div>

            {/* Mock Depth Visualization - SVG */}
            <svg className="w-full h-full absolute inset-0 z-0" preserveAspectRatio="none">
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
                <path d="M0 150 L0 80 C 20 80, 40 90, 60 95 S 100 100, 140 100 L 140 150 Z" fill="url(#bidGradient)" stroke="#10B981" strokeOpacity="0.8" vectorEffect="non-scaling-stroke" />

                {/* Asks (Right - Red/Orange) */}
                <path d="M300 150 L300 70 C 260 70, 240 85, 220 90 S 180 110, 160 110 L 160 150 Z" fill="url(#askGradient)" stroke="#ef4444" strokeOpacity="0.8" vectorEffect="non-scaling-stroke" />

                {/* Mid Price Line */}
                <line x1="50%" y1="0" x2="50%" y2="100%" stroke="rgba(255,255,255,0.2)" strokeDasharray="2 2" />
            </svg>

            {/* Price Labels */}
            <div className="w-full flex justify-between px-2 text-[8px] font-mono text-muted-foreground absolute bottom-1 z-10">
                <span>0.45</span>
                <span className="text-white">0.50</span>
                <span>0.55</span>
            </div>
        </div>
    );
}
