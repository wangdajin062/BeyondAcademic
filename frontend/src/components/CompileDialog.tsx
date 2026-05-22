import React from 'react';

interface CompileDialogProps {
  isOpen: boolean;
  compiledContent: string;
  isLoading: boolean;
  onClose: () => void;
  onExportMarkdown: () => void;
}

export default function CompileDialog({
  isOpen,
  compiledContent,
  isLoading,
  onClose,
  onExportMarkdown,
}: CompileDialogProps) {
  if (!isOpen) return null;

  return (
    <div className="compile-overlay" onClick={onClose}>
      <div className="compile-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="compile-dialog-header">
          <h2>Compiled Paper</h2>
          <button className="compile-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="compile-dialog-body">
          {isLoading ? (
            <div className="compile-loading">
              <p>Compiling paper...</p>
            </div>
          ) : compiledContent ? (
            <pre className="compile-content">{compiledContent}</pre>
          ) : (
            <div className="compile-empty">
              <p>No completed sections to compile. Write some content first, then try again.</p>
            </div>
          )}
        </div>

        <div className="compile-dialog-footer">
          <button className="compile-export-btn" onClick={onExportMarkdown} disabled={!compiledContent}>
            Export Markdown
          </button>
          <button className="compile-close-btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
