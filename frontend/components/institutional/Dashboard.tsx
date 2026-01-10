"use client";

import React, { useState, useEffect } from "react";
import { Activity, Radio, Shield, Zap, TrendingUp, Search, Check, X, Lock } from "lucide-react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

// Types
interface TradeSignal {
    market_id: string;
    market_question: string;
    signal_side: "BUY_YES" | "BUY_NO";
    price_estimate: number;
    kelly_size_usd: number;
    rationale: string;
    timestamp: number;
    status: "PENDING" | "APPROVED" | "EXECUTED" | "FAILED";
}

export default function InstitutionalDashboard() {
    const [mode, setMode] = useState<"HUMAN_REVIEW" | "FULL_AI">("HUMAN_REVIEW");
    const [signals, setSignals] = useState<TradeSignal[]>([]);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [apiKey, setApiKey] = useState("");
    const [secret, setSecret] = useState("");
    const [passphrase, setPassphrase] = useState("");
    const [markets, setMarkets] = useState<any[]>([]);

    // Portfolio Mock Data
    const portfolio = {
        equity: 1250000.00,
        cash: 450000.00,
        exposure: 800000.00,
        dailyPnL: 12450.00,
        dailyPnLPercent: 1.2
    };

    useEffect(() => {
        fetchMarkets();
        const interval = setInterval(fetchSignals, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchMarkets = async () => {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${apiUrl}/markets`);
            if (res.ok) {
                const data = await res.json();
                setMarkets(Array.isArray(data) ? data : []);
            }
        } catch (e) {
            console.error("Failed to fetch markets", e);
        }
    };

    const fetchSignals = async () => {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${apiUrl}/signals`);
            if (res.ok) {
                const data = await res.json();
                if (Array.isArray(data)) {
                    setSignals(data);
                } else {
                    console.error("Signals response is not an array:", data);
                    setSignals([]);
                }
            } else {
                console.error("Failed to fetch signals: SC", res.status);
            }
        } catch (e) {
            console.error("Failed to fetch signals", e);
        }
    };

    const toggleMode = async (newMode: "HUMAN_REVIEW" | "FULL_AI") => {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        setMode(newMode);
        try {
            await fetch(`${apiUrl}/mode/set`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mode: newMode })
            });
            toast.success(`Trading Mode switched to ${newMode.replace('_', ' ')}`);
        } catch (e) {
            // Squelch error for demo if offline
        }
    };

    const saveCredentials = async () => {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${apiUrl}/settings/credentials`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ api_key: apiKey, secret, passphrase })
            });
            if (res.ok) {
                toast.success("API Credentials Connected Successfully");
                setIsSettingsOpen(false);
            } else {
                toast.error("Failed to connect credentials");
            }
        } catch (e) {
            toast.error("Error saving credentials");
        }
    };

    const approveSignal = async (index: number) => {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            const res = await fetch(`${apiUrl}/signals/${index}/approve`, { method: "POST" });
            if (res.ok) {
                toast.success("Signal Approved for Execution");
                fetchSignals();
            }
        } catch (e) {
            toast.error("Execution Failed");
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white font-sans selection:bg-emerald-500/30">
            {/* Header */}
            <header className="border-b border-white/10 bg-[#0a0a0a]/50 backdrop-blur-md sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center">
                            <Activity className="text-black w-5 h-5" />
                        </div>
                        <span className="font-bold text-lg tracking-tight">ANTIGRAVITY <span className="text-emerald-500 text-xs align-top">INSTITUTIONAL</span></span>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="bg-white/5 rounded-full p-1 flex items-center border border-white/10">
                            <button
                                onClick={() => toggleMode("HUMAN_REVIEW")}
                                className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all ${mode === "HUMAN_REVIEW" ? "bg-emerald-500 text-black shadow-lg shadow-emerald-500/20" : "text-gray-400 hover:text-white"}`}
                            >
                                Human Review
                            </button>
                            <button
                                onClick={() => toggleMode("FULL_AI")}
                                className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-2 ${mode === "FULL_AI" ? "bg-purple-500 text-white shadow-lg shadow-purple-500/20" : "text-gray-400 hover:text-white"}`}
                            >
                                <Zap className="w-3 h-3" /> Full AI
                            </button>
                        </div>

                        <Dialog open={isSettingsOpen} onOpenChange={setIsSettingsOpen}>
                            <DialogTrigger asChild>
                                <button className="p-2 hover:bg-white/5 rounded-lg border border-transparent hover:border-white/10 transition-all">
                                    <Lock className="w-4 h-4 text-gray-400" />
                                </button>
                            </DialogTrigger>
                            <DialogContent className="bg-[#111] border-white/10 text-white">
                                <DialogHeader>
                                    <DialogTitle>Connect Polymarket API</DialogTitle>
                                </DialogHeader>
                                <div className="space-y-4 py-4">
                                    <div className="space-y-2">
                                        <label className="text-xs text-gray-400">API Key</label>
                                        <input
                                            type="text"
                                            value={apiKey}
                                            onChange={(e) => setApiKey(e.target.value)}
                                            className="w-full bg-black/50 border border-white/10 rounded px-3 py-2 text-sm focus:border-emerald-500 outline-none"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs text-gray-400">Secret</label>
                                        <input
                                            type="password"
                                            value={secret}
                                            onChange={(e) => setSecret(e.target.value)}
                                            className="w-full bg-black/50 border border-white/10 rounded px-3 py-2 text-sm focus:border-emerald-500 outline-none"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs text-gray-400">Passphrase</label>
                                        <input
                                            type="password"
                                            value={passphrase}
                                            onChange={(e) => setPassphrase(e.target.value)}
                                            className="w-full bg-black/50 border border-white/10 rounded px-3 py-2 text-sm focus:border-emerald-500 outline-none"
                                        />
                                    </div>
                                    <button
                                        onClick={saveCredentials}
                                        className="w-full bg-emerald-500 text-black font-bold py-2 rounded hover:bg-emerald-400 transition-colors"
                                    >
                                        Connect Wallet & API
                                    </button>
                                </div>
                            </DialogContent>
                        </Dialog>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-12 gap-8">
                {/* Left Column: Portfolio & Markets (4 cols) */}
                <div className="col-span-4 space-y-6">
                    {/* Portfolio Card */}
                    <div className="bg-[#111] border border-white/10 rounded-xl p-6 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <TrendingUp className="w-24 h-24" />
                        </div>
                        <h3 className="text-gray-400 text-xs font-medium uppercase tracking-wider mb-1">Total Equity</h3>
                        <div className="text-3xl font-mono font-bold text-white mb-4">
                            ${portfolio.equity.toLocaleString()}
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <div className="text-gray-500 text-[10px] uppercase">Cash</div>
                                <div className="text-sm font-mono text-gray-300">${portfolio.cash.toLocaleString()}</div>
                            </div>
                            <div>
                                <div className="text-gray-500 text-[10px] uppercase">Exposure</div>
                                <div className="text-sm font-mono text-gray-300">${portfolio.exposure.toLocaleString()}</div>
                            </div>
                        </div>
                        <div className="mt-4 flex items-center gap-2 text-emerald-500 text-sm">
                            <TrendingUp className="w-4 h-4" />
                            <span>+${portfolio.dailyPnL.toLocaleString()} ({portfolio.dailyPnLPercent}%)</span>
                            <span className="text-gray-500 text-xs ml-auto">24h</span>
                        </div>
                    </div>

                    {/* Market Scanner */}
                    <div className="bg-[#111] border border-white/10 rounded-xl overflow-hidden flex flex-col h-[500px]">
                        <div className="p-4 border-b border-white/10 flex items-center justify-between">
                            <h3 className="font-bold text-sm">Market Scanner</h3>
                            <Activity className="w-4 h-4 text-emerald-500 animate-pulse" />
                        </div>
                        <div className="overflow-y-auto flex-1 p-2 space-y-2">
                            {markets.map((m) => (
                                <div key={m.id} className="p-3 hover:bg-white/5 rounded-lg cursor-pointer group transition-colors border border-transparent hover:border-white/5">
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="text-xs text-blue-400 bg-blue-400/10 px-1.5 py-0.5 rounded">{m.category}</span>
                                        <span className="text-xs font-mono text-gray-400">${(m.volume_24h / 1000).toFixed(1)}k Vol</span>
                                    </div>
                                    <div className="text-sm font-medium leading-snug mb-2 group-hover:text-emerald-400 transition-colors">
                                        {m.question}
                                    </div>
                                    <div className="flex items-center justify-between text-xs text-gray-500">
                                        <span>Price: <span className="text-white font-mono">{m.last_price}</span></span>
                                        <button className="opacity-0 group-hover:opacity-100 bg-white/10 hover:bg-white/20 px-2 py-1 rounded text-[10px] text-white transition-all">
                                            Analyze
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right Column: Signals & Activity (8 cols) */}
                <div className="col-span-8 space-y-6">
                    {/* Signal Queue */}
                    <div className="bg-[#111] border border-white/10 rounded-xl min-h-[300px] flex flex-col">
                        <div className="p-4 border-b border-white/10 flex items-center justify-between bg-white/5">
                            <div className="flex items-center gap-2">
                                <Shield className="w-4 h-4 text-purple-500" />
                                <h3 className="font-bold text-sm">Signal Queue</h3>
                                <span className="bg-purple-500/20 text-purple-400 text-[10px] px-1.5 py-0.5 rounded-full">{signals.filter(s => s.status === 'PENDING').length} Pending</span>
                            </div>
                        </div>

                        <div className="p-4 space-y-4">
                            {signals.length === 0 ? (
                                <div className="flex flex-col items-center justify-center h-40 text-gray-500 space-y-2">
                                    <Search className="w-8 h-8 opacity-20" />
                                    <p className="text-sm">No signals pending review.</p>
                                </div>
                            ) : (
                                signals.map((signal, idx) => (
                                    <div key={idx} className="bg-black/40 border border-white/10 rounded-lg p-4 flex gap-4 items-start relative overflow-hidden">
                                        <div className={`absolute left-0 top-0 bottom-0 w-1 ${signal.status === 'PENDING' ? 'bg-yellow-500' : 'bg-emerald-500'}`} />
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-xs font-mono text-gray-500">{signal.market_id.substring(0, 8)}...</span>
                                                <span className="text-[10px] bg-white/10 px-1.5 rounded text-gray-300">{new Date(signal.timestamp * 1000).toLocaleTimeString()}</span>
                                            </div>
                                            <h4 className="font-medium text-sm mb-2">{signal.market_question}</h4>
                                            <p className="text-xs text-gray-400 bg-white/5 p-2 rounded mb-3 border border-white/5">
                                                {signal.rationale}
                                            </p>
                                            <div className="flex items-center gap-6">
                                                <div>
                                                    <div className="text-[10px] text-gray-500 uppercase">Side</div>
                                                    <div className={`text-sm font-bold ${signal.signal_side === 'BUY_YES' ? 'text-emerald-500' : 'text-red-500'}`}>{signal.signal_side}</div>
                                                </div>
                                                <div>
                                                    <div className="text-[10px] text-gray-500 uppercase">Size</div>
                                                    <div className="text-sm font-mono font-bold">${signal.kelly_size_usd.toFixed(2)}</div>
                                                </div>
                                                <div>
                                                    <div className="text-[10px] text-gray-500 uppercase">Est. Price</div>
                                                    <div className="text-sm font-mono">{signal.price_estimate.toFixed(2)}</div>
                                                </div>
                                            </div>
                                        </div>

                                        {signal.status === 'PENDING' && (
                                            <div className="flex flex-col gap-2">
                                                <button
                                                    onClick={() => approveSignal(idx)}
                                                    className="w-8 h-8 rounded bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-500 flex items-center justify-center border border-emerald-500/20 transition-colors"
                                                    title="Approve"
                                                >
                                                    <Check className="w-4 h-4" />
                                                </button>
                                                <button className="w-8 h-8 rounded bg-red-500/10 hover:bg-red-500/20 text-red-500 flex items-center justify-center border border-red-500/20 transition-colors" title="Reject">
                                                    <X className="w-4 h-4" />
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Logs / Chat Context */}
                    <div className="bg-[#111] border border-white/10 rounded-xl p-6">
                        <h3 className="font-bold text-sm mb-4">System Logistics</h3>
                        <div className="font-mono text-xs text-gray-400 space-y-1">
                            <p><span className="text-emerald-500">[SYSTEM]</span> Initialized Trading Agent v2.0</p>
                            <p><span className="text-blue-500">[NETWORK]</span> Connected to Polygon Mainnet (RPC: 13ms)</p>
                            <p><span className="text-yellow-500">[WARN]</span> Human Review Mode Active - Auto-execution disabled</p>
                        </div>
                    </div>

                </div>
            </main>
        </div>
    );
}
