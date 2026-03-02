"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Wallet, TrendingUp, BarChart3, AlertCircle, RefreshCw } from "lucide-react";

interface AlpacaAccount {
    account_number: string;
    equity: string;
    cash: string;
    buying_power: string;
    currency: string;
}

interface AlpacaPosition {
    symbol: string;
    qty: string;
    avg_entry_price: string;
    current_price: string;
    unrealized_pl: string;
}

export function AlpacaDashboard() {
    const [account, setAccount] = useState<AlpacaAccount | null>(null);
    const [positions, setPositions] = useState<AlpacaPosition[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('token');
            const apiKey = localStorage.getItem("ALPACA_API_KEY");
            const secretKey = localStorage.getItem("ALPACA_SECRET_KEY");

            const headers: Record<string, string> = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;
            if (apiKey) headers['x-alpaca-api-key'] = apiKey;
            if (secretKey) headers['x-alpaca-secret'] = secretKey;

            const accountResp = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/tools/call`, {
                method: 'POST',
                headers,
                body: JSON.stringify({ connector: 'alpaca', name: 'get_account', arguments: {} })
            });

            if (accountResp.ok) {
                const data = await accountResp.json();
                setAccount(data);
            } else {
                setError("Failed to fetch Alpaca account. Ensure credentials are set.");
            }

            const positionsResp = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/tools/call`, {
                method: 'POST',
                headers,
                body: JSON.stringify({ connector: 'alpaca', name: 'list_positions', arguments: {} })
            });

            if (positionsResp.ok) {
                const data = await positionsResp.json();
                setPositions(data);
            }
        } catch (err) {
            setError("Connection error. Is the backend running?");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const apiKey = localStorage.getItem("ALPACA_API_KEY");
        if (apiKey) {
            fetchData();
        } else {
            setLoading(false);
            setError("No Alpaca credentials found in settings. Please configure them in SYSTEM_CONFIG.");
        }
    }, []);

    if (loading && !account) {
        return (
            <Card className="glass-card border-white/10 bg-black/40">
                <CardContent className="p-6 flex items-center justify-center">
                    <RefreshCw className="w-6 h-6 text-primary animate-spin" />
                    <span className="ml-3 font-mono text-xs text-muted-foreground uppercase tracking-widest">Loading_Alpaca_Data...</span>
                </CardContent>
            </Card>
        );
    }

    if (error) {
        return (
            <Card className="glass-card border-red-500/20 bg-red-500/5">
                <CardContent className="p-6 flex flex-col items-center justify-center text-center">
                    <AlertCircle className="w-8 h-8 text-red-500 mb-2" />
                    <div className="text-xs font-black font-mono text-white uppercase mb-1">Integration_Error</div>
                    <p className="text-[10px] text-red-400 font-mono italic">{error}</p>
                    <button
                        onClick={fetchData}
                        className="mt-4 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded font-mono text-[10px] text-white transition-colors"
                    >
                        RETRY_CONNECTION
                    </button>
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/10 rounded-lg border border-primary/20">
                        <TrendingUp className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                        <h2 className="text-sm font-black text-white uppercase tracking-tighter">Alpaca_Markets</h2>
                        <div className="flex items-center gap-2">
                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                            <span className="text-[9px] font-mono text-muted-foreground uppercase">Connection_Active // Paper_Trading</span>
                        </div>
                    </div>
                </div>
                <button
                    onClick={fetchData}
                    className="p-2 hover:bg-white/5 rounded-full transition-colors text-muted-foreground hover:text-white"
                >
                    <RefreshCw className="w-4 h-4" />
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="glass-card border-white/10 bg-black/40 relative overflow-hidden group">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
                            <Wallet className="w-4 h-4 text-primary" /> Account_Equity
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-black text-white tracking-tight">
                            ${parseFloat(account?.equity || "0").toLocaleString()}
                        </div>
                        <div className="text-[9px] font-mono text-muted-foreground mt-1 lowercase">
                            Cash: ${parseFloat(account?.cash || "0").toLocaleString()} {account?.currency}
                        </div>
                    </CardContent>
                </Card>

                <Card className="glass-card border-white/10 bg-black/40 relative overflow-hidden group">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-[10px] font-black font-mono text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
                            <BarChart3 className="w-4 h-4 text-indigo" /> Buying_Power
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-black text-white tracking-tight">
                            ${parseFloat(account?.buying_power || "0").toLocaleString()}
                        </div>
                        <div className="text-[9px] font-mono text-muted-foreground mt-1 lowercase">
                            Available for immediate execution
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card className="glass-panel border-white/10 bg-black/40 overflow-hidden">
                <CardHeader className="border-b border-white/5 bg-white/[0.02] py-3">
                    <CardTitle className="text-xs font-black font-mono text-muted-foreground uppercase tracking-widest flex justify-between items-center">
                        Active_Positions
                        <Badge variant="outline" className="text-[9px] font-mono border-white/10 text-muted-foreground uppercase">
                            Count: {positions.length}
                        </Badge>
                    </CardTitle>
                </CardHeader>
                <div className="relative overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-white/[0.02] text-[9px] font-black font-mono uppercase text-muted-foreground/60 tracking-wider">
                            <tr>
                                <th className="px-6 py-3">Symbol</th>
                                <th className="px-6 py-3 text-right">Qty</th>
                                <th className="px-6 py-3 text-right">Avg Entry</th>
                                <th className="px-6 py-3 text-right">Mark Price</th>
                                <th className="px-6 py-3 text-right">Unrealized PnL</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {positions.length > 0 ? positions.map((pos, i) => (
                                <tr key={i} className="hover:bg-white/5 transition-colors group">
                                    <td className="px-6 py-3 text-xs font-bold text-white font-mono">{pos.symbol}</td>
                                    <td className="px-6 py-3 text-right font-mono text-xs text-muted-foreground">{pos.qty}</td>
                                    <td className="px-6 py-3 text-right font-mono text-xs text-muted-foreground">${parseFloat(pos.avg_entry_price).toFixed(2)}</td>
                                    <td className="px-6 py-3 text-right font-mono text-xs text-white font-bold">${parseFloat(pos.current_price).toFixed(2)}</td>
                                    <td className={`px-6 py-3 text-right font-mono text-xs font-bold ${parseFloat(pos.unrealized_pl) >= 0 ? 'text-primary' : 'text-red-400'}`}>
                                        {parseFloat(pos.unrealized_pl) >= 0 ? '+' : ''}${parseFloat(pos.unrealized_pl).toFixed(2)}
                                    </td>
                                </tr>
                            )) : (
                                <tr>
                                    <td colSpan={5} className="px-6 py-8 text-center text-[10px] font-mono text-muted-foreground italic uppercase">
                                        No_Active_Positions_Found
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}
