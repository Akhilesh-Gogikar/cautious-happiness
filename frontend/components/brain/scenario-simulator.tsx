'use client';

import React, { useState } from 'react';
import { Sliders, RefreshCw, Play } from 'lucide-react';
import * as Slider from '@radix-ui/react-slider';
import { cn } from '@/lib/utils';

export function ScenarioSimulator() {
    const [inflation, setInflation] = useState(3.2);
    const [interestRate, setInterestRate] = useState(5.5);
    const [simulationRunning, setSimulationRunning] = useState(false);

    const runSimulation = () => {
        setSimulationRunning(true);
        setTimeout(() => setSimulationRunning(false), 2000);
    };

    return (
        <div className="p-4 rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm">
            <div className="flex items-center gap-2 text-white/70 mb-4 pb-2 border-b border-white/10">
                <Sliders className="w-4 h-4" />
                <h3 className="font-bold text-xs uppercase tracking-wider">What-If Engine (Simulator)</h3>
            </div>

            <div className="space-y-6">
                <div className="space-y-3">
                    <div className="flex justify-between text-xs">
                        <span className="text-white/60">Inflation (CPI)</span>
                        <span className="text-emerald-400 font-mono">{inflation}%</span>
                    </div>
                    <Slider.Root
                        className="relative flex items-center select-none touch-none w-full h-5"
                        value={[inflation]}
                        max={10}
                        step={0.1}
                        onValueChange={(v) => setInflation(v[0])}
                    >
                        <Slider.Track className="bg-white/10 relative grow rounded-full h-[3px]">
                            <Slider.Range className="absolute bg-emerald-500 rounded-full h-full" />
                        </Slider.Track>
                        <Slider.Thumb className="block w-3 h-3 bg-white hover:scale-125 transition-transform rounded-full focus:outline-none" />
                    </Slider.Root>
                </div>

                <div className="space-y-3">
                    <div className="flex justify-between text-xs">
                        <span className="text-white/60">Fed Funds Rate</span>
                        <span className="text-blue-400 font-mono">{interestRate}%</span>
                    </div>
                    <Slider.Root
                        className="relative flex items-center select-none touch-none w-full h-5"
                        value={[interestRate]}
                        max={10}
                        step={0.25}
                        onValueChange={(v) => setInterestRate(v[0])}
                    >
                        <Slider.Track className="bg-white/10 relative grow rounded-full h-[3px]">
                            <Slider.Range className="absolute bg-blue-500 rounded-full h-full" />
                        </Slider.Track>
                        <Slider.Thumb className="block w-3 h-3 bg-white hover:scale-125 transition-transform rounded-full focus:outline-none" />
                    </Slider.Root>
                </div>

                <button
                    onClick={runSimulation}
                    disabled={simulationRunning}
                    className="w-full py-2 rounded bg-white/5 border border-white/10 hover:bg-white/10 text-xs text-white flex items-center justify-center gap-2 transition-all"
                >
                    {simulationRunning ? (
                        <>
                            <RefreshCw className="w-3 h-3 animate-spin" /> Simulating...
                        </>
                    ) : (
                        <>
                            <Play className="w-3 h-3" /> Run Scenario
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}
