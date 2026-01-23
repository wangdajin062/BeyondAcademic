/**
 * Article API Service
 * Handles all API calls related to article management
 */
import axios from 'axios';
import { Article, ArticleCreate, ArticleUpdate, ArticleVersion } from '../types/article';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const articleAPI = {
  /**
   * Create a new article
   */
  async createArticle(data: ArticleCreate, author: string = 'default_user'): Promise<Article> {
    const response = await axios.post(`${API_BASE_URL}/articles/`, data, {
      params: { author }
    });
    return response.data;
  },

  /**
   * Get all articles
   */
  async listArticles(status?: string, skip: number = 0, limit: number = 100): Promise<Article[]> {
    const response = await axios.get(`${API_BASE_URL}/articles/`, {
      params: { status, skip, limit }
    });
    return response.data;
  },

  /**
   * Get a specific article
   */
  async getArticle(articleId: string): Promise<Article> {
    const response = await axios.get(`${API_BASE_URL}/articles/${articleId}`);
    return response.data;
  },

  /**
   * Update an article
   */
  async updateArticle(
    articleId: string, 
    data: ArticleUpdate, 
    author: string = 'default_user'
  ): Promise<Article> {
    const response = await axios.put(`${API_BASE_URL}/articles/${articleId}`, data, {
      params: { author }
    });
    return response.data;
  },

  /**
   * Delete an article
   */
  async deleteArticle(articleId: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/articles/${articleId}`);
  },

  /**
   * Get version history
   */
  async getVersionHistory(articleId: string): Promise<ArticleVersion[]> {
    const response = await axios.get(`${API_BASE_URL}/articles/${articleId}/versions`);
    return response.data;
  },

  /**
   * Get specific version
   */
  async getVersion(articleId: string, versionNumber: number): Promise<ArticleVersion> {
    const response = await axios.get(
      `${API_BASE_URL}/articles/${articleId}/versions/${versionNumber}`
    );
    return response.data;
  },

  /**
   * Revert to a specific version
   */
  async revertToVersion(
    articleId: string, 
    versionNumber: number,
    author: string = 'default_user'
  ): Promise<Article> {
    const response = await axios.post(
      `${API_BASE_URL}/articles/${articleId}/revert/${versionNumber}`,
      {},
      { params: { author } }
    );
    return response.data;
  }
};
