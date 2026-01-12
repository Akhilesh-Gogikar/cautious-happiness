'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Activity, Database, Lock, Globe, Cpu } from 'lucide-react';

export interface ModuleState {
  name: string;
  status: 'ACTIVE' | 'PROCESSING' | 'BLOCKING' | 'OFFLINE';
  icon: React.ReactNode;
}

export function ModelStateIndicators() {
  const modules: ModuleState[] = [
    { name: 'SENTIMENT', status: 'ACTIVE', icon: <Globe className="w-3 h-3" /> },
    { name: 'MACRO', status: 'PROCESSING', icon: <Database className="w-3 h-3" /> },
    { name: 'RISK', status: 'ACTIVE', icon: <Lock className="w-3 h-3" /> },
    { name: 'EXECUTION', status: 'BLOCKING', icon: <Activity className="w-3 h-3" /> },
    { name: 'LLM CORE', status: 'ACTIVE', icon: <Cpu className="w-3 h-3" /> },
  ];

  return (
    <div className="grid grid-cols-5 gap-2 w-full">
      {modules.map((mod) => (
        <div 
          key={mod.name}
          className={cn(
            "flex flex-col items-center justify-center p-2 rounded bg-white/5 border border-white/10 transition-all hover:bg-white/10",
            mod.status === 'BLOCKING' && "border-yellow-500/50 bg-yellow-500/10",
            mod.status === 'OFFLINE' && "border-red-500/50 opacity-50"
          )}
        >
           <div className={cn(
               "mb-1 px-1.5 py-0.5 rounded-full text-[9px] font-bold tracking-wider",
               mod.status === 'ACTIVE' && "bg-emerald-500/20 text-emerald-300",
               mod.status === 'PROCESSING' && "bg-blue-500/20 text-blue-300 animate-pulse",
               mod.status === 'BLOCKING' && "bg-yellow-500/20 text-yellow-300",
               mod.status === 'OFFLINE' && "bg-red-500/20 text-red-300"
           )}>
              {mod.status}
           </div>
           <div className="text-white/40 mb-1">{mod.icon}</div>
           <span className="text-[9px] font-bold text-white/70 tracking-tight">{mod.name}</span>
        </div>
      ))}
    </div>
  );
}
