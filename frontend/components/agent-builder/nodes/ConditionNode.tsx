import { Handle, Position } from 'reactflow';
import { Filter } from 'lucide-react';

export function ConditionNode({ data, isConnectable }: any) {
    return (
        <div className="bg-zinc-900 border border-zinc-700 rounded-lg p-3 min-w-[200px] shadow-lg flex flex-col gap-2">
            <Handle
                type="target"
                position={Position.Top}
                isConnectable={isConnectable}
                className="w-3 h-3 bg-blue-500 border-zinc-900"
            />
            <div className="flex items-center gap-2 text-sm font-semibold text-blue-400">
                <Filter className="w-4 h-4" />
                Condition
            </div>
            <div className="text-xs text-zinc-400 bg-zinc-800 p-2 rounded border border-zinc-700">
                {data.label || 'IF condition is true'}
            </div>
            <Handle
                type="source"
                position={Position.Bottom}
                id="true"
                isConnectable={isConnectable}
                className="w-3 h-3 bg-blue-500 border-zinc-900 mr-[25%]"
            />
            <Handle
                type="source"
                position={Position.Bottom}
                id="false"
                isConnectable={isConnectable}
                className="w-3 h-3 bg-red-500 border-zinc-900 ml-[25%]"
            />
        </div>
    );
}
