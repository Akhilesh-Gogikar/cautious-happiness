"use client";

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight, Shield, Zap, Globe, BarChart3, Lock } from 'lucide-react';
import { useAuth } from '@/components/providers/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function LandingPage() {
    const { isAuthenticated, isLoading, login } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && isAuthenticated) {
            router.push('/tradedesk');
        }
    }, [isLoading, isAuthenticated, router]);

    if (isLoading) return null;

    return (
        <div className="flex flex-col min-h-screen bg-black text-white selection:bg-primary/30 selection:text-white overflow-x-hidden">
            {/* Background Effects */}
            <div className="fixed inset-0 pointer-events-none z-0">
                <div className="absolute top-[-20%] right-[-10%] w-[800px] h-[800px] bg-primary/20 blur-[120px] rounded-full opacity-30 animate-pulse-glow" />
                <div className="absolute bottom-[-20%] left-[-10%] w-[600px] h-[600px] bg-indigo-500/10 blur-[120px] rounded-full opacity-30" />
                <div className="absolute top-[20%] left-[20%] w-[400px] h-[400px] bg-blue-500/10 blur-[100px] rounded-full opacity-20" />
                <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]" />
            </div>

            {/* Navigation */}
            <header className="fixed top-0 w-full z-50 border-b border-white/5 bg-black/50 backdrop-blur-xl">
                <div className="container mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-emerald-600 flex items-center justify-center">
                            <Zap className="w-5 h-5 text-white fill-current" />
                        </div>
                        <span className="text-xl font-bold tracking-tight text-white">
                            Alpha<span className="text-primary">Signals</span>
                        </span>
                    </div>
                    <div className="flex items-center gap-4">
                        <Button
                            variant="ghost"
                            className="text-muted-foreground hover:text-white hover:bg-white/5"
                            onClick={() => login('trader')}
                        >
                            Log in
                        </Button>
                        <Button
                            className="bg-primary hover:bg-primary/90 text-black font-semibold shadow-[0_0_20px_rgba(16,185,129,0.3)]"
                            onClick={() => login('trader')}
                        >
                            Get Started <ArrowRight className="ml-2 w-4 h-4" />
                        </Button>
                    </div>
                </div>
            </header>

            <main className="flex-1 relative z-10 pt-32 pb-20">
                <div className="container mx-auto px-6">
                    {/* Hero Section */}
                    <div className="flex flex-col items-center text-center max-w-4xl mx-auto space-y-8 animate-fade-in">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-primary mb-4 animate-in fade-in slide-in-from-bottom-4 duration-1000">
                            <span className="flex h-2 w-2 relative">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                            </span>
                            v4.2.0 NOW LIVE
                        </div>

                        <h1 className="text-5xl md:text-7xl font-black tracking-tighter leading-[1.1] bg-clip-text text-transparent bg-gradient-to-b from-white via-white to-white/50 drop-shadow-2xl">
                            Institutional Grade <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-emerald-200 to-primary animate-pulse-slow">
                                Market Intelligence
                            </span>
                        </h1>

                        <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                            Advanced AI-driven analytics, real-time sentiment analysis, and predictive modeling for the modern trader.
                            Identify alpha before the market reacts.
                        </p>

                        <div className="flex flex-col sm:flex-row items-center gap-4 pt-4">
                            <Button
                                size="lg"
                                className="h-12 px-8 text-base bg-primary hover:bg-primary/90 text-black font-bold shadow-[0_0_30px_rgba(16,185,129,0.4)] transition-all hover:scale-105"
                                onClick={() => login('trader')}
                            >
                                Start Trading Now
                            </Button>
                            <Button
                                size="lg"
                                variant="outline"
                                className="h-12 px-8 text-base border-white/10 hover:bg-white/5 hover:text-white transition-all"
                                onClick={() => login('trader')}
                            >
                                View Live Demo
                            </Button>
                        </div>
                    </div>

                    {/* Features Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-32">
                        <FeatureCard
                            icon={<BarChart3 className="w-6 h-6 text-primary" />}
                            title="Predictive Analytics"
                            description="Proprietary ML models forecasting market movements with high-confidence intervals."
                        />
                        <FeatureCard
                            icon={<Globe className="w-6 h-6 text-indigo-400" />}
                            title="Global Sentiment"
                            description="Real-time aggregation of news, social media, and institutional flows."
                        />
                        <FeatureCard
                            icon={<Lock className="w-6 h-6 text-rose-400" />}
                            title="Enterprise Security"
                            description="Bank-grade encryption and secure infrastructure for your trading data."
                        />
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="border-t border-white/5 bg-black/50 py-12 relative z-10">
                <div className="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
                    <p className="text-sm text-muted-foreground">
                        © 2024 AlphaSignals. All rights reserved.
                    </p>
                    <div className="flex items-center gap-6 text-sm text-muted-foreground">
                        <Link href="#" className="hover:text-white transition-colors">Terms</Link>
                        <Link href="#" className="hover:text-white transition-colors">Privacy</Link>
                        <Link href="#" className="hover:text-white transition-colors">Contact</Link>
                    </div>
                </div>
            </footer>
        </div>
    );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
    return (
        <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 hover:bg-white/[0.04] transition-all group">
            <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                {icon}
            </div>
            <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
            <p className="text-muted-foreground leading-relaxed">
                {description}
            </p>
        </div>
    );
}
