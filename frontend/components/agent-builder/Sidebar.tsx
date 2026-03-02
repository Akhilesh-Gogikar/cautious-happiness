"use client";
import React from 'react';
import { Zap, Filter, Play, Database, Brain, Wrench } from 'lucide-react';

export function Sidebar() {
    const onDragStart = (event: React.DragEvent<HTMLDivElement>, nodeType: string) => {
        event.dataTransfer.setData('application/reactflow', nodeType);
        event.dataTransfer.effectAllowed = 'move';
    };

    return (
        <aside className="w-64 border-r border-white/10 bg-black/40 p-4 flex flex-col gap-4 overflow-y-auto">
            <div className="flex flex-col gap-1">
                <h3 className="text-sm font-semibold text-white/80">Triggers & Logic</h3>
                <p className="text-xs text-muted-foreground">Drag nodes to start</p>
            </div>

            <div
                className="p-3 border border-emerald-500/30 bg-emerald-500/5 rounded cursor-grab flex items-center gap-2 text-sm text-emerald-400 hover:bg-emerald-500/10 transition-colors"
                onDragStart={(event) => onDragStart(event, 'trigger')}
                draggable
            >
                <Zap className="w-4 h-4" /> Trigger Component
            </div>

            <div
                className="p-3 border border-blue-500/30 bg-blue-500/5 rounded cursor-grab flex items-center gap-2 text-sm text-blue-400 hover:bg-blue-500/10 transition-colors"
                onDragStart={(event) => onDragStart(event, 'condition')}
                draggable
            >
                <Filter className="w-4 h-4" /> Condition Logic
            </div>

            <div className="flex flex-col gap-1 mt-2">
                <h3 className="text-sm font-semibold text-white/80">AI & Data</h3>
            </div>

            <div
                className="p-3 border border-rose-500/30 bg-rose-500/5 rounded cursor-grab flex items-center gap-2 text-sm text-rose-400 hover:bg-rose-500/10 transition-colors"
                onDragStart={(event) => onDragStart(event, 'llm')}
                draggable
            >
                <Brain className="w-4 h-4" /> LLM Core
            </div>

            <div
                className="p-3 border border-cyan-500/30 bg-cyan-500/5 rounded cursor-grab flex items-center gap-2 text-sm text-cyan-400 hover:bg-cyan-500/10 transition-colors"
                onDragStart={(event) => onDragStart(event, 'knowledge')}
                draggable
            >
                <Database className="w-4 h-4" /> Knowledge Base
            </div>

            <div className="flex flex-col gap-1 mt-2">
                <h3 className="text-sm font-semibold text-white/80">Execution</h3>
            </div>

            <div
                className="p-3 border border-orange-500/30 bg-orange-500/5 rounded cursor-grab flex items-center gap-2 text-sm text-orange-400 hover:bg-orange-500/10 transition-colors"
                onDragStart={(event) => onDragStart(event, 'tool')}
                draggable
            >
                <Wrench className="w-4 h-4" /> Tool Integration
            </div>

            <div
                className="p-3 border border-purple-500/30 bg-purple-500/5 rounded cursor-grab flex items-center gap-2 text-sm text-purple-400 hover:bg-purple-500/10 transition-colors"
                onDragStart={(event) => onDragStart(event, 'action')}
                draggable
            >
                <Play className="w-4 h-4" /> Action Executor
            </div>
        </aside>
    );
}
