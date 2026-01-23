/**
 * Editor Types
 * Type definitions for the academic editor
 */

export enum SuggestionType {
  GRAMMAR = "grammar",
  SPELLING = "spelling",
  STYLE = "style",
  FORMATTING = "formatting",
  LATEX = "latex",
  CITATION = "citation"
}

export interface Suggestion {
  type: SuggestionType;
  position: number;
  length: number;
  original: string;
  suggestion: string;
  explanation: string;
  confidence: number;
}

export interface FormattingRule {
  rule_id: string;
  template: string;
  category: string;
  description: string;
  example: string;
}
