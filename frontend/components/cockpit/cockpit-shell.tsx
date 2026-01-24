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
            "flex flex-col h-full w-full overflow-hidden",
            className
        )}>
            <div className="flex flex-1 min-h-0">
                {/* Left Reasoning Sidebar - "The Stream" */}
                {sidebar && (
                    <aside className="w-[350px] flex-shrink-0 border-r border-white/5 bg-black/20 backdrop-blur-md transition-all duration-300">
                        <div className="flex h-full flex-col">
                            {sidebar}
                        </div>
                    </aside>
                )}

                {/* Main Content Area */}
                <main className="flex min-w-0 flex-1 flex-col relative overflow-hidden">
                    {/* Primary View */}
                    <div className="flex-1 overflow-y-auto p-6 scrollbar-hide">
                        {children}
                    </div>

                    {/* Bottom Timeline Overlay */}
                    {timeline && (
                        <div className="h-48 border-t border-white/10 bg-black/60 backdrop-blur-md transition-all duration-300 flex-shrink-0">
                            {timeline}
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
}
