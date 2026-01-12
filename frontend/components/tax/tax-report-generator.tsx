"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Download, Loader2 } from "lucide-react";

export function TaxReportGenerator({ taxYear }: { taxYear: number }) {
    const [loading, setLoading] = useState<string | null>(null);

    const downloadReport = async (reportType: "form-6781" | "form-8949" | "summary" | "csv") => {
        setLoading(reportType);
        try {
            const token = localStorage.getItem("token");
            let url = `http://localhost:8000/api/tax/`;

            if (reportType === "csv") {
                url += `export/${taxYear}?format=csv`;
            } else if (reportType === "summary") {
                url += `summary/${taxYear}`;
            } else {
                url += `${reportType}/${taxYear}`;
            }

            const response = await fetch(url, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.ok) {
                if (reportType === "csv") {
                    const blob = await response.blob();
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = downloadUrl;
                    a.download = `tax_report_${taxYear}.csv`;
                    a.click();
                } else {
                    const data = await response.json();
                    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = downloadUrl;
                    a.download = `${reportType}_${taxYear}.json`;
                    a.click();
                }
            }
        } catch (error) {
            console.error("Error downloading report:", error);
        } finally {
            setLoading(null);
        }
    };

    return (
        <div className="grid gap-4 md:grid-cols-2">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5" />
                        Form 6781 (Kalshi)
                    </CardTitle>
                    <CardDescription>
                        Section 1256 Contracts - 60/40 Tax Treatment
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                        Download Form 6781 data for Kalshi contracts. This includes all Section 1256
                        contract gains/losses with the 60% long-term / 40% short-term split.
                    </p>
                    <Button
                        onClick={() => downloadReport("form-6781")}
                        disabled={loading === "form-6781"}
                        className="w-full"
                    >
                        {loading === "form-6781" ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <Download className="mr-2 h-4 w-4" />
                                Download Form 6781 Data
                            </>
                        )}
                    </Button>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5" />
                        Form 8949 (AlphaSignals)
                    </CardTitle>
                    <CardDescription>
                        Capital Gains and Losses - Schedule D
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                        Download Form 8949 / Schedule D data for AlphaSignals positions. Includes
                        short-term and long-term capital gains with wash sale adjustments.
                    </p>
                    <Button
                        onClick={() => downloadReport("form-8949")}
                        disabled={loading === "form-8949"}
                        className="w-full"
                    >
                        {loading === "form-8949" ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <Download className="mr-2 h-4 w-4" />
                                Download Form 8949 Data
                            </>
                        )}
                    </Button>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5" />
                        Complete Tax Summary
                    </CardTitle>
                    <CardDescription>
                        Comprehensive tax report for {taxYear}
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                        Download a complete tax summary including both exchanges, realized/unrealized
                        gains, and all transaction details.
                    </p>
                    <Button
                        onClick={() => downloadReport("summary")}
                        disabled={loading === "summary"}
                        variant="outline"
                        className="w-full"
                    >
                        {loading === "summary" ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <Download className="mr-2 h-4 w-4" />
                                Download Summary (JSON)
                            </>
                        )}
                    </Button>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5" />
                        Transaction Export
                    </CardTitle>
                    <CardDescription>
                        CSV export for spreadsheet analysis
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                        Export all transactions to CSV format for import into tax software or
                        spreadsheet analysis.
                    </p>
                    <Button
                        onClick={() => downloadReport("csv")}
                        disabled={loading === "csv"}
                        variant="outline"
                        className="w-full"
                    >
                        {loading === "csv" ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <Download className="mr-2 h-4 w-4" />
                                Download CSV Export
                            </>
                        )}
                    </Button>
                </CardContent>
            </Card>

            <Card className="md:col-span-2 border-yellow-500">
                <CardHeader>
                    <CardTitle className="text-yellow-600">Important Tax Notice</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-sm">
                        These reports are provided for informational purposes only and do not constitute
                        tax advice. Please consult with a qualified tax professional for guidance specific
                        to your situation. Kalshi contracts may qualify for Section 1256 treatment; verify
                        eligibility with your tax advisor.
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
