/**
 * Recommendation Types
 * Type definitions for AI recommendations
 */

export enum RecommendationType {
  HIGH_IMPACT = "high_impact",
  HIGH_CITATION = "high_citation",
  RELEVANT = "relevant",
  RECENT = "recent",
  SEMINAL = "seminal"
}

export interface Paper {
  paper_id: string;
  title: string;
  authors: string[];
  abstract: string;
  year: number;
  venue: string;
  citations: number;
  url?: string;
  doi?: string;
  relevance_score: number;
}

export interface LanguageOptimization {
  original_sentence: string;
  optimized_sentence: string;
  improvements: string[];
  formality_score: number;
  clarity_score: number;
}

export interface ParagraphOptimization {
  original: string;
  optimized: string;
  sentence_optimizations: LanguageOptimization[];
  overall_formality: number;
  overall_clarity: number;
}
