import React, { useEffect, useState, useCallback } from 'react';
import { CompetitorCard } from '@/components/intelligence/CompetitorCard';
import { SourceFeed } from '@/components/intelligence/SourceFeed';
import { SentimentGauge } from '@/components/intelligence/SentimentGauge';
import { Competitor, AnalysisResult, Source } from '@/components/intelligence/types';
import { ShieldCheck, Zap, Activity, AlertTriangle, Globe } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DecisionProtocol } from '@/components/intelligence/DecisionProtocol';

const MOCK_COMPETITORS: Competitor[] = [
    {
        id: "comp_citadel_commodity",
        name: "Citadel (Commodities)",
        description: "High-frequency algorithmic trading desk.",
        tracked_urls: ["reuters.com", "bloomberg.com"],
        last_active: new Date().toISOString()
    },
    {
        id: "comp_glencore_algo",
        name: "Glencore (Algo Desk)",
        description: "Physical-backed algorithmic hedging strategies.",
        tracked_urls: ["platts.com", "argusmedia.com"],
        last_active: new Date().toISOString()
    }
];

export function IntelligenceView() {
    const [competitors, setCompetitors] = useState<Competitor[]>([]);
    const [selectedCompetitor, setSelectedCompetitor] = useState<string | null>(null);
    const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [sources, setSources] = useState<Source[]>([]);
    const [error, setError] = useState<string | null>(null);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    useEffect(() => {
        fetch(`${API_URL}/mirror/competitors`)
            .then(res => {
                if (!res.ok) throw new Error("Failed to fetch competitors");
                return res.json();
            })
            .then(data => setCompetitors(data))
            .catch(err => {
                console.error("Using Mock Competitors:", err);
                setCompetitors(MOCK_COMPETITORS);
            });
    }, [API_URL]);

    const handleAnalyze = async (id: string) => {
        setSelectedCompetitor(id);
        setIsAnalyzing(true);
        setAnalysis(null);
        setSources([]);
        setError(null);

        try {
            const res = await fetch(`${API_URL}/mirror/analyze/${id}`, {
                method: "POST"
            });
            if (!res.ok) throw new Error("Analysis failed");

            const result: AnalysisResult = await res.json();
            setAnalysis(result);

            // Simulation of sources for demo since API doesn't return them yet
            setSources([
                {
                    id: "src_1",
                    url: "#",
                    domain: "bloomberg.com",
                    title: `Algorithmic flow detected for ${id}`,
                    snippet: result.summary,
                    published_at: new Date().toISOString()
                },
                {
                    id: "src_2",
                    url: "#",
                    domain: "reuters.com",
                    title: "Market impact analysis",
                    snippet: "Crowd sentiment suggests high correlation with momentum factors.",
                    published_at: new Date().toISOString()
                }
            ]);

        } catch (error) {
            console.error(error);
            setError("CONNECTION_LOST // UNABLE TO MIRROR TARGET");
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="space-y-6 animate-fade-in h-full flex flex-col">
            <div className="flex items-center justify-between shrink-0">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                        <Zap className="w-6 h-6 text-primary" />
                        INTELLIGENCE_MIRROR
                    </h2>
                    <p className="text-sm text-muted-foreground font-mono">COUNTER-INTELLIGENCE // COMPETITOR TRACKING</p>
                </div>
                <div className="flex items-center gap-4">
                    {isAnalyzing && (
                        <div className="flex items-center gap-2 text-xs font-mono text-cyber-blue animate-pulse">
                            <Activity className="w-3 h-3" />
                            INTERCEPTING_SIGNALS...
                        </div>
                    )}
                    <div className="px-3 py-1 bg-primary/10 border border-primary/20 rounded-sm text-xs font-mono text-primary font-bold shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                        SYSTEM ACTIVE
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
                {/* Left Column: Watchlist (4 cols) */}
                <div className="lg:col-span-4 flex flex-col space-y-4 overflow-y-auto pr-2 custom-scrollbar">
                    <div className="flex items-center gap-2 text-sm font-mono text-muted-foreground mb-2">
                        <ShieldCheck className="w-4 h-4 text-primary" />
                        TARGET_PROTOCOL_LIST
                    </div>
                    {competitors.map(comp => (
                        <CompetitorCard
                            key={comp.id}
                            competitor={comp}
                            onAnalyze={handleAnalyze}
                        />
                    ))}
                </div>


                {/* Right Column: Analysis (8 cols) */}
                <div className="lg:col-span-8 flex flex-col space-y-6 overflow-y-auto pr-2 custom-scrollbar">

                    {/* Top Row: Gauge + Findings + Decision */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="md:col-span-1">
                            {analysis ? (
                                <SentimentGauge score={analysis.sentiment_score} conviction={analysis.crowd_conviction} />
                            ) : (
                                <Card className="h-full bg-black/40 border-dashed border-white/10 flex items-center justify-center min-h-[200px]">
                                    <div className="text-center p-6">
                                        <Activity className="h-8 w-8 mx-auto mb-2 text-muted-foreground/50" />
                                        <p className="text-xs font-mono text-muted-foreground">SELECT_TARGET_FOR_ANALYSIS</p>
                                    </div>
                                </Card>
                            )}
                        </div>

                        <div className="md:col-span-1">
                            <Card className="h-full border-primary/10 bg-black/40">
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm font-mono text-muted-foreground">KEY_FINDINGS</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    {isAnalyzing ? (
                                        <div className="space-y-4 animate-pulse">
                                            <div className="h-2 bg-primary/20 rounded w-3/4"></div>
                                            <div className="h-2 bg-primary/20 rounded w-1/2"></div>
                                            <div className="h-2 bg-primary/20 rounded w-5/6"></div>
                                            <div className="h-2 bg-primary/20 rounded w-2/3"></div>
                                        </div>
                                    ) : analysis ? (
                                        <div className="space-y-4">
                                            <p className="text-sm text-foreground/90 leading-relaxed font-mono">
                                                {analysis.summary}
                                            </p>
                                            <div className="flex flex-wrap gap-2">
                                                {analysis.key_phrases.map((phrase, i) => (
                                                    <span key={i} className="px-2 py-1 rounded-sm bg-primary/10 text-primary text-[10px] font-mono border border-primary/20">
                                                        {phrase}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    ) : error ? (
                                        <div className="flex flex-col items-center justify-center h-full text-red-400 space-y-2">
                                            <AlertTriangle className="h-6 w-6" />
                                            <p className="text-xs font-mono">{error}</p>
                                        </div>
                                    ) : (
                                        <div className="text-xs text-muted-foreground font-mono text-center pt-12 opacity-50">
                                            AWAITING_DATA...
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </div>

                        <div className="md:col-span-1">
                            {analysis ? (
                                <DecisionProtocol
                                    analysis={analysis}
                                    symbol={selectedCompetitor === "comp_citadel_commodity" ? "WTI" : "BRENT"}
                                />
                            ) : (
                                <Card className="h-full bg-black/40 border-dashed border-white/10 flex items-center justify-center min-h-[200px]">
                                    <div className="text-center p-6 opacity-30">
                                        <Zap className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                                        <p className="text-[10px] font-mono text-muted-foreground uppercase">Decision Protocol Disabled</p>
                                    </div>
                                </Card>
                            )}
                        </div>
                    </div>

                    {/* Bottom Row: Source Feed */}
                    <div className="flex-1 min-h-[300px]">
                        <div className="flex items-center gap-2 text-sm font-mono text-muted-foreground mb-4">
                            <Globe className="w-4 h-4 text-cyber-blue" />
                            INTERCEPTED_STREAMS
                        </div>
                        <SourceFeed sources={sources} />
                    </div>
                </div>
            </div>
        </div>
    );
}
