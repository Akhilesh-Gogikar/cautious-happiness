"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Bot, MessageSquare, X, ChevronUp, ChevronDown,
    Activity, Zap, Send, Sparkles
} from "lucide-react";
import { api } from "@/lib/api";

interface AgentStatus {
    id: string;
    name: string;
    role: string;
    status: string;
}

export function FloatingAgentPanel() {
    const [isExpanded, setIsExpanded] = useState(false);
    const [agents, setAgents] = useState<AgentStatus[]>([]);
    const [chatInput, setChatInput] = useState("");
    const [isAsking, setIsAsking] = useState(false);
    const [lastResponse, setLastResponse] = useState<string | null>(null);

    useEffect(() => {
        const fetchAgents = async () => {
            try {
                // Fetch built-in agents
                const response = await api.get("/agents");
                const data = Array.isArray(response) ? response : response?.data || [];

                // Fetch custom agents
                const customResponse = await api.get("/agents/custom");
                const customData = Array.isArray(customResponse) ? customResponse : customResponse?.data || [];

                // Map custom agents to shared status format
                const customFormatted = customData.map((a: any) => ({
                    id: `custom-${a.id}`,
                    name: a.name,
                    role: a.role,
                    status: a.is_active ? "IDLE" : "PAUSED"
                }));

                setAgents([...data, ...customFormatted]);
            } catch (err) {
                // Silently fail - panel is optional
            }
        };

        fetchAgents();
        const interval = setInterval(fetchAgents, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleQuickAsk = async () => {
        if (!chatInput.trim() || isAsking) return;

        setIsAsking(true);
        setLastResponse(null);

        try {
            const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                },
                body: JSON.stringify({
                    user_message: chatInput.trim(),
                    context: "Quick agent query"
                })
            });

            if (response.ok) {
                const reader = response.body?.getReader();
                const decoder = new TextDecoder();
                let fullResponse = "";

                if (reader) {
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        fullResponse += decoder.decode(value);
                    }
                }

                setLastResponse(fullResponse || "Agent response received.");
            } else {
                setLastResponse("Unable to reach agents.");
            }
        } catch (err) {
            setLastResponse("Connection error.");
        } finally {
            setIsAsking(false);
            setChatInput("");
        }
    };

    const activeCount = agents.filter(a => a.status === "BUSY").length;

    return (
        <div className="fixed bottom-4 right-4 z-50">
            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        className="mb-3 w-80 bg-black/95 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl"
                    >
                        {/* Header */}
                        <div className="p-4 border-b border-white/10 bg-gradient-to-r from-blue-500/10 to-indigo-500/10">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Sparkles className="w-4 h-4 text-blue-400" />
                                    <span className="text-sm font-bold text-white">AI Agents</span>
                                </div>
                                <button
                                    onClick={() => setIsExpanded(false)}
                                    className="text-white/50 hover:text-white transition-colors"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        </div>

                        {/* Agent List */}
                        <div className="p-3 max-h-48 overflow-y-auto space-y-2">
                            {agents.slice(0, 5).map(agent => (
                                <div
                                    key={agent.id}
                                    className="flex items-center justify-between p-2 bg-white/5 rounded-lg"
                                >
                                    <div className="flex items-center gap-2">
                                        <div className={`w-2 h-2 rounded-full ${agent.status === 'BUSY' ? 'bg-blue-500 animate-pulse' :
                                            agent.status === 'COMPLETED' ? 'bg-emerald-500' :
                                                'bg-white/30'
                                            }`} />
                                        <span className="text-xs font-medium text-white">{agent.name}</span>
                                    </div>
                                    <span className="text-[10px] text-white/40 uppercase">{agent.status}</span>
                                </div>
                            ))}
                            {agents.length === 0 && (
                                <div className="text-center text-white/40 text-xs py-4">
                                    No agents running
                                </div>
                            )}
                        </div>

                        {/* Quick Chat */}
                        <div className="p-3 border-t border-white/10">
                            {lastResponse && (
                                <div className="mb-3 p-2 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                                    <p className="text-xs text-blue-200 line-clamp-3">{lastResponse}</p>
                                </div>
                            )}
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={chatInput}
                                    onChange={(e) => setChatInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleQuickAsk()}
                                    placeholder="Quick ask..."
                                    className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-white/30 focus:outline-none focus:border-blue-500"
                                />
                                <button
                                    onClick={handleQuickAsk}
                                    disabled={isAsking || !chatInput.trim()}
                                    className="p-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-lg transition-colors"
                                >
                                    {isAsking ? (
                                        <Activity className="w-4 h-4 text-white animate-spin" />
                                    ) : (
                                        <Send className="w-4 h-4 text-white" />
                                    )}
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Toggle Button */}
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-500/30 flex items-center justify-center relative"
            >
                <Bot className="w-6 h-6 text-white" />

                {/* Activity indicator */}
                {activeCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center text-[10px] font-bold text-white animate-pulse">
                        {activeCount}
                    </span>
                )}
            </motion.button>
        </div>
    );
}
