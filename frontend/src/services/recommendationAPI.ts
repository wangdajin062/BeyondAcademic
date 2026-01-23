/**
 * Recommendation API Service
 * Handles all API calls related to AI-powered recommendations
 */
import axios from 'axios';
import { Paper, LanguageOptimization, ParagraphOptimization } from '../types/recommendation';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const recommendationAPI = {
  /**
   * Search for papers
   */
  async searchPapers(
    query: string, 
    limit: number = 10, 
    recommendationType?: string
  ): Promise<Paper[]> {
    const response = await axios.post(`${API_BASE_URL}/recommendations/search`, {
      query,
      limit,
      recommendation_type: recommendationType
    });
    return response.data;
  },

  /**
   * Get paper recommendations based on context
   */
  async recommendPapers(context: string, limit: number = 5): Promise<Paper[]> {
    const response = await axios.post(`${API_BASE_URL}/recommendations/recommend`, {
      context,
      limit
    });
    return response.data;
  },

  /**
   * Optimize a sentence
   */
  async optimizeSentence(sentence: string): Promise<LanguageOptimization> {
    const response = await axios.post(`${API_BASE_URL}/recommendations/optimize/sentence`, {
      sentence
    });
    return response.data;
  },

  /**
   * Optimize a paragraph
   */
  async optimizeParagraph(paragraph: string): Promise<ParagraphOptimization> {
    const response = await axios.post(`${API_BASE_URL}/recommendations/optimize/paragraph`, {
      paragraph
    });
    return response.data;
  },

  /**
   * Get citation suggestions
   */
  async getCitations(topic: string): Promise<string[]> {
    const response = await axios.post(`${API_BASE_URL}/recommendations/citations`, {
      topic
    });
    return response.data;
  },

  /**
   * Get high-impact papers
   */
  async getHighImpactPapers(field?: string, limit: number = 10): Promise<Paper[]> {
    const response = await axios.get(`${API_BASE_URL}/recommendations/papers/high-impact`, {
      params: { field, limit }
    });
    return response.data;
  },

  /**
   * Get recent papers
   */
  async getRecentPapers(field?: string, limit: number = 10): Promise<Paper[]> {
    const response = await axios.get(`${API_BASE_URL}/recommendations/papers/recent`, {
      params: { field, limit }
    });
    return response.data;
  }
};
