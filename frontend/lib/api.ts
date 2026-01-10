const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

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

export async function chatWithModel(payload: { question: string, context: string, user_message: string }) {
    const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Chat failed');
    return res.json();
}

export async function streamChat(payload: { question: string, context: string, user_message: string }) {
    const res = await fetch(`${API_URL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error('Chat stream failed');

    const reader = res.body?.getReader();
    const decoder = new TextDecoder();

    return async function* () {
        if (!reader) return;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            yield chunk;
        }
    };
}
