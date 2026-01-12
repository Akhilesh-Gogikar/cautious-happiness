import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const backendUrl = process.env.BACKEND_URL || 'http://backend:8000';
        const authHeader = req.headers.get('Authorization');
        const targetUrl = `${backendUrl}/chat/stream`;

        const response = await fetch(targetUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(authHeader ? { 'Authorization': authHeader } : {}),
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            return new NextResponse(response.body, {
                status: response.status,
                statusText: response.statusText,
            });
        }

        // Return the stream directly
        return new NextResponse(response.body, {
            headers: {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            },
        });

    } catch (error) {
        console.error('Streaming proxy error:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
