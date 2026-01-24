"use client";

import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TaxSummaryCards } from "@/components/tax/tax-summary-cards";
import { TaxLotTable } from "@/components/tax/tax-lot-table";
import { TaxTransactionTable } from "@/components/tax/tax-transaction-table";
import { TaxReportGenerator } from "@/components/tax/tax-report-generator";
import { TaxSettingsForm } from "@/components/tax/tax-settings-form";
import { Shield, FileText, Settings, List, Receipt } from "lucide-react";

function TaxContent() {
    const [taxYear, setTaxYear] = useState(new Date().getFullYear());

    return (
        <div className="p-6 space-y-6">
            {/* Year Selector */}
            <div className="flex justify-between items-center">
                <div>
                    <p className="text-white/60 text-sm">
                        FIFO/LIFO tracking with Section 1256 (Kalshi) and standard treatment (Polymarket)
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <span className="text-xs font-mono text-muted-foreground uppercase">Tax Year:</span>
                    <select
                        value={taxYear}
                        onChange={(e) => setTaxYear(Number(e.target.value))}
                        className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm font-mono focus:outline-none focus:border-primary"
                    >
                        {[2026, 2025, 2024, 2023].map((year) => (
                            <option key={year} value={year} className="bg-black">
                                {year}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Summary Cards */}
            <TaxSummaryCards taxYear={taxYear} />

            {/* Tabbed Content */}
            <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                <Tabs defaultValue="lots" className="w-full">
                    <div className="border-b border-white/10 px-4">
                        <TabsList className="bg-transparent h-12 gap-4">
                            <TabsTrigger value="lots" className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary rounded-lg px-4">
                                <List className="w-4 h-4 mr-2" />
                                Tax Lots
                            </TabsTrigger>
                            <TabsTrigger value="transactions" className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary rounded-lg px-4">
                                <Receipt className="w-4 h-4 mr-2" />
                                Transactions
                            </TabsTrigger>
                            <TabsTrigger value="reports" className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary rounded-lg px-4">
                                <FileText className="w-4 h-4 mr-2" />
                                Reports
                            </TabsTrigger>
                            <TabsTrigger value="settings" className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary rounded-lg px-4">
                                <Settings className="w-4 h-4 mr-2" />
                                Settings
                            </TabsTrigger>
                        </TabsList>
                    </div>

                    <TabsContent value="lots" className="p-6">
                        <div className="mb-4">
                            <h3 className="text-lg font-bold text-white">Tax Lot Details</h3>
                            <p className="text-sm text-muted-foreground">Purchase lots with cost basis tracking</p>
                        </div>
                        <TaxLotTable taxYear={taxYear} />
                    </TabsContent>

                    <TabsContent value="transactions" className="p-6">
                        <div className="mb-4">
                            <h3 className="text-lg font-bold text-white">Taxable Transactions</h3>
                            <p className="text-sm text-muted-foreground">Sales and mark-to-market events for {taxYear}</p>
                        </div>
                        <TaxTransactionTable taxYear={taxYear} />
                    </TabsContent>

                    <TabsContent value="reports" className="p-6">
                        <div className="mb-4">
                            <h3 className="text-lg font-bold text-white">Tax Reports</h3>
                            <p className="text-sm text-muted-foreground">Generate Form 6781 (Kalshi) and Form 8949 (Polymarket) data</p>
                        </div>
                        <TaxReportGenerator taxYear={taxYear} />
                    </TabsContent>

                    <TabsContent value="settings" className="p-6">
                        <div className="mb-4">
                            <h3 className="text-lg font-bold text-white">Tax Settings</h3>
                            <p className="text-sm text-muted-foreground">Accounting methods and preferences</p>
                        </div>
                        <TaxSettingsForm taxYear={taxYear} />
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    );
}

export default function TaxPage() {
    return (
        <DashboardLayout title="TAX CENTER" subtitle="COMPLIANCE_ACTIVE" icon={Shield}>
            <TaxContent />
        </DashboardLayout>
    );
}
