import { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

function OutputNode({ data, selected }: NodeProps) {
  return (
    <div className={`custom-node output-node ${selected ? 'selected' : ''}`}>
      <Handle type="target" position={Position.Top} className="node-handle" />
      <div className="node-header">Output</div>
      <div className="node-body">
        {data.output ? (data.output as string).substring(0, 80) + '...' : '等待执行...'}
      </div>
      <Handle type="source" position={Position.Bottom} className="node-handle" />
    </div>
  );
}

export default memo(OutputNode);
