'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
    PieChart, Pie, Cell, BarChart, Bar, LineChart, Line,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface AttributionSummary {
    total_trades: number;
    total_pnl: number;
    realized_pnl: number;
    unrealized_pnl: number;
    total_volume: number;
    win_rate: number;
    avg_pnl_per_trade: number;
    open_positions: number;
    closed_positions: number;
}

interface AttributionBreakdown {
    dimension_value: string;
    total_trades: number;
    total_pnl: number;
    realized_pnl: number;
    unrealized_pnl: number;
    total_volume: number;
    win_rate: number;
    avg_pnl_per_trade: number;
    [key: string]: any;
}

interface TimeSeriesPoint {
    timestamp: string;
    pnl: number;
    cumulative_pnl: number;
    num_positions: number;
    [key: string]: any;
}

interface Trade {
    id: number;
    market_question: string;
    side: string;
    entry_price: number;
    current_price: number;
    size_usd: number;
    model_used: string;
    data_sources: string[];
    strategy_type: string;
    category: string;
    unrealized_pnl: number;
    realized_pnl: number | null;
    is_closed: boolean;
    executed_at: string;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function AttributionDashboard() {
    const [summary, setSummary] = useState<AttributionSummary | null>(null);
    const [byModel, setByModel] = useState<AttributionBreakdown[]>([]);
    const [bySource, setBySource] = useState<any[]>([]);
    const [byStrategy, setByStrategy] = useState<AttributionBreakdown[]>([]);
    const [byCategory, setByCategory] = useState<AttributionBreakdown[]>([]);
    const [timeSeries, setTimeSeries] = useState<TimeSeriesPoint[]>([]);
    const [trades, setTrades] = useState<Trade[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAttributionData();
    }, []);

