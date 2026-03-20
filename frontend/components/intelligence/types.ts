export interface Source {
    id: string;
    url: string;
    domain: string;
    title: string;
    snippet: string;
    published_at: string;
}

export interface Competitor {
    id: string;
    name: string;
    description: string;
    tracked_urls: string[];
    last_active: string;
}

export interface AnalysisResult {
    target_id: string;
    sentiment_score: number;
    crowd_conviction: number;
    summary: string;
    key_phrases: string[];
    sources: Source[];
    analysis_status: string;
    timestamp: string;
}
