import React, { useState } from 'react';
import type { LiteratureItem } from '../types/literature';

interface Props {
  item: LiteratureItem;
  onClose: () => void;
  onEdit: (item: LiteratureItem) => void;
  onDelete: (id: string) => void;
}

export default function LiteratureDetail({ item, onClose, onEdit, onDelete }: Props) {
  const [showAbstract, setShowAbstract] = useState(false);

  const getTypeLabel = (type: string) => {
    const map: Record<string, string> = {
      article: 'Journal Article',
      book: 'Book',
      conference: 'Conference Paper',
      thesis: 'Thesis',
      report: 'Report',
    };
    return map[type] || type;
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog modal-lg" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Reference Details</h3>
          <button className="modal-close-btn" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body literature-detail">
          <div className="literature-detail-type">{getTypeLabel(item.ref_type)}</div>
          <h2 className="literature-detail-title">{item.title}</h2>

          {item.authors && item.authors.length > 0 && (
            <div className="literature-detail-section">
              <label>Authors</label>
              <p>{item.authors.join('; ')}</p>
            </div>
          )}

          <div className="literature-detail-grid">
            {item.year && (
              <div className="literature-detail-section">
                <label>Year</label>
                <p>{item.year}</p>
              </div>
            )}
            {item.journal && (
              <div className="literature-detail-section">
                <label>Journal / Publisher</label>
                <p>{item.journal}</p>
              </div>
            )}
            {item.volume && (
              <div className="literature-detail-section">
                <label>Volume</label>
                <p>{item.volume}</p>
              </div>
            )}
            {item.number && (
              <div className="literature-detail-section">
                <label>Number</label>
                <p>{item.number}</p>
              </div>
            )}
            {item.pages && (
              <div className="literature-detail-section">
                <label>Pages</label>
                <p>{item.pages}</p>
              </div>
            )}
          </div>

          {item.doi && (
            <div className="literature-detail-section">
              <label>DOI</label>
              <p>
                <a href={`https://doi.org/${item.doi}`} target="_blank" rel="noopener noreferrer">
                  {item.doi}
                </a>
              </p>
            </div>
          )}

          {item.url && (
            <div className="literature-detail-section">
              <label>URL</label>
              <p>
                <a href={item.url} target="_blank" rel="noopener noreferrer">{item.url}</a>
              </p>
            </div>
          )}

          {item.keywords && item.keywords.length > 0 && (
            <div className="literature-detail-section">
              <label>Keywords</label>
              <div className="literature-detail-keywords">
                {item.keywords.map((kw, i) => (
                  <span key={i} className="keyword-badge">{kw}</span>
                ))}
              </div>
            </div>
          )}

          {item.abstract && (
            <div className="literature-detail-section">
              <label>Abstract</label>
              <p className={`literature-detail-abstract ${showAbstract ? '' : 'collapsed'}`}>
                {item.abstract}
              </p>
              {item.abstract.length > 300 && (
                <button className="btn btn-sm btn-secondary" onClick={() => setShowAbstract(!showAbstract)}>
                  {showAbstract ? 'Show less' : 'Show more'}
                </button>
              )}
            </div>
          )}

          {item.notes && (
            <div className="literature-detail-section">
              <label>Notes</label>
              <p className="literature-detail-notes">{item.notes}</p>
            </div>
          )}

          <div className="literature-detail-meta">
            <span>Created: {new Date(item.created_at).toLocaleDateString()}</span>
            <span>Updated: {new Date(item.updated_at).toLocaleDateString()}</span>
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={() => onEdit(item)}>Edit</button>
          <button className="btn btn-secondary" onClick={() => onDelete(item.id)}>Delete</button>
          <button className="btn btn-primary" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