    const fetchAttributionData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            };

            // Fetch all attribution data in parallel
            const [summaryRes, modelRes, sourceRes, strategyRes, categoryRes, timeseriesRes, tradesRes] = await Promise.all([
                fetch('/api/attribution/summary', { headers }),
                fetch('/api/attribution/by-model', { headers }),
                fetch('/api/attribution/by-source', { headers }),
                fetch('/api/attribution/by-strategy', { headers }),
                fetch('/api/attribution/by-category', { headers }),
                fetch('/api/attribution/timeseries?interval=day', { headers }),
                fetch('/api/attribution/trades?limit=20', { headers })
            ]);

            const summaryData = await summaryRes.json();
            const modelData = await modelRes.json();
            const sourceData = await sourceRes.json();
            const strategyData = await strategyRes.json();
            const categoryData = await categoryRes.json();
            const timeseriesData = await timeseriesRes.json();
            const tradesData = await tradesRes.json();

            setSummary(summaryData);
            setByModel(modelData.breakdown || []);
            setBySource(sourceData.breakdown || []);
            setByStrategy(strategyData.breakdown || []);
            setByCategory(categoryData.breakdown || []);
            setTimeSeries(timeseriesData.timeseries || []);
            setTrades(tradesData.trades || []);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch attribution data:', error);
            setLoading(false);
        }
    };

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(value);
    };

    const formatPercent = (value: number) => {
        return `${(value * 100).toFixed(1)}%`;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-xl">Loading attribution data...</div>
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold">P&L Attribution Reporting</h1>
                <button
                    onClick={fetchAttributionData}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                    Refresh
                </button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-gray-500">Total P&L</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className={`text-2xl font-bold ${summary && summary.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {summary ? formatCurrency(summary.total_pnl) : '$0.00'}
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-gray-500">Win Rate</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {summary ? formatPercent(summary.win_rate) : '0%'}
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-gray-500">Total Trades</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {summary?.total_trades || 0}
                        </div>
                        <div className="text-sm text-gray-500">
                            {summary?.open_positions || 0} open, {summary?.closed_positions || 0} closed
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-gray-500">Avg P&L/Trade</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className={`text-2xl font-bold ${summary && summary.avg_pnl_per_trade >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {summary ? formatCurrency(summary.avg_pnl_per_trade) : '$0.00'}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Charts Row 1: Model and Source Attribution */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* P&L by Model */}
                <Card>
                    <CardHeader>
                        <CardTitle>P&L by AI Model</CardTitle>
                        <CardDescription>Performance breakdown by forecasting model</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={byModel}
                                    dataKey="total_pnl"
                                    nameKey="dimension_value"
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={100}
                                    label={(entry: any) => `${entry.dimension_value}: ${formatCurrency(entry.total_pnl)}`}
                                >
                                    {byModel.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                            </PieChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                {/* P&L by Data Source */}
                <Card>
                    <CardHeader>
                        <CardTitle>P&L by Data Source</CardTitle>
                        <CardDescription>Performance breakdown by data source</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={bySource}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="data_source" />
                                <YAxis />
                                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                                <Bar dataKey="total_pnl" fill="#3b82f6" />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            </div>

            {/* Charts Row 2: Strategy and Category */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* P&L by Strategy */}
                <Card>
                    <CardHeader>
                        <CardTitle>P&L by Strategy</CardTitle>
                        <CardDescription>Performance breakdown by trading strategy</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={byStrategy}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="dimension_value" />
                                <YAxis />
                                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                                <Legend />
                                <Bar dataKey="total_pnl" fill="#10b981" name="Total P&L" />
                                <Bar dataKey="realized_pnl" fill="#3b82f6" name="Realized P&L" />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                {/* P&L by Category */}
                <Card>
                    <CardHeader>
                        <CardTitle>P&L by Category</CardTitle>
                        <CardDescription>Performance breakdown by market category</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={byCategory}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="dimension_value" />
                                <YAxis />
                                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                                <Bar dataKey="total_pnl" fill="#f59e0b" />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            </div>

            {/* Time Series Chart */}
            <Card>
                <CardHeader>
                    <CardTitle>Cumulative P&L Over Time</CardTitle>
                    <CardDescription>Time-series view of portfolio performance</CardDescription>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={timeSeries}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis
                                dataKey="timestamp"
                                tickFormatter={(value) => new Date(value).toLocaleDateString()}
                            />
                            <YAxis />
                            <Tooltip
                                formatter={(value: number) => formatCurrency(value)}
                                labelFormatter={(label) => new Date(label).toLocaleString()}
                            />
                            <Legend />
                            <Line type="monotone" dataKey="cumulative_pnl" stroke="#3b82f6" strokeWidth={2} name="Cumulative P&L" />
                            <Line type="monotone" dataKey="pnl" stroke="#10b981" strokeWidth={2} name="Period P&L" />
                        </LineChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Trades Table */}
            <Card>
                <CardHeader>
                    <CardTitle>Recent Trades with Attribution</CardTitle>
                    <CardDescription>Detailed trade history with attribution metadata</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b">
                                    <th className="text-left p-2">Market</th>
                                    <th className="text-left p-2">Model</th>
                                    <th className="text-left p-2">Sources</th>
                                    <th className="text-left p-2">Strategy</th>
                                    <th className="text-left p-2">Category</th>
                                    <th className="text-right p-2">Size</th>
                                    <th className="text-right p-2">P&L</th>
                                    <th className="text-left p-2">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {trades.map((trade) => (
                                    <tr key={trade.id} className="border-b hover:bg-gray-50">
                                        <td className="p-2 max-w-xs truncate">{trade.market_question}</td>
                                        <td className="p-2">
                                            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                                                {trade.model_used}
                                            </span>
                                        </td>
                                        <td className="p-2">
                                            <div className="flex gap-1 flex-wrap">
                                                {trade.data_sources.map((source, idx) => (
                                                    <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                                                        {source}
                                                    </span>
                                                ))}
                                            </div>
                                        </td>
                                        <td className="p-2">
                                            <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                                                {trade.strategy_type}
                                            </span>
                                        </td>
                                        <td className="p-2">
                                            <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                                                {trade.category}
                                            </span>
                                        </td>
                                        <td className="p-2 text-right">{formatCurrency(trade.size_usd)}</td>
                                        <td className={`p-2 text-right font-medium ${(trade.realized_pnl || trade.unrealized_pnl) >= 0 ? 'text-green-600' : 'text-red-600'
                                            }`}>
                                            {formatCurrency(trade.realized_pnl || trade.unrealized_pnl)}
                                        </td>
                                        <td className="p-2">
                                            <span className={`px-2 py-1 rounded text-xs ${trade.is_closed ? 'bg-gray-100 text-gray-700' : 'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                {trade.is_closed ? 'Closed' : 'Open'}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
