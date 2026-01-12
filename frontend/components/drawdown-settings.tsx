"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { api } from "@/lib/api"
import { AlertCircle, CheckCircle2, TrendingDown } from "lucide-react"

interface DrawdownLimit {
    id: number
    user_id: number
    max_daily_drawdown_percent: number
    is_active: boolean
    created_at: string
}

interface DailyStats {
    id: number
    user_id: number
    date: string
    starting_balance: number
    current_pnl: number
    max_drawdown_reached: number
    is_paused: boolean
    pause_reason: string | null
}

export function DrawdownSettings() {
    const [limit, setLimit] = useState<DrawdownLimit | null>(null)
    const [stats, setStats] = useState<DailyStats | null>(null)
    const [drawdownPercent, setDrawdownPercent] = useState<number>(5.0)
    const [isActive, setIsActive] = useState<boolean>(true)
    const [loading, setLoading] = useState<boolean>(true)
    const [saving, setSaving] = useState<boolean>(false)
    const [message, setMessage] = useState<string | null>(null)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            setLoading(true)
            const [limitRes, statsRes] = await Promise.all([
                api.get("/api/trading/limits"),
                api.get("/api/trading/daily-stats")
            ])

            setLimit(limitRes.data)
            setStats(statsRes.data)
            setDrawdownPercent(limitRes.data.max_daily_drawdown_percent)
            setIsActive(limitRes.data.is_active)
        } catch (error) {
            console.error("Error fetching drawdown data:", error)
            setMessage("Failed to load drawdown settings")
        } finally {
            setLoading(false)
        }
    }

    const handleSave = async () => {
        try {
            setSaving(true)
            setMessage(null)

            await api.post("/api/trading/limits", {
                max_daily_drawdown_percent: drawdownPercent,
                is_active: isActive
            })

            setMessage("Settings saved successfully")
            await fetchData()
        } catch (error) {
            console.error("Error saving settings:", error)
            setMessage("Failed to save settings")
        } finally {
            setSaving(false)
        }
    }

    const handleReset = async () => {
        try {
            setSaving(true)
            setMessage(null)

            await api.post("/api/trading/reset-daily")

            setMessage("Daily stats reset successfully")
            await fetchData()
        } catch (error) {
            console.error("Error resetting stats:", error)
            setMessage("Failed to reset daily stats")
        } finally {
            setSaving(false)
        }
    }

    const currentDrawdown = stats && stats.starting_balance > 0
        ? (Math.abs(Math.min(0, stats.current_pnl)) / stats.starting_balance) * 100
        : 0

    const headroom = limit ? limit.max_daily_drawdown_percent - currentDrawdown : 0

    if (loading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Drawdown Limits</CardTitle>
                    <CardDescription>Loading...</CardDescription>
                </CardHeader>
            </Card>
        )
    }

    return (
        <div className="space-y-4">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <TrendingDown className="h-5 w-5" />
                        Drawdown Limits
                    </CardTitle>
                    <CardDescription>
                        Set hard stops to pause trading if losses exceed a threshold
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Status Badge */}
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Trading Status</span>
                        {stats?.is_paused ? (
                            <Badge variant="destructive" className="flex items-center gap-1">
                                <AlertCircle className="h-3 w-3" />
                                Paused
                            </Badge>
                        ) : (
                            <Badge variant="default" className="flex items-center gap-1 bg-green-600">
                                <CheckCircle2 className="h-3 w-3" />
                                Active
                            </Badge>
                        )}
                    </div>

                    {/* Pause Reason Alert */}
                    {stats?.is_paused && stats.pause_reason && (
                        <Alert variant="destructive">
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription>{stats.pause_reason}</AlertDescription>
                        </Alert>
                    )}

                    {/* Current Stats */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                            <p className="text-sm text-muted-foreground">Starting Balance</p>
                            <p className="text-2xl font-bold">
                                ${stats?.starting_balance.toFixed(2) || "0.00"}
                            </p>
                        </div>
                        <div className="space-y-1">
                            <p className="text-sm text-muted-foreground">Current P&L</p>
                            <p className={`text-2xl font-bold ${stats && stats.current_pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                                ${stats?.current_pnl.toFixed(2) || "0.00"}
                            </p>
                        </div>
                        <div className="space-y-1">
                            <p className="text-sm text-muted-foreground">Current Drawdown</p>
                            <p className="text-2xl font-bold text-orange-600">
                                {currentDrawdown.toFixed(2)}%
                            </p>
                        </div>
                        <div className="space-y-1">
                            <p className="text-sm text-muted-foreground">Headroom</p>
                            <p className={`text-2xl font-bold ${headroom > 2 ? "text-green-600" : "text-red-600"}`}>
                                {headroom.toFixed(2)}%
                            </p>
                        </div>
                    </div>

                    {/* Settings */}
                    <div className="space-y-4 pt-4 border-t">
                        <div className="space-y-2">
                            <Label htmlFor="drawdown-percent">
                                Max Daily Drawdown (%)
                            </Label>
                            <Input
                                id="drawdown-percent"
                                type="number"
                                min="0.1"
                                max="100"
                                step="0.1"
                                value={drawdownPercent}
                                onChange={(e) => setDrawdownPercent(parseFloat(e.target.value))}
                            />
                            <p className="text-xs text-muted-foreground">
                                Trading will pause if losses exceed this percentage of starting balance
                            </p>
                        </div>

                        <div className="flex items-center justify-between">
                            <Label htmlFor="active-toggle">Enable Drawdown Limits</Label>
                            <Switch
                                id="active-toggle"
                                checked={isActive}
                                onCheckedChange={setIsActive}
                            />
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2">
                        <Button onClick={handleSave} disabled={saving} className="flex-1">
                            {saving ? "Saving..." : "Save Settings"}
                        </Button>
                        <Button
                            onClick={handleReset}
                            disabled={saving}
                            variant="outline"
                        >
                            Reset Daily Stats
                        </Button>
                    </div>

                    {/* Message */}
                    {message && (
                        <Alert>
                            <AlertDescription>{message}</AlertDescription>
                        </Alert>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
