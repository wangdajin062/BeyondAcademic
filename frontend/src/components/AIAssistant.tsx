import React, { useState } from 'react';
import type { WritingStep } from '../types/paperWriting';

interface AIAssistantProps {
  step: WritingStep | null;
  generatedOutput: string | null;
  isGenerating: boolean;
  sectionContent: string;
  onGenerate: (stepId: string) => void;
  onAccept: (content: string) => void;
}

export default function AIAssistant({
  step,
  generatedOutput,
  isGenerating,
  sectionContent,
  onGenerate,
  onAccept,
}: AIAssistantProps) {
  if (!step) {
    return (
      <div className="ai-assistant">
        <div className="ai-assistant-empty">
          <p>Select a step from the workflow to begin writing.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-assistant">
      <div className="ai-assistant-header">
        <h3>AI Assistant</h3>
        <span className="ai-assistant-step-label">{step.label}</span>
      </div>

      <div className="ai-assistant-prompt">
        <details>
          <summary>Prompt Template</summary>
          <pre className="prompt-text">{step.prompt}</pre>
        </details>
        {step.systemPrompt && (
          <details>
            <summary>System Prompt</summary>
            <pre className="prompt-text">{step.systemPrompt}</pre>
          </details>
        )}
      </div>

      <div className="ai-assistant-actions">
        <button
          className="ai-generate-btn"
          onClick={() => onGenerate(step.id)}
          disabled={isGenerating}
        >
          {isGenerating ? 'Generating...' : 'Generate with AI'}
        </button>
      </div>

      <div className="ai-assistant-output">
        <h4>Generated Output</h4>
        {isGenerating ? (
          <div className="ai-loading">
            <div className="ai-loading-spinner" />
            <p>AI is generating content...</p>
          </div>
        ) : generatedOutput ? (
          <div className="ai-output-content">
            <pre className="generated-text">{generatedOutput}</pre>
            <div className="ai-output-actions">
              <button
                className="accept-btn"
                onClick={() => onAccept(generatedOutput)}
              >
                Accept Content
              </button>
              <button
                className="regenerate-btn"
                onClick={() => onGenerate(step.id)}
              >
                Regenerate
              </button>
            </div>
          </div>
        ) : (
          <p className="ai-output-empty">
            Click "Generate with AI" to create content for this section.
          </p>
        )}
      </div>
    </div>
  );
}
