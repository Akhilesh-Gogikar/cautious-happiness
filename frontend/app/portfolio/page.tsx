"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { Link, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { useToast } from "@/components/ui/use-toast";
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

// Define Types
type Position = {
    id: string;
    side: string;
    shares: string;
    avgEntry: string;
    current: string;
    pnl: string;
    pnlPercent: string;
}

export default function PortfolioPage() {
    const { toast } = useToast();
    const [positions, setPositions] = useState<Position[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    // Initial Mock Data Fallback
    const mockPositions: Position[] = [
        { id: "ETH_ETF_APPROVAL", side: "YES", shares: "1,500", avgEntry: "$0.85", current: "$0.92", pnl: "+$105.00", pnlPercent: "+8.2%" },
        { id: "FED_RATE_HIKE_MAR", side: "NO", shares: "500", avgEntry: "$0.40", current: "$0.32", pnl: "-$40.00", pnlPercent: "-20.0%" },
        { id: "TRUMP_WIN", side: "YES", shares: "10,000", avgEntry: "$0.52", current: "$0.55", pnl: "+$300.00", pnlPercent: "+5.7%" },
    ];

    useEffect(() => {
        // Fetch real portfolio data
        const fetchPortfolio = async () => {
            try {
                // In a real app we would use a proper fetch wrapper with auth headers
                // For this demo we rely on browser session or mock
                const res = await fetch("http://localhost:8000/portfolio");
                if (res.ok) {
                    const data = await res.json();
                    if (data.positions && data.positions.length > 0) {
                        // Transform basic API data to UI format if needed
                        // For now keep using mock if API returns empty structure
                        // setPositions(data.positions);
                        setPositions(mockPositions);
                    } else {
                        setPositions(mockPositions);
                    }
                } else {
                    setPositions(mockPositions);
                }
            } catch (e) {
                console.error(e);
                setPositions(mockPositions);
            } finally {
                setIsLoading(false);
            }
        };
        fetchPortfolio();
    }, []);

    const handleKillSwitch = async () => {
        try {
            const res = await fetch("http://localhost:8000/trade/panic", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    // "Authorization": "Bearer ..." // in prod
                }
            });
            const data = await res.json();

            if (data.status === "success") {
                toast({
                    title: "EMERGENCY STOP ACTIVATED",
                    description: `Cancelled ${data.cancelled_db_orders} active bots and clearing open orders.`,
                    variant: "destructive",
                });
            } else {
                toast({
                    title: "Kill Switch Failed",
                    description: "Could not verify cancellation.",
                    variant: "destructive",
                });
            }
        } catch (e) {
            toast({
                title: "Connection Error",
                description: "Failed to reach server for Emergency Stop.",
                variant: "destructive",
            });
        }
    };

    return (
        <main className="min-h-screen p-6 space-y-8 max-w-[1400px] mx-auto bg-black text-green-500 font-mono">
            <header className="flex justify-between items-center border-b border-green-900 pb-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tighter text-green-500 italic">
                        POLYMARKET <span className="text-white not-italic">PORTFOLIO</span>
                    </h1>
                    <a href="/" className="text-xs text-green-700 font-mono mt-1 hover:text-green-500 hover:underline">
                        &lt; RETURN TO TERMINAL
                    </a>
                </div>
                <div className="flex items-center gap-4">
                    <AlertDialog>
                        <AlertDialogTrigger asChild>
                            <Button variant="destructive" className="bg-red-600 hover:bg-red-700 text-white font-bold animate-pulse">
                                <AlertTriangle className="mr-2 h-4 w-4" /> EMERGENCY STOP
                            </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent className="bg-zinc-900 border-red-800 text-white">
                            <AlertDialogHeader>
                                <AlertDialogTitle className="text-red-500">INITIATE KILL SWITCH?</AlertDialogTitle>
                                <AlertDialogDescription className="text-zinc-400">
                                    This will immediately:
                                    <ul className="list-disc pl-5 mt-2 space-y-1">
                                        <li>Stop all active trading algorithms</li>
                                        <li>Cancel all open orders on the exchange</li>
                                        <li>Liquidate risk (optional configuration)</li>
                                    </ul>
                                    <br />
                                    <strong>This action cannot be undone.</strong>
                                </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                                <AlertDialogCancel className="bg-zinc-800 hover:bg-zinc-700 text-white border-zinc-700">Cancel</AlertDialogCancel>
                                <AlertDialogAction onClick={handleKillSwitch} className="bg-red-600 hover:bg-red-700 text-white">CONFIRM KILL</AlertDialogAction>
                            </AlertDialogFooter>
                        </AlertDialogContent>
                    </AlertDialog>
                    <ConnectButton showBalance={true} />
                </div>
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
