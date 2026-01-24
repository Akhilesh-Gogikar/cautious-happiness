"use client";

import { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Send, Bot, User, Sparkles, AlertTriangle, ShieldCheck, Activity } from 'lucide-react';
import { cn } from "@/lib/utils";
import { chatWithModel, streamChat, fetchChatHistory } from '@/lib/api';
import { ThinkingBlock } from '@/components/ui/thinking-block';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    persona?: 'Analyst' | 'RiskManager';
}

interface ChatViewProps {
    context?: string; // The text context (Question)
    contextId?: string; // The ID of the thread/market
}

function parseMessage(content: string) {
    const thinkMatch = content.match(/<think>([\s\S]*?)<\/think>/);
    const thinking = thinkMatch ? thinkMatch[1].trim() : null;

    // If we have an open <think> tag but no close tag yet, treat the rest as thinking
    const openThinkMatch = content.match(/<think>([\s\S]*)$/);
    const incompleteThinking = !thinkMatch && openThinkMatch ? openThinkMatch[1] : null;

    const effectiveThinking = thinking !== null ? thinking : incompleteThinking;

    // Remove the full think block or the open think block from response display
    let response = content.replace(/<think>[\s\S]*?<\/think>/, '');
    response = response.replace(/<think>[\s\S]*$/, '');

    return { thinking: effectiveThinking, response: response };
}

