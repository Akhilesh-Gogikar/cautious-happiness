"use client";
import React, { useState, useCallback, useRef } from 'react';
import ReactFlow, {
    ReactFlowProvider,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    addEdge,
    Connection,
    Edge
} from 'reactflow';
import 'reactflow/dist/style.css';

import { TriggerNode } from './nodes/TriggerNode';
import { ConditionNode } from './nodes/ConditionNode';
import { ActionNode } from './nodes/ActionNode';
import { KnowledgeNode } from './nodes/KnowledgeNode';
import { LLMNode } from './nodes/LLMNode';
import { ToolNode } from './nodes/ToolNode';
import { Sidebar } from './Sidebar';

const nodeTypes = {
    trigger: TriggerNode,
    condition: ConditionNode,
    action: ActionNode,
    knowledge: KnowledgeNode,
    llm: LLMNode,
    tool: ToolNode,
};

let id = 0;
const getId = () => `dndnode_${id++}`;

export function AgentBuilderCanvas() {
    const reactFlowWrapper = useRef<HTMLDivElement>(null);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);

    const onConnect = useCallback(
        (params: Edge | Connection) => setEdges((eds) => addEdge({ ...params, animated: true, style: { stroke: '#10B981' } }, eds)),
        [setEdges]
    );

    const onDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    const onDrop = useCallback(
        (event: React.DragEvent<HTMLDivElement>) => {
            event.preventDefault();

            const type = event.dataTransfer.getData('application/reactflow');
            if (typeof type === 'undefined' || !type) return;

            const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
            const position = reactFlowInstance.project({
                x: event.clientX - (reactFlowBounds?.left ?? 0),
                y: event.clientY - (reactFlowBounds?.top ?? 0),
            });

            let label = 'Node';
            if (type === 'trigger') label = 'Schedule Event';
            if (type === 'condition') label = 'Brent Crude drops 2%';
            if (type === 'action') label = 'Buy 10 contracts via Alpaca';
            if (type === 'knowledge') label = 'Select index...';
            if (type === 'llm') label = 'Configure model...';
            if (type === 'tool') label = 'Select tool...';

            const newNode = {
                id: getId(),
                type,
                position,
                data: { label },
            };

            setNodes((nds) => nds.concat(newNode));
        },
        [reactFlowInstance, setNodes]
    );

    return (
        <div className="flex h-full w-full bg-black">
            <ReactFlowProvider>
                <Sidebar />
                <div className="flex-1 h-full" ref={reactFlowWrapper}>
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onConnect={onConnect}
                        onInit={setReactFlowInstance}
                        onDrop={onDrop}
                        onDragOver={onDragOver}
                        nodeTypes={nodeTypes}
                        fitView
                        className="bg-black/90"
                    >
                        <Controls className="bg-zinc-800 border-zinc-700 fill-white" />
                        <Background color="#222" gap={16} />
                    </ReactFlow>
                </div>
            </ReactFlowProvider>
        </div>
    );
}
