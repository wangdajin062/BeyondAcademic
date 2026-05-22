/**
 * Literature Management API Service
 */
import axios from 'axios';
import type {
  LiteratureItem,
  LiteratureListResponse,
  LiteratureCreate,
  LiteratureUpdate,
  LiteratureImportResult,
} from '../types/literature';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8765/api';

export const literatureAPI = {
  /** List references with search, filter, pagination */
  async list(params?: {
    query?: string;
    field?: string;
    sort?: string;
    order?: string;
    page?: number;
    page_size?: number;
    ref_type?: string;
  }): Promise<LiteratureListResponse> {
    const response = await axios.get(`${API_BASE_URL}/literature/`, { params });
    return response.data;
  },

  /** Get single reference detail */
  async get(refId: string): Promise<LiteratureItem> {
    const response = await axios.get(`${API_BASE_URL}/literature/${refId}`);
    return response.data;
  },

  /** Create a new reference manually */
  async create(data: LiteratureCreate): Promise<LiteratureItem> {
    const response = await axios.post(`${API_BASE_URL}/literature/`, data);
    return response.data;
  },

  /** Update an existing reference */
  async update(refId: string, data: LiteratureUpdate): Promise<LiteratureItem> {
    const response = await axios.put(`${API_BASE_URL}/literature/${refId}`, data);
    return response.data;
  },

  /** Delete a reference */
  async delete(refId: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/literature/${refId}`);
  },

  /** Batch delete references */
  async batchDelete(refIds: string[]): Promise<{ deleted: number }> {
    const response = await axios.post(`${API_BASE_URL}/literature/batch-delete`, { ref_ids: refIds });
    return response.data;
  },

  /** Export references in specified format */
  async export(refIds?: string[], format: string = 'bibtex'): Promise<string> {
    const response = await axios.post(`${API_BASE_URL}/literature/export`,
      { ref_ids: refIds, format },
      { responseType: 'text' },
    );
    return typeof response.data === 'string' ? response.data : JSON.stringify(response.data);
  },

  /** Import RIS/BibTeX file */
  async importFile(file: File): Promise<LiteratureImportResult> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(`${API_BASE_URL}/literature/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
