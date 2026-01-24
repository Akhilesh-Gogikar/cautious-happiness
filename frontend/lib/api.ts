const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

export interface User {
    email: string;
    full_name: string;
    role: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    password: string;
    full_name: string;
    security_question: string;
    security_answer: string;
}

const getAuthToken = () => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('token');
    }
    return null;
};

export async function login(credentials: LoginRequest): Promise<AuthResponse> {
    const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
    });
    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(JSON.parse(errorText).detail || 'Login failed');
    }
    return res.json();
}

export async function register(userData: RegisterRequest): Promise<AuthResponse> {
    const res = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
    });
    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(JSON.parse(errorText).detail || 'Registration failed');
    }
    return res.json();
}

export async function getMe(): Promise<User> {
    const token = getAuthToken();
    if (!token) throw new Error('No token found');

    const res = await fetch(`${API_URL}/auth/me`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (!res.ok) throw new Error('Failed to fetch user profile');
    return res.json();
}


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
    const token = getAuthToken();
    const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Chat failed');
    return res.json();
}


export async function fetchChatHistory(context?: string) {
    const token = getAuthToken();
    const url = context
        ? `${API_URL}/auth/chat-history?context=${encodeURIComponent(context)}`
        : `${API_URL}/auth/chat-history`;

    const res = await fetch(url, {
        headers: {
            'Authorization': token ? `Bearer ${token}` : ''
        }
    });
    if (!res.ok) throw new Error('Failed to fetch chat history');
    return res.json();
}


export async function streamChat(payload: { question: string, context: string, user_message: string, selected_agents?: string[] }) {
    const token = getAuthToken();
    const res = await fetch(`${API_URL}/chat/stream`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        },
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

export const api = {
    get: async (url: string, options: RequestInit = {}) => {
        const fullUrl = url.startsWith('http') ? url : `${API_URL}${url}`;
        const token = getAuthToken();

        const res = await fetch(fullUrl, {
            ...options,
            headers: {
                'Authorization': token ? `Bearer ${token}` : '',
                ...options.headers
            }
        });

        if (!res.ok) {
            const errorText = await res.text();
            throw new Error(errorText || `API Error: ${res.statusText}`);
        }

        const data = await res.json();
        return { data };
    },

    post: async (url: string, body?: any, options: RequestInit = {}) => {
        const fullUrl = url.startsWith('http') ? url : `${API_URL}${url}`;
        const token = getAuthToken();

        const res = await fetch(fullUrl, {
            method: 'POST',
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : '',
                ...options.headers
            },
            body: body ? JSON.stringify(body) : undefined
        });

        if (!res.ok) {
            const errorText = await res.text();
            throw new Error(errorText || `API Error: ${res.statusText}`);
        }

        const data = await res.json();
        return { data };
    },
    updateUserRole: async (role: string) => {
        const res = await fetch(`${API_URL}/auth/role`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ role })
        });
        if (!res.ok) throw new Error('Failed to update role');
        return res.json();
    }
};

