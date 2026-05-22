import React, { useState, useEffect, useCallback } from 'react';
import { literatureAPI } from '../services/literatureAPI';
import type { LiteratureItem } from '../types/literature';
import LiteratureImport from './LiteratureImport';
import LiteratureForm from './LiteratureForm';
import LiteratureDetail from './LiteratureDetail';

const REF_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'article', label: 'Article' },
  { value: 'book', label: 'Book' },
  { value: 'conference', label: 'Conference' },
  { value: 'thesis', label: 'Thesis' },
  { value: 'report', label: 'Report' },
];

const PAGE_SIZE = 20;

export default function LiteratureList() {
  const [items, setItems] = useState<LiteratureItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Search & filter state
  const [query, setQuery] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [refType, setRefType] = useState('');
  const [sort, setSort] = useState('updated_at');
  const [order, setOrder] = useState('DESC');

  // Selection state
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [selectMode, setSelectMode] = useState(false);

  // Dialog state
  const [showImport, setShowImport] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editItem, setEditItem] = useState<LiteratureItem | null>(null);
  const [detailItem, setDetailItem] = useState<LiteratureItem | null>(null);

  const fetchItems = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await literatureAPI.list({
        query,
        field: 'all',
        sort,
        order,
        page,
        page_size: PAGE_SIZE,
        ref_type: refType || undefined,
      });
      setItems(result.items);
      setTotal(result.total);
    } catch (err) {
      setError('Failed to load references');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [query, sort, order, page, refType]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  // Reset page when search/filter changes
  useEffect(() => {
    setPage(1);
  }, [query, refType]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setQuery(searchInput);
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === items.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(items.map((i) => i.id)));
    }
  };

  const handleBatchDelete = async () => {
    if (selectedIds.size === 0) return;
    if (!window.confirm(`Delete ${selectedIds.size} selected references?`)) return;
    try {
      await literatureAPI.batchDelete(Array.from(selectedIds));
      setSelectedIds(new Set());
      setSelectMode(false);
      fetchItems();
    } catch (err) {
      console.error('Batch delete failed', err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Delete this reference?')) return;
    try {
      await literatureAPI.delete(id);
      fetchItems();
    } catch (err) {
      console.error('Delete failed', err);
    }
  };

  const handleEdit = (item: LiteratureItem) => {
    setEditItem(item);
    setShowForm(true);
  };

  const handleFormClose = (refreshed?: boolean) => {
    setShowForm(false);
    setEditItem(null);
    if (refreshed) fetchItems();
  };

  const handleImportClose = (refreshed?: boolean) => {
    setShowImport(false);
    if (refreshed) fetchItems();
  };

  const formatAuthors = (authors: string[]) => {
    if (!authors || authors.length === 0) return 'Unknown';
    if (authors.length <= 2) return authors.join(', ');
    return `${authors[0]} et al.`;
  };

  return (
    <div className="literature-page">
      {/* Header */}
      <div className="literature-header">
        <h2>Literature Library</h2>
        <div className="literature-header-actions">
          <button className="btn btn-secondary btn-sm" onClick={() => setShowImport(true)}>
            Import File
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => setShowForm(true)}>
            Add Reference
          </button>
          <button
            className={`btn btn-sm ${selectMode ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => { setSelectMode(!selectMode); setSelectedIds(new Set()); }}
          >
            {selectMode ? 'Cancel' : 'Select'}
          </button>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="literature-controls">
        <form className="literature-search" onSubmit={handleSearch}>
          <input
            className="form-input literature-search-input"
            placeholder="Search by title, author, keywords..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
          <button type="submit" className="btn btn-primary btn-sm">Search</button>
          {query && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => { setSearchInput(''); setQuery(''); }}
            >
              Clear
            </button>
          )}
        </form>
        <div className="literature-filters">
          <select className="form-select" value={refType} onChange={(e) => setRefType(e.target.value)}>
            {REF_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
          <select className="form-select" value={`${sort}:${order}`} onChange={(e) => {
            const [s, o] = e.target.value.split(':');
            setSort(s);
            setOrder(o);
          }}>
            <option value="updated_at:DESC">Recently Updated</option>
            <option value="created_at:DESC">Recently Added</option>
            <option value="title:ASC">Title A-Z</option>
            <option value="year:DESC">Year (newest)</option>
            <option value="year:ASC">Year (oldest)</option>
          </select>
          {selectMode && selectedIds.size > 0 && (
            <button className="btn btn-danger btn-sm" onClick={handleBatchDelete}>
              Delete ({selectedIds.size})
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="loading">Loading references...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : items.length === 0 ? (
        <div className="empty-state">
          {query || refType ? (
            <p>No references match your search criteria.</p>
          ) : (
            <>
              <p>Your literature library is empty.</p>
              <p style={{ marginTop: 8, fontSize: 13 }}>
                Import RIS/BibTeX files or add references manually to get started.
              </p>
            </>
          )}
        </div>
      ) : (
        <>
          {/* Selection bar */}
          {selectMode && (
            <div className="literature-select-bar">
              <label className="literature-select-all">
                <input type="checkbox" checked={selectedIds.size === items.length} onChange={toggleSelectAll} />
                <span>Select all {total} items</span>
              </label>
            </div>
          )}

          {/* Cards */}
          <div className="literature-grid">
            {items.map((item) => (
              <div key={item.id} className={`literature-card ${selectedIds.has(item.id) ? 'selected' : ''}`}>
                {selectMode && (
                  <div className="literature-card-checkbox">
                    <input type="checkbox" checked={selectedIds.has(item.id)} onChange={() => toggleSelect(item.id)} />
                  </div>
                )}
                <div className="literature-card-body" onClick={() => !selectMode && setDetailItem(item)}>
                  <div className="literature-card-type">{item.ref_type || 'article'}</div>
                  <h3 className="literature-card-title">{item.title}</h3>
                  <p className="literature-card-authors">{formatAuthors(item.authors)}</p>
                  <div className="literature-card-meta">
                    {item.year && <span>{item.year}</span>}
                    {item.journal && <span>{item.journal}</span>}
                    {item.doi && <span className="literature-card-doi">doi: {item.doi}</span>}
                  </div>
                </div>
                {!selectMode && (
                  <div className="literature-card-actions">
                    <button className="btn btn-sm btn-secondary" onClick={() => handleEdit(item)}>Edit</button>
                    <button className="btn btn-sm btn-secondary" onClick={() => handleDelete(item.id)}>Delete</button>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="btn btn-sm btn-secondary"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                Previous
              </button>
              <span className="pagination-info">
                Page {page} of {totalPages} ({total} total)
              </span>
              <button
                className="btn btn-sm btn-secondary"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Dialogs */}
      {showImport && <LiteratureImport onClose={handleImportClose} />}
      {showForm && <LiteratureForm item={editItem} onClose={handleFormClose} />}
      {detailItem && (
        <LiteratureDetail
          item={detailItem}
          onClose={() => setDetailItem(null)}
          onEdit={(item: LiteratureItem) => { setDetailItem(null); handleEdit(item); }}
          onDelete={(id: string) => { setDetailItem(null); handleDelete(id); }}
        />
      )}
    </div>
  );
}
