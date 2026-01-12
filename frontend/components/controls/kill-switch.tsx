'use client';

import React, { useState } from 'react';
import { Skull, AlertOctagon, X, Check } from 'lucide-react';
import * as Dialog from '@radix-ui/react-dialog';
import { cn } from '@/lib/utils';

export function KillSwitch() {
    const [open, setOpen] = useState(false);
    const [triggered, setTriggered] = useState(false);

    const handleKill = () => {
        setTriggered(true);
        setOpen(false);
        // TODO: Emit actual backend signal
        console.log("KILL SWITCH ACTIVATED");
    };

    if (triggered) {
        return (
            <div className="w-full p-4 rounded-xl bg-red-500/20 border border-red-500 flex flex-col items-center justify-center gap-2 animate-pulse">
                <Skull className="w-8 h-8 text-red-500" />
                <span className="font-bold text-red-500 tracking-widest uppercase">SYSTEM HALTED</span>
                <button
                    onClick={() => setTriggered(false)}
                    className="mt-2 text-xs underline text-red-400 hover:text-red-300"
                >
                    Reset System
                </button>
            </div>
        )
    }

    return (
        <Dialog.Root open={open} onOpenChange={setOpen}>
            <Dialog.Trigger asChild>
                <button className="w-full group relative overflow-hidden rounded-xl bg-red-950/30 border border-red-900/50 p-6 transition-all hover:bg-red-900/40 hover:border-red-500/50">
                    <div className="absolute inset-0 bg-[url('/danger-stripe.png')] opacity-10"></div>
                    <div className="flex flex-col items-center gap-2 relative z-10">
                        <div className="rounded-full bg-red-500/20 p-3 group-hover:scale-110 transition-transform">
                            <Skull className="w-6 h-6 text-red-500" />
                        </div>
                        <span className="font-bold text-red-500 tracking-[0.2em] font-mono text-sm">KILL SWITCH</span>
                        <span className="text-[10px] text-red-400/50">EMERGENCY LIQUIDATION</span>
                    </div>
                </button>
            </Dialog.Trigger>

            <Dialog.Portal>
                <Dialog.Overlay className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 animate-fade-in" />
                <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-md translate-x-[-50%] translate-y-[-50%] rounded-xl bg-black border border-red-500 shadow-[0_0_50px_rgba(239,68,68,0.5)] p-6 focus:outline-none animate-fade-in">
                    <div className="flex flex-col items-center text-center gap-4">
                        <div className="p-4 rounded-full bg-red-500/20 animate-pulse">
                            <AlertOctagon className="w-12 h-12 text-red-500" />
                        </div>

                        <Dialog.Title className="text-xl font-bold text-white uppercase tracking-widest">
                            Confirm Emergency Stop
                        </Dialog.Title>

                        <Dialog.Description className="text-red-200/70 text-sm">
                            This will immediately <strong className="text-red-400">LIQUIDATE ALL POSITIONS</strong> and halt all trading bots. This action cannot be undone.
                        </Dialog.Description>

                        <div className="flex w-full gap-4 mt-4">
                            <Dialog.Close asChild>
                                <button className="flex-1 p-3 rounded bg-white/10 hover:bg-white/20 text-white font-mono text-sm border border-white/5 transition-colors">
                                    CANCEL
                                </button>
                            </Dialog.Close>
                            <button
                                onClick={handleKill}
                                className="flex-1 p-3 rounded bg-red-600 hover:bg-red-500 text-white font-bold font-mono text-sm shadow-[0_0_20px_rgba(220,38,38,0.5)] transition-all hover:scale-105"
                            >
                                CONFIRM KILL
                            </button>
                        </div>
                    </div>
                </Dialog.Content>
            </Dialog.Portal>
        </Dialog.Root>
    );
}
