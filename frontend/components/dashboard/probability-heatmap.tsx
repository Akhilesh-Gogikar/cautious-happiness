"use client";

import { useState, useEffect } from 'react';
import { HeatmapData, HeatmapCell, DivergenceAlert } from '@/lib/heatmap-types';
import { TrendingUp, TrendingDown, AlertTriangle, Filter, Download } from 'lucide-react';

export function ProbabilityHeatmap() {
    const [heatmapData, setHeatmapData] = useState<HeatmapData | null>(null);
    const [alerts, setAlerts] = useState<DivergenceAlert[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [minDivergence, setMinDivergence] = useState<number>(0);
    const [hoveredCell, setHoveredCell] = useState<HeatmapCell | null>(null);

    useEffect(() => {
        fetchHeatmapData();
        fetchAlerts();

        // Refresh every 30 seconds
        const interval = setInterval(() => {
            fetchHeatmapData();
            fetchAlerts();
        }, 30000);

        return () => clearInterval(interval);
    }, [selectedCategory, minDivergence]);

    const fetchHeatmapData = async () => {
        try {
            const params = new URLSearchParams();
            if (selectedCategory) params.append('category', selectedCategory);
            if (minDivergence > 0) params.append('min_divergence', minDivergence.toString());

            const response = await fetch(`/api/heatmap/probability-comparison?${params}`, {
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                setHeatmapData(data);
            }
        } catch (error) {
            console.error('Error fetching heatmap data:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchAlerts = async () => {
        try {
            const response = await fetch('/api/heatmap/divergence-alerts', {
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                setAlerts(data.slice(0, 5)); // Top 5 alerts
            }
        } catch (error) {
            console.error('Error fetching alerts:', error);
        }
    };

    const getCellColor = (intensity: number): string => {
        // Green for AI > Market (positive divergence)
        // Red for Market > AI (negative divergence)
        if (intensity > 0) {
            const alpha = Math.abs(intensity);
            return `rgba(16, 185, 129, ${alpha * 0.8})`; // Green
        } else {
            const alpha = Math.abs(intensity);
            return `rgba(239, 68, 68, ${alpha * 0.8})`; // Red
        }
    };

    const getSeverityColor = (severity: string): string => {
        switch (severity) {
            case 'HIGH': return 'text-red-500 bg-red-500/10 border-red-500/20';
            case 'MEDIUM': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
            default: return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
        }
    };

    const categories = heatmapData?.cells
        ? Array.from(new Set(heatmapData.cells.map(c => c.category)))
        : [];

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header & Controls */}
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                <div>
                    <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                        <TrendingUp className="w-6 h-6 text-primary" />
                        Probability Heatmap
                    </h2>
                    <p className="text-sm text-muted-foreground mt-1">
                        Market vs AI Probability Divergence
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    {/* Category Filter */}
                    <select
                        value={selectedCategory || ''}
                        onChange={(e) => setSelectedCategory(e.target.value || null)}
                        className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary/50"
                    >
                        <option value="">All Categories</option>
                        {categories.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                        ))}
                    </select>

                    {/* Divergence Threshold */}
                    <div className="flex items-center gap-2 px-3 py-2 bg-white/5 border border-white/10 rounded-lg">
                        <Filter className="w-4 h-4 text-muted-foreground" />
                        <input
                            type="range"
                            min="0"
                            max="0.3"
                            step="0.05"
                            value={minDivergence}
                            onChange={(e) => setMinDivergence(parseFloat(e.target.value))}
                            className="w-24"
                        />
                        <span className="text-xs text-white font-mono">{(minDivergence * 100).toFixed(0)}%</span>
                    </div>

                    <button className="p-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors">
                        <Download className="w-4 h-4 text-white" />
                    </button>
                </div>
            </div>

            {/* Stats Summary */}
            {heatmapData && (
                <div className="grid grid-cols-4 gap-4">
                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider">Markets</div>
                        <div className="text-2xl font-bold text-white mt-1">{heatmapData.total_markets}</div>
                    </div>
                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider">Avg Divergence</div>
                        <div className="text-2xl font-bold text-white mt-1">
                            {(heatmapData.avg_divergence * 100).toFixed(1)}%
                        </div>
                    </div>
                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider">Max Divergence</div>
                        <div className="text-2xl font-bold text-primary mt-1">
                            {(heatmapData.max_divergence * 100).toFixed(1)}%
                        </div>
                    </div>
                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider">Min Divergence</div>
                        <div className="text-2xl font-bold text-red-500 mt-1">
                            {(heatmapData.min_divergence * 100).toFixed(1)}%
                        </div>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Heatmap Grid */}
                <div className="lg:col-span-2 bg-white/5 border border-white/10 rounded-lg p-6">
                    <div className="grid grid-cols-5 gap-2">
                        {heatmapData?.cells.map((cell) => (
                            <div
                                key={cell.market_id}
                                className="relative aspect-square rounded-lg border border-white/10 cursor-pointer transition-all hover:scale-105 hover:z-10"
                                style={{
                                    backgroundColor: getCellColor(cell.color_intensity)
                                }}
                                onMouseEnter={() => setHoveredCell(cell)}
                                onMouseLeave={() => setHoveredCell(null)}
                            >
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="text-center">
                                        <div className="text-xs font-bold text-white">
                                            {(cell.divergence * 100).toFixed(0)}%
                                        </div>
                                        {cell.divergence > 0 ? (
                                            <TrendingUp className="w-3 h-3 text-white mx-auto mt-1" />
                                        ) : (
                                            <TrendingDown className="w-3 h-3 text-white mx-auto mt-1" />
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Legend */}
                    <div className="mt-6 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded bg-red-500/80"></div>
                            <span className="text-xs text-muted-foreground">Market Higher</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded bg-green-500/80"></div>
                            <span className="text-xs text-muted-foreground">AI Higher</span>
                        </div>
                    </div>

                    {/* Tooltip */}
                    {hoveredCell && (
                        <div className="mt-4 p-4 bg-black/80 border border-white/20 rounded-lg">
                            <div className="text-sm font-bold text-white mb-2 line-clamp-2">
                                {hoveredCell.market_question}
                            </div>
                            <div className="grid grid-cols-2 gap-3 text-xs">
                                <div>
                                    <div className="text-muted-foreground">Market Prob</div>
                                    <div className="text-white font-mono">{(hoveredCell.implied_probability * 100).toFixed(1)}%</div>
                                </div>
                                <div>
                                    <div className="text-muted-foreground">AI Prob</div>
                                    <div className="text-white font-mono">{(hoveredCell.ai_probability * 100).toFixed(1)}%</div>
                                </div>
                                <div>
                                    <div className="text-muted-foreground">Divergence</div>
                                    <div className={`font-mono ${hoveredCell.divergence > 0 ? 'text-green-500' : 'text-red-500'}`}>
                                        {hoveredCell.divergence > 0 ? '+' : ''}{(hoveredCell.divergence * 100).toFixed(1)}%
                                    </div>
                                </div>
                                <div>
                                    <div className="text-muted-foreground">Category</div>
                                    <div className="text-white">{hoveredCell.category}</div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Alerts Panel */}
                <div className="bg-white/5 border border-white/10 rounded-lg p-6">
                    <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-yellow-500" />
                        Top Divergences
                    </h3>

                    <div className="space-y-3">
                        {alerts.map((alert, idx) => (
                            <div
                                key={alert.market_id}
                                className={`p-3 rounded-lg border ${getSeverityColor(alert.severity)}`}
                            >
                                <div className="flex items-start justify-between mb-2">
                                    <span className="text-xs font-bold uppercase">{alert.severity}</span>
                                    <span className="text-xs font-mono">
                                        {alert.divergence > 0 ? '+' : ''}{(alert.divergence * 100).toFixed(0)}%
                                    </span>
                                </div>
                                <div className="text-xs text-white/90 line-clamp-2 mb-2">
                                    {alert.market_question}
                                </div>
                                <div className="text-xs text-muted-foreground">
                                    {alert.recommendation}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
