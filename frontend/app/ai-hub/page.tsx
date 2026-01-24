"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { DashboardLayout } from "@/components/layout";
import { AgentCard } from "@/components/agents/AgentCard";
import { AgentBuilder } from "@/components/ai-hub";
import { CollaborativeChat } from "@/components/ai/CollaborativeChat";
import {
    Cpu, Zap, Shield, Terminal, Activity,
    MessageSquare, BarChart2, Plus, Play,
    Pause, Settings, Bot
} from "lucide-react";
import { api } from "@/lib/api";

interface CustomAgent {
    id: string;
    name: string;
    role: string;
    status: string;
    is_active: boolean;
    data_sources: string[];
}

function AIHubContent() {
    const [agents, setAgents] = useState<any[]>([]);
    const [customAgents, setCustomAgents] = useState<CustomAgent[]>([]);
    const [view, setView] = useState<"agents" | "chat">("agents");
    const [isCoordinating, setIsCoordinating] = useState(false);
    const [lastResult, setLastResult] = useState<any>(null);
    const [showBuilder, setShowBuilder] = useState(false);

    const fetchAgents = async () => {
        try {
            // Fetch built-in agents
            const response = await api.get("/agents");
            setAgents(Array.isArray(response) ? response : response?.data || []);

            // Fetch custom agents
            const customResponse = await api.get("/agents/custom");
            setCustomAgents(Array.isArray(customResponse) ? customResponse : customResponse?.data || []);
        } catch (err) {
            console.error("Failed to fetch agents", err);
        }
    };

    useEffect(() => {
        fetchAgents();
        const interval = setInterval(fetchAgents, 5000);
        return () => clearInterval(interval);
    }, []);

    const runCoordination = async () => {
        setIsCoordinating(true);
        try {
            const result = await api.post("/agents/coordinate", {
                query: "Current Market Outlook and Opportunities"
            });
            setLastResult(result);
        } catch (err) {
            console.error("Coordination failed", err);
        } finally {
            setIsCoordinating(false);
        }
    };

    const handleSaveAgent = async (agentData: any) => {
        try {
            await api.post("/agents/custom", agentData);
            // Refresh list
            fetchAgents();
        } catch (e) {
            console.error("Failed to create agent", e);
        }
    };

    const activeCount = agents.filter(a => a.status === "BUSY").length;
    const completedCount = agents.filter(a => a.status === "COMPLETED").length;

    return (
        <div className="p-6 space-y-6">
            {/* Agent Builder Modal */}
            {showBuilder && (
                <AgentBuilder
                    onClose={() => setShowBuilder(false)}
                    onSave={handleSaveAgent}
                />
            )}

            {/* Top Actions Bar */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 bg-white/5 rounded-full p-1 border border-white/10">
                    <button
                        onClick={() => setView("agents")}
                        className={`px-4 py-2 rounded-full text-sm font-bold transition-all ${view === "agents"
                            ? "bg-white text-black"
                            : "text-white/60 hover:text-white"
                            }`}
                    >
                        <div className="flex items-center gap-2">
                            <Bot className="w-4 h-4" />
                            Agents
                        </div>
                    </button>
                    <button
                        onClick={() => setView("chat")}
                        className={`px-4 py-2 rounded-full text-sm font-bold transition-all ${view === "chat"
                            ? "bg-white text-black"
                            : "text-white/60 hover:text-white"
                            }`}
                    >
                        <div className="flex items-center gap-2">
                            <MessageSquare className="w-4 h-4" />
                            Chat
                        </div>
                    </button>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={() => setShowBuilder(true)}
                        className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors flex items-center gap-2 border border-white/10"
                    >
                        <Plus className="w-4 h-4" />
                        New Agent
                    </button>
                    <button
                        onClick={runCoordination}
                        disabled={isCoordinating}
                        className="px-6 py-2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white font-bold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2"
                    >
                        {isCoordinating ? (
                            <>
                                <Activity className="w-4 h-4 animate-spin" />
                                Running...
                            </>
                        ) : (
                            <>
                                <Play className="w-4 h-4" />
                                Coordinate All
                            </>
                        )}
                    </button>
                </div>
            </div>

            {view === "agents" ? (
                <>
                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            { icon: Zap, label: "Total Agents", value: agents.length + customAgents.length, color: "text-amber-400", bg: "from-amber-500/20" },
                            { icon: Activity, label: "Active Now", value: activeCount, color: "text-blue-400", bg: "from-blue-500/20" },
                            { icon: Shield, label: "Completed", value: completedCount, color: "text-emerald-400", bg: "from-emerald-500/20" },
                            { icon: Terminal, label: "Total Logs", value: agents.reduce((acc, a) => acc + (a.log_count || 0), 0), color: "text-purple-400", bg: "from-purple-500/20" },
                        ].map((stat, i) => (
                            <div
                                key={i}
                                className={`bg-gradient-to-br ${stat.bg} to-transparent border border-white/10 p-5 rounded-xl`}
                            >
                                <div className="flex items-center gap-3">
                                    <stat.icon className={`w-6 h-6 ${stat.color}`} />
                                    <div>
                                        <p className="text-[10px] text-white/40 uppercase font-black tracking-widest">{stat.label}</p>
                                        <p className="text-2xl font-black">{stat.value}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Custom Agents Section */}
                    {customAgents.length > 0 && (
                        <div>
                            <h2 className="text-sm font-black uppercase tracking-widest text-muted-foreground mb-4 flex items-center gap-2">
                                <Zap className="w-4 h-4 text-amber-500" />
                                Your Custom Agents
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {customAgents.map((agent) => (
                                    <div
                                        key={agent.id}
                                        className="bg-white/5 border border-white/10 rounded-xl p-4 hover:border-primary/30 transition-colors"
                                    >
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center gap-2">
                                                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
                                                    <Bot className="w-4 h-4 text-white" />
                                                </div>
                                                <div>
                                                    <h3 className="font-bold text-white">{agent.name}</h3>
                                                    <p className="text-[10px] text-white/40 uppercase">{agent.role}</p>
                                                </div>
                                            </div>
                                            <div className={`w-2 h-2 rounded-full ${agent.is_active ? 'bg-emerald-500' : 'bg-white/20'}`} />
                                        </div>
                                        <div className="flex items-center gap-2 text-xs text-white/50">
                                            <span>{agent.data_sources.length} data sources</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Built-in Agents Grid */}
                    <div>
                        <h2 className="text-sm font-black uppercase tracking-widest text-muted-foreground mb-4 flex items-center gap-2">
                            <Cpu className="w-4 h-4 text-blue-500" />
                            System Agents
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {agents.map((agent) => (
                                <AgentCard key={agent.id} agent={agent} />
                            ))}
                        </div>
                    </div>

                    {/* Consensus Result */}
                    {lastResult && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bg-white/5 border border-white/10 rounded-xl p-6"
                        >
                            <div className="flex items-center gap-2 mb-4">
                                <Zap className="w-5 h-5 text-amber-500" />
                                <h2 className="text-lg font-black">STRATEGY CONSENSUS</h2>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div>
                                    <p className="text-xs font-bold text-white/40 mb-2 uppercase tracking-widest">Global Outlook</p>
                                    <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
                                        {lastResult.data?.consensus || lastResult.consensus || "N/A"}
                                    </div>
                                    <p className="mt-4 text-white/60 text-sm">
                                        Aggregated signals from {(lastResult.data?.agent_results || lastResult.agent_results)?.length || 0} active agents.
                                    </p>
                                </div>

                                <div className="space-y-2">
                                    <p className="text-xs font-bold text-white/40 uppercase tracking-widest">Agent Outputs</p>
                                    {(lastResult.data?.agent_results || lastResult.agent_results)?.map((res: any, i: number) => (
                                        <div key={i} className="p-3 bg-white/5 rounded-lg border border-white/10">
                                            <div className="flex justify-between items-center mb-1">
                                                <span className="text-xs font-bold text-white/70">{res.agent}</span>
                                                <span className="text-[10px] text-emerald-400 px-2 py-0.5 bg-emerald-400/10 rounded-full font-bold">
                                                    {res.status || "OK"}
                                                </span>
                                            </div>
                                            <div className="text-sm font-mono text-blue-400 truncate">
                                                {res.summary || res.signal || res.verdict || res.mood_summary || `$${res.size_usd?.toFixed(2) || "0.00"}`}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    )}
                </>
            ) : (
                /* Chat View */
                <div className="h-[calc(100vh-280px)]">
                    <CollaborativeChat />
                </div>
            )}
        </div>
    );
}

export default function AIHubPage() {
    return (
        <DashboardLayout title="AI HUB" subtitle="NEURAL_NETWORK_ONLINE" icon={Cpu}>
            <AIHubContent />
        </DashboardLayout>
    );
}
