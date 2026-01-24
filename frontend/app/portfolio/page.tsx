"use client";

import { DashboardLayout } from "@/components/layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { AlertTriangle, PieChart, TrendingUp, Wallet, DollarSign } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { api } from "@/lib/api";

type Position = {
    id: string;
    side: string;
    shares: string;
    avgEntry: string;
    current: string;
    pnl: string;
    pnlPercent: string;
};

const mockPositions: Position[] = [
    { id: "ETH_ETF_APPROVAL", side: "YES", shares: "1,500", avgEntry: "$0.85", current: "$0.92", pnl: "+$105.00", pnlPercent: "+8.2%" },
    { id: "FED_RATE_HIKE_MAR", side: "NO", shares: "500", avgEntry: "$0.40", current: "$0.32", pnl: "-$40.00", pnlPercent: "-20.0%" },
    { id: "TRUMP_WIN", side: "YES", shares: "10,000", avgEntry: "$0.52", current: "$0.55", pnl: "+$300.00", pnlPercent: "+5.7%" },
    { id: "BTC_100K_2025", side: "YES", shares: "2,500", avgEntry: "$0.65", current: "$0.72", pnl: "+$175.00", pnlPercent: "+10.8%" },
];

function PortfolioContent() {
    const [positions, setPositions] = useState<Position[]>(mockPositions);

    const handleKillSwitch = async () => {
        try {
            await api.post("/trade/panic");
            toast.success("Emergency stop activated - all orders cancelled");
        } catch (e) {
            toast.error("Failed to activate kill switch");
        }
    };

    const totalEquity = 12450.0;
    const totalPnL = 540.0;
    const exposure = 8200.0;

    return (
        <div className="p-6 space-y-6">
            {/* Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white/5 border border-white/10 rounded-xl p-5 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                    <div className="relative z-10">
                        <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">
                            <Wallet className="w-3 h-3" />
                            Total Equity
                        </div>
                        <div className="text-3xl font-black text-white">${totalEquity.toLocaleString()}</div>
                        <div className="text-xs text-primary mt-1">+3.2% Today</div>
                    </div>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-5">
                    <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">
                        <TrendingUp className="w-3 h-3" />
                        Unrealized P&L
                    </div>
                    <div className={`text-2xl font-black ${totalPnL >= 0 ? 'text-primary' : 'text-red-500'}`}>
                        {totalPnL >= 0 ? '+' : ''}${totalPnL.toLocaleString()}
                    </div>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-5">
                    <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-2">
                        <DollarSign className="w-3 h-3" />
                        Market Exposure
                    </div>
                    <div className="text-2xl font-black text-white">${exposure.toLocaleString()}</div>
                </div>

                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-5 flex items-center justify-center">
                    <AlertDialog>
                        <AlertDialogTrigger asChild>
                            <Button variant="destructive" className="w-full bg-red-600 hover:bg-red-700 text-white font-black uppercase tracking-wider">
                                <AlertTriangle className="mr-2 h-4 w-4" />
                                Emergency Stop
                            </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent className="bg-zinc-900 border-red-800 text-white">
                            <AlertDialogHeader>
                                <AlertDialogTitle className="text-red-500">INITIATE KILL SWITCH?</AlertDialogTitle>
                                <AlertDialogDescription className="text-zinc-400">
                                    This will immediately stop all trading algorithms and cancel open orders.
                                    <br /><br />
                                    <strong>This action cannot be undone.</strong>
                                </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                                <AlertDialogCancel className="bg-zinc-800 hover:bg-zinc-700 text-white border-zinc-700">Cancel</AlertDialogCancel>
                                <AlertDialogAction onClick={handleKillSwitch} className="bg-red-600 hover:bg-red-700 text-white">CONFIRM</AlertDialogAction>
                            </AlertDialogFooter>
                        </AlertDialogContent>
                    </AlertDialog>
                </div>
            </div>

            {/* Positions Table */}
            <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                <div className="p-4 border-b border-white/10 flex items-center justify-between">
                    <h2 className="text-xs font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                        <PieChart className="w-4 h-4 text-primary" />
                        Active Positions
                    </h2>
                    <span className="text-[10px] bg-primary/20 text-primary px-2 py-1 rounded font-mono">{positions.length} OPEN</span>
                </div>
                <Table>
                    <TableHeader>
                        <TableRow className="border-white/10 hover:bg-transparent">
                            <TableHead className="text-muted-foreground text-xs font-mono">MARKET</TableHead>
                            <TableHead className="text-muted-foreground text-xs font-mono">SIDE</TableHead>
                            <TableHead className="text-right text-muted-foreground text-xs font-mono">SHARES</TableHead>
                            <TableHead className="text-right text-muted-foreground text-xs font-mono">AVG ENTRY</TableHead>
                            <TableHead className="text-right text-muted-foreground text-xs font-mono">MARK</TableHead>
                            <TableHead className="text-right text-muted-foreground text-xs font-mono">P&L</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {positions.map((p) => (
                            <TableRow key={p.id} className="border-white/5 hover:bg-white/5">
                                <TableCell className="font-mono text-xs text-white">{p.id}</TableCell>
                                <TableCell>
                                    <span className={`font-mono text-xs font-bold px-2 py-0.5 rounded ${p.side === 'YES' ? 'bg-primary/20 text-primary' : 'bg-red-500/20 text-red-400'}`}>
                                        {p.side}
                                    </span>
                                </TableCell>
                                <TableCell className="font-mono text-xs text-right text-white/70">{p.shares}</TableCell>
                                <TableCell className="font-mono text-xs text-right text-white/70">{p.avgEntry}</TableCell>
                                <TableCell className="font-mono text-xs text-right text-white">{p.current}</TableCell>
                                <TableCell className={`font-mono text-xs text-right font-bold ${p.pnl.startsWith('+') ? 'text-primary' : 'text-red-500'}`}>
                                    {p.pnl} <span className="text-white/40">({p.pnlPercent})</span>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}

export default function PortfolioPage() {
    return (
        <DashboardLayout title="PORTFOLIO" subtitle="POSITIONS_LIVE" icon={PieChart}>
            <PortfolioContent />
        </DashboardLayout>
    );
}
