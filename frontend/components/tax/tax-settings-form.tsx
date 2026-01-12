"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent, CardDescription } from "@/components/ui/card";
import { Loader2, Save, CheckCircle2 } from "lucide-react";

interface TaxSettings {
    id: number;
    kalshi_method: string;
    polymarket_method: string;
    enable_wash_sale_detection: boolean;
    tax_year: number;
}

export function TaxSettingsForm({ taxYear }: { taxYear: number }) {
    const [settings, setSettings] = useState<TaxSettings | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await fetch(`http://localhost:8000/api/tax/settings?tax_year=${taxYear}`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                if (response.ok) {
                    const data = await response.json();
                    setSettings(data);
                }
            } catch (error) {
                console.error("Error fetching settings:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchSettings();
    }, [taxYear]);

    const saveSettings = async () => {
        if (!settings) return;

        setSaving(true);
        setSaved(false);
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`http://localhost:8000/api/tax/settings`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    kalshi_method: settings.kalshi_method,
                    polymarket_method: settings.polymarket_method,
                    enable_wash_sale_detection: settings.enable_wash_sale_detection,
                    tax_year: taxYear,
                }),
            });

            if (response.ok) {
                setSaved(true);
                setTimeout(() => setSaved(false), 3000);
            }
        } catch (error) {
            console.error("Error saving settings:", error);
        } finally {
            setSaving(false);
        }
    };

    if (loading || !settings) {
        return (
            <div className="flex items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <Card>
                <CardContent className="pt-6 space-y-4">
                    <CardDescription>
                        Configure tax accounting methods for each exchange. Changes apply to future transactions.
                    </CardDescription>

                    <div className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="kalshi-method">Kalshi Accounting Method</Label>
                            <Select
                                value={settings.kalshi_method}
                                onValueChange={(value) => setSettings({ ...settings, kalshi_method: value })}
                            >
                                <SelectTrigger id="kalshi-method">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="FIFO">FIFO (First-In-First-Out)</SelectItem>
                                    <SelectItem value="LIFO">LIFO (Last-In-First-Out)</SelectItem>
                                    <SelectItem value="SPECID">Specific Identification</SelectItem>
                                </SelectContent>
                            </Select>
                            <p className="text-xs text-muted-foreground">
                                Note: Kalshi contracts use Section 1256 treatment (60/40 split) regardless of method.
                            </p>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="polymarket-method">AlphaSignals Accounting Method</Label>
                            <Select
                                value={settings.polymarket_method}
                                onValueChange={(value) => setSettings({ ...settings, polymarket_method: value })}
                            >
                                <SelectTrigger id="polymarket-method">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="FIFO">FIFO (First-In-First-Out)</SelectItem>
                                    <SelectItem value="LIFO">LIFO (Last-In-First-Out)</SelectItem>
                                    <SelectItem value="SPECID">Specific Identification</SelectItem>
                                </SelectContent>
                            </Select>
                            <p className="text-xs text-muted-foreground">
                                FIFO is the IRS default. LIFO and SpecID require detailed record-keeping.
                            </p>
                        </div>

                        <div className="flex items-center justify-between space-x-2 pt-4">
                            <div className="space-y-1">
                                <Label htmlFor="wash-sale">Enable Wash Sale Detection</Label>
                                <p className="text-xs text-muted-foreground">
                                    Automatically detect and adjust for wash sales (AlphaSignals only)
                                </p>
                            </div>
                            <Switch
                                id="wash-sale"
                                checked={settings.enable_wash_sale_detection}
                                onCheckedChange={(checked) =>
                                    setSettings({ ...settings, enable_wash_sale_detection: checked })
                                }
                            />
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-blue-500">
                <CardContent className="pt-6 space-y-2">
                    <h4 className="font-semibold text-blue-600">Method Comparison</h4>
                    <div className="text-sm space-y-2">
                        <div>
                            <strong>FIFO:</strong> Sells oldest lots first. May result in higher gains in rising markets.
                        </div>
                        <div>
                            <strong>LIFO:</strong> Sells newest lots first. Can reduce gains in rising markets.
                        </div>
                        <div>
                            <strong>Specific ID:</strong> Choose exact lots to sell. Optimal for tax planning but requires
                            meticulous records.
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-yellow-500">
                <CardContent className="pt-6">
                    <h4 className="font-semibold text-yellow-600 mb-2">Wash Sale Rules</h4>
                    <p className="text-sm">
                        Wash sale rules apply when you sell at a loss and repurchase the same or substantially
                        identical asset within 30 days (before or after the sale). The loss is disallowed and
                        added to the cost basis of the repurchased asset. Section 1256 contracts (Kalshi) are
                        NOT subject to wash sale rules.
                    </p>
                </CardContent>
            </Card>

            <div className="flex justify-end">
                <Button onClick={saveSettings} disabled={saving || saved}>
                    {saving ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Saving...
                        </>
                    ) : saved ? (
                        <>
                            <CheckCircle2 className="mr-2 h-4 w-4" />
                            Saved!
                        </>
                    ) : (
                        <>
                            <Save className="mr-2 h-4 w-4" />
                            Save Settings
                        </>
                    )}
                </Button>
            </div>
        </div>
    );
}
