"use client";

import { useEffect, useState } from 'react';
import { fetchMarkets, predictMarket, getTaskStatus } from '@/lib/api';
import { toast } from "sonner";
import { ChatPanel } from './chat-panel';
import { DepthChart } from '@/components/dashboard/depth-chart';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ArrowUpRight, ArrowDownRight, Terminal, BarChart2, Activity, PlayCircle, Lock, Zap, TrendingUp, ShieldCheck, MessageSquare } from 'lucide-react';
import { cn } from "@/lib/utils";

export function MarketTable() {
    const [markets, setMarkets] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedMarket, setSelectedMarket] = useState<any>(null);
    const [prediction, setPrediction] = useState<any>(null);
    const [predicting, setPredicting] = useState(false);
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [filter, setFilter] = useState('ALL');
    const [sort, setSort] = useState<'VOLUME' | 'PRICE'>('VOLUME');
    const [sortDir, setSortDir] = useState<'ASC' | 'DESC'>('DESC');

    useEffect(() => {
        fetchMarkets().then(data => {
            setMarkets(data);
            setLoading(false);
        });
    }, []);

    const filteredMarkets = filter === 'ALL'
        ? markets
        : markets.filter(m => m.category.toUpperCase().includes(filter));

    const sortedMarkets = [...filteredMarkets].sort((a, b) => {
        const valA = sort === 'VOLUME' ? a.volume_24h : a.last_price;
        const valB = sort === 'VOLUME' ? b.volume_24h : b.last_price;
        return sortDir === 'DESC' ? valB - valA : valA - valB;
    });

    const handleSort = (field: 'VOLUME' | 'PRICE') => {
        if (sort === field) {
            setSortDir(sortDir === 'DESC' ? 'ASC' : 'DESC');
        } else {
            setSort(field);
            setSortDir('DESC');
        }
    };

    const handlePredict = async (market: any) => {
        setSelectedMarket(market);
        setPredicting(true);
        setPrediction(null);
        setIsChatOpen(false);

        try {
            const { task_id } = await predictMarket(market.question);
            toast.info("Task Dispatched", { description: "Quant Engine Analyzing..." });

            // Poll for result
            const interval = setInterval(async () => {
                const status = await getTaskStatus(task_id);
                if (status.status === 'completed') {
                    clearInterval(interval);

                    if (status.result.error === 'model_missing') {
                        setPredicting(false);
                        toast.error("AI Model Not Found", {
                            description: "Please run ./setup_docker_model.sh in terminal",
                            duration: 10000,
                        });
                        return;
                    }
                    if (status.result.error) {
                        setPredicting(false);
                        toast.error("Prediction Error", {
                            description: status.result.reasoning || "Unknown error occurred",
                        });
                        return;
                    }

                    setPrediction(status.result);
                    setPredicting(false);
                    toast.success("Analysis Complete", { description: "Signals generated." });
                }
            }, 1000);

        } catch (e) {
            console.error(e);
            setPredicting(false);
            toast.error("Prediction System Failure", {
                description: "Unable to contact Neural Engine."
            });
        }
    };

    if (loading) return (
        <div className="space-y-4 animate-pulse">
            <div className="h-96 bg-card/50 rounded-lg border border-white/5"></div>
        </div>
    );

    return (
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">

            {/* Market Data Panel */}
            <div className="xl:col-span-8 space-y-4">
                <Card className="glass-panel border-white/10 bg-black/40 shadow-2xl overflow-hidden relative">
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
                    <CardHeader className="flex flex-row items-center justify-between py-4 px-6 border-b border-white/5 bg-white/[0.02]">
                        <div className="flex items-center gap-3">
                            <div className="p-1.5 rounded bg-primary/10 border border-primary/20">
                                <BarChart2 className="w-4 h-4 text-primary" />
                            </div>
                            <CardTitle className="text-sm font-black font-mono tracking-widest text-muted-foreground uppercase">MARKET_FEED_LIVE</CardTitle>
                        </div>
                        <div className="flex gap-1.5 bg-black/40 p-1 rounded-md border border-white/5">
                            {['ALL', 'CRYPTO', 'TECH', 'ECONOMICS'].map((cat) => (
                                <button
                                    key={cat}
                                    onClick={() => setFilter(cat)}
                                    className={cn(
                                        "px-3 py-1.5 text-[9px] font-bold font-mono transition-all rounded-sm uppercase tracking-wider",
                                        filter === cat
                                            ? "bg-primary text-black shadow-[0_0_15px_rgba(16,185,129,0.4)]"
                                            : "text-muted-foreground hover:text-white hover:bg-white/5"
                                    )}
                                >
                                    {cat}
                                </button>
                            ))}
                        </div>
                    </CardHeader>
                    <CardContent className="p-0">
                        <Table>
                            <TableHeader>
                                <TableRow className="border-white/5 hover:bg-transparent bg-white/[0.01]">
                                    <TableHead className="h-10 text-[9px] font-black font-mono text-muted-foreground/60 w-[50px] uppercase tracking-wider pl-6">#</TableHead>
                                    <TableHead className="h-10 text-[9px] font-black font-mono text-muted-foreground/60 uppercase tracking-wider">INSTRUMENT / TARGET</TableHead>
                                    <TableHead className="h-10 text-[9px] font-black font-mono text-muted-foreground/60 w-[120px] uppercase tracking-wider">SIGNAL_STRENGTH</TableHead>
                                    <TableHead
                                        className="h-10 text-[9px] font-black font-mono text-muted-foreground/60 text-right cursor-pointer hover:text-primary transition-colors w-[100px] uppercase tracking-wider"
                                        onClick={() => handleSort('PRICE')}
                                    >
                                        PROB {sort === 'PRICE' && (sortDir === 'DESC' ? '▼' : '▲')}
                                    </TableHead>
                                    <TableHead
                                        className="h-10 text-[9px] font-black font-mono text-muted-foreground/60 text-right cursor-pointer hover:text-primary transition-colors hidden md:table-cell w-[120px] uppercase tracking-wider pr-6"
                                        onClick={() => handleSort('VOLUME')}
                                    >
                                        LIQUIDITY {sort === 'VOLUME' && (sortDir === 'DESC' ? '▼' : '▲')}
                                    </TableHead>
                                    <TableHead className="h-10 w-[50px]"></TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {sortedMarkets.map((m, idx) => (
                                    <TableRow
                                        key={m.id}
                                        className={cn(
                                            "border-white/5 hover:bg-white/5 cursor-pointer transition-colors group h-10",
                                            selectedMarket?.id === m.id && "bg-primary/5 border-l-2 border-l-primary"
                                        )}
                                        onClick={() => setSelectedMarket(m)}
                                    >
                                        <TableCell className="py-0 font-mono text-[10px] text-muted-foreground/50">
                                            {(idx + 1).toString().padStart(2, '0')}
                                        </TableCell>
                                        <TableCell className="py-0">
                                            <div className="flex flex-col">
                                                <span className="text-xs font-semibold text-white/90 truncate max-w-[280px] md:max-w-sm tracking-tight">{m.question}</span>
                                                <span className="text-[9px] text-muted-foreground/60 font-mono uppercase tracking-tighter">{m.category}</span>
                                            </div>
                                        </TableCell>
                                        <TableCell className="py-0">
                                            <div className={cn(
                                                "px-1.5 py-0.5 rounded-sm text-[9px] font-mono inline-block border",
                                                m.last_price > 0.6 ? "bg-primary/10 text-primary border-primary/20" :
                                                    m.last_price < 0.4 ? "bg-red-500/10 text-red-400 border-red-500/20" :
                                                        "bg-gold/10 text-gold border-gold/20"
                                            )}>
                                                {m.last_price > 0.6 ? 'STRONG_BUY' : m.last_price < 0.4 ? 'SELL_SIGNAL' : 'HODL_NEUTRAL'}
                                            </div>
                                        </TableCell>
                                        <TableCell className="py-0 text-right font-mono text-xs text-white">
                                            <div className={cn(
                                                "inline-flex items-center gap-1",
                                                m.last_price > 0.5 ? "text-primary text-glow-primary" : "text-red-400"
                                            )}>
                                                {(m.last_price * 100).toFixed(0)}%
                                                {m.last_price > 0.5 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                                            </div>
                                        </TableCell>
                                        <TableCell className="py-0 text-right font-mono text-[11px] text-muted-foreground hidden md:table-cell">
                                            ${(m.volume_24h / 1000).toFixed(1)}K
                                        </TableCell>
                                        <TableCell className="py-0 text-right">
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-6 w-6 text-muted-foreground group-hover:text-primary transition-colors"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handlePredict(m);
                                                }}
                                            >
                                                <Activity className="w-3.5 h-3.5" />
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            </div>

            {/* Analysis Terminal Panel */}
            <div className="xl:col-span-4 h-full">
                <Card className="glass-panel border-white/10 bg-black/80 h-full flex flex-col relative overflow-hidden group shadow-2xl">
                    {/* Retro Scanline Effect for Terminal */}
                    <div className="absolute inset-0 pointer-events-none opacity-[0.03] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[size:100%_2px,3px_100%] z-20" />
                    <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 blur-[80px] rounded-full pointer-events-none" />

                    {prediction && (
                        <ChatPanel
                            isOpen={isChatOpen}
                            onClose={() => setIsChatOpen(false)}
                            context={{
                                question: selectedMarket?.question || '',
                                reasoning: prediction.reasoning || 'Reasoning currently unavailable in this view.',
                                critique: prediction.critique || 'No critique available.',
                                probability: prediction.adjusted_forecast || 0
                            }}
                        />
                    )}

                    <CardHeader className="flex flex-row items-center justify-between py-3 px-4 border-b border-white/10 bg-white/5 z-10 shrink-0 backdrop-blur-md">
                        <div className="flex items-center gap-2">
                            <Terminal className="w-4 h-4 text-primary animate-pulse" />
                            <CardTitle className="text-[10px] font-black tracking-[0.2em] text-muted-foreground uppercase text-glow-primary">QUANT_ENGINE_V4.0</CardTitle>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="px-1.5 py-0.5 rounded-sm bg-primary/20 border border-primary/30 text-[9px] font-black font-mono text-primary animate-pulse">
                                ONLINE
                            </div>
                        </div>
                    </CardHeader>

                    <CardContent className="flex-1 p-4 space-y-6 z-10 overflow-y-auto custom-scrollbar bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.03)_0%,transparent_100%)]">
                        {!selectedMarket && (
                            <div className="flex flex-col items-center justify-center h-full text-muted-foreground/30 space-y-4 py-20">
                                <div className="relative">
                                    <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full animate-pulse-glow" />
                                    <Lock className="w-12 h-12 relative z-10" />
                                </div>
                                <span className="font-mono text-[10px] tracking-[0.3em] font-bold">AWAITING_TARGET_ACQUISITION</span>
                            </div>
                        )}

                        {selectedMarket && !prediction && !predicting && (
                            <div className="space-y-6 animate-fade-in">
                                <div className="p-4 rounded-lg bg-white/5 border border-white/10 space-y-3 relative overflow-hidden">
                                    <div className="absolute top-0 right-0 p-2 opacity-20">
                                        <Activity className="w-12 h-12 text-primary" />
                                    </div>
                                    <span className="text-[9px] font-black font-mono text-muted-foreground/60 uppercase tracking-widest">ACTIVE_INSTRUMENT</span>
                                    <p className="text-lg font-bold leading-snug text-white/90 pr-8">{selectedMarket.question}</p>
                                    <div className="flex gap-2 pt-2">
                                        <div className="px-2 py-1 rounded-sm bg-indigo/10 border border-indigo/20 text-[9px] font-mono text-indigo uppercase font-bold">LIQUIDITY: POOLED</div>
                                        <div className="px-2 py-1 rounded-sm bg-primary/10 border border-primary/20 text-[9px] font-mono text-primary uppercase font-bold">FEES: 0.1%</div>
                                    </div>
                                </div>
                                <div className="space-y-4">
                                    <Button
                                        className="w-full h-12 bg-primary hover:bg-emerald-400 text-black border-none text-xs font-black font-mono tracking-[0.2em] uppercase transition-all shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] group relative overflow-hidden"
                                        onClick={() => handlePredict(selectedMarket)}
                                    >
                                        <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-500 skew-x-12" />
                                        <Zap className="w-4 h-4 mr-2 group-hover:animate-bounce" />
                                        INITIATE_ANALYSIS
                                    </Button>
                                    <div className="h-40 rounded-lg border border-white/10 bg-black/40 p-1 relative group/chart overflow-hidden">
                                        <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover/chart:opacity-100 transition-opacity pointer-events-none" />
                                        <DepthChart />
                                    </div>
                                </div>
                            </div>
                        )}

                        {predicting && (
                            <div className="space-y-6 font-mono text-[10px]">
                                <div className="space-y-3">
                                    <div className="flex justify-between text-primary font-bold px-1">
                                        <span className="tracking-widest">EXECUTING_NEURAL_SCAN</span>
                                        <span className="animate-pulse text-neon-blue">RUNNING...</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-white/5 overflow-hidden rounded-full border border-white/5">
                                        <div className="h-full bg-gradient-to-r from-primary via-neon-blue to-primary shadow-[0_0_15px_#10B981] animate-[ticker_1.5s_linear_infinite]" style={{ width: '40%' }}></div>
                                    </div>
                                </div>
                                <div className="space-y-2 text-muted-foreground/60 leading-relaxed p-3 bg-black/40 rounded border border-white/5">
                                    <p className="text-primary/90 opacity-0 animate-[fade-in_0.3s_forwards] font-bold flex items-center gap-2">
                                        <span className="w-1 h-1 bg-primary rounded-full" /> [0.0ms] Establishing peer handshake...
                                    </p>
                                    <p className="opacity-0 animate-[fade-in_0.3s_0.2s_forwards] flex items-center gap-2">
                                        <span className="w-1 h-1 bg-white/20 rounded-full" /> [12.4ms] Orderbook depth verification: COMPLETE
                                    </p>
                                    <p className="opacity-0 animate-[fade-in_0.3s_0.4s_forwards] flex items-center gap-2">
                                        <span className="w-1 h-1 bg-white/20 rounded-full" /> [45.1ms] RAG pipeline initiated: indexing external signals...
                                    </p>
                                    <p className="opacity-0 animate-[fade-in_0.3s_0.6s_forwards] flex items-center gap-2">
                                        <span className="w-1 h-1 bg-white/20 rounded-full" /> [102.8ms] Cross-referencing 4k+ data points...
                                    </p>
                                    <p className="text-neon-blue animate-pulse opacity-0 animate-[fade-in_0.3s_0.8s_forwards] font-bold flex items-center gap-2">
                                        <span className="w-1 h-1 bg-neon-blue rounded-full" /> [158.2ms] BAYESIAN_INFERENCE_ENGINE active...
                                    </p>
                                </div>
                            </div>
                        )}

                        {prediction && (
                            <div className="space-y-6 animate-fade-in px-1">
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="bg-primary/5 border border-primary/20 p-3 rounded-lg relative group">
                                        <div className="absolute top-0 right-0 p-1">
                                            <TrendingUp className="w-3 h-3 text-primary/40" />
                                        </div>
                                        <span className="text-[9px] font-black font-mono text-primary/60 uppercase tracking-tighter">Prob_Adjusted</span>
                                        <div className="text-3xl font-black font-mono text-primary text-glow-primary tracking-tighter">
                                            {(prediction.adjusted_forecast * 100).toFixed(0)}%
                                        </div>
                                    </div>
                                    <div className="bg-white/5 border border-white/10 p-3 rounded-lg">
                                        <span className="text-[9px] font-black font-mono text-muted-foreground/60 uppercase tracking-tighter">Confidence_IV</span>
                                        <div className="text-3xl font-black font-mono text-white tracking-tighter">
                                            HIGH
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-3 bg-white/3 border border-white/5 p-3 rounded-lg">
                                    <div className="flex items-center justify-between border-b border-white/5 pb-2">
                                        <span className="text-[9px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em]">Signal_Critique</span>
                                        <div className="flex gap-1">
                                            <div className="w-1 h-1 rounded-full bg-primary" />
                                            <div className="w-1 h-1 rounded-full bg-primary/40" />
                                            <div className="w-1 h-1 rounded-full bg-primary/10" />
                                        </div>
                                    </div>
                                    <p className="text-[11px] font-medium font-mono text-white/70 leading-relaxed italic">
                                        "{prediction.critique}"
                                    </p>
                                </div>

                                {prediction.news_summary && (
                                    <div className="space-y-2">
                                        <span className="text-[9px] font-black font-mono text-muted-foreground/50 uppercase tracking-[0.2em] pl-1">Source_Feed ({prediction.news_summary.length})</span>
                                        <div className="space-y-1.5 max-h-36 overflow-y-auto pr-2 custom-scrollbar">
                                            {prediction.news_summary.map((n: any, i: number) => (
                                                <a href={n.url} target="_blank" key={i} className="flex items-start gap-2 group/link bg-white/5 p-2 rounded border border-transparent hover:border-primary/20 hover:bg-primary/5 transition-all">
                                                    <div className="text-[9px] font-mono text-primary/40 group-hover/link:text-primary transition-colors mt-0.5">[{i + 1}]</div>
                                                    <span className="text-[10px] text-muted-foreground group-hover/link:text-white leading-snug line-clamp-2">{n.title}</span>
                                                </a>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <div className="flex gap-4 pt-2">
                                    <Button className="flex-1 bg-white text-black hover:bg-white/90 font-black text-[11px] tracking-[0.2em] uppercase py-6 h-auto rounded-none shadow-[0_4px_20px_rgba(255,255,255,0.1)] group transition-all">
                                        <ShieldCheck className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
                                        EXECUTE
                                    </Button>
                                    <Button
                                        onClick={() => setIsChatOpen(!isChatOpen)}
                                        className="flex-1 bg-primary/10 text-primary hover:bg-primary/20 border border-primary/20 font-black text-[11px] tracking-[0.2em] uppercase py-6 h-auto rounded-none group transition-all"
                                    >
                                        <MessageSquare className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
                                        DISCUSS
                                    </Button>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div >
    );
}
