'use client';

import React from 'react';
import { GitBranch, CheckCircle, XCircle, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

export function DecisionTreeViz() {
    return (
        <div className="flex flex-col h-full overflow-hidden relative">
            {/* Background Grid */}
            <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10 pointer-events-none"></div>

            <div className="flex-1 flex items-center justify-center p-8 overflow-x-auto">
                <div className="flex gap-8 items-center min-w-max">
                    {/* Root Node */}
                    <div className="flex flex-col items-center gap-2">
                        <div className="p-4 rounded-xl border border-blue-500/50 bg-blue-500/10 backdrop-blur-md shadow-[0_0_20px_rgba(59,130,246,0.2)]">
                            <div className="flex items-center gap-2 text-blue-300 mb-1">
                                <GitBranch className="w-4 h-4" />
                                <span className="font-bold text-xs uppercase">Trigger Event</span>
                            </div>
                            <div className="text-sm font-bold text-white">New Poll: CNN</div>
                        </div>
                        <div className="h-8 w-px bg-blue-500/30"></div>
                        <div className="px-2 py-0.5 rounded bg-black border border-white/10 text-[10px] text-white/50">Timestamp: 14:02:22</div>
                    </div>

                    <ArrowRight className="text-white/20 w-6 h-6" />

                    {/* Branch Node 1 */}
                    <div className="flex flex-col items-center gap-2">
                        <div className="p-4 rounded-xl border border-purple-500/50 bg-purple-500/10 backdrop-blur-md">
                            <div className="flex items-center gap-2 text-purple-300 mb-1">
                                <span className="font-bold text-xs uppercase">Analysis</span>
                            </div>
                            <div className="text-sm font-bold text-white">Trump +2% Shift</div>
                        </div>
                        <div className="h-8 w-px bg-purple-500/30"></div>
                        <div className="px-2 py-0.5 rounded bg-black border border-white/10 text-[10px] text-white/50">Confidence: 0.88</div>
                    </div>

                    <ArrowRight className="text-white/20 w-6 h-6" />

                    {/* Branch Node 2 */}
                    <div className="flex flex-col items-center gap-2">
                        <div className="p-4 rounded-xl border border-emerald-500/50 bg-emerald-500/10 backdrop-blur-md">
                            <div className="flex items-center gap-2 text-emerald-300 mb-1">
                                <span className="font-bold text-xs uppercase">Strategy</span>
                            </div>
                            <div className="text-sm font-bold text-white">Momentum Long</div>
                        </div>
                        <div className="h-8 w-px bg-emerald-500/30"></div>
                        <div className="px-2 py-0.5 rounded bg-black border border-white/10 text-[10px] text-white/50">Risk Check: PASS</div>
                    </div>

                    <ArrowRight className="text-white/20 w-6 h-6" />

                    {/* Leaf Node */}
                    <div className="flex flex-col items-center gap-2">
                        <div className="p-4 rounded-xl border border-emerald-500 bg-emerald-500/20 backdrop-blur-md shadow-[0_0_30px_rgba(16,185,129,0.3)] animate-pulse">
                            <div className="flex items-center gap-2 text-emerald-300 mb-1">
                                <CheckCircle className="w-4 h-4" />
                                <span className="font-bold text-xs uppercase">Execution</span>
                            </div>
                            <div className="text-sm font-bold text-white">Buy YES Shares</div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-black/40 border-t border-white/10 p-2 text-xs text-white/40 flex justify-between items-center">
                <span>Trace ID: 8f7a-2b1c-9d3e</span>
                <button className="hover:text-white transition-colors">View Full Log &rarr;</button>
            </div>
        </div>
    );
}
