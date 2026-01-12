"use client";

import { useEffect, useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Download } from "lucide-react";

interface TaxLot {
    id: number;
    exchange: string;
    market_question: string;
    purchase_date: string;
    shares_purchased: number;
    shares_remaining: number;
    cost_basis_per_share: number;
    total_cost_basis: number;
    is_closed: boolean;
}

export function TaxLotTable({ taxYear }: { taxYear: number }) {
    const [lots, setLots] = useState<TaxLot[]>([]);
    const [loading, setLoading] = useState(true);
    const [exchangeFilter, setExchangeFilter] = useState<string>("all");
    const [statusFilter, setStatusFilter] = useState<string>("all");

    useEffect(() => {
        const fetchLots = async () => {
            try {
                const token = localStorage.getItem("token");
                let url = `http://localhost:8000/api/tax/lots?`;
                if (exchangeFilter !== "all") url += `exchange=${exchangeFilter}&`;
                if (statusFilter !== "all") url += `is_closed=${statusFilter === "closed"}`;

                const response = await fetch(url, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                if (response.ok) {
                    const data = await response.json();
                    setLots(data);
                }
            } catch (error) {
                console.error("Error fetching tax lots:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchLots();
    }, [taxYear, exchangeFilter, statusFilter]);

    const exportToCSV = () => {
        const headers = ["ID", "Exchange", "Market", "Purchase Date", "Shares", "Cost/Share", "Total Cost", "Status"];
        const rows = lots.map((lot) => [
            lot.id,
            lot.exchange,
            lot.market_question,
            new Date(lot.purchase_date).toLocaleDateString(),
            lot.shares_remaining,
            lot.cost_basis_per_share.toFixed(4),
            lot.total_cost_basis.toFixed(2),
            lot.is_closed ? "Closed" : "Open",
        ]);

        const csvContent = [headers, ...rows].map((row) => row.join(",")).join("\n");
        const blob = new Blob([csvContent], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `tax_lots_${taxYear}.csv`;
        a.click();
    };

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <div className="flex gap-2">
                    <Select value={exchangeFilter} onValueChange={setExchangeFilter}>
                        <SelectTrigger className="w-[150px]">
                            <SelectValue placeholder="Exchange" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Exchanges</SelectItem>
                            <SelectItem value="KALSHI">Kalshi</SelectItem>
                            <SelectItem value="POLYMARKET">AlphaSignals</SelectItem>
                        </SelectContent>
                    </Select>

                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                        <SelectTrigger className="w-[150px]">
                            <SelectValue placeholder="Status" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Lots</SelectItem>
                            <SelectItem value="open">Open Only</SelectItem>
                            <SelectItem value="closed">Closed Only</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <Button onClick={exportToCSV} variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    Export CSV
                </Button>
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Exchange</TableHead>
                            <TableHead>Market</TableHead>
                            <TableHead>Purchase Date</TableHead>
                            <TableHead className="text-right">Shares</TableHead>
                            <TableHead className="text-right">Cost/Share</TableHead>
                            <TableHead className="text-right">Total Cost</TableHead>
                            <TableHead>Status</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan={7} className="text-center py-8">
                                    Loading...
                                </TableCell>
                            </TableRow>
                        ) : lots.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                                    No tax lots found
                                </TableCell>
                            </TableRow>
                        ) : (
                            lots.map((lot) => (
                                <TableRow key={lot.id}>
                                    <TableCell>
                                        <Badge variant={lot.exchange === "KALSHI" ? "default" : "secondary"}>
                                            {lot.exchange}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="max-w-md truncate">{lot.market_question}</TableCell>
                                    <TableCell>{new Date(lot.purchase_date).toLocaleDateString()}</TableCell>
                                    <TableCell className="text-right">{lot.shares_remaining.toFixed(2)}</TableCell>
                                    <TableCell className="text-right">${lot.cost_basis_per_share.toFixed(4)}</TableCell>
                                    <TableCell className="text-right">${lot.total_cost_basis.toFixed(2)}</TableCell>
                                    <TableCell>
                                        <Badge variant={lot.is_closed ? "outline" : "default"}>
                                            {lot.is_closed ? "Closed" : "Open"}
                                        </Badge>
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
