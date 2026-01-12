"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TaxSummaryCards } from "@/components/tax/tax-summary-cards";
import { TaxLotTable } from "@/components/tax/tax-lot-table";
import { TaxTransactionTable } from "@/components/tax/tax-transaction-table";
import { TaxReportGenerator } from "@/components/tax/tax-report-generator";
import { TaxSettingsForm } from "@/components/tax/tax-settings-form";
import { Loader2 } from "lucide-react";

export default function TaxPage() {
    const [loading, setLoading] = useState(true);
    const [taxYear, setTaxYear] = useState(new Date().getFullYear());

    useEffect(() => {
        // Simulate initial load
        setTimeout(() => setLoading(false), 500);
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6 space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Tax Accounting</h1>
                    <p className="text-muted-foreground">
                        FIFO/LIFO tracking with distinct treatments for Kalshi (Section 1256) and AlphaSignals
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <label className="text-sm font-medium">Tax Year:</label>
                    <select
                        value={taxYear}
                        onChange={(e) => setTaxYear(Number(e.target.value))}
                        className="px-3 py-2 border rounded-md bg-background"
                    >
                        {[2026, 2025, 2024, 2023].map((year) => (
                            <option key={year} value={year}>
                                {year}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            <TaxSummaryCards taxYear={taxYear} />

            <Tabs defaultValue="lots" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="lots">Tax Lots</TabsTrigger>
                    <TabsTrigger value="transactions">Transactions</TabsTrigger>
                    <TabsTrigger value="reports">Reports</TabsTrigger>
                    <TabsTrigger value="settings">Settings</TabsTrigger>
                </TabsList>

                <TabsContent value="lots" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Tax Lot Details</CardTitle>
                            <CardDescription>
                                View all purchase lots with cost basis tracking
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <TaxLotTable taxYear={taxYear} />
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="transactions" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Taxable Transactions</CardTitle>
                            <CardDescription>
                                All sales and mark-to-market events for {taxYear}
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <TaxTransactionTable taxYear={taxYear} />
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="reports" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Tax Reports</CardTitle>
                            <CardDescription>
                                Generate Form 6781 (Kalshi) and Form 8949 (AlphaSignals) data
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <TaxReportGenerator taxYear={taxYear} />
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="settings" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Tax Settings</CardTitle>
                            <CardDescription>
                                Configure accounting methods and preferences
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <TaxSettingsForm taxYear={taxYear} />
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}
