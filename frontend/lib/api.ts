export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchMarkets() {
    const res = await fetch(`${API_URL}/markets`);
    if (!res.ok) throw new Error('Failed to fetch markets');
    return res.json();
}

export async function predictMarket(question: string) {
    const res = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
    });
    if (!res.ok) throw new Error('Failed to start prediction');
    return res.json();
}

export async function getTaskStatus(taskId: string) {
    const res = await fetch(`${API_URL}/task/${taskId}`);
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

export async function chatWithModel(payload: {
    question: string;
    history?: ChatMessage[];
    context?: ChatContext;
    model?: string;
}) {
    const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // In a real app, add Authorization header here
            // 'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify(payload),
    });
    if (!res.ok) {
        const err = await res.text();
        throw new Error(`Chat failed: ${err}`);
    }
    return res.json();
}
