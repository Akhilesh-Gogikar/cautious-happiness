import React, { useEffect, useState } from 'react';
import { ShieldCheck, Zap, Activity, AlertTriangle, Globe } from 'lucide-react';

import { CompetitorCard } from '@/components/intelligence/CompetitorCard';
import { DecisionProtocol } from '@/components/intelligence/DecisionProtocol';
import { SourceFeed } from '@/components/intelligence/SourceFeed';
import { SentimentGauge } from '@/components/intelligence/SentimentGauge';
import type { Competitor, AnalysisResult, Source } from '@/components/intelligence/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { analyzeMirrorTarget, fetchMirrorCompetitors } from '@/lib/api';

const MOCK_COMPETITORS: Competitor[] = [
    {
        id: 'comp_citadel_commodity',
        name: 'Citadel (Commodities)',
        description: 'High-frequency algorithmic trading desk.',
        tracked_urls: ['reuters.com', 'bloomberg.com'],
        last_active: new Date().toISOString(),
    },
    {
        id: 'comp_glencore_algo',
        name: 'Glencore (Algo Desk)',
        description: 'Physical-backed algorithmic hedging strategies.',
        tracked_urls: ['platts.com', 'argusmedia.com'],
        last_active: new Date().toISOString(),
    },
];

const FALLBACK_SOURCES: Record<string, Source[]> = {
    comp_citadel_commodity: [
        {
            id: 'fallback_1',
            url: '#',
            domain: 'reuters.com',
            title: 'Macro desks rotate into energy-linked momentum signals',
            snippet: 'Fallback feed used because the mirror endpoint returned no live source bundle.',
            published_at: new Date().toISOString(),
        },
    ],
    comp_glencore_algo: [
        {
            id: 'fallback_2',
            url: '#',
            domain: 'argusmedia.com',
            title: 'Physical hedging desks lean on freight and inventory noise',
            snippet: 'Fallback feed used because the mirror endpoint returned no live source bundle.',
            published_at: new Date().toISOString(),
        },
    ],
};

export function IntelligenceView() {
    const [competitors, setCompetitors] = useState<Competitor[]>([]);
    const [selectedCompetitor, setSelectedCompetitor] = useState<string | null>(null);
    const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [sources, setSources] = useState<Source[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchMirrorCompetitors()
            .then(data => setCompetitors(data))
            .catch(err => {
                console.error('Using Mock Competitors:', err);
                setCompetitors(MOCK_COMPETITORS);
            });
    }, []);

    const handleAnalyze = async (id: string) => {
        setSelectedCompetitor(id);
        setIsAnalyzing(true);
        setAnalysis(null);
        setSources([]);
        setError(null);

        try {
            const result = await analyzeMirrorTarget(id);
            setAnalysis(result);
            setSources(result.sources.length > 0 ? result.sources : (FALLBACK_SOURCES[id] ?? []));
        } catch (analysisError) {
            console.error(analysisError);
            setError('CONNECTION_LOST // UNABLE TO MIRROR TARGET');
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
                <div className="lg:col-span-4 flex flex-col space-y-4 overflow-y-auto pr-2 custom-scrollbar">
                    <div className="flex items-center gap-2 text-sm font-mono text-muted-foreground mb-2">
                        <ShieldCheck className="w-4 h-4 text-primary" />
                        TARGET_PROTOCOL_LIST
                    </div>
                    {competitors.map(comp => (
                        <CompetitorCard key={comp.id} competitor={comp} onAnalyze={handleAnalyze} />
                    ))}
                </div>

                <div className="lg:col-span-8 flex flex-col space-y-6 overflow-y-auto pr-2 custom-scrollbar">
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
                                            <div className="flex items-center justify-between gap-4 border-y border-white/5 py-2 text-[10px] font-mono text-muted-foreground">
                                                <span>STATUS: {analysis.analysis_status.toUpperCase()}</span>
                                                <span>SOURCES: {sources.length}</span>
                                            </div>
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
                                    symbol={selectedCompetitor === 'comp_citadel_commodity' ? 'WTI' : 'BRENT'}
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

                    <div className="flex-1 min-h-[300px]">
                        <div className="flex items-center justify-between gap-2 text-sm font-mono text-muted-foreground mb-4">
                            <div className="flex items-center gap-2">
                                <Globe className="w-4 h-4 text-cyber-blue" />
                                INTERCEPTED_STREAMS
                            </div>
                            {analysis && <span className="text-[10px]">LAST UPDATE: {new Date(analysis.timestamp).toLocaleTimeString()}</span>}
                        </div>
                        <SourceFeed sources={sources} />
                    </div>
                </div>
            </div>
        </div>
    );
}
