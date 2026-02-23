"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthContext';
import { ArrowRight, ShieldCheck, Zap, Activity, Globe } from 'lucide-react';
import Link from 'next/link';

export default function LandingPage() {
    const { user, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && user) {
            router.push('/dashboard');
        }
    }, [user, isLoading, router]);

    if (isLoading) {
        return <div className="min-h-screen bg-background flex items-center justify-center">
            <div className="w-8 h-8 rounded-full border-t-2 border-primary animate-spin" />
        </div>;
    }

    return (
        <div className="min-h-screen bg-background text-foreground overflow-hidden font-sans selection:bg-primary/30 selection:text-white relative flex flex-col items-center justify-center">
            {/* Visual Background Elements */}
            <div className="absolute inset-0 pointer-events-none z-0">
                <div className="absolute top-[10%] left-[10%] w-[800px] h-[800px] bg-primary/10 blur-[120px] rounded-full opacity-40 mix-blend-screen animate-pulse-glow" />
                <div className="absolute bottom-[20%] right-[10%] w-[600px] h-[600px] bg-indigo/10 blur-[120px] rounded-full opacity-40 mix-blend-screen" />
                <div className="absolute top-[40%] left-[40%] w-[400px] h-[400px] bg-cyber-blue/5 blur-[100px] rounded-full opacity-30" />
            </div>

            {/* Grid Overlay */}
            <div className="absolute inset-0 z-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))] opacity-5" />

            <div className="relative z-10 w-full max-w-5xl px-6 flex flex-col items-center text-center space-y-12 animate-fade-in">

                {/* Header Section */}
                <div className="flex flex-col items-center space-y-6">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center relative overflow-hidden group">
                            <div className="absolute inset-0 bg-primary/20 translate-y-full group-hover:translate-y-0 transition-transform duration-500" />
                            <Zap className="w-6 h-6 text-primary relative z-10" />
                        </div>
                        <div className="flex flex-col text-left">
                            <h2 className="text-xl font-black tracking-tighter text-white leading-none">
                                <span className="text-primary text-glow-primary">ALPHA</span>
                                <span className="ml-1">INSIGHTS</span>
                            </h2>
                            <p className="text-[10px] text-muted-foreground/60 font-mono mt-1 tracking-[0.2em] font-bold uppercase">Terminal_v4.2</p>
                        </div>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white drop-shadow-2xl">
                        AI-Native <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-primary to-teal-500 animate-pulse-glow">Superintelligence</span> <br /> for the Modern Quant.
                    </h1>

                    <p className="text-lg md:text-xl text-muted-foreground max-w-2xl font-mono tracking-tight leading-relaxed">
                        Deploy specialized micro-agents, analyze real-time market sentiment, and synthesize master forecasts to outmaneuver the competition.
                    </p>
                </div>

                {/* Call To Action */}
                <div className="flex flex-col sm:flex-row gap-6 items-center w-full justify-center max-w-md">
                    <Link href="/login" className="w-full relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-primary/50 to-emerald-400/50 rounded-lg blur opacity-25 group-hover:opacity-100 transition duration-1000 group-hover:duration-200" />
                        <button className="relative w-full bg-black border border-primary/50 hover:border-primary text-white font-bold py-4 px-8 rounded-lg flex items-center justify-between transition-all group-hover:bg-primary/5">
                            <span className="font-mono uppercase tracking-widest text-sm text-primary">Initialize Access</span>
                            <ArrowRight className="w-5 h-5 text-primary group-hover:translate-x-1 transition-transform" />
                        </button>
                    </Link>
                </div>

                {/* Status Bar */}
                <div className="flex flex-wrap items-center justify-center gap-6 md:gap-12 text-[10px] font-mono text-muted-foreground uppercase tracking-[0.2em] mt-12 border-t border-white/10 pt-8 w-full">
                    <div className="flex items-center gap-2 group">
                        <Activity className="w-4 h-4 text-emerald-500/50 group-hover:text-emerald-500 transition-colors" />
                        <span>System: <span className="text-emerald-500">Operational</span></span>
                    </div>
                    <div className="flex items-center gap-2 group">
                        <ShieldCheck className="w-4 h-4 text-blue-500/50 group-hover:text-blue-500 transition-colors" />
                        <span>Security: <span className="text-blue-500">Quantum_Encrypted</span></span>
                    </div>
                    <div className="flex items-center gap-2 group">
                        <Globe className="w-4 h-4 text-purple-500/50 group-hover:text-purple-500 transition-colors" />
                        <span>Network: <span className="text-purple-500">Global_Mesh</span></span>
                    </div>
                </div>

            </div>
        </div>
    );
}
