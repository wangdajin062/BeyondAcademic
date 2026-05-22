import React, { useRef, useCallback, useEffect } from 'react';
import Editor from '@monaco-editor/react';

interface SectionEditorProps {
  content: string;
  autoSaveStatus: 'idle' | 'saving' | 'saved' | 'error';
  onContentChange: (content: string) => void;
  sectionLabel: string;
}

export default function SectionEditor({
  content,
  autoSaveStatus,
  onContentChange,
  sectionLabel,
}: SectionEditorProps) {
  const handleChange = useCallback(
    (value: string | undefined) => {
      onContentChange(value || '');
    },
    [onContentChange]
  );

  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
  const charCount = content.length;

  const autoSaveColor =
    autoSaveStatus === 'saved'
      ? '#4caf50'
      : autoSaveStatus === 'saving'
      ? '#ff9800'
      : autoSaveStatus === 'error'
      ? '#f44336'
      : '#999';

  const autoSaveText =
    autoSaveStatus === 'saved'
      ? 'Saved'
      : autoSaveStatus === 'saving'
      ? 'Saving...'
      : autoSaveStatus === 'error'
      ? 'Save failed'
      : '';

  return (
    <div className="section-editor">
      <div className="section-editor-header">
        <h2 className="section-editor-title">{sectionLabel}</h2>
        <div className="section-editor-statusbar">
          {autoSaveText && (
            <span className="auto-save-indicator" style={{ color: autoSaveColor }}>
              {autoSaveText}
            </span>
          )}
          <span className="word-count">{wordCount} words</span>
          <span className="char-count">{charCount} chars</span>
        </div>
      </div>
      <div className="section-editor-body">
        <Editor
          height="100%"
          defaultLanguage="markdown"
          theme="vs-dark"
          value={content}
          onChange={handleChange}
          options={{
            minimap: { enabled: false },
            wordWrap: 'on',
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            fontSize: 14,
            padding: { top: 12 },
          }}
        />
      </div>
    </div>
  );
}
