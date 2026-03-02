"use client";

import { useState, useRef, useEffect } from 'react';
import { Terminal, Code2, AlertCircle, Play, Sparkles } from 'lucide-react';
import { Card, CardContent } from "@/components/ui/card";
import { chatWithModel } from '@/lib/api';
import { cn } from '@/lib/utils';

interface TerminalLine {
    id: string;
    type: 'system' | 'user' | 'agent' | 'error' | 'success';
    content: string | React.ReactNode;
    timestamp: Date;
}

export function StrategyView() {
    const [lines, setLines] = useState<TerminalLine[]>([]);
    const [input, setInput] = useState('');
    const [isBooting, setIsBooting] = useState(true);
    const [isProcessing, setIsProcessing] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Boot sequence
    useEffect(() => {
        const bootSequence = [
            { type: 'system' as const, content: 'Initializing Quant Engine Strategy Terminal...', delay: 100 },
            { type: 'system' as const, content: 'Authenticating connection to neural core [OK]', delay: 600 },
            { type: 'system' as const, content: 'Loading active algorithms: Convergence Arb, Mean Reversion', delay: 1100 },
            { type: 'system' as const, content: 'Establishing secure websocket to execution layer...', delay: 1600 },
            { type: 'agent' as const, content: 'Hello. I am your specialized Strategy Architect Agent. I can write, backtest, and deploy new trading logic. Type /help to see commands, or describe the strategy you want to build.', delay: 2400 },
        ];

        let timeoutIds: NodeJS.Timeout[] = [];

        bootSequence.forEach((step, index) => {
            const id = setTimeout(() => {
                setLines(prev => [...prev, {
                    id: Math.random().toString(36).substring(7),
                    type: step.type,
                    content: step.content,
                    timestamp: new Date()
                }]);
                if (index === bootSequence.length - 1) {
                    setIsBooting(false);
                    setTimeout(() => inputRef.current?.focus(), 100);
                }
            }, step.delay);
            timeoutIds.push(id);
        });

        return () => timeoutIds.forEach(clearTimeout);
    }, []);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [lines]);

    const handleCommand = async () => {
        if (!input.trim() || isProcessing) return;

        const cmd = input.trim();
        setInput('');

        // Add user command
        setLines(prev => [...prev, {
            id: Math.random().toString(36).substring(7),
            type: 'user',
            content: cmd,
            timestamp: new Date()
        }]);

        setIsProcessing(true);

        // Local command handling
        if (cmd.startsWith('/')) {
            await handleLocalCommand(cmd);
            setIsProcessing(false);
            return;
        }

        // Send to LLM as a general query
        try {
            const history = lines
                .filter(l => l.type === 'user' || l.type === 'agent')
                .map(l => ({
                    role: (l.type === 'user' ? 'user' : 'assistant') as 'user' | 'assistant',
                    content: typeof l.content === 'string' ? l.content : '',
                    timestamp: l.timestamp.getTime() / 1000
                }));

            const res = await chatWithModel({
                question: cmd,
                history,
                context: { route_path: "Dashboard/StrategyArchitect" }
            });

            setLines(prev => [...prev, {
                id: Math.random().toString(36).substring(7),
                type: 'agent',
                content: res.response || "No response received.",
                timestamp: new Date()
            }]);
        } catch (error) {
            setLines(prev => [...prev, {
                id: Math.random().toString(36).substring(7),
                type: 'error',
                content: "Error communicating with Strategy Factory backend. Please check connection.",
                timestamp: new Date()
            }]);
        } finally {
            setIsProcessing(false);
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    };

    const handleLocalCommand = async (cmd: string) => {
        const parts = cmd.split(' ');
        const base = parts[0].toLowerCase();

        switch (base) {
            case '/help':
                setLines(prev => [...prev, {
                    id: Math.random().toString(36).substring(7),
                    type: 'system',
                    content: (
                        <div className="space-y-1 mt-2">
                            <div className="font-bold text-white mb-2">AVAILABLE COMMANDS:</div>
                            <div className="grid grid-cols-[100px_1fr] gap-2">
                                <span className="text-primary">/help</span> <span className="opacity-80">Show this message</span>
                                <span className="text-primary">/list</span> <span className="opacity-80">List active strategies</span>
                                <span className="text-primary">/status</span> <span className="opacity-80">Check engine health</span>
                                <span className="text-primary">/clear</span> <span className="opacity-80">Clear terminal output</span>
                                <span className="text-emerald-400">/deploy</span> <span className="opacity-80">Deploy generated logic</span>
                            </div>
                        </div>
                    ),
                    timestamp: new Date()
                }]);
                break;
            case '/list':
                setLines(prev => [...prev, {
                    id: Math.random().toString(36).substring(7),
                    type: 'system',
                    content: (
                        <div className="space-y-2 mt-2 border border-white/10 bg-black/40 p-3 rounded">
                            <div className="flex border-b border-white/10 pb-2 mb-2 font-bold text-white text-xs">
                                <div className="w-1/3">STRATEGY</div>
                                <div className="w-1/3">STATUS</div>
                                <div className="w-1/3 text-right">ROI</div>
                            </div>
                            <div className="flex text-xs opacity-90">
                                <div className="w-1/3 text-indigo-400">Convergence Arb</div>
                                <div className="w-1/3 text-emerald-400">RUNNING</div>
                                <div className="w-1/3 text-right text-emerald-400">+12.4%</div>
                            </div>
                            <div className="flex text-xs opacity-90">
                                <div className="w-1/3 text-indigo-400">Mean Reversion</div>
                                <div className="w-1/3 text-zinc-500">PAUSED</div>
                                <div className="w-1/3 text-right text-red-400">-1.2%</div>
                            </div>
                        </div>
                    ),
                    timestamp: new Date()
                }]);
                break;
            case '/clear':
                setLines([]);
                break;
            case '/status':
                setLines(prev => [...prev, {
                    id: Math.random().toString(36).substring(7),
                    type: 'success',
                    content: "Engine CPU: 12% | Mem: 4.2GB | Neural Core: Connected | Latency: 14ms",
                    timestamp: new Date()
                }]);
                break;
            case '/deploy':
                setLines(prev => [...prev, {
                    id: Math.random().toString(36).substring(7),
                    type: 'error',
                    content: "No active strategy staged for deployment. Ask me to write one first.",
                    timestamp: new Date()
                }]);
                break;
            default:
                setLines(prev => [...prev, {
                    id: Math.random().toString(36).substring(7),
                    type: 'error',
                    content: `Command not found: ${base}. Type /help for available commands.`,
                    timestamp: new Date()
                }]);
        }
    };

    return (
        <div className="h-[calc(100vh-140px)] flex flex-col space-y-4 animate-fade-in relative font-mono">
            {/* Background Glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 blur-[120px] rounded-full pointer-events-none z-0" />

            <div className="flex items-center justify-between z-10">
                <div className="space-y-1">
                    <h2 className="text-xl font-black tracking-tighter text-white flex items-center gap-2">
                        <Terminal className="w-5 h-5 text-primary" /> STRATEGY_CLI
                    </h2>
                    <p className="text-[10px] text-muted-foreground uppercase tracking-widest">Agentic Logic Architect</p>
                </div>
                <div className="flex gap-2">
                    <div className="px-3 py-1 bg-black/40 border border-white/10 rounded text-[10px] text-primary flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-primary animate-pulse" /> CORE_ONLINE
                    </div>
                </div>
            </div>

            <Card className="flex-1 glass-panel border-white/10 bg-[#0a0a0a]/90 backdrop-blur-xl flex flex-col overflow-hidden relative shadow-2xl z-10">
                {/* Scanline Overlay */}
                <div className="absolute inset-0 pointer-events-none opacity-[0.03] bg-[size:100%_4px] bg-repeat-y bg-[linear-gradient(transparent_50%,rgba(0,0,0,1)_50%)] z-20" />

                {/* Header Strip */}
                <div className="h-8 border-b border-white/10 bg-white/[0.02] flex items-center justify-between px-4 z-30">
                    <div className="flex gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-white/20" />
                        <div className="w-2.5 h-2.5 rounded-full bg-white/20" />
                        <div className="w-2.5 h-2.5 rounded-full bg-white/20" />
                    </div>
                    <div className="text-[9px] text-muted-foreground uppercase tracking-[0.2em]">Strategy_Terminal_v2.0</div>
                </div>

                {/* Terminal Output */}
                <CardContent className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 custom-scrollbar text-sm z-30 flex flex-col" ref={scrollRef}>
                    {lines.map((line) => (
                        <div key={line.id} className="flex gap-3 group animate-in slide-in-from-bottom-2 fade-in duration-300">
                            <div className="text-[10px] opacity-40 pt-0.5 min-w-[50px] select-none">
                                {line.timestamp.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                            </div>

                            {/* Icon / Prefix */}
                            <div className="shrink-0 pt-0.5">
                                {line.type === 'system' && <span className="text-zinc-500">[*]</span>}
                                {line.type === 'user' && <span className="text-primary">❯</span>}
                                {line.type === 'agent' && <Sparkles className="w-4 h-4 text-primary animate-pulse" />}
                                {line.type === 'error' && <AlertCircle className="w-4 h-4 text-red-500" />}
                                {line.type === 'success' && <span className="text-emerald-400">[OK]</span>}
                            </div>

                            {/* Content */}
                            <div className={cn(
                                "flex-1 whitespace-pre-wrap leading-relaxed",
                                line.type === 'system' && "text-zinc-400",
                                line.type === 'user' && "text-white font-medium",
                                line.type === 'agent' && "text-primary/90",
                                line.type === 'error' && "text-red-400",
                                line.type === 'success' && "text-emerald-400",
                            )}>
                                {line.content}
                            </div>
                        </div>
                    ))}

                    {isProcessing && (
                        <div className="flex gap-3 animate-pulse">
                            <div className="text-[10px] opacity-40 min-w-[50px]">--:--:--</div>
                            <Sparkles className="w-4 h-4 text-primary" />
                            <div className="text-primary/60">Processing...</div>
                        </div>
                    )}
                </CardContent>

                {/* Input Area */}
                <div className="p-4 border-t border-white/10 bg-black/60 z-30">
                    <div className="flex items-center gap-3">
                        <span className="text-primary font-bold">❯</span>
                        <input
                            ref={inputRef}
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') handleCommand();
                            }}
                            disabled={isBooting || isProcessing}
                            className="flex-1 bg-transparent border-none outline-none text-white focus:ring-0 placeholder:text-white/20 text-sm"
                            placeholder={isBooting ? "Booting..." : "Type a command or describe a strategy (e.g. 'Write a moving average crossover macro')..."}
                        />
                    </div>
                </div>
            </Card>
        </div>
    );
}

