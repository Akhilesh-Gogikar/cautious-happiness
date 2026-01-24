"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, CheckCircle, AlertCircle, Loader2, Brain, ChevronDown, ChevronUp } from "lucide-react";

interface AgentProps {
    agent: {
        id: string;
        name: string;
        role: string;
        status: string;
        current_task?: string;
        log_count: number;
        last_thought?: string;
    };
}

export const AgentCard: React.FC<AgentProps> = ({ agent }) => {
    const [showThoughts, setShowThoughts] = useState(false);

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "COMPLETED":
                return <CheckCircle className="w-5 h-5 text-emerald-400" />;
            case "BUSY":
                return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
            case "ERROR":
                return <AlertCircle className="w-5 h-5 text-rose-400" />;
            default:
                return <Activity className="w-5 h-5 text-gray-400" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "COMPLETED": return "border-emerald-500/30 bg-gradient-to-br from-emerald-500/10 to-emerald-500/5";
            case "BUSY": return "border-blue-500/30 bg-gradient-to-br from-blue-500/10 to-blue-500/5";
            case "ERROR": return "border-rose-500/30 bg-gradient-to-br from-rose-500/10 to-rose-500/5";
            default: return "border-white/10 bg-gradient-to-br from-white/5 to-transparent";
        }
    };

    const getAgentIcon = (name: string) => {
        if (name.includes("Alpha")) return "🎯";
        if (name.includes("Macro")) return "🌍";
        if (name.includes("Sentiment")) return "💬";
        if (name.includes("Risk")) return "🛡️";
        if (name.includes("Trade") || name.includes("Executor")) return "⚡";
        return "🤖";
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`rounded-2xl border backdrop-blur-xl transition-all duration-300 hover:scale-[1.02] ${getStatusColor(agent.status)}`}
        >
            <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-3">
                        <span className="text-2xl">{getAgentIcon(agent.name)}</span>
                        <div>
                            <h3 className="text-lg font-bold text-white tracking-tight">{agent.name}</h3>
                            <p className="text-xs font-medium text-white/50 uppercase tracking-widest">{agent.role}</p>
                        </div>
                    </div>
                    {getStatusIcon(agent.status)}
                </div>

                <div className="space-y-4">
                    <div>
                        <p className="text-[10px] text-white/30 uppercase font-bold mb-1">Current Task</p>
                        <div className="text-sm text-white/90 font-mono line-clamp-2 min-h-[40px]">
                            {agent.current_task || "Standby - Waiting for command"}
                        </div>
                    </div>

                    <div className="flex items-center justify-between text-xs">
                        <span className="text-white/40">Operation Logs</span>
                        <span className="px-2 py-0.5 rounded-full bg-white/10 text-white/60">{agent.log_count} pts</span>
                    </div>

                    <div className="w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{
                                width: agent.status === "BUSY" ? "60%" : agent.status === "COMPLETED" ? "100%" : "0%",
                            }}
                            transition={{ duration: 0.5, ease: "easeOut" }}
                            className={`h-full ${agent.status === "ERROR" ? "bg-rose-500" : agent.status === "COMPLETED" ? "bg-emerald-500" : "bg-blue-500"}`}
                        />
                    </div>
                </div>
            </div>

            {/* Thought Reflection Panel */}
            <div className="border-t border-white/10">
                <button
                    onClick={() => setShowThoughts(!showThoughts)}
                    className="w-full px-6 py-3 flex items-center justify-between text-xs text-white/50 hover:text-white/70 transition-colors"
                >
                    <div className="flex items-center gap-2">
                        <Brain className="w-3 h-3" />
                        <span className="uppercase font-bold tracking-widest">Thought Reflection</span>
                    </div>
                    {showThoughts ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>

                <AnimatePresence>
                    {showThoughts && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="overflow-hidden"
                        >
                            <div className="px-6 pb-4">
                                <div className="bg-black/30 rounded-lg p-3 text-xs font-mono text-white/60 leading-relaxed max-h-32 overflow-y-auto">
                                    {agent.last_thought || (
                                        <span className="text-white/30 italic">
                                            Agent internal reasoning will appear here during active operations...
                                        </span>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </motion.div>
    );
};
