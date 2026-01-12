'use client';

import React from 'react';
import { BookOpen, ThumbsUp, ThumbsDown, MessageSquare, Award } from 'lucide-react';
import { cn } from '@/lib/utils';

export function CoachDebrief() {
    return (
        <div className="h-full flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                        <BookOpen className="w-6 h-6" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-white tracking-wide">Flight Recorder & Debrief</h2>
                        <p className="text-xs text-white/50">Post-mortem analysis of recent autonomous decisions.</p>
                    </div>
                </div>

                <div className="flex gap-2">
                    <div className="px-3 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
                        <Award className="w-4 h-4" />
                        <span>Win Rate: 68%</span>
                    </div>
                </div>
            </div>

            <div className="flex-1 grid grid-cols-2 gap-6 min-h-0">
                {/* Recent Decision Log */}
                <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm p-4 overflow-hidden flex flex-col">
                    <h3 className="text-white/70 text-sm font-bold uppercase tracking-wider mb-4">Recent Decisions</h3>
                    <div className="flex-1 overflow-y-auto pr-2 space-y-4">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="p-4 rounded-lg bg-black/40 border border-white/5 hover:border-white/20 transition-all cursor-pointer group">
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex flex-col">
                                        <span className="text-sm font-bold text-white group-hover:text-indigo-400 transition-colors">Entered Short: NVDA</span>
                                        <span className="text-xs text-white/40">14:02:11 • Signal: Overbought RSI</span>
                                    </div>
                                    <span className={cn("text-xs font-bold", i === 1 ? "text-red-400" : "text-emerald-400")}>
                                        {i === 1 ? "-$120.00" : "+$450.00"}
                                    </span>
                                </div>
                                <p className="text-xs text-white/60 mb-3 bg-white/5 p-2 rounded">
                                    "Model detected divergence in RSI on 5m timeframe combined with negative sentiment spike on X."
                                </p>
                                <div className="flex gap-2">
                                    <button className="flex-1 py-1.5 rounded flex items-center justify-center gap-2 bg-white/5 hover:bg-emerald-500/20 text-white/30 hover:text-emerald-400 text-xs transition-colors">
                                        <ThumbsUp className="w-3 h-3" /> Good Move
                                    </button>
                                    <button className="flex-1 py-1.5 rounded flex items-center justify-center gap-2 bg-white/5 hover:bg-red-500/20 text-white/30 hover:text-red-400 text-xs transition-colors">
                                        <ThumbsDown className="w-3 h-3" /> Bad Move
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Feedback Loop / Adjustments */}
                <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm p-4 flex flex-col">
                    <h3 className="text-white/70 text-sm font-bold uppercase tracking-wider mb-4">Behavioral Adjustment</h3>

                    <div className="flex-1 bg-black/40 rounded-lg border border-white/5 p-4 flex flex-col gap-4">
                        <div className="flex items-center gap-2 text-indigo-300 mb-2">
                            <MessageSquare className="w-4 h-4" />
                            <span className="font-bold text-sm">Coach's Notes</span>
                        </div>

                        <textarea
                            className="w-full flex-1 bg-white/5 border border-white/10 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-indigo-500/50 resize-none"
                            placeholder="Provide natural language feedback to adjust the agent's future behavior..."
                        ></textarea>

                        <div className="flex justify-end">
                            <button className="px-6 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm shadow-[0_0_15px_rgba(79,70,229,0.4)] transition-all">
                                Submit Feedback
                            </button>
                        </div>
                    </div>

                    <div className="mt-4 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                        <h4 className="text-emerald-400 text-xs font-bold uppercase mb-2">Active Learnings</h4>
                        <ul className="text-xs text-white/70 list-disc list-inside space-y-1">
                            <li>Avoid trading CPI releases during first 5 mins.</li>
                            <li>Prioritize volume over price action for small caps.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
