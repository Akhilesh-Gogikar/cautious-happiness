'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Brain, Terminal, ChevronDown, Activity, GripVertical } from 'lucide-react';
import { cn } from '@/lib/utils';

export type LogLevel = 'INFO' | 'WARNING' | 'CRITICAL' | 'SUCCESS' | 'DEBUG';

export interface ThoughtLog {
    id: string;
    timestamp: string;
    module: string;
    message: string;
    level: LogLevel;
    details?: Record<string, any>;
}

interface ReasoningStreamProps {
    initialLogs?: ThoughtLog[];
    isConnected?: boolean;
}

export function ReasoningStream({ initialLogs = [], isConnected = true }: ReasoningStreamProps) {
    const [logs, setLogs] = useState<ThoughtLog[]>(initialLogs);
    const scrollRef = useRef<HTMLDivElement>(null);
    const [autoScroll, setAutoScroll] = useState(true);

    // Mock data generator for demo purposes if no real implementation yet
    useEffect(() => {
        const interval = setInterval(() => {
            const newLog: ThoughtLog = {
                id: Math.random().toString(36).substring(7),
                timestamp: new Date().toLocaleTimeString(),
                module: ['SENTIMENT', 'RISK', 'MACRO', 'EXECUTION'][Math.floor(Math.random() * 4)],
                message: [
                    'Scanning for arbitrage opportunities...',
                    'Detected 0.5% drift in AlphaSignals vs Kalshi.',
                    'Sentiment analysis indicates hawkish Fed tone.',
                    'Risk limits check passed. Awaiting execution trigger.',
                    'Latency spike detected in data feed (150ms).',
                ][Math.floor(Math.random() * 5)],
                level: ['INFO', 'INFO', 'WARNING', 'SUCCESS', 'DEBUG'][Math.floor(Math.random() * 5)] as LogLevel,
            };

            setLogs(prev => [...prev.slice(-50), newLog]); // Keep last 50
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (autoScroll && scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs, autoScroll]);

    const handleScroll = () => {
        if (!scrollRef.current) return;
        const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
        if (scrollHeight - scrollTop - clientHeight > 50) {
            setAutoScroll(false);
        } else {
            setAutoScroll(true);
        }
    };

    return (
        <div className="flex flex-col h-full bg-black/40 text-xs font-mono border-r border-white/10">
            {/* Header */}
            <div className="flex items-center justify-between p-3 border-b border-white/10 bg-white/5 backdrop-blur-md">
                <div className="flex items-center gap-2">
                    <Brain className="w-4 h-4 text-emerald-500" />
                    <span className="font-bold text-emerald-100 tracking-wider">NEURAL_STREAM</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className={cn("w-2 h-2 rounded-full animate-pulse", isConnected ? "bg-emerald-500" : "bg-red-500")}></span>
                    <span className="text-[10px] text-white/50">{isConnected ? "LIVE" : "OFFLINE"}</span>
                </div>
            </div>

            {/* Stream Window */}
            <div
                ref={scrollRef}
                onScroll={handleScroll}
                className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar"
            >
                {logs.map((log) => (
                    <div
                        key={log.id}
                        className={cn(
                            "group relative p-2 rounded border border-transparent hover:border-white/10 hover:bg-white/5 transition-all animate-fade-in",
                            log.level === 'CRITICAL' && "bg-red-500/10 border-red-500/30 text-red-200",
                            log.level === 'SUCCESS' && "bg-emerald-500/10 border-emerald-500/30 text-emerald-200",
                            log.level === 'WARNING' && "bg-yellow-500/5 text-yellow-200",
                            log.level === 'INFO' && "text-blue-100",
                            log.level === 'DEBUG' && "text-gray-500"
                        )}
                    >
                        <div className="flex items-baseline gap-2">
                            <span className="opacity-30 whitespace-nowrap text-[10px]">{log.timestamp}</span>
                            <span className={cn(
                                "font-bold px-1 rounded text-[10px]",
                                log.level === 'CRITICAL' ? "bg-red-500 text-black" :
                                    log.level === 'WARNING' ? "bg-yellow-500 text-black" :
                                        log.level === 'SUCCESS' ? "text-emerald-400" :
                                            "text-blue-400"
                            )}>
                                [{log.module}]
                            </span>
                            <span className="flex-1 leading-relaxed break-words opacity-90">{log.message}</span>
                        </div>

                        {/* Context/Why tooltip trigger */}
                        <div className="hidden group-hover:flex absolute right-2 top-2 gap-1">
                            <button className="p-1 hover:bg-white/10 rounded" title="Explain Why">
                                <Activity className="w-3 h-3 text-white/50" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Auto-scroll indicator */}
            {!autoScroll && (
                <div
                    onClick={() => { setAutoScroll(true); scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' }); }}
                    className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-blue-500/90 text-white px-3 py-1 rounded-full shadow-lg cursor-pointer hover:bg-blue-400 transition-colors flex items-center gap-1 z-10 backdrop-blur-sm"
                >
                    <ChevronDown className="w-3 h-3" />
                    <span>Resume Stream</span>
                </div>
            )}
        </div>
    );
}
