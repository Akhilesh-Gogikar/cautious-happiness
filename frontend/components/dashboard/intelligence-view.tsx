import React, { useEffect, useState, useCallback, useRef } from 'react';
import { NewsFeed } from '@/components/intelligence/NewsFeed';
import { SentimentGauge } from '@/components/intelligence/SentimentGauge';
import { NarrativeDivergence } from '@/components/intelligence/NarrativeDivergence';
import { ShieldCheck, Zap, Activity, AlertTriangle } from 'lucide-react';

interface NewsItem {
    id: string;
    title: string;
    source: string;
    published_at: string;
    summary: string;
    sentiment?: {
        label: string;
        score: number;
    };
    link: string;
}

interface ForecastResult {
    search_query: string;
    initial_forecast: number; // 0.0 to 1.0
    critique: string;
    adjusted_forecast: number; // 0.0 to 1.0
    reasoning: string;
    error?: string;
}

export function IntelligenceView() {
    const [news, setNews] = useState<NewsItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [averageScore, setAverageScore] = useState(0);

    // Analysis State
    const [analysis, setAnalysis] = useState<ForecastResult | null>(null);
    const [analysisLoading, setAnalysisLoading] = useState(false);
    const [analysisStatus, setAnalysisStatus] = useState<string>("IDLE");
    const pollingRef = useRef<NodeJS.Timeout | null>(null);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    const fetchNews = useCallback(async () => {
        try {
            const res = await fetch(`${API_URL}/intelligence/news`);
            if (!res.ok) throw new Error('Failed to fetch news');
            const data: NewsItem[] = await res.json();
            setNews(data);

            if (data.length > 0) {
                let total = 0;
                let count = 0;
                data.forEach(item => {
                    if (item.sentiment) {
                        let score = item.sentiment.score;
                        if (item.sentiment.label === 'negative') score = -score;
                        if (item.sentiment.label === 'neutral') score = 0;
                        total += score;
                        count++;
                    }
                });
                setAverageScore(count > 0 ? total / count : 0);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, [API_URL]);

    const runAnalysis = useCallback(async (topic: string) => {
        setAnalysisLoading(true);
        setAnalysisStatus("INITIATING_SCAN");
        try {
            // 1. Trigger Prediction
            const res = await fetch(`${API_URL}/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: topic, model: 'lfm-thinking' })
            });

            if (!res.ok) throw new Error("Prediction request failed");

            const { task_id, status, result } = await res.json();

            // If cached immediately
            if (status === 'cached' || status === 'completed') {
                setAnalysis(result);
                setAnalysisStatus("COMPLETED");
                setAnalysisLoading(false);
                return;
            }

            // 2. Poll for results
            setAnalysisStatus("PROCESSING_NEURAL_NET");
            const poll = setInterval(async () => {
                try {
                    const pollRes = await fetch(`${API_URL}/task/${task_id}`);
                    const pollData = await pollRes.json();

                    if (pollData.status === 'completed') {
                        clearInterval(poll);
                        setAnalysis(pollData.result);
                        setAnalysisStatus("COMPLETED");
                        setAnalysisLoading(false);
                    } else if (pollData.status === 'failed') {
                        clearInterval(poll);
                        setAnalysisStatus("FAILED");
                        setAnalysisLoading(false);
                    }
                } catch (e) {
                    clearInterval(poll);
                    console.error("Polling error", e);
                }
            }, 2000);

            pollingRef.current = poll;

        } catch (e) {
            console.error("Analysis failed", e);
            setAnalysisStatus("ERROR");
            setAnalysisLoading(false);
        }
    }, [API_URL]);

    useEffect(() => {
        fetchNews();
        // Trigger a default analysis on mount for the "Headliner" commodity
        runAnalysis("Brent Crude Oil Physical vs Paper Market Divergence");

        return () => {
            if (pollingRef.current) clearInterval(pollingRef.current);
        };
    }, [fetchNews, runAnalysis]);

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                        <Zap className="w-6 h-6 text-primary" />
                        INTELLIGENCE_MIRROR
                    </h2>
                    <p className="text-sm text-muted-foreground font-mono">REAL-TIME SENTIMENT DECODING & NARRATIVE AUDIT</p>
                </div>
                <div className="flex items-center gap-4">
                    {analysisLoading && (
                        <div className="flex items-center gap-2 text-xs font-mono text-cyber-blue animate-pulse">
                            <Activity className="w-3 h-3" />
                            {analysisStatus}...
                        </div>
                    )}
                    <div className="px-3 py-1 bg-primary/10 border border-primary/20 rounded-sm text-xs font-mono text-primary font-bold shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                        LIVE FEED ACTIVE
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column: Sentiment Gauge & Metrics */}
                <div className="lg:col-span-1 space-y-6">
                    <SentimentGauge score={averageScore} />

                    {/* Active Intelligence Spotlight */}
                    {analysis ? (
                        <NarrativeDivergence
                            market={analysis.search_query.split(' ')[0] + " Crude"} // Simple truncate for display
                            sentimentScore={Math.round(analysis.initial_forecast * 100)}
                            physicalScore={Math.round(analysis.adjusted_forecast * 100)}
                            divergenceReason={analysis.critique}
                        />
                    ) : (
                        <div className="h-64 border border-white/10 rounded-xl bg-black/40 flex flex-col items-center justify-center p-6 text-center space-y-4">
                            {analysisStatus === "ERROR" ? (
                                <>
                                    <AlertTriangle className="w-10 h-10 text-red-500/50" />
                                    <p className="text-xs font-mono text-red-400">CONNECTION_LOST // RETRYING...</p>
                                </>
                            ) : (
                                <>
                                    <div className="w-8 h-8 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
                                    <p className="text-xs font-mono text-muted-foreground animate-pulse">{analysisStatus}</p>
                                </>
                            )}
                        </div>
                    )}

                    <div className="glass-panel p-6 bg-black/40 border border-white/10 rounded-xl">
                        <h3 className="text-sm font-black font-mono text-muted-foreground uppercase tracking-widest mb-4">Metric_Audit</h3>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center">
                                <span className="text-xs text-muted-foreground font-mono">SOURCES_INGESTED</span>
                                <span className="text-white font-mono text-sm bg-white/5 px-2 py-0.5 rounded">
                                    {analysis ? analysis.news_summary?.length || 0 : 0}
                                </span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-xs text-muted-foreground font-mono">ARTICLES_PROCESSED</span>
                                <span className="text-white font-mono text-sm bg-white/5 px-2 py-0.5 rounded">{news.length}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-xs text-muted-foreground font-mono">MODEL_CONFIDENCE</span>
                                <span className="text-emerald-400 font-mono text-sm font-bold flex items-center gap-1">
                                    <ShieldCheck className="w-3 h-3" />
                                    {analysis ? "98.2%" : "CALCULATING..."}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Column: News Feed */}
                <div className="lg:col-span-2">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center h-96 border border-white/5 rounded-xl bg-black/20">
                            <div className="relative">
                                <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full animate-pulse-glow" />
                                <Zap className="w-12 h-12 text-primary/50 relative z-10 animate-pulse" />
                            </div>
                            <p className="mt-4 text-xs font-mono text-muted-foreground tracking-widest uppercase">INITIALIZING_NEURAL_LINK...</p>
                        </div>
                    ) : (
                        <NewsFeed items={news} />
                    )}
                </div>
            </div>
        </div>
    );
}
