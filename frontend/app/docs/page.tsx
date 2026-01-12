"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import {
    ChevronLeft,
    Book,
    Cpu,
    Zap,
    ShieldCheck,
    Globe,
    Terminal,
    ArrowRight,
    Search,
    ChevronRight,
    Activity,
    Layers,
    MessageSquare,
    BarChart3
} from 'lucide-react';
import { cn } from "@/lib/utils";

const sections = [
    {
        id: 'overview',
        title: 'Product Overview',
        icon: Globe,
        content: (
            <div className="space-y-4">
                <p className="text-muted-foreground leading-relaxed">
                    Alpha Terminal is an institutional-grade predictive analytics dashboard designed for the Alpha Prediction Market. It synthesizes real-time market data with advanced AI-driven insights to provide traders with a decisive edge.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                    <div className="p-4 bg-white/5 border border-white/10 rounded-xl">
                        <h4 className="text-white font-bold mb-2 flex items-center gap-2">
                            <Zap className="w-4 h-4 text-primary" />
                            Real-time Execution
                        </h4>
                        <p className="text-xs text-muted-foreground">Ultra-low latency connection to prediction market CLOBs for millisecond execution.</p>
                    </div>
                    <div className="p-4 bg-white/5 border border-white/10 rounded-xl">
                        <h4 className="text-white font-bold mb-2 flex items-center gap-2">
                            <Cpu className="w-4 h-4 text-indigo" />
                            AI Synthesis
                        </h4>
                        <p className="text-xs text-muted-foreground">Dual-agent system processing news, sentiment, and historical data for every market.</p>
                    </div>
                </div>
            </div>
        )
    },
    {
        id: 'ai-engine',
        title: 'Neural Engine Architecture',
        icon: Cpu,
        content: (
            <div className="space-y-6">
                <p className="text-muted-foreground leading-relaxed">
                    The core of Alpha Terminal is its proprietary neural engine, which utilizes a multi-agent orchestrated approach to market analysis.
                </p>
                <div className="space-y-4">
                    <div className="flex gap-4 p-4 bg-primary/5 border border-primary/20 rounded-xl">
                        <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center shrink-0">
                            <Zap className="w-6 h-6 text-primary" />
                        </div>
                        <div>
                            <h4 className="text-white font-bold mb-1">OpenForecaster-8B (The Analyst)</h4>
                            <p className="text-xs text-muted-foreground line-clamp-2">A specialized fine-tuned LLM running locally via Ollama. It analyzes market liquidity, order book depth, and probability distributions to generate raw alpha signals.</p>
                        </div>
                    </div>
                    <div className="flex gap-4 p-4 bg-indigo/5 border border-indigo/20 rounded-xl">
                        <div className="w-10 h-10 rounded-lg bg-indigo/20 flex items-center justify-center shrink-0">
                            <ShieldCheck className="w-6 h-6 text-indigo" />
                        </div>
                        <div>
                            <h4 className="text-white font-bold mb-1">Critic Agent (The Risk Manager)</h4>
                            <p className="text-xs text-muted-foreground line-clamp-2">Powered by Gemini Pro, this agent scrutinizes signals from OpenForecaster for logical fallacies, edge-case risks, and regime shifts.</p>
                        </div>
                    </div>
                </div>
            </div>
        )
    },
    {
        id: 'trading-modes',
        title: 'Institutional Trading Modes',
        icon: Layers,
        content: (
            <div className="space-y-4">
                <p className="text-muted-foreground">Tailor the automation level to your institutional risk profile.</p>
                <div className="space-y-3">
                    <div className="group p-4 bg-white/5 border border-white/10 rounded-xl hover:border-emerald-500/50 transition-colors">
                        <div className="flex items-center justify-between mb-2">
                            <h4 className="font-bold text-emerald-400">Human Review Mode</h4>
                            <span className="text-[10px] font-mono text-muted-foreground">DEFAULT</span>
                        </div>
                        <p className="text-xs text-muted-foreground">Signals are queued for human approval. The UI provides a full rationale and confidence score for every recommendation.</p>
                    </div>
                    <div className="group p-4 bg-white/5 border border-white/10 rounded-xl hover:border-purple-500/50 transition-colors">
                        <div className="flex items-center justify-between mb-2">
                            <h4 className="font-bold text-purple-400">Full AI Mode</h4>
                            <span className="text-[10px] font-mono text-muted-foreground">HIGH_PERFORMANCE</span>
                        </div>
                        <p className="text-xs text-muted-foreground">Autonomous execution. Once the dual-agent signal meets a specific confidence threshold (default 85%), orders are routed directly to the exchange.</p>
                    </div>
                </div>
            </div>
        )
    },
    {
        id: 'setup',
        title: 'System Deployment',
        icon: Terminal,
        content: (
            <div className="space-y-4">
                <p className="text-muted-foreground">Alpha Terminal is architected for privacy-first, local-first deployment.</p>
                <div className="bg-black/80 rounded-lg p-4 font-mono text-xs border border-white/5 text-emerald-400">
                    <p className="mb-2"># Clone and bootstrap</p>
                    <p className="mb-2">git clone https://github.com/alpha/terminal.git</p>
                    <p className="mb-2">./run.sh</p>
                    <p className="text-muted-foreground mt-4">// Setup handles Docker orchestration & model downloads</p>
                </div>
                <div className="p-4 bg-gold/5 border border-gold/20 rounded-xl">
                    <h4 className="text-gold font-bold mb-2 flex items-center gap-2 text-sm">
                        <Activity className="w-4 h-4" />
                        Hardware Requirements
                    </h4>
                    <ul className="text-xs text-muted-foreground space-y-1 ml-4 list-disc">
                        <li>Minimum 16GB RAM for local LLM inference</li>
                        <li>NVIDIA GPU (8GB+ VRAM) recommended for low latency</li>
                        <li>PostgreSQL 15+ & Redis 7+ (included in Docker)</li>
                    </ul>
                </div>
            </div>
        )
    }
];

