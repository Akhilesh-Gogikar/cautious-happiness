'use client';

import React from 'react';
import { Terminal, Activity, Brain } from 'lucide-react';

export function ReasoningSidebar() {
    return (
        <div className="flex h-full flex-col text-[#00ff94] font-mono text-sm">
            <div className="flex items-center gap-2 border-b border-white/10 p-4 bg-white/5">
                <Brain className="h-4 w-4" />
                <span className="font-bold tracking-wider text-xs uppercase opacity-80">Reasoning Stream</span>
                <div className="ml-auto flex items-center gap-1.5">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span className="text-[10px] text-emerald-500 font-bold">LIVE</span>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono">
                {/* Mock Stream Items */}
                <div className="flex gap-3 animate-fade-in opacity-50">
                    <span className="text-white/30 text-xs whitespace-nowrap">12:58:01</span>
                    <div>
                        <span className="text-blue-400 font-bold">[DATA_INGEST]</span>
                        <span className="text-white/70 ml-2">Parsing Bloomberg API... Received 45 packets.</span>
                    </div>
                </div>

                <div className="flex gap-3 animate-fade-in opacity-70">
                    <span className="text-white/30 text-xs whitespace-nowrap">12:58:04</span>
                    <div>
                        <span className="text-purple-400 font-bold">[SENTIMENT]</span>
                        <span className="text-white/70 ml-2">Analyzed &quot;Fed Speech&quot;. Hawkish tone detected (0.78).</span>
                    </div>
                </div>

                <div className="flex gap-3 animate-fade-in text-white shadow-[0_0_10px_rgba(0,255,148,0.2)] p-2 -mx-2 rounded bg-white/5 border-l-2 border-[#00ff94]">
                    <span className="text-white/50 text-xs whitespace-nowrap">12:58:09</span>
                    <div className="flex flex-col gap-1">
                        <div>
                            <span className="text-[#00ff94] font-bold">[DECISION]</span>
                            <span className="text-white ml-2">Probability Divergence found in POLY-294.</span>
                        </div>
                        <div className="pl-4 border-l border-white/10 text-xs text-white/60">
                            &gt; Market: 45% | Model: 65%<br />
                            &gt; Action: PREPARE_BUY<br />
                            &gt; Confidence: High
                        </div>
                    </div>
                </div>
            </div>

            <div className="p-2 border-t border-white/10 bg-black/20 text-xs text-white/40 flex items-center justify-between">
                <span>Latency: 12ms</span>
                <span className="flex items-center gap-1"><Terminal className="w-3 h-3" /> Ready</span>
            </div>
        </div>
    );
}
