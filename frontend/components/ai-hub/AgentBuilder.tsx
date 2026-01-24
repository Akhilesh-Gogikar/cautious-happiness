"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
    Plus, Cpu, Database, Zap, MessageSquare,
    Check, ChevronRight, Sparkles, Settings,
    Play, Pause, Trash2, Edit2
} from "lucide-react";
import { toast } from "sonner";

interface DataSource {
    id: string;
    name: string;
    type: string;
    icon: string;
}

const availableDataSources: DataSource[] = [
    { id: "binance", name: "Binance", type: "exchange", icon: "₿" },
    { id: "coingecko", name: "CoinGecko", type: "market", icon: "🦎" },
    { id: "yahoo", name: "Yahoo Finance", type: "macro", icon: "📈" },
    { id: "polymarket", name: "Polymarket CLOB", type: "prediction", icon: "🎯" },
    { id: "pgvector", name: "Vector DB (PGVector)", type: "database", icon: "🧠" },
    { id: "chat_history", name: "Chat History", type: "database", icon: "💬" },
];

interface AgentBuilderProps {
    onClose: () => void;
    onSave: (agent: any) => void;
}

export function AgentBuilder({ onClose, onSave }: AgentBuilderProps) {
    const [step, setStep] = useState(1);
    const [name, setName] = useState("");
    const [role, setRole] = useState("analyst");
    const [prompt, setPrompt] = useState("");
    const [selectedSources, setSelectedSources] = useState<string[]>([]);
    const [trigger, setTrigger] = useState("manual");
    const [outputAction, setOutputAction] = useState("chat");

    const toggleSource = (id: string) => {
        setSelectedSources(prev =>
            prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
        );
    };

    const handleCreate = () => {
        if (!name.trim() || !prompt.trim()) {
            toast.error("Please fill in name and prompt");
            return;
        }

        onSave({
            name,
            role,
            system_prompt: prompt,
            data_sources: selectedSources,
            trigger,
            output_action: outputAction,
        });
        toast.success(`Agent "${name}" created successfully!`);
        onClose();
    };

    return (
        <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-xl flex items-center justify-center p-8">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-2xl bg-zinc-900 border border-white/10 rounded-2xl overflow-hidden"
            >
                {/* Header */}
                <div className="p-6 border-b border-white/10 bg-gradient-to-r from-blue-500/10 to-indigo-500/10">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center">
                                <Sparkles className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h2 className="text-lg font-bold text-white">Create New Agent</h2>
                                <p className="text-xs text-white/50">Step {step} of 4</p>
                            </div>
                        </div>
                        <button onClick={onClose} className="text-white/50 hover:text-white transition-colors">
                            ✕
                        </button>
                    </div>

                    {/* Progress */}
                    <div className="flex gap-2 mt-4">
                        {[1, 2, 3, 4].map(s => (
                            <div
                                key={s}
                                className={`flex-1 h-1 rounded-full transition-colors ${s <= step ? 'bg-blue-500' : 'bg-white/10'}`}
                            />
                        ))}
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 min-h-[300px]">
                    {step === 1 && (
                        <div className="space-y-4">
                            <h3 className="text-sm font-bold text-white/60 uppercase tracking-wider">Identity</h3>
                            <div>
                                <label className="text-xs text-white/50 mb-1 block">Agent Name</label>
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="e.g., Alpha Scanner, Risk Monitor..."
                                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-blue-500"
                                />
                            </div>
                            <div>
                                <label className="text-xs text-white/50 mb-1 block">Role</label>
                                <select
                                    value={role}
                                    onChange={(e) => setRole(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                                >
                                    <option value="analyst">Analyst</option>
                                    <option value="monitor">Monitor</option>
                                    <option value="executor">Executor</option>
                                    <option value="sentinel">Sentinel</option>
                                </select>
                            </div>
                        </div>
                    )}

                    {step === 2 && (
                        <div className="space-y-4">
                            <h3 className="text-sm font-bold text-white/60 uppercase tracking-wider">System Prompt</h3>
                            <p className="text-xs text-white/40">Describe what this agent should do in natural language</p>
                            <textarea
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                placeholder="You are an AI agent that monitors Bitcoin price movements. Alert me when BTC moves more than 2% in either direction within an hour. Provide context about potential causes and suggest whether to hold or adjust positions..."
                                className="w-full h-48 bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-blue-500 resize-none"
                            />
                        </div>
                    )}

                    {step === 3 && (
                        <div className="space-y-4">
                            <h3 className="text-sm font-bold text-white/60 uppercase tracking-wider">Data Sources</h3>
                            <p className="text-xs text-white/40">Select which data sources this agent can access</p>
                            <div className="grid grid-cols-2 gap-3">
                                {availableDataSources.map(source => (
                                    <button
                                        key={source.id}
                                        onClick={() => toggleSource(source.id)}
                                        className={`p-4 rounded-xl border text-left transition-all ${selectedSources.includes(source.id)
                                            ? 'bg-blue-500/20 border-blue-500/50 text-white'
                                            : 'bg-white/5 border-white/10 text-white/70 hover:border-white/20'
                                            }`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <span className="text-xl">{source.icon}</span>
                                            <div>
                                                <div className="font-bold text-sm">{source.name}</div>
                                                <div className="text-[10px] text-white/40 uppercase">{source.type}</div>
                                            </div>
                                            {selectedSources.includes(source.id) && (
                                                <Check className="w-4 h-4 text-blue-400 ml-auto" />
                                            )}
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {step === 4 && (
                        <div className="space-y-4">
                            <h3 className="text-sm font-bold text-white/60 uppercase tracking-wider">Behavior</h3>
                            <div>
                                <label className="text-xs text-white/50 mb-2 block">Trigger</label>
                                <div className="grid grid-cols-3 gap-2">
                                    {['manual', 'scheduled', 'event'].map(t => (
                                        <button
                                            key={t}
                                            onClick={() => setTrigger(t)}
                                            className={`p-3 rounded-lg border text-sm capitalize transition-all ${trigger === t
                                                ? 'bg-blue-500/20 border-blue-500/50 text-white'
                                                : 'bg-white/5 border-white/10 text-white/50'
                                                }`}
                                        >
                                            {t}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <label className="text-xs text-white/50 mb-2 block">Output Action</label>
                                <div className="grid grid-cols-3 gap-2">
                                    {['chat', 'alert', 'signal'].map(a => (
                                        <button
                                            key={a}
                                            onClick={() => setOutputAction(a)}
                                            className={`p-3 rounded-lg border text-sm capitalize transition-all ${outputAction === a
                                                ? 'bg-blue-500/20 border-blue-500/50 text-white'
                                                : 'bg-white/5 border-white/10 text-white/50'
                                                }`}
                                        >
                                            {a === 'chat' ? '💬 ' : a === 'alert' ? '🔔 ' : '📊 '}{a}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Summary */}
                            <div className="mt-6 p-4 bg-white/5 rounded-xl border border-white/10">
                                <h4 className="text-xs font-bold text-white/60 uppercase mb-2">Summary</h4>
                                <div className="space-y-1 text-sm">
                                    <p><span className="text-white/40">Name:</span> <span className="text-white">{name || '—'}</span></p>
                                    <p><span className="text-white/40">Role:</span> <span className="text-white capitalize">{role}</span></p>
                                    <p><span className="text-white/40">Sources:</span> <span className="text-white">{selectedSources.length} connected</span></p>
                                    <p><span className="text-white/40">Trigger:</span> <span className="text-white capitalize">{trigger}</span></p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-white/10 flex justify-between">
                    <button
                        onClick={() => step > 1 ? setStep(step - 1) : onClose()}
                        className="px-4 py-2 text-white/50 hover:text-white transition-colors"
                    >
                        {step > 1 ? 'Back' : 'Cancel'}
                    </button>
                    <button
                        onClick={() => step < 4 ? setStep(step + 1) : handleCreate()}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg transition-colors flex items-center gap-2"
                    >
                        {step < 4 ? 'Next' : 'Create Agent'}
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
            </motion.div>
        </div>
    );
}
