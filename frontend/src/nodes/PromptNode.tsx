import { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

function PromptNode({ data, selected }: NodeProps) {
  return (
    <div className={`custom-node prompt-node ${selected ? 'selected' : ''}`}>
      <Handle type="target" position={Position.Top} className="node-handle" />
      <div className="node-header">Prompt</div>
      <div className="node-body">
        {data.prompt ? (data.prompt as string).substring(0, 60) + ((data.prompt as string).length > 60 ? '...' : '') : '点击配置提示词'}
      </div>
      {data.provider && (
        <div style={{ fontSize: 11, color: '#888', padding: '2px 12px 8px' }}>
          Model: {String(data.provider)}/{String(data.model || 'default')}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} className="node-handle" />
    </div>
  );
}

export default memo(PromptNode);
