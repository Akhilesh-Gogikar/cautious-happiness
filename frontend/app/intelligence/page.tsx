"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CompetitorCard } from "@/components/intelligence/CompetitorCard";
import { SourceFeed } from "@/components/intelligence/SourceFeed";
import { SentimentGauge } from "@/components/intelligence/SentimentGauge";
import { Competitor, AnalysisResult, Source } from "@/components/intelligence/types";
import { Activity, ShieldCheck, Globe } from "lucide-react";
import { toast } from "sonner";

// Mock Data for Initial State if API fails or for seamless demo
const MOCK_COMPETITORS: Competitor[] = [
    {
        id: "comp_citadel_commodity",
        name: "Citadel (Commodities)",
        description: "High-frequency algorithmic trading desk focusing on energy spreads.",
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

export default function IntelligencePage() {
    const [competitors, setCompetitors] = useState<Competitor[]>([]);
    const [selectedCompetitor, setSelectedCompetitor] = useState<string | null>(null);
    const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [sources, setSources] = useState<Source[]>([]);

    useEffect(() => {
        // Fetch competitors on load
        fetch("http://localhost:8000/mirror/competitors")
            .then(res => res.json())
            .then(data => setCompetitors(data))
            .catch(err => {
                console.error("Failed to fetch competitors", err);
                setCompetitors(MOCK_COMPETITORS);
            });
    }, []);

    const handleAnalyze = async (id: string) => {
        setSelectedCompetitor(id);
        setIsAnalyzing(true);
        setAnalysis(null);
        setSources([]); // Clear previous sources

        try {
            const res = await fetch(`http://localhost:8000/mirror/analyze/${id}`, {
                method: "POST"
            });
            if (!res.ok) throw new Error("Analysis failed");

            const result: AnalysisResult = await res.json();
            setAnalysis(result);

            // Mock sources for the demo as the API doesn't return them in the AnalysisResult yet
            // In a real app, AnalysisResult would probably include the sources used.
            // For now, I'll generate some mock sources based on the ID to show the UI.
            setSources([
                {
                    id: "src_1",
                    title: `Market movements for ${id} sector`,
                    url: "#",
                    domain: "bloomberg.com",
                    snippet: result.summary.substring(0, 100) + "...",
                    published_at: new Date().toISOString()
                },
                {
                    id: "src_2",
                    title: `Algo activity report: ${id}`,
                    url: "#",
                    domain: "reuters.com",
                    snippet: "High volume detected in correlated assets...",
                    published_at: new Date().toISOString()
                }
            ]);

        } catch (error) {
            console.error(error);
            // alert("Analysis failed. See console.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="container mx-auto p-6 space-y-8 min-h-screen bg-background text-foreground">
            <div className="flex flex-col space-y-2">
                <h1 className="text-3xl font-bold tracking-tight font-mono text-primary">INTELLIGENCE MIRROR</h1>
                <p className="text-muted-foreground font-mono text-sm max-w-2xl">
                    COUNTER-INTELLIGENCE DASHBOARD // TRACKING COMPETITOR ALGORITHMS & CROWD SENTIMENT
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-6">

                {/* Left Column: Competitor Watchlist */}
                <div className="md:col-span-4 space-y-4">
                    <Card className="border-primary/20 bg-background/50">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-sm font-mono flex items-center gap-2">
                                <ShieldCheck className="h-4 w-4 text-primary" />
                                WATCHLIST
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="grid gap-4">
                            {competitors.map(comp => (
                                <CompetitorCard
                                    key={comp.id}
                                    competitor={comp}
                                    onAnalyze={handleAnalyze}
                                />
                            ))}
                        </CardContent>
                    </Card>
                </div>

                {/* Right Column: Analysis & Feed */}
                <div className="md:col-span-8 space-y-6">
                    {/* Live Analysis Section */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Sentiment Gauge */}
                        <div className="md:col-span-1">
                            {analysis ? (
                                <SentimentGauge score={analysis.sentiment_score} conviction={analysis.crowd_conviction} />
                            ) : (
                                <Card className="h-full flex items-center justify-center border-dashed opacity-50 min-h-[200px]">
                                    <div className="text-center p-6">
                                        <Activity className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                                        <p className="text-xs font-mono text-muted-foreground">SELECT TARGET TO ANALYZE SENTIMENT</p>
                                    </div>
                                </Card>
                            )}
                        </div>

                        {/* Key Findings */}
                        <div className="md:col-span-1">
                            <Card className="h-full border-primary/10">
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm font-mono">KEY FINDINGS</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    {isAnalyzing ? (
                                        <div className="space-y-2 animate-pulse">
                                            <div className="h-4 bg-muted rounded w-3/4"></div>
                                            <div className="h-4 bg-muted rounded w-1/2"></div>
                                            <div className="h-4 bg-muted rounded w-5/6"></div>
                                        </div>
                                    ) : analysis ? (
                                        <div className="space-y-4">
                                            <p className="text-sm text-foreground/90 leading-relaxed">
                                                {analysis.summary}
                                            </p>
                                            <div className="flex flex-wrap gap-2">
                                                {analysis.key_phrases.map((phrase, i) => (
                                                    <span key={i} className="px-2 py-1 rounded-sm bg-primary/10 text-primary text-[10px] font-mono border border-primary/20">
                                                        {phrase}
                                                    </span>
                                                ))}
                                            </div>
                                            <div className="text-[10px] text-muted-foreground font-mono pt-2 border-t border-border">
                                                ANALYSIS TIMESTAMP: {new Date(analysis.timestamp).toLocaleTimeString()}
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="text-xs text-muted-foreground font-mono text-center pt-8">
                                            WAITING FOR DATA STREAM...
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </div>
                    </div>

                    {/* Source Feed */}
                    <div className="space-y-2">
                        <h3 className="text-sm font-mono text-muted-foreground flex items-center gap-2">
                            <Globe className="h-3 w-3" />
                            INTERCEPTED INTELLIGENCE STREAMS
                        </h3>
                        <SourceFeed sources={sources} />
                    </div>
                </div>
            </div>
        </div>
    );
}
