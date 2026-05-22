/**
 * Literature Management Types
 */

export interface LiteratureItem {
  id: string;
  title: string;
  authors: string[];
  year: string;
  journal: string;
  volume: string;
  number: string;
  pages: string;
  doi: string;
  abstract: string;
  keywords: string[];
  url: string;
  ref_type: string;
  notes: string;
  raw_data: string;
  created_at: string;
  updated_at: string;
}

export interface LiteratureListResponse {
  items: LiteratureItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface LiteratureCreate {
  title: string;
  authors?: string[];
  year?: string;
  journal?: string;
  volume?: string;
  number?: string;
  pages?: string;
  doi?: string;
  abstract?: string;
  keywords?: string[];
  url?: string;
  ref_type?: string;
  notes?: string;
}

export type LiteratureUpdate = Partial<LiteratureCreate>;

export interface LiteratureImportResult {
  imported: number;
  references: LiteratureItem[];
}
