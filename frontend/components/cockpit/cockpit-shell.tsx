'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface CockpitShellProps {
    children?: React.ReactNode;
    sidebar?: React.ReactNode;
    timeline?: React.ReactNode;
    className?: string;
}

export function CockpitShell({
    children,
    sidebar,
    timeline,
    className
}: CockpitShellProps) {
    return (
        <div className={cn(
            "flex h-screen w-full overflow-hidden bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-gray-900 via-[#0a0a0a] to-black",
            className
        )}>
            {/* Left Reasoning Sidebar - "The Stream" */}
            <aside className="w-[400px] flex-shrink-0 border-r border-white/10 bg-black/40 backdrop-blur-xl transition-all duration-300">
                <div className="flex h-full flex-col">
                    {sidebar}
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex min-w-0 flex-1 flex-col relative">
                {/* Top Header / Status Bar could go here */}

                {/* Primary View */}
                <div className="flex-1 overflow-y-auto p-6 scrollbar-hide">
                    {children}
                </div>

                {/* Bottom Timeline Overlay */}
                <div className="h-48 border-t border-white/10 bg-black/60 backdrop-blur-md transition-all duration-300">
                    {timeline}
                </div>
            </main>
        </div>
    );
}
