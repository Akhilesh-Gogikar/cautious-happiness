"use client";

import { useCallback, useEffect, useMemo, useState } from 'react';
import { fetchMarkets, predictMarket, getTaskStatus, API_URL } from '@/lib/api';
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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUpRight, ArrowDownRight, Terminal, BarChart2, Activity, PlayCircle, Lock, Zap, TrendingUp, ShieldCheck, MessageSquare, Globe, AlertTriangle, RefreshCcw, Search } from 'lucide-react';
import { cn } from "@/lib/utils";

// Mock data for Macro Views and Signals
const MACRO_VIEWS = [
    { symbol: 'SPX', name: 'S&P 500', value: '4,958.61', change: '+1.07%', trend: 'up' },
    { symbol: 'NDX', name: 'Nasdaq 100', value: '17,642.73', change: '+1.74%', trend: 'up' },
    { symbol: 'VIX', name: 'Volatility Index', value: '13.85', change: '-4.68%', trend: 'down' },
    { symbol: 'DXY', name: 'US Dollar Index', value: '103.92', change: '+0.15%', trend: 'up' },
    { symbol: 'US10Y', name: 'US 10 Year Yield', value: '4.18%', change: '+0.03%', trend: 'up' },
    { symbol: 'CL=F', name: 'Crude Oil', value: '76.22', change: '-2.09%', trend: 'down' },
];

const MOCK_SIGNALS = [
    { id: 1, type: 'critical', asset: 'Brent Crude', message: 'EXTREME NOISE DETECTED. Algo flows diverging from physical supply metrics.', time: '2m ago' },
    { id: 2, type: 'info', asset: 'USD/JPY', message: 'Liquidity forming at 148.50 level. Passive order imblance.', time: '14m ago' },
    { id: 3, type: 'warning', asset: 'Gold', message: 'Systemic volatility spike predicted in next 4h based on macro correlations.', time: '1h ago' },
];

