import { Handle, Position } from 'reactflow';
import { Wrench } from 'lucide-react';

export function ToolNode({ data, isConnectable }: any) {
    return (
        <div className="bg-zinc-900 border border-zinc-700 rounded-lg p-3 min-w-[200px] shadow-lg flex flex-col gap-2">
            <Handle
                type="target"
                position={Position.Top}
                isConnectable={isConnectable}
                className="w-3 h-3 bg-orange-500 border-zinc-900"
            />
            <div className="flex items-center gap-2 text-sm font-semibold text-orange-400">
                <Wrench className="w-4 h-4" />
                Tool Integration
            </div>
            <div className="text-xs text-zinc-400 bg-zinc-800 p-2 rounded border border-zinc-700">
                {data.label || 'Configure tool details'}
            </div>
            <Handle
                type="source"
                position={Position.Bottom}
                isConnectable={isConnectable}
                className="w-3 h-3 bg-orange-500 border-zinc-900"
            />
        </div>
    );
}
