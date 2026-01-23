/**
 * ArticleList Component
 * Displays list of articles with filtering options
 */
import React, { useState, useEffect } from 'react';
import { articleAPI } from '../services/articleAPI';
import { Article, ArticleStatus } from '../types/article';

export const ArticleList: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<ArticleStatus | undefined>(undefined);

  useEffect(() => {
    loadArticles();
  }, [statusFilter]);

  const loadArticles = async () => {
    try {
      setLoading(true);
      const data = await articleAPI.listArticles(statusFilter);
      setArticles(data);
      setError(null);
    } catch (err) {
      setError('Failed to load articles');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (articleId: string) => {
    if (window.confirm('Are you sure you want to delete this article?')) {
      try {
        await articleAPI.deleteArticle(articleId);
        loadArticles();
      } catch (err) {
        setError('Failed to delete article');
        console.error(err);
      }
    }
  };

  if (loading) return <div className="loading">Loading articles...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="article-list">
      <div className="article-list-header">
        <h2>My Articles</h2>
        <div className="filters">
          <label>
            Filter by status:
            <select 
              value={statusFilter || ''} 
              onChange={(e) => setStatusFilter(e.target.value as ArticleStatus || undefined)}
            >
              <option value="">All</option>
              <option value={ArticleStatus.DRAFT}>Draft</option>
              <option value={ArticleStatus.IN_REVIEW}>In Review</option>
              <option value={ArticleStatus.REVISED}>Revised</option>
              <option value={ArticleStatus.SUBMITTED}>Submitted</option>
              <option value={ArticleStatus.PUBLISHED}>Published</option>
            </select>
          </label>
        </div>
      </div>
      
      <div className="articles">
        {articles.length === 0 ? (
          <p>No articles found. Create your first article to get started!</p>
        ) : (
          articles.map(article => (
            <div key={article.article_id} className="article-card">
              <h3>{article.title}</h3>
              <div className="article-meta">
                <span className="status">{article.status}</span>
                <span className="version">v{article.current_version}</span>
                <span className="template">{article.template}</span>
              </div>
              <p className="article-excerpt">
                {article.abstract || article.content.substring(0, 150)}...
              </p>
              <div className="article-actions">
                <button onClick={() => window.location.href = `/editor/${article.article_id}`}>
                  Edit
                </button>
                <button onClick={() => handleDelete(article.article_id)}>
                  Delete
                </button>
              </div>
              <div className="article-footer">
                <small>Updated: {new Date(article.updated_at).toLocaleDateString()}</small>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
