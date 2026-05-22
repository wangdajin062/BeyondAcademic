import React, { useState } from 'react';
import { literatureAPI } from '../services/literatureAPI';
import type { LiteratureItem, LiteratureCreate } from '../types/literature';

interface Props {
  item?: LiteratureItem | null;
  onClose: (refreshed?: boolean) => void;
}

const REF_TYPE_OPTIONS = [
  { value: 'article', label: 'Article' },
  { value: 'book', label: 'Book' },
  { value: 'conference', label: 'Conference' },
  { value: 'thesis', label: 'Thesis' },
  { value: 'report', label: 'Report' },
];

export default function LiteratureForm({ item, onClose }: Props) {
  const isEdit = !!item;
  const [form, setForm] = useState<LiteratureCreate>({
    title: item?.title || '',
    authors: item?.authors || [],
    year: item?.year || '',
    journal: item?.journal || '',
    volume: item?.volume || '',
    number: item?.number || '',
    pages: item?.pages || '',
    doi: item?.doi || '',
    abstract: item?.abstract || '',
    keywords: item?.keywords || [],
    url: item?.url || '',
    ref_type: item?.ref_type || 'article',
    notes: item?.notes || '',
  });
  const [authorsStr, setAuthorsStr] = useState((item?.authors || []).join(', '));
  const [keywordsStr, setKeywordsStr] = useState((item?.keywords || []).join(', '));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateField = (field: keyof LiteratureCreate, value: any) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) {
      setError('Title is required');
      return;
    }

    const payload = {
      ...form,
      authors: authorsStr.split(',').map((s) => s.trim()).filter(Boolean),
      keywords: keywordsStr.split(',').map((s) => s.trim()).filter(Boolean),
    };

    setLoading(true);
    setError(null);
    try {
      if (isEdit && item) {
        await literatureAPI.update(item.id, payload);
      } else {
        await literatureAPI.create(payload);
      }
      onClose(true);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Save failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={() => onClose()}>
      <div className="modal-dialog modal-lg" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{isEdit ? 'Edit Reference' : 'Add Reference'}</h3>
          <button className="modal-close-btn" onClick={() => onClose()}>&times;</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body literature-form">
            <div className="form-group">
              <label className="form-label">Title *</label>
              <input className="form-input" value={form.title} onChange={(e) => updateField('title', e.target.value)} placeholder="Publication title" />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Authors (comma separated)</label>
                <input className="form-input" value={authorsStr} onChange={(e) => setAuthorsStr(e.target.value)} placeholder="Smith, J., Doe, A." />
              </div>
              <div className="form-group">
                <label className="form-label">Year</label>
                <input className="form-input" value={form.year} onChange={(e) => updateField('year', e.target.value)} placeholder="2024" />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Journal / Publisher</label>
              <input className="form-input" value={form.journal} onChange={(e) => updateField('journal', e.target.value)} placeholder="Journal name" />
            </div>

            <div className="form-row form-row-4">
              <div className="form-group">
                <label className="form-label">Volume</label>
                <input className="form-input" value={form.volume} onChange={(e) => updateField('volume', e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Number</label>
                <input className="form-input" value={form.number} onChange={(e) => updateField('number', e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Pages</label>
                <input className="form-input" value={form.pages} onChange={(e) => updateField('pages', e.target.value)} placeholder="1-10" />
              </div>
              <div className="form-group">
                <label className="form-label">Type</label>
                <select className="form-select" value={form.ref_type} onChange={(e) => updateField('ref_type', e.target.value)}>
                  {REF_TYPE_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">DOI</label>
                <input className="form-input" value={form.doi} onChange={(e) => updateField('doi', e.target.value)} placeholder="10.1234/example" />
              </div>
              <div className="form-group">
                <label className="form-label">URL</label>
                <input className="form-input" value={form.url} onChange={(e) => updateField('url', e.target.value)} placeholder="https://..." />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Keywords (comma separated)</label>
              <input className="form-input" value={keywordsStr} onChange={(e) => setKeywordsStr(e.target.value)} placeholder="keyword1, keyword2" />
            </div>

            <div className="form-group">
              <label className="form-label">Abstract</label>
              <textarea className="form-textarea" rows={4} value={form.abstract} onChange={(e) => updateField('abstract', e.target.value)} />
            </div>

            <div className="form-group">
              <label className="form-label">Notes</label>
              <textarea className="form-textarea" rows={2} value={form.notes} onChange={(e) => updateField('notes', e.target.value)} />
            </div>

            {error && <p className="form-error">{error}</p>}
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={() => onClose()}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Saving...' : isEdit ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