export function MarketTable() {
    const [markets, setMarkets] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedMarket, setSelectedMarket] = useState<any>(null);
    const [prediction, setPrediction] = useState<any>(null);
    const [predicting, setPredicting] = useState(false);
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [filter, setFilter] = useState('ALL');
    const [searchQuery, setSearchQuery] = useState('');
    const [statusMessage, setStatusMessage] = useState('Initializing...');
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [loadError, setLoadError] = useState<string | null>(null);

    const loadMarkets = useCallback(async (isManualRefresh = false) => {
        if (isManualRefresh) {
            setIsRefreshing(true);
        } else {
            setLoading(true);
        }

        try {
            const data = await fetchMarkets();
            setMarkets(data);
            setLoadError(null);
            if (isManualRefresh) {
                toast.success('Watchlist refreshed', { description: `${data.length} markets synchronized.` });
            }
        } catch {
            const message = 'Unable to load markets. Verify backend connectivity.';
            setLoadError(message);
            toast.error('Market feed unavailable', { description: message });
        } finally {
            setLoading(false);
            setIsRefreshing(false);
        }
    }, []);

    useEffect(() => {
        loadMarkets();
    }, [loadMarkets]);

    const filteredMarkets = useMemo(() => {
        const categoryFiltered = filter === 'ALL'
            ? markets
            : markets.filter(m => m.category.toUpperCase().includes(filter));

        if (!searchQuery.trim()) {
            return categoryFiltered;
        }

        const normalizedQuery = searchQuery.toLowerCase();
        return categoryFiltered.filter((market) =>
            market.question.toLowerCase().includes(normalizedQuery)
        );
    }, [filter, markets, searchQuery]);

    // Sort by volume descending for watchlist
    const sortedMarkets = [...filteredMarkets].sort((a, b) => b.volume_24h - a.volume_24h);

    const handlePredict = async (market: any) => {
        setSelectedMarket(market);
        setPredicting(true);
        setPrediction(null);
        setIsChatOpen(false);

        try {
            const { task_id } = await predictMarket(market.question);
            toast.info("Mirroring Initialized", { description: "Establishing Neural Handshake..." });
            setStatusMessage("Establishing peer handshake...");

            const wsUrl = API_URL.replace('http', 'ws') + `/ws/lifecycle/${task_id}`;
            const ws = new WebSocket(wsUrl);

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.event === 'status') {
                    setStatusMessage(data.message);
                } else if (data.event === 'complete') {
                    ws.close();
                    getTaskStatus(task_id).then(status => {
                        if (status.result?.error === 'model_missing') {
                            setPredicting(false);
                            toast.error("AI Model Not Found", { description: "Please run ./setup_docker_model.sh" });
                            return;
                        }
                        setPrediction(status.result);
                        setPredicting(false);
                        toast.success("Analysis Complete", { description: "Divergence audited." });
                    });
                } else if (data.event === 'failed') {
                    ws.close();
                    setPredicting(false);
                    toast.error("Analysis Failed", { description: data.message });
                }
            };

            ws.onerror = (err) => {
                console.error("WS Error:", err);
                setPredicting(false);
            };

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
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 h-full min-h-[600px]">
            {/* Column 1: Macro Views */}
            <div className="xl:col-span-3 space-y-4 flex flex-col">
                <Card className="glass-panel border-white/10 bg-black/40 shadow-2xl overflow-hidden relative flex-1 flex flex-col">
                    <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyber-blue/50 to-transparent" />
                    <CardHeader className="py-4 px-5 border-b border-white/5 bg-white/[0.02]">
                        <CardTitle className="text-[10px] font-black font-mono tracking-widest text-muted-foreground uppercase flex items-center gap-2">
                            <Globe className="w-4 h-4 text-cyber-blue" />
                            Macro_State
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4 space-y-3 flex-1 overflow-y-auto custom-scrollbar">
                        {MACRO_VIEWS.map((macro, idx) => (
                            <div key={idx} className="p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors flex justify-between items-center group cursor-default">
                                <div>
                                    <div className="text-xs font-bold text-white/90">{macro.symbol}</div>
                                    <div className="text-[9px] font-mono text-muted-foreground uppercase">{macro.name}</div>
                                </div>
                                <div className="text-right">
                                    <div className="text-xs font-mono text-white/90">{macro.value}</div>
                                    <div className={cn("text-[10px] font-mono flex items-center justify-end gap-1 mt-0.5", macro.trend === 'up' ? "text-primary" : "text-destructive")}>
                                        {macro.change}
                                        {macro.trend === 'up' ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                                    </div>
                                </div>
                            </div>
                        ))}

                        <div className="mt-4 pt-4 border-t border-white/5 space-y-2">
                            <span className="text-[9px] font-black font-mono text-muted-foreground uppercase tracking-widest">Global Heatmap</span>
                            <div className="h-24 rounded border border-white/10 bg-black/40 relative overflow-hidden flex items-center justify-center group pointer-events-none">
                                <div className="absolute inset-0 bg-[#0f172a] mix-blend-screen opacity-50" />
                                <div className="absolute inset-0 bg-[url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg')] bg-no-repeat bg-center opacity-10 bg-contain" />
                                <div className="absolute top-[30%] left-[20%] w-2 h-2 bg-primary rounded-full animate-ping" />
                                <div className="absolute top-[50%] right-[30%] w-2 h-2 bg-gold/80 rounded-full animate-ping [animation-delay:500ms]" />
                                <div className="absolute bottom-[20%] left-[40%] w-2 h-2 bg-cyber-blue rounded-full animate-ping [animation-delay:1000ms]" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Column 2: Proprietary Signals (Terminal Space) */}
            <div className="xl:col-span-5 space-y-4 flex flex-col">
                <Card className="glass-panel border-white/10 bg-black/80 shadow-2xl overflow-hidden relative flex-1 flex flex-col group">
                    {/* Retro Scanline Effect for Terminal */}
                    <div className="absolute inset-0 pointer-events-none opacity-[0.03] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[size:100%_2px,3px_100%] z-20" />

                    {prediction && (
                        <ChatPanel
                            isOpen={isChatOpen}
                            onClose={() => setIsChatOpen(false)}
                            context={{
                                question: selectedMarket?.question || '',
                                reasoning: prediction.reasoning || '',
                                critique: prediction.critique || '',
                                probability: prediction.adjusted_forecast || 0
                            }}
                        />
                    )}

                    <CardHeader className="py-4 px-5 border-b border-white/10 bg-white/5 z-10 shrink-0 backdrop-blur-md flex flex-row items-center justify-between">
                        <CardTitle className="text-[10px] font-black font-mono tracking-widest text-muted-foreground uppercase flex items-center gap-2 text-glow-primary">
                            <Terminal className="w-4 h-4 text-primary animate-pulse" />
                            Proprietary_Signals
                        </CardTitle>
                        <div className="px-1.5 py-0.5 rounded-sm bg-primary/20 border border-primary/30 text-[9px] font-black font-mono text-primary animate-pulse">
                            ENGINE_IDLE
                        </div>
                    </CardHeader>
                    <CardContent className="p-4 space-y-4 flex-1 overflow-y-auto custom-scrollbar relative z-10 bg-[radial-gradient(circle_at_center,rgba(16,185,129,0.03)_0%,transparent_100%)]">

                        {/* Selected Market Context OR General Feed */}
                        {!selectedMarket && !predicting && !prediction && (
                            <div className="space-y-4">
                                <span className="text-[9px] font-black font-mono text-muted-foreground/60 uppercase tracking-widest pl-1">Recent Intelligence Broadcasts</span>
                                <div className="space-y-3">
                                    {MOCK_SIGNALS.map((signal) => (
                                        <div key={signal.id} className="p-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors cursor-pointer flex gap-3">
                                            <div className="mt-0.5">
                                                {signal.type === 'critical' ? <AlertTriangle className="w-4 h-4 text-destructive" /> :
                                                    signal.type === 'warning' ? <AlertTriangle className="w-4 h-4 text-gold" /> :
                                                        <Activity className="w-4 h-4 text-cyber-blue" />}
                                            </div>
                                            <div className="space-y-1">
                                                <div className="flex items-center justify-between">
                                                    <span className={cn("text-[9px] font-black font-mono uppercase tracking-wider",
                                                        signal.type === 'critical' ? 'text-destructive' :
                                                            signal.type === 'warning' ? 'text-gold' : 'text-cyber-blue')}>
                                                        {signal.asset}
                                                    </span>
                                                    <span className="text-[9px] font-mono text-muted-foreground">{signal.time}</span>
                                                </div>
                                                <p className="text-[11px] font-mono leading-relaxed text-white/80">
                                                    {signal.message}
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div className="pt-10 flex flex-col items-center justify-center text-muted-foreground/30 space-y-4">
                                    <div className="relative">
                                        <div className="absolute inset-0 bg-primary/10 blur-xl rounded-full animate-pulse-glow" />
                                        <Lock className="w-8 h-8 relative z-10" />
                                    </div>
                                    <span className="font-mono text-[10px] tracking-[0.3em] font-bold">SELECT_ASSET_FROM_WATCHLIST</span>
                                </div>
                            </div>
                        )}

                        {selectedMarket && !prediction && !predicting && (
                            <div className="space-y-6 animate-fade-in flex flex-col h-full">
                                <div className="p-4 rounded-lg bg-white/5 border border-white/10 space-y-3 relative overflow-hidden">
                                    <div className="absolute top-0 right-0 p-2 opacity-20">
                                        <Activity className="w-12 h-12 text-primary" />
                                    </div>
                                    <span className="text-[9px] font-black font-mono text-muted-foreground/60 uppercase tracking-widest">Target_Acquired</span>
                                    <p className="text-sm font-bold leading-snug text-white/90 pr-8">{selectedMarket.question}</p>
                                    <div className="flex gap-2 pt-2">
                                        <div className="px-2 py-1 rounded-sm bg-primary/10 border border-primary/20 text-[9px] font-mono text-primary uppercase font-bold">CATEGORY: {selectedMarket.category}</div>
                                    </div>
                                </div>

                                <div className="space-y-4 pt-4 mt-auto">
                                    <div className="h-40 rounded-lg border border-white/10 bg-black/40 p-1 relative group/chart overflow-hidden">
                                        <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover/chart:opacity-100 transition-opacity pointer-events-none" />
                                        <DepthChart />
                                    </div>
                                    <Button
                                        className="w-full h-12 bg-primary hover:bg-emerald-400 text-black border-none text-xs font-black font-mono tracking-[0.2em] uppercase transition-all shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] group relative overflow-hidden"
                                        onClick={() => handlePredict(selectedMarket)}
                                    >
                                        <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-500 skew-x-12" />
                                        <Zap className="w-4 h-4 mr-2 group-hover:animate-bounce" />
                                        EXECUTE_NEURAL_AUDIT
                                    </Button>
                                </div>
                            </div>
                        )}

                        {predicting && (
                            <div className="space-y-6 font-mono text-[10px] py-10">
                                <div className="space-y-3">
                                    <div className="flex justify-between text-primary font-bold px-1">
                                        <span className="tracking-widest uppercase">{statusMessage}</span>
                                        <span className="animate-pulse text-neon-blue">SCANNING...</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-white/5 overflow-hidden rounded-full border border-white/5">
                                        <div className="h-full bg-gradient-to-r from-primary via-neon-blue to-primary shadow-[0_0_15px_#10B981] animate-[ticker_1.5s_linear_infinite]" style={{ width: '40%' }}></div>
                                    </div>
                                </div>
                                <div className="space-y-2 text-muted-foreground/60 leading-relaxed p-3 bg-black/40 rounded border border-white/5 font-mono text-[9px] uppercase">
                                    <p className="text-primary/90 flex items-center gap-2">
                                        <span className="w-1 h-1 bg-primary rounded-full animate-pulse" /> [SYNC] Neural_Domain_Active
                                    </p>
                                    <p className="flex items-center gap-2">
                                        <span className="w-1 h-1 bg-white/20 rounded-full" /> [AUTH] Privilege_Level: Analyst
                                    </p>
                                    <p className="flex items-center gap-2">
                                        <span className="w-1 h-1 bg-white/20 rounded-full" /> [DATA] RAG_Pipeline_Stabilized
                                    </p>
                                    <p className="text-neon-blue animate-pulse font-bold flex items-center gap-2">
                                        <span className="w-1 h-1 bg-neon-blue rounded-full" /> [FLOW] Auditing_In_Progress...
                                    </p>
                                </div>
                            </div>
                        )}

                        {prediction && (
                            <div className="space-y-4 animate-fade-in flex flex-col h-full">
                                <div className="grid grid-cols-2 gap-3 shrink-0">
                                    <div className="bg-primary/5 border border-primary/20 p-3 rounded-lg relative group">
                                        <div className="absolute top-0 right-0 p-1">
                                            <TrendingUp className="w-3 h-3 text-primary/40" />
                                        </div>
                                        <span className="text-[9px] font-black font-mono text-primary/60 uppercase tracking-tighter">Confidence</span>
                                        <div className="text-3xl font-black font-mono text-primary text-glow-primary tracking-tighter">
                                            {(prediction.adjusted_forecast * 100).toFixed(0)}%
                                        </div>
                                    </div>
                                    <div className="bg-white/5 border border-white/10 p-3 rounded-lg">
                                        <span className="text-[9px] font-black font-mono text-muted-foreground/60 uppercase tracking-tighter">Severity</span>
                                        <div className="text-3xl font-black font-mono text-white tracking-tighter">
                                            HIGH
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-3 bg-white/5 border border-white/5 p-3 rounded-lg shrink-0">
                                    <div className="flex items-center justify-between border-b border-white/5 pb-2">
                                        <span className="text-[9px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em]">Neural_Synthesis</span>
                                        <div className="flex gap-1">
                                            <div className="w-1 h-1 rounded-full bg-primary" />
                                            <div className="w-1 h-1 rounded-full bg-primary/40" />
                                            <div className="w-1 h-1 rounded-full bg-primary/10" />
                                        </div>
                                    </div>
                                    <p className="text-[10px] font-medium font-mono text-white/80 leading-relaxed italic line-clamp-4 hover:line-clamp-none transition-all">
                                        &quot;{prediction.critique}&quot;
                                    </p>
                                </div>

                                <div className="flex gap-4 pt-2 mt-auto">
                                    <Button
                                        onClick={() => setIsChatOpen(!isChatOpen)}
                                        className="flex-1 bg-primary/10 text-primary hover:bg-primary/20 border border-primary/20 font-black text-[10px] tracking-[0.1em] uppercase py-5 h-auto rounded shadow-sm group transition-all"
                                    >
                                        <MessageSquare className="w-3 h-3 mr-2 group-hover:scale-110 transition-transform" />
                                        DISCUSS_FINDINGS
                                    </Button>
                                    <Button className="flex-1 bg-white text-black hover:bg-white/90 font-black text-[10px] tracking-[0.1em] uppercase py-5 h-auto rounded shadow-sm group transition-all"
                                        onClick={() => {
                                            setSelectedMarket(null);
                                            setPrediction(null);
                                        }}>
                                        <Activity className="w-3 h-3 mr-2 group-hover:scale-110 transition-transform" />
                                        RESET_TARGET
                                    </Button>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Column 3: Watchlist */}
            <div className="xl:col-span-4 space-y-4 flex flex-col">
                <Card className="glass-panel border-white/10 bg-black/40 shadow-2xl overflow-hidden relative flex-1 flex flex-col">
                    <div className="absolute top-0 right-0 w-full h-[1px] bg-gradient-to-l from-transparent via-gold/50 to-transparent" />
                    <CardHeader className="py-4 px-5 border-b border-white/5 bg-white/[0.02] flex flex-row items-center justify-between flex-wrap gap-2">
                        <CardTitle className="text-[10px] font-black font-mono tracking-widest text-muted-foreground uppercase flex items-center gap-2">
                            <BarChart2 className="w-4 h-4 text-gold" />
                            Watchlist
                        </CardTitle>
                        <div className="flex gap-1.5 bg-black/40 p-1 rounded-md border border-white/5">
                            {['ALL', 'ENERGY', 'METALS', 'AGRI'].map((cat) => (
                                <button
                                    key={cat}
                                    onClick={() => setFilter(cat)}
                                    className={cn(
                                        "px-2 py-1 text-[8px] font-bold font-mono transition-all rounded-sm uppercase tracking-wider",
                                        filter === cat
                                            ? "bg-gold/20 text-gold shadow-[0_0_10px_rgba(250,204,21,0.2)] border border-gold/30"
                                            : "text-muted-foreground hover:text-white hover:bg-white/5 border border-transparent"
                                    )}
                                >
                                    {cat}
                                </button>
                            ))}
                        </div>
                        <div className="w-full flex items-center gap-2 mt-1">
                            <div className="relative flex-1">
                                <Search className="w-3 h-3 text-muted-foreground absolute left-2.5 top-1/2 -translate-y-1/2" />
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(event) => setSearchQuery(event.target.value)}
                                    placeholder="Search assets..."
                                    className="w-full h-8 pl-8 pr-2 bg-black/30 border border-white/10 rounded text-[10px] font-mono text-white placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-gold/50"
                                />
                            </div>
                            <Button
                                variant="outline"
                                size="icon"
                                className="h-8 w-8 border-white/10 bg-black/30 hover:bg-white/10"
                                onClick={() => loadMarkets(true)}
                                disabled={isRefreshing}
                                aria-label="Refresh watchlist"
                            >
                                <RefreshCcw className={cn('w-3 h-3', isRefreshing && 'animate-spin')} />
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent className="p-0 flex-1 overflow-auto custom-scrollbar">
                        <Table>
                            <TableHeader className="sticky top-0 bg-black/80 backdrop-blur-md z-10">
                                <TableRow className="border-white/5 hover:bg-transparent">
                                    <TableHead className="h-8 text-[8px] font-black font-mono text-muted-foreground/60 uppercase tracking-wider pl-4">Asset</TableHead>
                                    <TableHead className="h-8 text-[8px] font-black font-mono text-muted-foreground/60 text-right w-[60px] uppercase tracking-wider">Price</TableHead>
                                    <TableHead className="h-8 w-[40px]"></TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {loadError && (
                                    <TableRow className="border-white/5 hover:bg-transparent">
                                        <TableCell colSpan={3} className="py-6 px-4 text-center text-[10px] font-mono text-red-300">
                                            {loadError}
                                        </TableCell>
                                    </TableRow>
                                )}
                                {!loadError && sortedMarkets.length === 0 && (
                                    <TableRow className="border-white/5 hover:bg-transparent">
                                        <TableCell colSpan={3} className="py-6 px-4 text-center text-[10px] font-mono text-muted-foreground">
                                            No markets match the current filters.
                                        </TableCell>
                                    </TableRow>
                                )}
                                {sortedMarkets.map((m, idx) => (
                                    <TableRow
                                        key={m.id}
                                        className={cn(
                                            "border-white/5 hover:bg-white/5 cursor-pointer transition-colors group h-12",
                                            selectedMarket?.id === m.id && "bg-primary/5 border-l-2 border-l-primary"
                                        )}
                                        onClick={() => setSelectedMarket(m)}
                                    >
                                        <TableCell className="py-2 pl-4">
                                            <div className="flex flex-col">
                                                <span className="text-[11px] font-bold text-white/90 truncate max-w-[140px] tracking-tight">{m.question}</span>
                                                <div className="flex items-center gap-2 mt-0.5">
                                                    <span className={cn(
                                                        "px-1 py-[1px] rounded-[2px] text-[7px] font-mono border",
                                                        m.last_price > 0.6 ? "bg-primary/10 text-primary border-primary/20" :
                                                            m.last_price < 0.4 ? "bg-red-500/10 text-red-400 border-red-500/20" :
                                                                "bg-gold/10 text-gold border-gold/20"
                                                    )}>
                                                        {m.last_price > 0.6 ? 'OVERSOLD' : m.last_price < 0.4 ? 'OVERBOUGHT' : 'NEUTRAL'}
                                                    </span>
                                                </div>
                                            </div>
                                        </TableCell>
                                        <TableCell className="py-2 text-right font-mono text-[10px] text-white">
                                            <div className={cn(
                                                "inline-flex items-center gap-0.5",
                                                m.last_price > 0.5 ? "text-primary" : "text-destructive"
                                            )}>
                                                {(m.last_price * 100).toFixed(1)}
                                            </div>
                                            <div className="text-[8px] text-muted-foreground mt-0.5">${(m.volume_24h / 1000).toFixed(0)}k Vol</div>
                                        </TableCell>
                                        <TableCell className="py-2 text-right pr-4">
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-6 w-6 text-muted-foreground group-hover:text-primary transition-colors hover:bg-primary/10"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handlePredict(m);
                                                }}
                                            >
                                                <PlayCircle className="w-3.5 h-3.5" />
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            </div>

        </div>
    );
}
