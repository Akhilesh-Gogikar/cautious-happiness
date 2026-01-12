"use client";

import { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Send, Bot, User, Sparkles, AlertTriangle, ShieldCheck, Activity } from 'lucide-react';
import { cn } from "@/lib/utils";
import { chatWithModel, streamChat } from '@/lib/api';
import { ThinkingBlock } from '@/components/ui/thinking-block';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    persona?: 'Analyst' | 'RiskManager';
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

    // Only trim the final response if we are not actively streaming an open think block
    // Actually, it's safer to just not trim here and let the CSS/rendering handle it,
    // but a leading trim is usually fine for the very start of the message.
    return { thinking: effectiveThinking, response: response };
}

export function ChatView() {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: "I am the Quant Engine Analyst. I can discuss market trends, specific assets, or explain my previous forecasts. What's on your mind?",
            persona: 'Analyst'
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [tps, setTPS] = useState<number>(0);
    const [persona, setPersona] = useState<'Analyst' | 'RiskManager'>('Analyst');
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMsg = input;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setIsLoading(true);
        setTPS(0);

        try {
            let context = "General Market Discussion.";
            if (persona === 'RiskManager') {
                context = "You are a conservative Risk Manager. Focus on downside protection, variance, and black swan events. Be skeptical.";
            } else {
                context = "You are an aggressive Alpha Seeker. Focus on asymmetric upside, potential catalysts, and 'moonshots'.";
            }

            const stream = await streamChat({
                question: "General Chat",
                context: context,
                user_message: userMsg
            });

            setMessages(prev => [...prev, { role: 'assistant', content: "", persona }]);

            let fullContent = "";
            let tokenCount = 0;
            const startTime = performance.now();

            for await (const chunk of stream()) {
                fullContent += chunk;
                tokenCount++;

                // Update TPS roughly every 10 tokens or 500ms to avoid too many renders if needed
                // But specifically requested TPS display, so we update it.
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
            setMessages(prev => {
                const newMsgs = [...prev];
                const errorContent = `Error communicating with the neural core: ${error.message || 'Unknown Error'}`;
                // Check if we already added a message slot
                if (newMsgs[newMsgs.length - 1].role === 'assistant' && newMsgs[newMsgs.length - 1].content === "") {
                    newMsgs[newMsgs.length - 1].content = errorContent;
                } else {
                    newMsgs.push({ role: 'assistant', content: errorContent, persona });
                }
                return newMsgs;
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="h-[calc(100vh-140px)] grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Sidebar / Persona Selector */}
            <div className="lg:col-span-1 space-y-4">
                <Card className="glass-panel border-white/10 bg-black/40 h-full">
                    <CardHeader className="border-b border-white/5 pb-4">
                        <CardTitle className="text-xs font-black tracking-widest text-muted-foreground uppercase">PERSONA_SELECT</CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 space-y-4">
                        <button
                            onClick={() => setPersona('Analyst')}
                            className={cn(
                                "w-full text-left p-4 rounded-lg border transition-all relative overflow-hidden group",
                                persona === 'Analyst'
                                    ? "bg-primary/10 border-primary/40 text-primary"
                                    : "bg-white/5 border-white/10 text-muted-foreground hover:bg-white/10"
                            )}
                        >
                            <div className="flex items-center gap-3 mb-2">
                                <Sparkles className="w-5 h-5" />
                                <span className="font-bold font-mono tracking-wider text-sm">ALPHA_SEEKER</span>
                            </div>
                            <p className="text-[10px] opacity-80 leading-relaxed">
                                Optimistic. Looks for growth, catalysts, and high-EV opportunities.
                            </p>
                        </button>

                        <button
                            onClick={() => setPersona('RiskManager')}
                            className={cn(
                                "w-full text-left p-4 rounded-lg border transition-all relative overflow-hidden group",
                                persona === 'RiskManager'
                                    ? "bg-indigo/10 border-indigo/40 text-indigo"
                                    : "bg-white/5 border-white/10 text-muted-foreground hover:bg-white/10"
                            )}
                        >
                            <div className="flex items-center gap-3 mb-2">
                                <ShieldCheck className="w-5 h-5" />
                                <span className="font-bold font-mono tracking-wider text-sm">RISK_GUARD</span>
                            </div>
                            <p className="text-[10px] opacity-80 leading-relaxed">
                                Pessimistic. Focuses on capital preservation, hedging, and tail risks.
                            </p>
                        </button>
                    </CardContent>
                </Card>
            </div>

            {/* Chat Area */}
            <div className="lg:col-span-3">
                <Card className="glass-panel border-white/10 bg-black/60 h-full flex flex-col relative overflow-hidden">
                    {/* Header */}
                    <CardHeader className="py-3 px-6 border-b border-white/10 bg-white/5 flex flex-row items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Bot className={cn("w-5 h-5 animate-pulse", persona === 'Analyst' ? "text-primary" : "text-indigo")} />
                            <span className="text-sm font-black tracking-[0.2em] text-white uppercase">
                                {persona === 'Analyst' ? 'QUANT_ANALYST_AGENT' : 'RISK_MANAGEMENT_CORE'}
                            </span>
                        </div>
                        <div className="flex items-center gap-4">
                            {isLoading && (
                                <div className="flex items-center gap-2 text-[10px] font-mono text-neon-blue animate-pulse">
                                    <Activity className="w-3 h-3" />
                                    <span>{tps} TOKENS/SEC</span>
                                </div>
                            )}
                            <div className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[10px] font-mono text-muted-foreground">
                                model: <span className="text-white">OpenForecaster (Local)</span>
                            </div>
                        </div>
                    </CardHeader>

                    {/* Messages */}
                    <CardContent className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar" ref={scrollRef}>
                        {messages.map((m, i) => {
                            const { thinking, response } = parseMessage(m.content);
                            const isLastMessage = i === messages.length - 1;
                            const isThinkingActive = isLoading && isLastMessage && (m.content.includes('<think>') && !m.content.includes('</think>'));

                            return (
                                <div key={i} className={cn("flex w-full gap-4", m.role === 'user' ? "justify-end" : "justify-start")}>
                                    {m.role === 'assistant' && (
                                        <div className={cn(
                                            "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border",
                                            m.persona === 'Analyst'
                                                ? "bg-primary/10 border-primary/30 text-primary"
                                                : "bg-indigo/10 border-indigo/30 text-indigo"
                                        )}>
                                            <Bot className="w-4 h-4" />
                                        </div>
                                    )}

                                    <div className={cn(
                                        "max-w-[75%] rounded-lg p-4 text-sm leading-relaxed shadow-lg backdrop-blur-sm",
                                        m.role === 'user'
                                            ? "bg-white/10 text-white border border-white/10"
                                            : m.persona === 'Analyst'
                                                ? "bg-primary/5 text-gray-200 border border-primary/20"
                                                : "bg-indigo/5 text-gray-200 border border-indigo/20"
                                    )}>
                                        {(thinking || isThinkingActive) && (
                                            <ThinkingBlock
                                                content={thinking || ""}
                                                isStreaming={isThinkingActive}
                                            />
                                        )}
                                        <div className="whitespace-pre-wrap font-sans min-h-[1.5em]">{response}</div>
                                    </div>

                                    {m.role === 'user' && (
                                        <div className="w-8 h-8 rounded-full bg-white/10 border border-white/20 flex items-center justify-center shrink-0 text-white">
                                            <User className="w-4 h-4" />
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </CardContent>

                    {/* Input */}
                    <div className="p-4 border-t border-white/10 bg-black/40">
                        <div className="flex gap-4 max-w-4xl mx-auto">
                            <Input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                placeholder={`Ask the ${persona === 'Analyst' ? 'Analyst' : 'Risk Manager'}...`}
                                className="bg-white/5 border-white/10 text-sm font-mono focus-visible:ring-primary/50 h-12"
                                autoFocus
                            />
                            <Button size="icon" onClick={handleSend} disabled={isLoading} className={cn(
                                "h-12 w-12 text-black transition-all",
                                persona === 'Analyst' ? "bg-primary hover:bg-emerald-400" : "bg-indigo text-white hover:bg-indigo-400"
                            )}>
                                <Send className="w-5 h-5" />
                            </Button>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
}

