import { Handle, Position } from 'reactflow';
import { Play } from 'lucide-react';

export function ActionNode({ data, isConnectable }: any) {
    return (
        <div className="bg-zinc-900 border border-zinc-700 rounded-lg p-3 min-w-[200px] shadow-lg flex flex-col gap-2">
            <Handle
                type="target"
                position={Position.Top}
                isConnectable={isConnectable}
                className="w-3 h-3 bg-purple-500 border-zinc-900"
            />
            <div className="flex items-center gap-2 text-sm font-semibold text-purple-400">
                <Play className="w-4 h-4" />
                Action
            </div>
            <div className="text-xs text-zinc-400 bg-zinc-800 p-2 rounded border border-zinc-700">
                {data.label || 'Execute action'}
            </div>
        </div>
    );
}
