"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, DollarSign, FileText } from "lucide-react";

interface TaxSummary {
    tax_year: number;
    summary: {
        kalshi: {
            realized_gain_loss: number;
            long_term_portion: number;
            short_term_portion: number;
            unrealized_gain_loss: number;
            num_transactions: number;
        };
        polymarket: {
            realized_short_term: number;
            realized_long_term: number;
            realized_total: number;
            unrealized_gain_loss: number;
            num_transactions: number;
            wash_sale_disallowed: number;
        };
        combined: {
            total_realized: number;
            total_unrealized: number;
        };
    };
}

export function TaxSummaryCards({ taxYear }: { taxYear: number }) {
    const [summary, setSummary] = useState<TaxSummary | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSummary = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await fetch(`http://localhost:8000/api/tax/summary/${taxYear}`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                if (response.ok) {
                    const data = await response.json();
                    setSummary(data);
                }
            } catch (error) {
                console.error("Error fetching tax summary:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchSummary();
    }, [taxYear]);

    if (loading || !summary) {
        return (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {[1, 2, 3, 4].map((i) => (
                    <Card key={i} className="animate-pulse">
                        <CardHeader className="pb-2">
                            <div className="h-4 bg-muted rounded w-3/4"></div>
                        </CardHeader>
                        <CardContent>
                            <div className="h-8 bg-muted rounded w-1/2"></div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        );
    }

    const { kalshi, polymarket, combined } = summary.summary;

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Realized Gains</CardTitle>
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className={`text-2xl font-bold ${combined.total_realized >= 0 ? "text-green-600" : "text-red-600"}`}>
                        ${combined.total_realized.toFixed(2)}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                        Kalshi: ${kalshi.realized_gain_loss.toFixed(2)} | AlphaSignals: ${polymarket.realized_total.toFixed(2)}
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Kalshi (Section 1256)</CardTitle>
                    <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">${kalshi.realized_gain_loss.toFixed(2)}</div>
                    <p className="text-xs text-muted-foreground mt-1">
                        60% LT: ${kalshi.long_term_portion.toFixed(2)} | 40% ST: ${kalshi.short_term_portion.toFixed(2)}
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">AlphaSignals (Capital Gains)</CardTitle>
                    <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">${polymarket.realized_total.toFixed(2)}</div>
                    <p className="text-xs text-muted-foreground mt-1">
                        LT: ${polymarket.realized_long_term.toFixed(2)} | ST: ${polymarket.realized_short_term.toFixed(2)}
                    </p>
                </CardContent>
            </Card>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Unrealized Gains</CardTitle>
                    {combined.total_unrealized >= 0 ? (
                        <TrendingUp className="h-4 w-4 text-green-600" />
                    ) : (
                        <TrendingDown className="h-4 w-4 text-red-600" />
                    )}
                </CardHeader>
                <CardContent>
                    <div className={`text-2xl font-bold ${combined.total_unrealized >= 0 ? "text-green-600" : "text-red-600"}`}>
                        ${combined.total_unrealized.toFixed(2)}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                        Kalshi: ${kalshi.unrealized_gain_loss.toFixed(2)} | AlphaSignals: ${polymarket.unrealized_gain_loss.toFixed(2)}
                    </p>
                </CardContent>
            </Card>

            {polymarket.wash_sale_disallowed > 0 && (
                <Card className="md:col-span-2 lg:col-span-4 border-yellow-500">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-yellow-600">Wash Sale Alert</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm">
                            ${polymarket.wash_sale_disallowed.toFixed(2)} in losses disallowed due to wash sale rules.
                            Cost basis has been adjusted on repurchased lots.
                        </p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
