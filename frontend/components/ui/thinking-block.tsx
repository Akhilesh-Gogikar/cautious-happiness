"use client";

import { useState } from 'react';
import { ChevronDown, ChevronRight, BrainCircuit } from 'lucide-react';
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from 'framer-motion';

interface ThinkingBlockProps {
    content: string;
    isStreaming?: boolean;
}

export function ThinkingBlock({ content, isStreaming }: ThinkingBlockProps) {
    const [isExpanded, setIsExpanded] = useState(false);

    if (!content && !isStreaming) return null;

    return (
        <div className="my-2 border border-white/10 rounded-lg overflow-hidden bg-black/20">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center gap-2 p-2 hover:bg-white/5 transition-colors text-left"
            >
                {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-muted-foreground" />
                ) : (
                    <ChevronRight className="w-4 h-4 text-muted-foreground" />
                )}
                <BrainCircuit className={cn("w-4 h-4", isExpanded ? "text-primary" : "text-muted-foreground", isStreaming && !isExpanded && "animate-pulse text-neon-blue")} />
                <span className="text-xs font-mono text-muted-foreground flex items-center gap-2">
                    {isExpanded
                        ? (isStreaming ? "Thinking Process" : "Reasoning Process")
                        : (isStreaming ? <span className="animate-pulse font-bold text-neon-blue">Thinking...</span> : "View Reasoning")
                    }
                    {isStreaming && !isExpanded && (
                        <span className="flex gap-0.5">
                            <span className="w-1 h-1 bg-current rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                            <span className="w-1 h-1 bg-current rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                            <span className="w-1 h-1 bg-current rounded-full animate-bounce"></span>
                        </span>
                    )}
                </span>
            </button>
            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        <div className="p-3 pt-0 border-t border-white/10 bg-black/10">
                            <div className="text-xs text-muted-foreground font-mono whitespace-pre-wrap leading-relaxed opacity-90">
                                {content}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
