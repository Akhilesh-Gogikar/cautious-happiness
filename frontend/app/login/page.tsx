"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthContext';
import { User, Lock, ArrowRight, ShieldCheck, Zap, Loader2 } from 'lucide-react';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const { login } = useAuth();
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!username.trim() || !password) {
            setError('Enter your username and password.');
            return;
        }

        setSubmitting(true);
        try {
            // The backend checks the credentials and issues the session token.
            await login(username.trim(), password);
            router.push('/dashboard');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Sign-in failed.');
            setSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden font-sans">
            {/* Visual Background Elements */}
            <div className="absolute inset-0 pointer-events-none z-0">
                <div className="absolute top-[10%] left-[20%] w-[600px] h-[600px] bg-primary/10 blur-[120px] rounded-full opacity-40 mix-blend-screen animate-pulse-glow" />
                <div className="absolute bottom-[10%] right-[20%] w-[500px] h-[500px] bg-indigo/10 blur-[120px] rounded-full opacity-40 mix-blend-screen" />
            </div>

            <div className="w-full max-w-md p-8 relative z-10 animate-fade-in">
                <div className="flex flex-col items-center justify-center mb-10 text-center">
                    <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(16,185,129,0.2)] border border-primary/20">
                        <Zap className="w-8 h-8 text-primary" />
                    </div>
                    <h1 className="text-4xl font-black tracking-tighter text-white mb-2">
                        ALPHA <span className="text-primary text-glow-primary">INSIGHTS</span>
                    </h1>
                    <p className="text-sm font-mono text-muted-foreground uppercase tracking-widest">
                        Neural Domain Access
                    </p>
                </div>

                <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl relative overflow-hidden group">
                    <div className="absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent opacity-50" />

                    <form onSubmit={handleSubmit} className="space-y-6 relative z-10">
                        <div className="space-y-2">
                            <label htmlFor="username" className="text-xs font-mono text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                                <User className="w-3 h-3 text-primary" />
                                Username
                            </label>
                            <input
                                id="username"
                                type="text"
                                autoComplete="username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="operator"
                                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all font-mono text-sm"
                            />
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="password" className="text-xs font-mono text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                                <Lock className="w-3 h-3 text-primary" />
                                Password
                            </label>
                            <input
                                id="password"
                                type="password"
                                autoComplete="current-password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all font-mono text-sm"
                            />
                        </div>

                        {error && (
                            <p role="alert" className="text-[11px] text-red-500 font-mono">
                                {error}
                            </p>
                        )}

                        <button
                            type="submit"
                            disabled={submitting}
                            className="w-full bg-primary hover:bg-emerald-400 disabled:opacity-60 disabled:hover:scale-100 text-black font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all transform hover:scale-[1.02] active:scale-[0.98] mt-4 shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)]"
                        >
                            <span>{submitting ? 'Signing In' : 'Initialize Uplink'}</span>
                            {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
                        </button>
                    </form>

                    <div className="mt-8 pt-6 border-t border-white/5 flex flex-col items-center gap-3">
                        <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground/60">
                            <ShieldCheck className="w-3 h-3 text-primary/50" />
                            <span>Quantum-Encrypted Connection</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
