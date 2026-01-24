"use client"

import React from 'react';
import { useAuth } from '@/components/providers/auth-context';
import { cn } from "@/lib/utils";
import { UserCog, Shield, Terminal, Search, User } from 'lucide-react';

const roles = [
    { id: 'trader', label: 'Trader', icon: Terminal, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    { id: 'risk_manager', label: 'Risk Manager', icon: Shield, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { id: 'developer', label: 'Developer', icon: UserCog, color: 'text-purple-500', bg: 'bg-purple-500/10' },
    { id: 'auditor', label: 'Auditor', icon: Search, color: 'text-amber-500', bg: 'bg-amber-500/10' },
];

export function RoleSwitcher() {
    const { user, switchRole } = useAuth();

    return (
        <div className="space-y-2 p-2 bg-white/5 rounded-lg border border-white/10">
            <p className="text-[9px] font-black font-mono text-muted-foreground/40 uppercase tracking-[0.2em] px-1">Role Control</p>
            <div className="grid grid-cols-2 gap-1">
                {roles.map((role) => {
                    const Icon = role.icon;
                    const isActive = user?.role === role.id;

                    return (
                        <button
                            key={role.id}
                            onClick={() => switchRole(role.id)}
                            className={cn(
                                "flex items-center gap-2 p-1.5 rounded transition-all border",
                                isActive
                                    ? `${role.bg} border-${role.id === 'trader' ? 'emerald' : role.id === 'risk_manager' ? 'blue' : role.id === 'developer' ? 'purple' : 'amber'}-500/30`
                                    : "bg-transparent border-transparent hover:bg-white/5"
                            )}
                        >
                            <Icon className={cn("w-3 h-3", isActive ? role.color : "text-muted-foreground")} />
                            <span className={cn("text-[10px] font-medium", isActive ? "text-white" : "text-muted-foreground")}>
                                {role.label.split(' ')[0]}
                            </span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
