export const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

async function fetchWithRetry(url: string, options: RequestInit, retries = 3, backoff = 1000) {
    try {
        const res = await fetch(url, options);
        if (!res.ok) {
            const errorText = await res.text();
            throw new Error(errorText || `Status ${res.status}`);
        }
        return await res.json();
    } catch (err: any) {
        if (retries > 0) {
            console.warn(`Fetch failed: ${err.message}. Retrying in ${backoff}ms... (${retries} attempts left)`);
            await new Promise(resolve => setTimeout(resolve, backoff));
            return fetchWithRetry(url, options, retries - 1, backoff * 2);
        }
        throw err;
    }
}

export async function fetchMarkets() {
    const res = await fetch(`${API_URL}/markets`);
    if (!res.ok) throw new Error('Failed to fetch markets');
    return res.json();
}

export async function predictMarket(question: string) {
    return fetchWithRetry(`${API_URL}/prediction/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
    });
}

export async function getTaskStatus(taskId: string) {
    const res = await fetch(`${API_URL}/prediction/task/${taskId}`);
    if (!res.ok) throw new Error('Failed to fetch task status');
    return res.json();
}

export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: number;
}

export interface ChatContext {
    route_path: string;
    client_state?: any;
}

export interface SystemHealth {
    status: 'ok' | 'degraded';
    details: {
        ollama: boolean;
        redis: boolean;
        database: boolean;
        gemini_configured: boolean;
    };
}

export interface MirrorSource {
    id: string;
    url: string;
    domain: string;
    title: string;
    snippet: string;
    published_at: string;
}

export interface MirrorCompetitor {
    id: string;
    name: string;
    description: string;
    tracked_urls: string[];
    last_active: string;
}

export interface MirrorAnalysisResult {
    target_id: string;
    sentiment_score: number;
    crowd_conviction: number;
    summary: string;
    key_phrases: string[];
    sources: MirrorSource[];
    analysis_status: string;
    timestamp: string;
}

export async function fetchMirrorCompetitors(): Promise<MirrorCompetitor[]> {
    const res = await fetch(`${API_URL}/mirror/competitors`);
    if (!res.ok) throw new Error('Failed to fetch competitors');
    return res.json();
}

export async function analyzeMirrorTarget(targetId: string): Promise<MirrorAnalysisResult> {
    return fetchWithRetry(`${API_URL}/mirror/analyze/${targetId}`, {
        method: 'POST',
    });
}

export async function fetchSystemHealth(): Promise<SystemHealth> {
    const res = await fetch(`${API_URL}/health`);
    if (!res.ok) throw new Error('Failed to fetch system health');
    return res.json();
}

export async function chatWithModel(payload: {
    question: string;
    history?: ChatMessage[];
    context?: ChatContext;
    model?: string;
}) {
    return fetchWithRetry(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });
}

export async function chatWithModelStream(
    payload: {
        question: string;
        history?: ChatMessage[];
        context?: ChatContext;
        model?: string;
    },
    handlers: {
        onThinking?: (message: string) => void;
        onToken?: (token: string) => void;
        onDone?: (response: string) => void;
    }
) {
    const res = await fetch(`${API_URL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });

    if (!res.ok || !res.body) {
        throw new Error(`Streaming chat failed: ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop() || '';

        for (const rawEvent of events) {
            const lines = rawEvent.split('\n');
            const event = lines.find(l => l.startsWith('event:'))?.slice(6).trim();
            const dataLine = lines.find(l => l.startsWith('data:'))?.slice(5).trim();
            if (!event || !dataLine) continue;

            try {
                const data = JSON.parse(dataLine);
                if (event === 'thinking' && data.message) handlers.onThinking?.(data.message);
                if (event === 'token' && data.token) handlers.onToken?.(data.token);
                if (event === 'done') handlers.onDone?.(data.response || '');
            } catch {
                // Ignore malformed events, keep stream alive.
            }
        }
    }
}
