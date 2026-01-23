/**
 * Editor API Service
 * Handles all API calls related to the academic editor
 */
import axios from 'axios';
import { Suggestion, FormattingRule } from '../types/editor';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const editorAPI = {
  /**
   * Check grammar in text
   */
  async checkGrammar(text: string, template: string = 'Generic'): Promise<Suggestion[]> {
    const response = await axios.post(`${API_BASE_URL}/editor/check/grammar`, {
      text,
      template
    });
    return response.data;
  },

  /**
   * Check formatting
   */
  async checkFormatting(text: string, template: string): Promise<Suggestion[]> {
    const response = await axios.post(`${API_BASE_URL}/editor/check/formatting`, {
      text,
      template
    });
    return response.data;
  },

  /**
   * Convert text to LaTeX
   */
  async convertToLatex(text: string): Promise<string> {
    const response = await axios.post(`${API_BASE_URL}/editor/convert/latex`, {
      text,
      from_format: 'plain',
      to_format: 'latex'
    });
    return response.data.latex;
  },

  /**
   * Get improvement suggestions
   */
  async suggestImprovements(paragraph: string): Promise<string[]> {
    const response = await axios.post(`${API_BASE_URL}/editor/improve`, {
      paragraph
    });
    return response.data;
  },

  /**
   * Get formatting rules for template
   */
  async getFormattingRules(template: string): Promise<FormattingRule[]> {
    const response = await axios.get(`${API_BASE_URL}/editor/templates/${template}/rules`);
    return response.data;
  },

  /**
   * Validate citations
   */
  async validateCitations(text: string, template: string = 'Generic'): Promise<any> {
    const response = await axios.post(`${API_BASE_URL}/editor/validate/citations`, {
      text,
      template
    });
    return response.data;
  }
};
