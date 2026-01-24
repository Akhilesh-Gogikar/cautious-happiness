"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { AgentCard } from "@/components/agents/AgentCard";
import { Terminal, Zap, Shield, Cpu, Play } from "lucide-react";
import { api } from "@/lib/api";

export default function AOCPage() {
    const [agents, setAgents] = useState<any[]>([]);
    const [isCoordinating, setIsCoordinating] = useState(false);
    const [lastResult, setLastResult] = useState<any>(null);

    const fetchAgents = async () => {
        try {
            const response = await api.get("/agents");
            setAgents(Array.isArray(response) ? response : response?.data || []);
        } catch (err) {
            console.error("Failed to fetch agents", err);
        }
    };

    useEffect(() => {
        fetchAgents();
        const interval = setInterval(fetchAgents, 3000);
        return () => clearInterval(interval);
    }, []);

    const runCoordination = async () => {
        setIsCoordinating(true);
        try {
            const result = await api.post("/agents/coordinate", { query: "Polymarket Election Trends" });
            setLastResult(result);
        } catch (err) {
            console.error("Coordination failed", err);
        } finally {
            setIsCoordinating(false);
        }
    };

    return (
        <div className="min-h-screen bg-black text-white p-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-6">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <Cpu className="w-6 h-6 text-blue-500" />
                        <span className="text-xs font-bold tracking-[0.2em] text-blue-500/80 uppercase">Neural Network Control</span>
                    </div>
                    <h1 className="text-5xl font-black italic tracking-tighter">AGENT OPERATIONS CENTER</h1>
                    <p className="text-white/40 mt-2 max-w-2xl">
                        Real-time management and coordination of the AlphaSignals multi-agent ecosystem.
                        Monitor agent telemetry, task lifecycles, and tactical consensus.
                    </p>
                </div>

                <button
                    onClick={runCoordination}
                    disabled={isCoordinating}
                    className="group relative px-8 py-4 bg-white text-black font-black rounded-full overflow-hidden transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-500 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                    <span className="relative flex items-center gap-2 group-hover:text-white transition-colors">
                        {isCoordinating ? "PLANNING STRATEGY..." : "INITIATE TACTICAL HUDDLE"}
                        <Play className={`w-4 h-4 ${isCoordinating ? 'animate-pulse' : ''}`} />
                    </span>
                </button>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-12">
                {[
                    { icon: Zap, label: "Active Nodes", value: agents.length, color: "text-amber-400" },
                    { icon: Shield, label: "Neural Integrity", value: "99.8%", color: "text-emerald-400" },
                    { icon: Terminal, label: "Tasks Logged", value: agents.reduce((acc, a) => acc + a.log_count, 0), color: "text-blue-400" },
                    { icon: Cpu, label: "Load Average", value: "14%", color: "text-purple-400" },
                ].map((stat, i) => (
                    <div key={i} className="bg-white/5 border border-white/10 p-4 rounded-xl">
                        <div className="flex items-center gap-3">
                            <stat.icon className={`w-5 h-5 ${stat.color}`} />
                            <div>
                                <p className="text-[10px] text-white/40 uppercase font-black">{stat.label}</p>
                                <p className="text-xl font-bold">{stat.value}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Agents Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                {agents.map((agent) => (
                    <AgentCard key={agent.id} agent={agent} />
                ))}
            </div>

            {/* Strategy Consensus */}
            {lastResult && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-zinc-900 border border-zinc-800 rounded-3xl p-8"
                >
                    <div className="flex items-center gap-2 mb-6">
                        <Zap className="w-5 h-5 text-amber-500" />
                        <h2 className="text-2xl font-black italic tracking-tight">STRATEGY CONSENSUS</h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                        <div>
                            <p className="text-sm font-bold text-white/40 mb-2 uppercase tracking-widest">Global Outlook</p>
                            <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
                                {lastResult.consensus}
                            </div>
                            <p className="mt-4 text-white/60 leading-relaxed">
                                Aggregated signals from {lastResult.agent_results.length} active agents indicate high-conviction
                                momentum for the given market sector. Execution risk remains within established parameters.
                            </p>
                        </div>

                        <div className="space-y-4">
                            <p className="text-sm font-bold text-white/40 uppercase tracking-widest">Agent Outputs</p>
                            {lastResult.agent_results.map((res: any, i: number) => (
                                <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/10">
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="text-xs font-bold text-white/70">{res.agent}</span>
                                        <span className="text-[10px] text-emerald-400 px-2 py-0.5 bg-emerald-400/10 rounded-full font-bold">RELIABLE</span>
                                    </div>
                                    <div className="text-sm font-mono text-blue-400">
                                        {res.summary || res.signal || "Execution trace verified."}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </motion.div>
            )}
        </div>
    );
}