export default function DocsPage() {
    const [activeSection, setActiveSection] = useState('overview');

    return (
        <div className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-primary/30">
            {/* Header */}
            <header className="h-16 border-b border-white/10 bg-black/40 backdrop-blur-xl flex items-center justify-between px-6 sticky top-0 z-50">
                <div className="flex items-center gap-4">
                    <Link href="/" className="hover:text-primary transition-colors flex items-center gap-2">
                        <ChevronLeft className="w-4 h-4" />
                        <span className="text-xs font-mono font-bold tracking-widest uppercase">Back to Terminal</span>
                    </Link>
                    <div className="h-4 w-[1px] bg-white/10" />
                    <div className="flex items-center gap-2">
                        <Book className="w-4 h-4 text-primary" />
                        <h1 className="text-sm font-black tracking-tighter text-white uppercase">Documentation</h1>
                    </div>
                </div>

                <div className="hidden md:flex items-center gap-4">
                    <div className="relative">
                        <Search className="w-3 h-3 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                        <input
                            placeholder="Search documentation..."
                            className="bg-white/5 border border-white/10 rounded-full py-1.5 pl-8 pr-4 text-[10px] w-48 focus:w-64 focus:border-primary/50 outline-none transition-all"
                        />
                    </div>
                </div>
            </header>

            <div className="flex-1 flex max-w-7xl mx-auto w-full relative">
                {/* Side Nav */}
                <aside className="w-64 border-r border-white/5 p-8 hidden lg:block sticky top-16 h-[calc(100vh-64px)] overflow-y-auto custom-scrollbar">
                    <div className="space-y-8">
                        <div>
                            <p className="text-[10px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em] mb-4">Foundation</p>
                            <nav className="space-y-1">
                                {sections.map((section) => (
                                    <button
                                        key={section.id}
                                        onClick={() => setActiveSection(section.id)}
                                        className={cn(
                                            "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs transition-all group",
                                            activeSection === section.id
                                                ? "bg-primary/10 text-primary border border-primary/20"
                                                : "text-muted-foreground hover:bg-white/5 hover:text-white"
                                        )}
                                    >
                                        <section.icon className={cn("w-4 h-4", activeSection === section.id ? "text-primary" : "group-hover:text-primary transition-colors")} />
                                        <span>{section.title}</span>
                                    </button>
                                ))}
                            </nav>
                        </div>

                        <div>
                            <p className="text-[10px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em] mb-4">Resources</p>
                            <nav className="space-y-1">
                                <a href="http://localhost:8000/docs" target="_blank" className="flex items-center justify-between px-3 py-2 rounded-lg text-xs text-muted-foreground hover:bg-white/5 hover:text-white transition-all group">
                                    <div className="flex items-center gap-3">
                                        <Terminal className="w-4 h-4 group-hover:text-cyber-blue" />
                                        <span>API Reference</span>
                                    </div>
                                    <ArrowRight className="w-3 h-3 opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0 transition-all" />
                                </a>
                                <div className="flex items-center gap-3 px-3 py-2 rounded-lg text-xs text-muted-foreground cursor-not-allowed opacity-50">
                                    <MessageSquare className="w-4 h-4" />
                                    <span>Community Support</span>
                                </div>
                            </nav>
                        </div>
                    </div>
                </aside>

                {/* Content */}
                <main className="flex-1 p-8 md:p-12 lg:p-16 max-w-3xl overflow-y-auto">
                    <div className="animate-fade-in">
                        {sections.map((section) => (
                            <section
                                key={section.id}
                                className={cn("space-y-8 pb-16 border-b border-white/5 mb-16 last:border-0", activeSection === section.id ? "" : "opacity-40 grayscale hover:grayscale-0 hover:opacity-100 transition-all cursor-pointer")}
                                onClick={() => setActiveSection(section.id)}
                            >
                                <div className="space-y-4">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
                                            <section.icon className="w-5 h-5 text-primary" />
                                        </div>
                                        <h2 className="text-2xl font-black tracking-tight text-white uppercase">{section.title}</h2>
                                    </div>
                                    <div className="text-lg">
                                        {section.content}
                                    </div>
                                </div>
                            </section>
                        ))}
                    </div>

                    {/* Footer */}
                    <footer className="mt-12 pt-12 border-t border-white/5 text-center space-y-4">
                        <div className="flex items-center justify-center gap-2">
                            <div className="w-8 h-8 bg-primary rounded flex items-center justify-center shadow-[0_0_15px_rgba(16,185,129,0.5)]">
                                <Zap className="w-5 h-5 text-black fill-current" />
                            </div>
                            <span className="font-bold text-sm text-white">ALPHA TERMINAL CORE</span>
                        </div>
                        <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
                            Built for Institutional Excellence // © 2026 ALPHA
                        </p>
                    </footer>
                </main>

                {/* Table of Contents / Quick Links - Desktop */}
                <aside className="w-48 p-12 hidden xl:block sticky top-16 h-[calc(100vh-64px)]">
                    <div className="space-y-4">
                        <p className="text-[9px] font-bold text-muted-foreground/40 uppercase tracking-widest">On this page</p>
                        <nav className="flex flex-col gap-2">
                            {sections.map((s) => (
                                <button
                                    key={s.id}
                                    onClick={() => setActiveSection(s.id)}
                                    className={cn(
                                        "text-[10px] text-left hover:text-white transition-colors py-1 pl-3 border-l",
                                        activeSection === s.id ? "border-primary text-white" : "border-white/5 text-muted-foreground"
                                    )}
                                >
                                    {s.title}
                                </button>
                            ))}
                        </nav>
                    </div>
                </aside>
            </div>

            {/* Visual background decorations */}
            <div className="fixed inset-0 pointer-events-none z-[-1] opacity-20">
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/10 blur-[150px] rounded-full" />
                <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-indigo/10 blur-[130px] rounded-full" />
            </div>
        </div>
    );
}
