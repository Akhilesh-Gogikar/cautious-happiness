"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { Link, ArrowLeft, RefreshCw, LayoutDashboard } from "lucide-react";
import { PortfolioView } from "@/components/dashboard/portfolio-view";

export default function PortfolioPage() {
    return (
        <main className="min-h-screen bg-[#050505] text-white p-6 space-y-8 max-w-[1600px] mx-auto relative overflow-hidden">
            {/* Background Glows */}
            <div className="fixed top-0 left-0 w-[800px] h-[800px] bg-blue-900/10 rounded-full blur-[120px] pointer-events-none -translate-x-1/2 -translate-y-1/2" />
            <div className="fixed bottom-0 right-0 w-[600px] h-[600px] bg-emerald-900/10 rounded-full blur-[100px] pointer-events-none translate-x-1/2 translate-y-1/2" />

            <header className="flex justify-between items-center border-b border-white/10 pb-6 relative z-10 backdrop-blur-sm">
                <div className="space-y-1">
                    <div className="flex items-center gap-3">
                        <h1 className="text-3xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-white to-white/60">
                            COMMAND // <span className="text-primary italic">PORTFOLIO</span>
                        </h1>
                        <span className="px-2.5 py-0.5 rounded-full bg-primary/20 text-primary border border-primary/30 text-[10px] font-mono font-bold uppercase tracking-widest shadow-[0_0_15px_rgba(16,185,129,0.2)] flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" /> Live_Sync
                        </span>
                    </div>
                    <a href="/" className="inline-flex items-center gap-1.5 text-[11px] text-muted-foreground font-mono hover:text-white transition-colors group">
                        <ArrowLeft className="w-3 h-3 group-hover:-translate-x-0.5 transition-transform" /> RETURN TO TERMINAL
                    </a>
                </div>
                <div className="flex items-center gap-4">
                    <button className="h-10 w-10 flex items-center justify-center rounded-lg bg-white/5 border border-white/10 text-muted-foreground hover:text-white hover:bg-white/10 transition-colors">
                        <RefreshCw className="w-4 h-4" />
                    </button>
                    <button className="h-10 px-4 flex items-center justify-center gap-2 rounded-lg bg-white/5 border border-white/10 text-muted-foreground hover:text-white hover:bg-white/10 transition-colors text-xs font-mono font-bold">
                        <LayoutDashboard className="w-4 h-4" /> LAYOUT
                    </button>
                    {/* Assuming RainbowKit is configured, kept for wallet integration */}
                    <div className="scale-90 transform origin-right">
                        <ConnectButton showBalance={true} />
                    </div>
                </div>
            </header>

            <div className="relative z-10 animate-slide-up">
                {/* Embeds the newly designed comprehensive PortfolioView */}
                <PortfolioView />
            </div>

            {/* Optional dedicated details section underneath if needed */}
            <div className="relative z-10 grid grid-cols-1 mt-6 animate-slide-up" style={{ animationDelay: "150ms" }}>
                <Card className="glass-panel border-white/10 bg-black/40">
                    <CardHeader className="border-b border-white/5 bg-white/[0.02] py-4">
                        <CardTitle className="text-xs font-black font-mono text-muted-foreground uppercase tracking-widest">
                            Recent_Execution_Log
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                        <Table>
                            <TableHeader>
                                <TableRow className="border-white/5 hover:bg-transparent">
                                    <TableHead className="text-[10px] font-mono text-muted-foreground">TIMESTAMP</TableHead>
                                    <TableHead className="text-[10px] font-mono text-muted-foreground">ASSET</TableHead>
                                    <TableHead className="text-[10px] font-mono text-muted-foreground">ACTION</TableHead>
                                    <TableHead className="text-right text-[10px] font-mono text-muted-foreground">SIZE</TableHead>
                                    <TableHead className="text-right text-[10px] font-mono text-muted-foreground">FILL PRICE</TableHead>
                                    <TableHead className="text-right text-[10px] font-mono text-muted-foreground">ROUTING</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {[
                                    { time: "14:23:45.021", asset: "SPY 505C 0DTE", action: "BOT", size: "150", price: "$2.45", route: "SMART" },
                                    { time: "14:15:12.115", asset: "BTC/USD", action: "SOLD", size: "2.5", price: "$64,210.00", route: "KRAKEN" },
                                    { time: "13:58:04.992", asset: "ETH_ETF_APPROVAL", action: "BOT", size: "5,000", price: "$0.87", route: "POLY" },
                                ].map((t, i) => (
                                    <TableRow key={i} className="border-white/5 hover:bg-white/[0.02] transition-colors">
                                        <TableCell className="font-mono text-xs text-muted-foreground">{t.time}</TableCell>
                                        <TableCell className="font-mono text-xs font-bold text-white">{t.asset}</TableCell>
                                        <TableCell className="font-mono text-xs">
                                            <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${t.action === 'BOT' ? 'bg-primary/10 text-primary border border-primary/20' : 'bg-rose-500/10 text-rose-500 border border-rose-500/20'}`}>
                                                {t.action}
                                            </span>
                                        </TableCell>
                                        <TableCell className="font-mono text-xs text-right text-white">{t.size}</TableCell>
                                        <TableCell className="font-mono text-xs text-right text-muted-foreground">{t.price}</TableCell>
                                        <TableCell className="font-mono text-xs text-right">
                                            <span className="text-[10px] text-muted-foreground border border-white/10 px-1.5 py-0.5 rounded bg-white/5">{t.route}</span>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            </div>
        </main>
    );
}
