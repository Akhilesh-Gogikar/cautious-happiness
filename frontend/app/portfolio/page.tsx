"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { Link } from "lucide-react";

export default function PortfolioPage() {
    // Mock Data for "My Positions"
    const positions = [
        { id: "ETH_ETF_APPROVAL", side: "YES", shares: "1,500", avgEntry: "$0.85", current: "$0.92", pnl: "+$105.00", pnlPercent: "+8.2%" },
        { id: "FED_RATE_HIKE_MAR", side: "NO", shares: "500", avgEntry: "$0.40", current: "$0.32", pnl: "-$40.00", pnlPercent: "-20.0%" },
        { id: "TRUMP_WIN", side: "YES", shares: "10,000", avgEntry: "$0.52", current: "$0.55", pnl: "+$300.00", pnlPercent: "+5.7%" },
    ];

    return (
        <main className="min-h-screen p-6 space-y-8 max-w-[1400px] mx-auto">
            <header className="flex justify-between items-center border-b border-green-900 pb-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tighter text-green-500 italic">
                        POLYMARKET <span className="text-white not-italic">PORTFOLIO</span>
                    </h1>
                    <a href="/" className="text-xs text-green-700 font-mono mt-1 hover:text-green-500 hover:underline">
                        &lt; RETURN TO TERMINAL
                    </a>
                </div>
                <ConnectButton showBalance={true} />
            </header>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card className="md:col-span-1 border-green-900 bg-black/50">
                    <CardHeader>
                        <CardTitle className="text-green-500 text-sm">TOTAL EQUITY</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl text-green-400 font-mono">$12,450.00</div>
                        <div className="text-xs text-green-600 mt-1">+3.2% Today</div>
                    </CardContent>
                </Card>

                <Card className="md:col-span-3 border-green-900 bg-black/50">
                    <CardHeader>
                        <CardTitle className="text-green-500 text-sm">ACTIVE POSITIONS</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow className="border-green-900 hover:bg-transparent">
                                    <TableHead className="text-green-700">MARKET</TableHead>
                                    <TableHead className="text-green-700">SIDE</TableHead>
                                    <TableHead className="text-right text-green-700">SHARES</TableHead>
                                    <TableHead className="text-right text-green-700">AVG ENTRY</TableHead>
                                    <TableHead className="text-right text-green-700">MARK</TableHead>
                                    <TableHead className="text-right text-green-700">P/L</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {positions.map((p) => (
                                    <TableRow key={p.id} className="border-green-900/50 hover:bg-green-900/10">
                                        <TableCell className="font-mono text-xs text-green-400">{p.id}</TableCell>
                                        <TableCell className="font-mono text-xs">
                                            <span className={p.side === 'YES' ? 'text-green-500' : 'text-red-500'}>{p.side}</span>
                                        </TableCell>
                                        <TableCell className="font-mono text-xs text-right text-green-600">{p.shares}</TableCell>
                                        <TableCell className="font-mono text-xs text-right text-green-600">{p.avgEntry}</TableCell>
                                        <TableCell className="font-mono text-xs text-right text-green-400">{p.current}</TableCell>
                                        <TableCell className={`font-mono text-xs text-right ${p.pnl.startsWith('+') ? 'text-green-400' : 'text-red-500'}`}>
                                            {p.pnl} ({p.pnlPercent})
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
