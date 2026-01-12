'use client';

import React from 'react';
import { Clock } from 'lucide-react';

export function TimelineOverlay() {
    return (
        <div className="h-full w-full flex flex-col">
            <div className="flex items-center justify-between px-4 py-2 border-b border-white/5 bg-white/5">
                <div className="flex items-center gap-2 text-white/60">
                    <Clock className="w-4 h-4" />
                    <span className="text-xs font-mono uppercase tracking-wider">Unified Temporal Axis</span>
                </div>
                <div className="flex gap-2">
                    {/* Zoom Controls Placeholder */}
                    <div className="h-1.5 w-16 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full w-1/3 bg-blue-500/50"></div>
                    </div>
                </div>
            </div>

            <div className="flex-1 relative w-full overflow-hidden">
                {/* Grid Lines */}
                <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:100px_100%]"></div>

                {/* Mock Events on Timeline */}
                <div className="absolute top-1/2 left-0 w-full h-[1px] bg-white/10"></div>

                {/* News Event */}
                <div className="absolute top-1/2 left-[20%] -translate-y-1/2 flex flex-col items-center gap-2 group cursor-pointer">
                    <div className="w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)] group-hover:scale-125 transition-transform"></div>
                    <div className="absolute top-6 left-1/2 -translate-x-1/2 text-[10px] text-blue-400 whitespace-nowrap opacity-50 group-hover:opacity-100 transition-opacity">CPI Release</div>
                </div>

                {/* Trade Event */}
                <div className="absolute top-1/2 left-[45%] -translate-y-1/2 flex flex-col items-center gap-2 group cursor-pointer">
                    <div className="w-3 h-3 rounded-full bg-[#00ff94] shadow-[0_0_10px_rgba(0,255,148,0.5)] group-hover:scale-125 transition-transform"></div>
                    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 text-[10px] text-[#00ff94] whitespace-nowrap opacity-50 group-hover:opacity-100 transition-opacity">Bought Yes</div>
                </div>

                {/* Alert Event */}
                <div className="absolute top-1/2 left-[70%] -translate-y-1/2 flex flex-col items-center gap-2 group cursor-pointer">
                    <div className="w-3 h-3 rounded-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)] group-hover:scale-125 transition-transform"></div>
                    <div className="absolute top-6 left-1/2 -translate-x-1/2 text-[10px] text-red-400 whitespace-nowrap opacity-50 group-hover:opacity-100 transition-opacity">Drawdown Warning</div>
                </div>
            </div>
        </div>
    );
}
