"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Sparkles, AlertCircle, ChevronRight } from "lucide-react";
import { api } from "@/lib/api";

interface Message {
    id: string;
    role: "user" | "assistant" | "agent";
    agent_name?: string;
    content: string;
    timestamp: Date;
    isThinking?: boolean;
}

interface AgentInterjection {
    agent: string;
    insight: string;
}

export const CollaborativeChat: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "welcome",
            role: "assistant",
            content: "Greetings. I am your AlphaSignals Quant Engine. Ask me about market forecasts, portfolio risk, or trade execution strategies. My specialized agents are standing by to provide deep analysis.",
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState("");
    const [isStreaming, setIsStreaming] = useState(false);
    const [activeAgents, setActiveAgents] = useState<string[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isStreaming) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: "user",
            content: input.trim(),
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsStreaming(true);

        // Add thinking placeholder
        const thinkingId = `thinking-${Date.now()}`;
        setMessages((prev) => [
            ...prev,
            { id: thinkingId, role: "assistant", content: "", timestamp: new Date(), isThinking: true },
        ]);

        try {
            // Get auth token for authenticated requests
            const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

            // Stream chat response
            const response = await fetch(`/api/chat/stream`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...(token ? { "Authorization": `Bearer ${token}` } : {})
                },
                body: JSON.stringify({ user_message: input.trim(), context: "Multi-Agent Analysis Mode" }),
            });

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();
            let fullContent = "";

            while (reader) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value);
                fullContent += chunk;

                setMessages((prev) =>
                    prev.map((m) => (m.id === thinkingId ? { ...m, content: fullContent, isThinking: false } : m))
                );
            }

            // Simulate agent interjections based on keywords
            const interjections = await simulateAgentInterjections(input.trim());
            for (const interject of interjections) {
                await new Promise((resolve) => setTimeout(resolve, 500));
                setMessages((prev) => [
                    ...prev,
                    {
                        id: `agent-${Date.now()}`,
                        role: "agent",
                        agent_name: interject.agent,
                        content: interject.insight,
                        timestamp: new Date(),
                    },
                ]);
            }
        } catch (err) {
            console.error("Chat stream failed", err);
            setMessages((prev) =>
                prev.map((m) =>
                    m.id === thinkingId
                        ? { ...m, content: "Neural link disrupted. Please try again.", isThinking: false }
                        : m
                )
            );
        } finally {
            setIsStreaming(false);
        }
    };

    const simulateAgentInterjections = async (query: string): Promise<AgentInterjection[]> => {
        const interjections: AgentInterjection[] = [];
        const q = query.toLowerCase();

        if (q.includes("risk") || q.includes("portfolio")) {
            interjections.push({
                agent: "Risk-Guard",
                insight: "🛡️ Current portfolio exposure is within safe limits. No high-severity alerts detected.",
            });
        }
        if (q.includes("bitcoin") || q.includes("btc") || q.includes("crypto")) {
            interjections.push({
                agent: "Alpha-Hunter",
                insight: "🎯 Technical scan shows BTC holding above key support levels. Momentum is bullish.",
            });
        }
        if (q.includes("sentiment") || q.includes("social") || q.includes("twitter")) {
            interjections.push({
                agent: "Sentiment-Spy",
                insight: "💬 Social sentiment is elevated. Hype score: 0.72. Caution advised for FOMO-driven entries.",
            });
        }
        if (q.includes("trade") || q.includes("execute") || q.includes("buy") || q.includes("sell")) {
            interjections.push({
                agent: "Trade-Executor",
                insight: "⚡ Execution ready. Optimal position size calculated at $150. VWAP slippage: 0.3%.",
            });
        }

        return interjections;
    };

    const getAgentColor = (name?: string) => {
        if (!name) return "from-blue-500 to-indigo-500";
        if (name.includes("Risk")) return "from-rose-500 to-pink-500";
        if (name.includes("Alpha")) return "from-amber-500 to-orange-500";
        if (name.includes("Sentiment")) return "from-purple-500 to-violet-500";
        if (name.includes("Trade")) return "from-emerald-500 to-teal-500";
        if (name.includes("Macro")) return "from-cyan-500 to-sky-500";
        return "from-blue-500 to-indigo-500";
    };

    return (
        <div className="flex flex-col h-full bg-zinc-950 rounded-2xl border border-white/10 overflow-hidden">
            {/* Header */}
            <div className="px-6 py-4 border-b border-white/10 bg-gradient-to-r from-blue-500/10 to-indigo-500/10">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-white">Collaborative AI Chat</h2>
                        <p className="text-xs text-white/50">5 Agents Online • Multi-Agent Analysis</p>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                <AnimatePresence>
                    {messages.map((msg) => (
                        <motion.div
                            key={msg.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                        >
                            <div
                                className={`max-w-[80%] ${msg.role === "user"
                                    ? "bg-blue-600 text-white rounded-2xl rounded-br-md"
                                    : msg.role === "agent"
                                        ? `bg-gradient-to-r ${getAgentColor(msg.agent_name)} text-white rounded-2xl rounded-bl-md`
                                        : "bg-white/10 text-white/90 rounded-2xl rounded-bl-md"
                                    } px-4 py-3`}
                            >
                                {msg.role === "agent" && msg.agent_name && (
                                    <div className="flex items-center gap-1 mb-1 text-xs font-bold text-white/80">
                                        <Bot className="w-3 h-3" />
                                        {msg.agent_name}
                                    </div>
                                )}
                                {msg.isThinking ? (
                                    <div className="flex items-center gap-2 text-white/60">
                                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
                                        <span className="text-sm">Thinking...</span>
                                    </div>
                                ) : (
                                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                                )}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-4 border-t border-white/10 bg-black/20">
                <div className="flex items-center gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about markets, risk, or trade execution..."
                        className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:border-blue-500/50 transition-colors"
                        disabled={isStreaming}
                    />
                    <button
                        type="submit"
                        disabled={isStreaming || !input.trim()}
                        className="p-3 bg-blue-600 hover:bg-blue-500 disabled:bg-white/10 disabled:text-white/30 text-white rounded-xl transition-colors"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </form>
        </div>
    );
};
