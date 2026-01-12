"use client";

import { useEffect, useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface TaxTransaction {
    id: number;
    transaction_type: string;
    exchange: string;
    market_question: string;
    transaction_date: string;
    shares: number;
    proceeds: number;
    cost_basis: number;
    gain_loss: number;
    holding_period_days: number;
    is_long_term: boolean;
    is_section_1256: boolean;
    long_term_portion: number | null;
    short_term_portion: number | null;
    wash_sale_disallowed: number;
    matching_method: string;
}

export function TaxTransactionTable({ taxYear }: { taxYear: number }) {
    const [transactions, setTransactions] = useState<TaxTransaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [exchangeFilter, setExchangeFilter] = useState<string>("all");

    useEffect(() => {
        const fetchTransactions = async () => {
            try {
                const token = localStorage.getItem("token");
                let url = `http://localhost:8000/api/tax/transactions/${taxYear}`;
                if (exchangeFilter !== "all") url += `?exchange=${exchangeFilter}`;

                const response = await fetch(url, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                if (response.ok) {
                    const data = await response.json();
                    setTransactions(data);
                }
            } catch (error) {
                console.error("Error fetching transactions:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchTransactions();
    }, [taxYear, exchangeFilter]);

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <Select value={exchangeFilter} onValueChange={setExchangeFilter}>
                    <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Exchange" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Exchanges</SelectItem>
                        <SelectItem value="KALSHI">Kalshi</SelectItem>
                        <SelectItem value="POLYMARKET">AlphaSignals</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Date</TableHead>
                            <TableHead>Exchange</TableHead>
                            <TableHead>Market</TableHead>
                            <TableHead className="text-right">Shares</TableHead>
                            <TableHead className="text-right">Proceeds</TableHead>
                            <TableHead className="text-right">Cost Basis</TableHead>
                            <TableHead className="text-right">Gain/Loss</TableHead>
                            <TableHead>Tax Treatment</TableHead>
                            <TableHead>Method</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan={9} className="text-center py-8">
                                    Loading...
                                </TableCell>
                            </TableRow>
                        ) : transactions.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                                    No transactions found for {taxYear}
                                </TableCell>
                            </TableRow>
                        ) : (
                            transactions.map((txn) => (
                                <TableRow key={txn.id}>
                                    <TableCell>{new Date(txn.transaction_date).toLocaleDateString()}</TableCell>
                                    <TableCell>
                                        <Badge variant={txn.exchange === "KALSHI" ? "default" : "secondary"}>
                                            {txn.exchange}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="max-w-xs truncate">{txn.market_question}</TableCell>
                                    <TableCell className="text-right">{txn.shares.toFixed(2)}</TableCell>
                                    <TableCell className="text-right">${txn.proceeds.toFixed(2)}</TableCell>
                                    <TableCell className="text-right">${txn.cost_basis.toFixed(2)}</TableCell>
                                    <TableCell className={`text-right font-medium ${txn.gain_loss >= 0 ? "text-green-600" : "text-red-600"}`}>
                                        ${txn.gain_loss.toFixed(2)}
                                    </TableCell>
                                    <TableCell>
                                        {txn.is_section_1256 ? (
                                            <div className="text-xs">
                                                <div>Section 1256</div>
                                                <div className="text-muted-foreground">
                                                    60% LT / 40% ST
                                                </div>
                                            </div>
                                        ) : (
                                            <Badge variant={txn.is_long_term ? "default" : "outline"}>
                                                {txn.is_long_term ? "Long-Term" : "Short-Term"}
                                            </Badge>
                                        )}
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant="outline">{txn.matching_method}</Badge>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
