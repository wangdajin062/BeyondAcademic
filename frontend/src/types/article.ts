/**
 * Article Types
 * Type definitions for article management
 */

export enum ArticleStatus {
  DRAFT = "draft",
  IN_REVIEW = "in_review",
  REVISED = "revised",
  SUBMITTED = "submitted",
  PUBLISHED = "published"
}

export enum TemplateType {
  IEEE = "IEEE",
  ELSEVIER = "Elsevier",
  ACM = "ACM",
  SPRINGER = "Springer",
  NATURE = "Nature",
  SCIENCE = "Science",
  GENERIC = "Generic"
}

export interface ArticleVersion {
  version_id: string;
  version_number: number;
  content: string;
  created_at: string;
  changes_summary?: string;
  author: string;
}

export interface Article {
  article_id: string;
  title: string;
  abstract?: string;
  content: string;
  status: ArticleStatus;
  template: TemplateType;
  authors: string[];
  keywords: string[];
  references: string[];
  current_version: number;
  versions: ArticleVersion[];
  created_at: string;
  updated_at: string;
  submitted_at?: string;
  published_at?: string;
}

export interface ArticleCreate {
  title: string;
  abstract?: string;
  content?: string;
  template?: TemplateType;
  authors?: string[];
  keywords?: string[];
}

export interface ArticleUpdate {
  title?: string;
  abstract?: string;
  content?: string;
  status?: ArticleStatus;
  template?: TemplateType;
  authors?: string[];
  keywords?: string[];
  references?: string[];
  changes_summary?: string;
}
