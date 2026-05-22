import { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

function CodeNode({ data, selected }: NodeProps) {
  return (
    <div className={`custom-node code-node ${selected ? 'selected' : ''}`}>
      <Handle type="target" position={Position.Top} className="node-handle" />
      <div className="node-header">Code</div>
      <div className="node-body">
        {data.description ? (data.description as string).substring(0, 60) : '点击配置代码任务'}
      </div>
      {data.file_path && (
        <div style={{ fontSize: 11, color: '#888', padding: '2px 12px 8px' }}>
          File: {String(data.file_path).split('\\').pop()}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} className="node-handle" />
    </div>
  );
}

export default memo(CodeNode);
