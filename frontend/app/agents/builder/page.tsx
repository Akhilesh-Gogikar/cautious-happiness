
"use client";

import { useState, useRef, useEffect } from 'react';
import { Share2, Play, Save, Trash2, Settings, Plus, Terminal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface Node {
    id: string;
    type: 'agent' | 'tool' | 'trigger';
    position: { x: number; y: number };
    data: { label: string; details?: string };
}

interface Connection {
    id: string;
    source: string;
    target: string;
}

export default function AgentBuilderPage() {
    const [nodes, setNodes] = useState<Node[]>([]);
    const [connections, setConnections] = useState<Connection[]>([]);
    const [selectedNode, setSelectedNode] = useState<string | null>(null);
    const canvasRef = useRef<HTMLDivElement>(null);

    // Mock tool state to satisfy linter
    const [isLoadingTools] = useState(false);
    const [dynamicTools] = useState([
        { name: 'Data Fetcher', description: 'Fetch market data from API' },
        { name: 'Sentiment Analyzer', description: 'Analyze text sentiment' }
    ]);

    // dragging state
    const [isDragging, setIsDragging] = useState(false);
    const [draggedNodeId, setDraggedNodeId] = useState<string | null>(null);
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

    // connection state
    const [connectingSource, setConnectingSource] = useState<string | null>(null);

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        const type = e.dataTransfer.getData('nodeType');
        const label = e.dataTransfer.getData('nodeLabel');

        if (canvasRef.current) {
            const rect = canvasRef.current.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const newNode: Node = {
                id: `node-${Date.now()}`,
                type: type as any,
                position: { x, y },
                data: { label }
            };
            setNodes(prev => [...prev, newNode]);
        }
    };

    const handleDragOver = (e: React.DragEvent) => e.preventDefault();

    const startConnection = (nodeId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        setConnectingSource(nodeId);
        toast.info("Select target node to connect");
    };

    const completeConnection = (targetId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (connectingSource && connectingSource !== targetId) {
            setConnections(prev => [...prev, {
                id: `conn-${Date.now()}`,
                source: connectingSource,
                target: targetId
            }]);
            setConnectingSource(null);
            toast.success("Connected!");
        }
    };

    const handleMouseDown = (e: React.MouseEvent, nodeId: string) => {
        e.stopPropagation();
        setIsDragging(true);
        setDraggedNodeId(nodeId);
        setSelectedNode(nodeId);

        // Calculate offset
        const node = nodes.find(n => n.id === nodeId);
        if (node && canvasRef.current) {
            const rect = canvasRef.current.getBoundingClientRect();
            setDragOffset({
                x: e.clientX - rect.left - node.position.x,
                y: e.clientY - rect.top - node.position.y
            });
        }
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (isDragging && draggedNodeId && canvasRef.current) {
            const rect = canvasRef.current.getBoundingClientRect();
            const x = e.clientX - rect.left - dragOffset.x;
            const y = e.clientY - rect.top - dragOffset.y;

            setNodes(prev => prev.map(n =>
                n.id === draggedNodeId ? { ...n, position: { x, y } } : n
            ));
        }
    };

    const handleMouseUp = () => {
        setIsDragging(false);
        setDraggedNodeId(null);
    };

    const deleteSelected = () => {
        if (selectedNode) {
            setNodes(prev => prev.filter(n => n.id !== selectedNode));
            setConnections(prev => prev.filter(c => c.source !== selectedNode && c.target !== selectedNode));
            setSelectedNode(null);
        }
    };

    const runSimulation = () => {
        toast.promise(
            new Promise(resolve => setTimeout(resolve, 3000)),
            {
                loading: 'Orchestrating Agents... (Mirror -> Critic -> Kelly)',
                success: 'Workflow executed! Optimal Size: $420.69 (VWAP: 0.82)',
                error: 'Execution failed',
            }
        );
    };

    return (
        <div className="flex h-screen bg-background overflow-hidden" onMouseUp={handleMouseUp} onMouseMove={handleMouseMove}>
            {/* Sidebar */}
            <div className="w-64 border-r border-white/10 flex flex-col bg-black/20 backdrop-blur-md">
                <div className="p-4 border-b border-white/10">
                    <h2 className="font-bold text-sm tracking-widest text-white flex items-center gap-2">
                        <Share2 className="w-4 h-4 text-primary" />
                        WORKFLOW_NODES
                    </h2>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-6">
                    <div className="space-y-2">
                        <p className="text-xs text-muted-foreground font-mono uppercase">Core Agents</p>
                        <DraggableItem type="agent" label="Intelligence Mirror" details="Forecast Engine" />
                        <DraggableItem type="agent" label="The Critic" details="Hallucination Firewall" />
                        <DraggableItem type="agent" label="Kelly Engine" details="Slippage-Aware Sizing" />
                    </div>

                    <div className="space-y-2">
                        <p className="text-xs text-muted-foreground font-mono uppercase">Dynamic Tools (MCP)</p>
                        {isLoadingTools ? (
                            <div className="p-4 text-center text-xs animate-pulse opacity-50">Loading MCP tools...</div>
                        ) : (
                            dynamicTools.map(tool => (
                                <DraggableItem key={tool.name} type="tool" label={tool.name} details={tool.description} />
                            ))
                        )}
                    </div>

                    <div className="space-y-2">
                        <p className="text-xs text-muted-foreground font-mono uppercase">Triggers</p>
                        <DraggableItem type="trigger" label="Price Alert" />
                        <DraggableItem type="trigger" label="Schedule (Daily)" />
                    </div>
                </div>
            </div>

            {/* Main Canvas Area */}
            <div className="flex-1 flex flex-col relative">
                {/* Visual Grid Background */}
                <div className="absolute inset-0 bg-[size:20px_20px] bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] pointer-events-none" />

                {/* Toolbar */}
                <div className="h-14 border-b border-white/10 flex items-center justify-between px-4 bg-black/10 z-10 backdrop-blur-sm">
                    <div className="flex items-center gap-2">
                        <Button size="sm" variant="ghost">File</Button>
                        <Button size="sm" variant="ghost">Edit</Button>
                        <Button size="sm" variant="ghost">View</Button>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button size="sm" variant="outline" className="gap-2" onClick={deleteSelected} disabled={!selectedNode}>
                            <Trash2 className="w-4 h-4" />
                            Delete
                        </Button>
                        <Button size="sm" className="bg-primary hover:bg-emerald-600 text-black font-bold gap-2" onClick={runSimulation}>
                            <Play className="w-4 h-4" />
                            Run Workflow
                        </Button>
                    </div>
                </div>

                {/* Canvas */}
                <div
                    ref={canvasRef}
                    className="flex-1 relative overflow-hidden custom-scrollbar"
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                >
                    <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
                        {connections.map(conn => {
                            const source = nodes.find(n => n.id === conn.source);
                            const target = nodes.find(n => n.id === conn.target);
                            if (!source || !target) return null;

                            // Simple bezier curve logic
                            // assuming node width ~150, height ~60, center connection
                            const sx = source.position.x + 150;
                            const sy = source.position.y + 40;
                            const tx = target.position.x;
                            const ty = target.position.y + 40;

                            return (
                                <path
                                    key={conn.id}
                                    d={`M ${sx} ${sy} C ${sx + 50} ${sy}, ${tx - 50} ${ty}, ${tx} ${ty}`}
                                    stroke="#10B981"
                                    strokeWidth="2"
                                    fill="none"
                                />
                            );
                        })}
                        {connectingSource && (
                            // Draw temporary line following mouse? Requires mouse state. Omitted for MVP simplicty.
                            null
                        )}
                    </svg>

                    {nodes.map(node => (
                        <div
                            key={node.id}
                            style={{
                                left: node.position.x,
                                top: node.position.y,
                                width: '180px'
                            }}
                            className={`absolute z-10 p-3 rounded-lg border backdrop-blur-md cursor-grab active:cursor-grabbing transition-shadow group
                                ${node.type === 'agent' ? 'bg-indigo-900/40 border-indigo-500/30 text-indigo-100' : ''}
                                ${node.type === 'tool' ? 'bg-emerald-900/40 border-emerald-500/30 text-emerald-100' : ''}
                                ${node.type === 'trigger' ? 'bg-amber-900/40 border-amber-500/30 text-amber-100' : ''}
                                ${selectedNode === node.id ? 'ring-2 ring-white/50 shadow-lg shadow-primary/20' : ''}
                            `}
                            onMouseDown={(e) => handleMouseDown(e, node.id)}
                            onClick={(e) => completeConnection(node.id, e)}
                        >
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-mono opacity-70 uppercase">{node.type}</span>
                                <Settings className="w-3 h-3 opacity-50 hover:opacity-100 cursor-pointer" />
                            </div>
                            <p className="font-bold text-sm truncate">{node.data.label}</p>

                            {/* Connection Handles */}
                            <div
                                className="absolute right-[-6px] top-1/2 -translate-y-1/2 w-3 h-3 bg-white/50 rounded-full cursor-crosshair hover:bg-white hover:scale-125 transition-all"
                                onClick={(e) => startConnection(node.id, e)}
                                title="Connect Output"
                            />
                            <div className="absolute left-[-6px] top-1/2 -translate-y-1/2 w-3 h-3 bg-white/20 rounded-full pointer-events-none" />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

function DraggableItem({ type, label, details }: { type: string, label: string, details?: string }) {
    const handleDragStart = (e: React.DragEvent) => {
        e.dataTransfer.setData('nodeType', type);
        e.dataTransfer.setData('nodeLabel', label);
        if (details) e.dataTransfer.setData('nodeDetails', details);
        e.dataTransfer.effectAllowed = 'copy';
    };

    return (
        <div
            draggable
            onDragStart={handleDragStart}
            className="p-3 rounded border border-white/5 bg-white/5 hover:bg-white/10 hover:border-primary/30 transition-colors cursor-grab active:cursor-grabbing flex flex-col group gap-1"
        >
            <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{label}</span>
                <Plus className="w-4 h-4 opacity-0 group-hover:opacity-50" />
            </div>
            {details && <p className="text-[10px] opacity-40 uppercase font-mono truncate">{details}</p>}
        </div>
    );
}
