// Heatmap-specific types

export interface ProbabilitySnapshot {
    market_id: string;
    market_question: string;
    category: string;
    timestamp: string;
    market_price: number;
    implied_probability: number;
    ai_probability: number;
    divergence: number;
    divergence_percent: number;
    volume_24h?: number;
    liquidity_depth?: number;
}

export interface HeatmapCell {
    market_id: string;
    market_question: string;
    category: string;
    implied_probability: number;
    ai_probability: number;
    divergence: number;
    divergence_percent: number;
    color_intensity: number; // -1.0 to 1.0
    last_updated: string;
    confidence_score?: number;
}

export interface HeatmapData {
    cells: HeatmapCell[];
    timestamp: string;
    total_markets: number;
    avg_divergence: number;
    max_divergence: number;
    min_divergence: number;
}

export interface DivergenceAlert {
    market_id: string;
    market_question: string;
    category: string;
    implied_probability: number;
    ai_probability: number;
    divergence: number;
    divergence_percent: number;
    severity: 'HIGH' | 'MEDIUM' | 'LOW';
    timestamp: string;
    recommendation: string;
}

export interface ProbabilityHistoryPoint {
    timestamp: string;
    market_price: number;
    implied_probability: number;
    ai_probability: number;
    divergence: number;
}

export interface MarketProbabilityHistory {
    market_id: string;
    market_question: string;
    history: ProbabilityHistoryPoint[];
    timeframe: string;
}