export function ChatView({ context, contextId }: ChatViewProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: "I am the Quant Engine Analyst. Select a trade thread to begin analysis.",
            persona: 'Analyst'
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [tps, setTPS] = useState<number>(0);
    const [selectedAgents, setSelectedAgents] = useState<string[]>(['Analyst']);

    // UI Refs
    const scrollRef = useRef<HTMLDivElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Available Agents
    const agents = [
        { id: 'Researcher', name: 'Info Researcher', icon: Globe, color: 'text-blue-400', desc: 'Scans live web/news data.' },
        { id: 'Analyst', name: 'Data Analyst', icon: Activity, color: 'text-emerald-400', desc: 'Analyzes numbers & correlations.' },
        { id: 'Risk', name: 'Risk Guard', icon: ShieldCheck, color: 'text-indigo-400', desc: 'Identifies downsides & swans.' },
        { id: 'Hunter', name: 'Alpha Hunter', icon: Sparkles, color: 'text-amber-400', desc: 'Seeks high-EV opportunities.' },
    ];

    const toggleAgent = (id: string) => {
        setSelectedAgents(prev =>
            prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
        );
    };

    // Fetch History
    useEffect(() => {
        if (!context) return;

        const loadHistory = async () => {
            setIsLoading(true);
            try {
                const history = await fetchChatHistory(context);
                if (history && history.length > 0) {
                    setMessages(history.map((m: any) => ({
                        role: m.role,
                        content: m.content,
                        persona: 'Analyst'
                    })));
                } else {
                    setMessages([{
                        role: 'assistant',
                        content: `Starting analysis for: "${context}"\n\nI am ready. Select agents to assist me.`,
                        persona: 'Analyst'
                    }]);
                }
            } catch (e) {
                console.error("Failed to load history", e);
            } finally {
                setIsLoading(false);
            }
        };
        loadHistory();
    }, [context]);

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const activeContext = context || "General Market Analysis";
        const userMsg = input;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setIsLoading(true);
        setTPS(0);

        try {
            const stream = await streamChat({
                question: activeContext,
                context: `Context: ${activeContext}`,
                user_message: userMsg,
                selected_agents: selectedAgents
            });

            setMessages(prev => [...prev, { role: 'assistant', content: "", persona: 'Analyst' }]);

            let fullContent = "";
            let tokenCount = 0;
            const startTime = performance.now();

            for await (const chunk of stream()) {
                fullContent += chunk;
                tokenCount++;

                const elapsedSec = (performance.now() - startTime) / 1000;
                if (elapsedSec > 0) {
                    setTPS(Math.round(tokenCount / elapsedSec));
                }

                setMessages(prev => {
                    const newMsgs = [...prev];
                    const lastMsg = newMsgs[newMsgs.length - 1];
                    lastMsg.content = fullContent;
                    return newMsgs;
                });
            }

        } catch (error: any) {
            setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${error.message}`, persona: 'Analyst' }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-black/60 backdrop-blur-md rounded-xl border border-white/10 overflow-hidden relative">
            {/* Header / Agent Selector */}
            <div className="flex-none p-4 border-b border-white/10 bg-white/5 flex flex-col gap-3 shrink-0 z-10">
                <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <Bot className="w-5 h-5 text-primary animate-pulse" />
                        <span className="text-xs font-black tracking-[0.2em] uppercase text-white">
                            QUANT_ENGINE_V2
                        </span>
                    </div>
                    {isLoading && (
                        <div className="flex items-center gap-2 text-[10px] font-mono text-neon-blue animate-pulse">
                            <Activity className="w-3 h-3" />
                            <span>{tps} T/S</span>
                        </div>
                    )}
                </div>

                {/* Agent Toggles */}
                <div className="flex flex-wrap gap-2">
                    {agents.map(agent => (
                        <button
                            key={agent.id}
                            onClick={() => toggleAgent(agent.id)}
                            className={cn(
                                "flex items-center gap-2 px-3 py-1.5 rounded-full text-[10px] font-bold uppercase transition-all border",
                                selectedAgents.includes(agent.id)
                                    ? "bg-white/10 border-white/30 text-white shadow-[0_0_10px_rgba(255,255,255,0.1)]"
                                    : "bg-transparent border-white/5 text-muted-foreground hover:bg-white/5 opacity-60"
                            )}
                        >
                            <agent.icon className={cn("w-3 h-3", selectedAgents.includes(agent.id) ? agent.color : "text-gray-500")} />
                            {agent.name}
                        </button>
                    ))}
                </div>
            </div>

            {/* Messages Area - Flex Grow & Scroll */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar min-h-0 flex flex-col relative z-0">
                {messages.map((m, i) => {
                    const { thinking, response } = parseMessage(m.content);
                    const isLastMessage = i === messages.length - 1;
                    const isThinkingActive = isLoading && isLastMessage && (m.content.includes('<think>') && !m.content.includes('</think>'));

                    return (
                        <div key={i} className={cn("flex w-full gap-4 shrink-0", m.role === 'user' ? "justify-end" : "justify-start")}>
                            {m.role === 'assistant' && (
                                <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0">
                                    <Bot className="w-4 h-4 text-primary" />
                                </div>
                            )}

                            <div className={cn(
                                "max-w-[85%] rounded-lg p-3 text-sm leading-relaxed shadow-lg backdrop-blur-sm",
                                m.role === 'user'
                                    ? "bg-white/10 text-white border border-white/10"
                                    : "bg-black/40 text-gray-200 border border-white/5"
                            )}>
                                {(thinking || isThinkingActive) && (
                                    <ThinkingBlock
                                        content={thinking || ""}
                                        isStreaming={isThinkingActive}
                                    />
                                )}
                                <div className="whitespace-pre-wrap font-sans min-h-[1em]">{response}</div>
                            </div>
                        </div>
                    );
                })}
                <div ref={messagesEndRef} className="h-px shrink-0" />
            </div>

            {/* Input Area - Fixed Bottom */}
            <div className="flex-none p-4 border-t border-white/10 bg-black/40 shrink-0 z-10 w-full relative">
                <div className="flex gap-4">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder={context ? `Analyze "${context.substring(0, 20)}..." with enabled agents` : "Ask market questions..."}
                        className="bg-white/5 border-white/10 text-sm font-mono focus-visible:ring-primary/50 h-10 w-full"
                        autoFocus
                    />
                    <Button size="icon" onClick={handleSend} disabled={isLoading} className="h-10 w-10 bg-primary hover:bg-emerald-400 text-black shrink-0">
                        <Send className="w-4 h-4" />
                    </Button>
                </div>
            </div>
        </div>
    );
}

// Remove the standalone call at the bottom if any
