"use client";

import { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
// import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, X } from 'lucide-react';
import { cn } from "@/lib/utils";
import { chatWithModel } from '@/lib/api';
import { ThinkingBlock } from "@/components/ui/thinking-block";

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

interface ChatPanelProps {
    isOpen: boolean;
    onClose: () => void;
    context: {
        question: string;
        reasoning: string;
        critique: string;
        probability: number;
    };
}

function parseMessage(content: string) {
    const thinkMatch = content.match(/<think>([\s\S]*?)<\/think>/);
    const thinking = thinkMatch ? thinkMatch[1].trim() : null;

    // If we have an open <think> tag but no close tag yet, treat the rest as thinking
    const openThinkMatch = content.match(/<think>([\s\S]*)$/);
    const incompleteThinking = !thinkMatch && openThinkMatch ? openThinkMatch[1].trim() : null;

    const effectiveThinking = thinking || incompleteThinking;

    // Remove the full think block or the open think block from response display
    let response = content.replace(/<think>[\s\S]*?<\/think>/, '');
    response = response.replace(/<think>[\s\S]*$/, '');

    return { thinking: effectiveThinking, response: response.trim() };
}

export function ChatPanel({ isOpen, onClose, context }: ChatPanelProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Initial context message
    useEffect(() => {
        if (isOpen && messages.length === 0) {
            setMessages([
                {
                    role: 'assistant',
                    content: `<think>${context.reasoning}\n\nCritique:\n${context.critique}</think>I've analyzed "${context.question}". What would you like to know about my reasoning?`
                }
            ]);
        }
    }, [isOpen, context]);

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

        try {
            const res = await chatWithModel({
                question: context.question,
                context: `Reasoning: ${context.reasoning}\nCritique: ${context.critique}\nForecast: ${context.probability}`,
                user_message: userMsg
            });

            setMessages(prev => [...prev, { role: 'assistant', content: res.response }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: "Error communicating with the model." }]);
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="absolute right-0 top-0 bottom-0 w-[400px] z-50 animate-in slide-in-from-right duration-300 shadow-2xl">
            <Card className="h-full border-l border-white/10 bg-black/95 backdrop-blur-xl flex flex-col rounded-none">
                <CardHeader className="flex flex-row items-center justify-between py-3 px-4 border-b border-white/10 bg-white/5">
                    <div className="flex items-center gap-2">
                        <Bot className="w-4 h-4 text-neon-blue animate-pulse" />
                        <CardTitle className="text-xs font-black tracking-[0.2em] uppercase text-glow-neon">ORACLE_CHAT</CardTitle>
                    </div>
                    <Button variant="ghost" size="icon" className="h-6 w-6 rounded-full hover:bg-white/10" onClick={onClose}>
                        <X className="w-4 h-4" />
                    </Button>
                </CardHeader>

                <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar" ref={scrollRef}>
                        {messages.map((m, i) => {
                            const { thinking, response } = parseMessage(m.content);
                            return (
                                <div key={i} className={cn("flex w-full", m.role === 'user' ? "justify-end" : "justify-start")}>
                                    <div className={cn(
                                        "max-w-[85%] rounded-lg p-3 text-xs leading-relaxed",
                                        m.role === 'user'
                                            ? "bg-primary/20 text-primary-foreground border border-primary/20"
                                            : "bg-white/5 text-muted-foreground border border-white/10"
                                    )}>
                                        {thinking && <ThinkingBlock content={thinking} />}
                                        <div className="whitespace-pre-wrap font-mono">{response}</div>
                                    </div>
                                </div>
                            );
                        })}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                                    <span className="animate-pulse text-xs font-mono text-neon-blue">THINKING...</span>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="p-4 border-t border-white/10 bg-black/40">
                        <div className="flex gap-2">
                            <Input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                placeholder="Interrogate the reasoning..."
                                className="bg-white/5 border-white/10 text-xs font-mono focus-visible:ring-primary/50"
                            />
                            <Button size="icon" onClick={handleSend} disabled={isLoading} className="bg-primary hover:bg-primary/80 text-black">
                                <Send className="w-4 h-4" />
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
