import React from 'react';
import type { WritingStep } from '../types/paperWriting';

interface WorkflowOutlineProps {
  steps: WritingStep[];
  selectedStepId: string | null;
  sectionStatuses: Record<string, string>;
  onStepSelect: (stepId: string) => void;
}

const statusIcon: Record<string, string> = {
  complete: '✓',
  generating: '◦',
};

export default function WorkflowOutline({
  steps,
  selectedStepId,
  sectionStatuses,
  onStepSelect,
}: WorkflowOutlineProps) {
  if (steps.length === 0) {
    return (
      <div className="workflow-outline-empty">
        <p>No workflow steps defined.</p>
      </div>
    );
  }

  return (
    <div className="workflow-outline">
      <h3 className="workflow-outline-title">Writing Workflow</h3>
      <ul className="workflow-step-list">
        {steps.map((step, index) => {
          const status = sectionStatuses[step.id] || 'pending';
          const isSelected = step.id === selectedStepId;
          return (
            <li
              key={step.id}
              className={`workflow-step-item ${isSelected ? 'selected' : ''} ${status}`}
              onClick={() => onStepSelect(step.id)}
            >
              <div className="workflow-step-indicator">
                <span className="step-number">{index + 1}</span>
                <span className={`step-status-badge ${status}`}>
                  {status === 'complete' ? '✓' : status === 'generating' ? '◦' : ''}
                </span>
              </div>
              <div className="workflow-step-info">
                <span className="step-label">{step.label}</span>
                <span className="step-status-text">
                  {status === 'complete' ? 'Done' : status === 'generating' ? 'Generating...' : 'Pending'}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
