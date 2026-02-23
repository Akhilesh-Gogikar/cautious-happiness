
"use client";

import { useState, useRef, useEffect } from 'react';
import { Send, X, MessageSquare, Loader2, Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { chatWithModel, ChatMessage } from '@/lib/api';
import { toast } from 'sonner';

export function SidebarChat() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom of chat
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isOpen]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMsg: ChatMessage = {
            role: 'user',
            content: input.trim(),
            timestamp: Date.now()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            // Get current path for context
            const path = window.location.pathname;

            const response = await chatWithModel({
                question: userMsg.content,
                history: messages,
                context: {
                    route_path: path
                }
            });

            const assistantMsg: ChatMessage = {
                role: 'assistant',
                content: response.response,
                timestamp: Date.now()
            };

            setMessages(prev => [...prev, assistantMsg]);
        } catch (error) {
            toast.error("Failed to get response");
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            {/* Toggle Button */}
            <div className="fixed bottom-6 right-6 z-50">
                <Button
                    onClick={() => setIsOpen(!isOpen)}
                    className={cn(
                        "h-14 w-14 rounded-full shadow-2xl transition-all duration-300",
                        isOpen ? "bg-destructive hover:bg-destructive/90 rotate-90" : "bg-primary hover:bg-primary/90 hover:scale-105"
                    )}
                >
                    {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
                </Button>
            </div>

            {/* Chat Panel */}
            <div
                className={cn(
                    "fixed top-0 right-0 h-full w-[400px] bg-background/95 backdrop-blur-xl border-l border-white/10 z-40 shadow-2xl transition-transform duration-500 ease-in-out flex flex-col",
                    isOpen ? "translate-x-0" : "translate-x-full"
                )}
            >
                {/* Header */}
                <div className="p-4 border-b border-white/10 flex items-center justify-between bg-black/20">
                    <div className="flex items-center gap-2">
                        <Bot className="w-5 h-5 text-primary" />
                        <h2 className="font-bold text-sm tracking-widest text-white">ALPHA_INTELLIGENCE</h2>
                    </div>
                </div>

                {/* Messages Area */}
                <div
                    ref={scrollRef}
                    className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar"
                >
                    {messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-muted-foreground p-8 text-center opacity-50">
                            <Bot className="w-12 h-12 mb-4" />
                            <p className="text-sm">System ready. Awaiting inquiry.</p>
                        </div>
                    )}

                    {messages.map((msg, i) => (
                        <div
                            key={i}
                            className={cn(
                                "flex gap-3 max-w-[90%]",
                                msg.role === 'user' ? "ml-auto flex-row-reverse" : "mr-auto"
                            )}
                        >
                            <div className={cn(
                                "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border",
                                msg.role === 'user' ? "bg-primary/10 border-primary/20 text-primary" : "bg-indigo-500/10 border-indigo-500/20 text-indigo-400"
                            )}>
                                {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                            </div>

                            <div className={cn(
                                "p-3 rounded-lg text-sm border",
                                msg.role === 'user'
                                    ? "bg-primary/10 border-primary/20 text-white rounded-tr-none"
                                    : "bg-white/5 border-white/10 text-gray-300 rounded-tl-none"
                            )}>
                                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex gap-3">
                            <div className="w-8 h-8 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0">
                                <Bot className="w-4 h-4 text-indigo-400" />
                            </div>
                            <div className="bg-white/5 border border-white/10 p-3 rounded-lg rounded-tl-none">
                                <div className="flex gap-1">
                                    <span className="w-1.5 h-1.5 bg-indigo-400/50 rounded-full animate-bounce [animation-delay:-0.3s]" />
                                    <span className="w-1.5 h-1.5 bg-indigo-400/50 rounded-full animate-bounce [animation-delay:-0.15s]" />
                                    <span className="w-1.5 h-1.5 bg-indigo-400/50 rounded-full animate-bounce" />
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-white/10 bg-black/20">
                    <div className="relative">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSend();
                                }
                            }}
                            placeholder="Ask about market data..."
                            className="w-full bg-black/40 border border-white/10 rounded-xl p-3 pr-12 text-sm text-white placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 resize-none h-14 custom-scrollbar"
                        />
                        <Button
                            onClick={handleSend}
                            disabled={isLoading || !input.trim()}
                            size="icon"
                            variant="ghost"
                            className="absolute right-2 top-2 h-10 w-10 hover:bg-primary/10 hover:text-primary transition-colors"
                        >
                            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                        </Button>
                    </div>
                </div>
            </div>

            {/* Backdrop for mobile */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 md:hidden animate-fade-in"
                    onClick={() => setIsOpen(false)}
                />
            )}
        </>
    );
}

// Helper util if not present
// import { type ClassValue, clsx } from 'clsx';
// import { twMerge } from 'tailwind-merge';
// export function cn(...inputs: ClassValue[]) {
//   return twMerge(clsx(inputs));
// }
