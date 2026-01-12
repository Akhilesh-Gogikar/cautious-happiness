"use client"

import { useAuth } from '@/components/providers/auth-context';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ProfilePage() {
    const { user, isAuthenticated, isLoading, logout } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.push('/login');
        }
    }, [isLoading, isAuthenticated, router]);

    if (isLoading || !user) {
        return <div className="flex h-screen items-center justify-center text-muted-foreground font-mono">LOADING_PROFILE...</div>;
    }

    return (
        <div className="container max-w-4xl mx-auto py-10 space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-6">
                <div>
                    <h1 className="text-3xl font-black tracking-tight text-white">USER PROFILE</h1>
                    <p className="text-muted-foreground font-mono text-sm mt-1">IDENTITY_MANAGEMENT // {user.email}</p>
                </div>
                <Button variant="destructive" onClick={logout} className="gap-2">
                    <span className="font-mono uppercase text-xs">Terminate Session</span>
                </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* Identity Card */}
                <Card className="md:col-span-2 bg-black/20 border-white/10 backdrop-blur-sm">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-primary" />
                            Identity Information
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="grid grid-cols-2 gap-6">
                            <div className="space-y-1">
                                <label className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">Full Name</label>
                                <div className="text-lg font-medium text-white">{user.full_name}</div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">Role / Clearance</label>
                                <div className="flex items-center gap-2">
                                    <div className="px-2 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono font-bold uppercase tracking-widest">
                                        {user.role}
                                    </div>
                                </div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">Email Address</label>
                                <div className="text-base font-mono text-white/80">{user.email}</div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">Account Status</label>
                                <div className="text-base font-mono text-emerald-400 flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                                    ACTIVE
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* RBAC / Permissions Card */}
                <Card className="bg-black/20 border-white/10 backdrop-blur-sm">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-indigo-500" />
                            Access Control
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="p-3 rounded bg-white/5 border border-white/10">
                                <div className="text-xs font-mono text-muted-foreground mb-2">CURRENT CLEARANCE</div>
                                <div className="text-xl font-black text-white uppercase tracking-tight">{user.role}</div>
                            </div>

                            <div className="space-y-2">
                                <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">Modules Enabled</div>
                                <ul className="space-y-1.5">
                                    {['Dashboard Access', 'Market Data', 'Execution'].map((perm) => (
                                        <li key={perm} className="flex items-center gap-2 text-sm text-white/70">
                                            <div className="w-1 h-1 bg-emerald-500 rounded-full" />
                                            {perm}
                                        </li>
                                    ))}
                                    {user.role === 'admin' && (
                                        <li className="flex items-center gap-2 text-sm text-white/70">
                                            <div className="w-1 h-1 bg-gold rounded-full" />
                                            System Configuration
                                        </li>
                                    )}
                                </ul>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Security Settings */}
                <Card className="md:col-span-3 bg-black/20 border-white/10 backdrop-blur-sm">
                    <CardHeader>
                        <CardTitle className="text-lg font-bold flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-red-500" />
                            Security & 2FA
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex items-center justify-between">
                        <div>
                            <p className="text-white font-medium">Password Recovery</p>
                            <p className="text-sm text-muted-foreground">Security questions are configured.</p>
                        </div>
                        <Button variant="outline" disabled className="opacity-50 cursor-not-allowed">
                            Manage Keys
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
