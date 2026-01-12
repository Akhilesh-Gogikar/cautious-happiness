'use client';

import React, { useState } from 'react';
import { CockpitShell } from '@/components/cockpit/cockpit-shell';
import { ReasoningSidebar } from '@/components/cockpit/reasoning-sidebar';
import { ReasoningStream } from '@/components/brain/reasoning-stream';
import { CoachDebrief } from '@/components/brain/coach-debrief';
import { ConfidenceGauge } from '@/components/brain/confidence-gauge';
import { ModelStateIndicators } from '@/components/brain/model-state-indicators';
import { KillSwitch } from '@/components/controls/kill-switch';
import { SensitivitySlider } from '@/components/controls/sensitivity-slider';
import { OverrideInput } from '@/components/controls/override-input';
import { ApprovalQueue } from '@/components/controls/approval-queue';
import { ScenarioSimulator } from '@/components/brain/scenario-simulator';
import { DecisionTreeViz } from '@/components/brain/decision-tree-viz';
import { TimelineOverlay } from '@/components/cockpit/timeline-overlay';
import { AlertTriangle, ShieldCheck, Zap, Layers, Eye, EyeOff, BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';

type ViewMode = 'PILOT' | 'ENGINEER';

export default function CockpitPage() {
    const [viewMode, setViewMode] = useState<ViewMode>('PILOT');
    const [showDebrief, setShowDebrief] = useState(false);

    return (
        <CockpitShell
            sidebar={viewMode === 'ENGINEER' ? <ReasoningStream /> : null}
            timeline={viewMode === 'ENGINEER' ? <TimelineOverlay /> : null}
            className={viewMode === 'PILOT' ? 'bg-black' : ''} // Simpler bg for Pilot
        >
            {/* Coach Debrief Overlay */}
            {showDebrief && (
                <div className="fixed inset-0 z-50 bg-black/95 backdrop-blur-xl p-8 animate-fade-in">
                    <div className="max-w-7xl mx-auto h-full flex flex-col">
                        <div className="flex justify-end mb-4">
                            <button
                                onClick={() => setShowDebrief(false)}
                                className="px-4 py-2 rounded-full border border-white/10 hover:bg-white/10 text-white/50 hover:text-white transition-colors text-xs uppercase tracking-widest"
                            >
                                Close Debrief
                            </button>
                        </div>
                        <CoachDebrief />
                    </div>
                </div>
            )}

            <div className="flex flex-col h-full gap-6">

                {/* Header / Mode Toggle */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <h1 className="text-2xl font-bold text-white tracking-widest uppercase">
                            AlphaSignals <span className="text-emerald-500">Brain</span>
                        </h1>
                        <div className="px-2 py-1 rounded bg-white/10 text-[10px] items-center flex gap-1 text-white/50 border border-white/5">
                            <div className={cn("w-2 h-2 rounded-full", viewMode === 'PILOT' ? "bg-blue-400" : "bg-purple-500")}></div>
                            {viewMode} MODE
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setShowDebrief(true)}
                            className="px-4 py-1.5 rounded-full border border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/10 hover:text-white transition-colors text-xs font-bold uppercase tracking-wider flex items-center gap-2"
                        >
                            <BookOpen className="w-3 h-3" /> Debrief
                        </button>

                        <div className="flex items-center bg-white/5 rounded-full p-1 border border-white/10">
                            <button
                                onClick={() => setViewMode('PILOT')}
                                className={cn(
                                    "flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium transition-all",
                                    viewMode === 'PILOT' ? "bg-white/10 text-white shadow-lg" : "text-white/40 hover:text-white"
                                )}
                            >
                                <Eye className="w-3 h-3" /> Pilot
                            </button>
                            <button
                                onClick={() => setViewMode('ENGINEER')}
                                className={cn(
                                    "flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium transition-all",
                                    viewMode === 'ENGINEER' ? "bg-purple-500/20 text-purple-200 border border-purple-500/30 shadow-[0_0_15px_rgba(168,85,247,0.3)]" : "text-white/40 hover:text-white"
                                )}
                            >
                                <Layers className="w-3 h-3" /> Engineer
                            </button>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-12 gap-6 flex-1 min-h-0">
                    {/* Main Central Area - The "HUD" */}
                    <div className={cn("flex flex-col gap-6 transition-all duration-500", viewMode === 'PILOT' ? "col-span-12" : "col-span-9")}>

                        {/* Model State Indicators (Visible in both, but maybe more detailed in Engineer) */}
                        <ModelStateIndicators />

                        {/* Top Stats Row */}
                        <div className="grid grid-cols-3 gap-4">
                            <div className="p-4 rounded-xl border border-white/10 bg-white/5 backdrop-blur-md relative overflow-hidden group">
                                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                <h3 className="text-white/50 text-xs font-mono uppercase tracking-wider mb-1">Total PnL</h3>
                                <div className="text-3xl font-bold text-emerald-400 text-glow-primary">+$12,450.00</div>
                                <div className="text-emerald-500/70 text-xs flex items-center gap-1 mt-2">
                                    <Zap className="w-3 h-3" /> +2.4% Today
                                </div>
                            </div>

                            <div className="p-4 rounded-xl border border-white/10 bg-white/5 backdrop-blur-md relative overflow-hidden group">
                                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                <h3 className="text-white/50 text-xs font-mono uppercase tracking-wider mb-1">Active Positions</h3>
                                <div className="text-3xl font-bold text-blue-400 text-glow-indigo">14</div>
                                <div className="text-blue-500/70 text-xs flex items-center gap-1 mt-2">
                                    4 Pending Entry
                                </div>
                            </div>

                            <div className="p-4 rounded-xl border border-white/10 bg-white/5 backdrop-blur-md relative overflow-hidden group">
                                <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                <h3 className="text-white/50 text-xs font-mono uppercase tracking-wider mb-1">System Health</h3>
                                <div className="text-3xl font-bold text-purple-400 text-glow-neon">98%</div>
                                <div className="text-purple-500/70 text-xs flex items-center gap-1 mt-2">
                                    <ShieldCheck className="w-3 h-3" /> All Systems Nominal
                                </div>
                            </div>
                        </div>

                        {/* Main Chart / Visualizer Area */}
                        <div className="flex-1 rounded-xl border border-white/10 bg-black/40 backdrop-blur-sm relative overflow-hidden group min-h-[400px] flex flex-col">
                            <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/5">
                                <h3 className="text-white/80 font-bold text-sm">Active Markets Analysis</h3>
                                {viewMode === 'ENGINEER' && (
                                    <div className="flex gap-2">
                                        <button className="px-3 py-1 rounded-full bg-white/10 border border-white/10 text-xs text-white hover:bg-white/20 transition-colors">Decision Tree</button>
                                        <button className="px-3 py-1 rounded-full bg-transparent border border-white/10 text-xs text-white/50 hover:text-white transition-colors">Market Depth</button>
                                        <button className="px-3 py-1 rounded-full bg-transparent border border-white/10 text-xs text-white/50 hover:text-white transition-colors">Correlation</button>
                                    </div>
                                )}
                            </div>

                            <div className="flex-1 relative">
                                {viewMode === 'ENGINEER' ? (
                                    <DecisionTreeViz />
                                ) : (
                                    <div className="p-6 grid grid-cols-2 lg:grid-cols-4 gap-4 overflow-y-auto h-full">
                                        {/* Active Trade Cards / Gauges */}
                                        <ConfidenceGauge
                                            label="FED RATE HOLD"
                                            marketProb={45}
                                            aiConfidence={65}
                                            className="p-4 bg-white/5 rounded-xl border border-white/5 hover:border-emerald-500/50 transition-all"
                                        />
                                        <ConfidenceGauge
                                            label="TRUMP GILLIBRAND"
                                            marketProb={88}
                                            aiConfidence={92}
                                            className="p-4 bg-white/5 rounded-xl border border-white/5 hover:border-emerald-500/50 transition-all"
                                        />
                                        <ConfidenceGauge
                                            label="CPI > 3.2%"
                                            marketProb={12}
                                            aiConfidence={10}
                                            className="p-4 bg-white/5 rounded-xl border border-white/5 hover:border-emerald-500/50 transition-all"
                                        />
                                        <ConfidenceGauge
                                            label="ETH > 3000 DEC"
                                            marketProb={50}
                                            aiConfidence={52}
                                            className="p-4 bg-white/5 rounded-xl border border-white/5 hover:border-emerald-500/50 transition-all"
                                        />
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Right Control Panel / Alerts */}
                    {/* Conditional: In PILOT mode, maybe we show less or different controls? For now, we keep it, but maybe hide advanced debugs */}
                    {viewMode === 'ENGINEER' && (
                        <div className="col-span-3 flex flex-col gap-4 animate-fade-in">

                            {/* Approval Queue */}
                            <ApprovalQueue />

                            {/* Quick Actions / Control */}
                            <div className="flex-1 rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm p-4">
                                <h3 className="text-white/50 text-xs font-mono uppercase tracking-wider mb-4 border-b border-white/10 pb-2">Manual Intervention</h3>
                                <div className="space-y-3">
                                    {/* Risk Controls */}
                                    <div className="space-y-6">
                                        <SensitivitySlider
                                            label="Risk Tolerance"
                                            defaultValue={45}
                                            className="p-3 rounded border border-white/10 bg-white/5 hover:border-emerald-500/30 transition-colors"
                                        />
                                        <SensitivitySlider
                                            label="Execution Speed"
                                            defaultValue={80}
                                            className="p-3 rounded border border-white/10 bg-white/5 hover:border-blue-500/30 transition-colors"
                                        />
                                        <OverrideInput />
                                        <div className="pt-4 border-t border-white/10">
                                            <ScenarioSimulator />
                                        </div>
                                    </div>

                                    {/* Kill Switch Module */}
                                    <div className="mt-8 flex items-center justify-center">
                                        <KillSwitch />
                                    </div>
                                </div>
                            </div>

                        </div>
                    )}
                </div>
            </div>
        </CockpitShell>
    );
}
