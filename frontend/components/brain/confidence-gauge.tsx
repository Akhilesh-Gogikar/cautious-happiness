'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { HelpCircle } from 'lucide-react';

interface ConfidenceGaugeProps {
    label: string;
    marketProb: number; // 0 to 100
    aiConfidence: number; // 0 to 100
    className?: string;
}

export function ConfidenceGauge({ label, marketProb, aiConfidence, className }: ConfidenceGaugeProps) {
    // SVG Config
    const radius = 40;
    const stroke = 8;
    const normalizedRadius = radius - stroke * 2;
    const circumference = normalizedRadius * 2 * Math.PI;

    const marketOffset = circumference - (marketProb / 100) * circumference;
    const aiOffset = circumference - (aiConfidence / 100) * circumference;

    // Determine color based on divergence
    const divergence = Math.abs(aiConfidence - marketProb);
    const color = divergence > 15 ? 'text-emerald-500' : divergence > 5 ? 'text-blue-400' : 'text-gray-400';

    return (
        <div className={cn("relative flex flex-col items-center group", className)}>
            {/* Tooltip Trigger */}
            <div className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                <HelpCircle className="w-3 h-3 text-white/30 hover:text-white cursor-help" />
            </div>

            <div className="relative w-32 h-32 flex items-center justify-center">
                {/* Background Circle */}
                <svg
                    height={radius * 2.5}
                    width={radius * 2.5}
                    className="rotate-[-90deg]"
                >
                    <circle
                        stroke="rgba(255,255,255,0.1)"
                        strokeWidth={stroke}
                        fill="transparent"
                        r={normalizedRadius}
                        cx={radius * 1.25}
                        cy={radius * 1.25}
                    />
                    {/* Market Probability Ring (Outer/Background reference) */}
                    <circle
                        stroke="rgba(59, 130, 246, 0.3)" // Blue for Market
                        strokeWidth={stroke}
                        strokeDasharray={`${circumference} ${circumference}`}
                        strokeDashoffset={marketOffset}
                        strokeLinecap="round"
                        fill="transparent"
                        r={normalizedRadius}
                        cx={radius * 1.25}
                        cy={radius * 1.25}
                        className="transition-all duration-1000 ease-out"
                    />
                    {/* AI Confidence Ring (Inner/Main) */}
                    <circle
                        stroke="currentColor"
                        strokeWidth={stroke}
                        strokeDasharray={`${circumference} ${circumference}`}
                        strokeDashoffset={aiOffset}
                        strokeLinecap="round"
                        fill="transparent"
                        r={normalizedRadius}
                        cx={radius * 1.25}
                        cy={radius * 1.25}
                        className={cn("transition-all duration-1000 ease-out", color)}
                        style={{ filter: "drop-shadow(0 0 4px currentColor)" }}
                    />
                </svg>

                {/* Center Text */}
                <div className="absolute flex flex-col items-center">
                    <span className={cn("text-xl font-bold font-mono tracking-tighter", color)}>
                        {aiConfidence}%
                    </span>
                    <span className="text-[9px] text-white/40 uppercase tracking-widest">CONF</span>
                </div>
            </div>

            {/* Labels / Legend */}
            <div className="flex flex-col items-center gap-1 mt-1">
                <span className="text-xs font-bold text-white/90">{label}</span>
                <div className="flex gap-2 text-[10px]">
                    <span className="text-blue-400/80">Mkt: {marketProb}%</span>
                    <span className={cn(color)}>AI: {aiConfidence}%</span>
                </div>
            </div>
        </div>
    );
}
