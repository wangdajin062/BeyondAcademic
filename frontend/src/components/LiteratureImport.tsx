import React, { useState, useRef } from 'react';
import { literatureAPI } from '../services/literatureAPI';

interface Props {
  onClose: (refreshed?: boolean) => void;
}

export default function LiteratureImport({ onClose }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ imported: number; message: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f && (f.name.endsWith('.ris') || f.name.endsWith('.bib'))) {
      setFile(f);
      setError(null);
    } else {
      setError('Please drop a .ris or .bib file');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await literatureAPI.importFile(file);
      setResult({
        imported: res.imported,
        message: `Successfully imported ${res.imported} reference${res.imported !== 1 ? 's' : ''}.`,
      });
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Import failed');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    onClose(!!result);
  };

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-dialog modal-sm" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Import References</h3>
          <button className="modal-close-btn" onClick={handleClose}>&times;</button>
        </div>
        <div className="modal-body">
          {result ? (
            <div className="import-result">
              <div className="import-result-icon success">&#10003;</div>
              <p>{result.message}</p>
            </div>
          ) : (
            <>
              <div
                className={`import-dropzone ${dragOver ? 'drag-over' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => inputRef.current?.click()}
              >
                {file ? (
                  <div className="import-file-info">
                    <span className="import-file-icon">&#128196;</span>
                    <span className="import-file-name">{file.name}</span>
                    <span className="import-file-size">{(file.size / 1024).toFixed(1)} KB</span>
                  </div>
                ) : (
                  <>
                    <span className="import-dropzone-icon">&#128229;</span>
                    <p>Drop a .ris or .bib file here, or click to browse</p>
                  </>
                )}
                <input ref={inputRef} type="file" accept=".ris,.bib" hidden onChange={handleFileSelect} />
              </div>
              {error && <p className="form-error">{error}</p>}
            </>
          )}
        </div>
        <div className="modal-footer">
          {!result ? (
            <>
              <button className="btn btn-secondary" onClick={handleClose}>Cancel</button>
              <button className="btn btn-primary" onClick={handleUpload} disabled={!file || loading}>
                {loading ? 'Importing...' : 'Import'}
              </button>
            </>
          ) : (
            <button className="btn btn-primary" onClick={handleClose}>Done</button>
          )}
        </div>
      </div>
    </div>
  );
}
