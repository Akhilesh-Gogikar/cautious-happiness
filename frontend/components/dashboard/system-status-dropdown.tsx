"use client";

import { useState, useRef, useEffect } from 'react';
import { Activity, Cpu, Zap, Server, ChevronDown } from 'lucide-react';
import { fetchSystemHealth } from '@/lib/api';
import { getSelectedModel, DEFAULT_LLM_PROVIDER } from '@/lib/llm-config';

export function SystemStatusDropdown() {
    const [openDropdown, setOpenDropdown] = useState<string | null>(null);
    const [health, setHealth] = useState<{ ollama: boolean; redis: boolean; database: boolean; gemini_configured: boolean } | null>(null);
    const [healthError, setHealthError] = useState<string | null>(null);
    const [activeModel, setActiveModel] = useState('lfm-thinking');
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setOpenDropdown(null);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
        setActiveModel(getSelectedModel());

        const loadHealth = async () => {
            try {
                const res = await fetchSystemHealth();
                setHealth(res.details);
                setHealthError(null);
            } catch (e) {
                setHealthError('Health endpoint unavailable');
            }
        };

        loadHealth();
        const interval = setInterval(loadHealth, 15000);
        return () => clearInterval(interval);
    }, []);

    const toggleDropdown = (id: string) => {
        setOpenDropdown(openDropdown === id ? null : id);
    };

    const llmOnline = health?.ollama ?? false;

    return (
        <div className="flex items-center gap-4 relative" ref={containerRef}>
            <div className="relative">
                <button
                    onClick={() => toggleDropdown('system')}
                    className="flex items-center gap-1.5 text-[10px] text-muted-foreground font-mono hover:text-white transition-colors group outline-none"
                >
                    <Activity className="w-3 h-3 text-primary animate-pulse" />
                    {healthError ? 'SYSTEM_DEGRADED' : 'SYSTEM_OPTIMAL'}
                    <ChevronDown className={`w-3 h-3 transition-transform ${openDropdown === 'system' ? 'rotate-180 text-white' : 'opacity-50 group-hover:opacity-100'}`} />
                </button>
                {openDropdown === 'system' && (
                    <div className="absolute top-full mt-2 left-0 w-64 bg-black/95 border border-white/10 p-4 rounded-md shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-200 backdrop-blur-xl">
                        <div className="text-xs font-mono text-white/50 mb-3 pb-2 border-b border-white/10 uppercase tracking-wider">Core Systems Health</div>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center text-[10px] font-mono">
                                <span className="text-muted-foreground">Main Database</span>
                                <span className="text-primary flex items-center gap-1.5">
                                    <span className={`w-1.5 h-1.5 rounded-full ${health?.database ? 'bg-primary' : 'bg-red-500'}`} />
                                    {health?.database ? 'ONLINE' : 'OFFLINE'}
                                </span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] font-mono">
                                <span className="text-muted-foreground">Execution Engine</span>
                                <span className="text-primary flex items-center gap-1.5">
                                    <span className={`w-1.5 h-1.5 rounded-full ${llmOnline ? 'bg-primary' : 'bg-red-500'}`} />
                                    {llmOnline ? 'OPTIMAL' : 'DEGRADED'}
                                </span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] font-mono">
                                <span className="text-muted-foreground">Data Feeds (Redis)</span>
                                <span className="text-primary flex items-center gap-1.5">
                                    <span className={`w-1.5 h-1.5 rounded-full ${health?.redis ? 'bg-primary' : 'bg-red-500'}`} />
                                    {health?.redis ? 'SYNCED' : 'DISCONNECTED'}
                                </span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] font-mono pt-1 mt-1 border-t border-white/5">
                                <span className="text-muted-foreground">Critic API</span>
                                <span className="text-white">{health?.gemini_configured ? 'Configured' : 'Not Set'}</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="relative">
                <button
                    onClick={() => toggleDropdown('neural')}
                    className="flex items-center gap-1.5 text-[10px] text-muted-foreground font-mono hover:text-white transition-colors group outline-none"
                >
                    <Cpu className="w-3 h-3 text-indigo" />
                    NEURAL_ENGINE_ACTIVE
                    <ChevronDown className={`w-3 h-3 transition-transform ${openDropdown === 'neural' ? 'rotate-180 text-white' : 'opacity-50 group-hover:opacity-100'}`} />
                </button>
                {openDropdown === 'neural' && (
                    <div className="absolute top-full mt-2 left-0 w-80 bg-black/95 border border-indigo/20 p-4 rounded-md shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-200 backdrop-blur-xl">
                        <div className="text-xs font-mono text-indigo/60 mb-3 pb-2 border-b border-indigo/20 flex items-center justify-between uppercase tracking-wider">
                            <span>Active Models</span>
                            <span className="text-[9px] bg-indigo/10 px-1.5 py-0.5 rounded text-indigo font-bold tracking-widest">{DEFAULT_LLM_PROVIDER}</span>
                        </div>
                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between items-center text-[10px] font-mono mb-1.5">
                                    <span className="text-white flex items-center gap-1.5">
                                        <Server className="w-3 h-3 text-indigo" />
                                        {activeModel}
                                    </span>
                                    <span className={llmOnline ? 'text-primary' : 'text-red-400'}>{llmOnline ? 'CONNECTED' : 'DISCONNECTED'}</span>
                                </div>
                                <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                                    <div className={`h-full opacity-80 ${llmOnline ? 'bg-indigo w-[85%]' : 'bg-red-500 w-[30%]'}`} />
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="relative">
                <button
                    onClick={() => toggleDropdown('latency')}
                    className="flex items-center gap-1.5 text-[10px] text-muted-foreground font-mono hover:text-white transition-colors group outline-none"
                >
                    <Zap className="w-3 h-3 text-gold" />
                    LOW_LATENCY
                    <ChevronDown className={`w-3 h-3 transition-transform ${openDropdown === 'latency' ? 'rotate-180 text-white' : 'opacity-50 group-hover:opacity-100'}`} />
                </button>
                {openDropdown === 'latency' && (
                    <div className="absolute top-full mt-2 left-0 w-64 bg-black/95 border border-gold/20 p-4 rounded-md shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-200 backdrop-blur-xl">
                        <div className="text-xs font-mono text-gold/60 mb-3 pb-2 border-b border-gold/20 uppercase tracking-wider">Network Latency</div>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center text-[10px] font-mono">
                                <span className="text-muted-foreground">API Gateway</span>
                                <span className="text-gold">12ms</span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] font-mono">
                                <span className="text-muted-foreground">Matching Engine</span>
                                <span className="text-gold">4ms</span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] font-mono">
                                <span className="text-muted-foreground">Market Data Feed</span>
                                <span className="text-gold">8ms</span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] font-mono pt-1 mt-1 border-t border-white/5">
                                <span className="text-muted-foreground">LLM Inference TTFT</span>
                                <span className="text-white opacity-80">145ms</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
