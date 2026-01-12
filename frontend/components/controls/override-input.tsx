'use client';

import React, { useState } from 'react';
import { Send, CornerDownLeft, AlertCircle } from 'lucide-react';

export function OverrideInput() {
    const [input, setInput] = useState('');
    const [isSending, setIsSending] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        setIsSending(true);
        // Simulate API call
        setTimeout(() => {
            console.log("Injecting axiom:", input);
            setInput('');
            setIsSending(false);
        }, 1000);
    };

    return (
        <div className="mt-4 p-4 rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 p-2 opacity-10">
                <CornerDownLeft className="w-24 h-24" />
            </div>

            <h3 className="text-white/50 text-xs font-mono uppercase tracking-wider mb-2 flex items-center gap-2">
                <AlertCircle className="w-3 h-3 text-purple-400" />
                Axiom Injection (Override)
            </h3>

            <form onSubmit={handleSubmit} className="relative">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ex: Assume inflation data is delayed by 24h..."
                    className="w-full bg-black/40 border border-white/10 rounded-lg py-3 pl-4 pr-12 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-purple-500/50 transition-colors"
                    disabled={isSending}
                />
                <button
                    type="submit"
                    disabled={!input.trim() || isSending}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-md bg-purple-500/20 text-purple-300 hover:bg-purple-500 hover:text-white disabled:opacity-50 disabled:hover:bg-purple-500/20 transition-all"
                >
                    <Send className="w-3 h-3" />
                </button>
            </form>
            <p className="text-[9px] text-white/30 mt-2 ml-1">
                * This will force a recalculation of all probabilistic models based on your input.
            </p>
        </div>
    );
}
