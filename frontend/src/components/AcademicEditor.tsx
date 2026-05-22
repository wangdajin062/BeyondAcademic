/**
 * AcademicEditor Component
 * Main editor interface with grammar checking and formatting
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { articleAPI } from '../services/articleAPI';
import { editorAPI } from '../services/editorAPI';
import { recommendationAPI } from '../services/recommendationAPI';
import { Suggestion } from '../types/editor';
import { Paper } from '../types/recommendation';
import { Article, ArticleUpdate } from '../types/article';

export const AcademicEditor: React.FC = () => {
  const { articleId } = useParams<{ articleId: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [content, setContent] = useState('');
  const [template, setTemplate] = useState<string>('GENERIC');
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [recommendations, setRecommendations] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'editor' | 'suggestions' | 'recommendations'>('editor');

  useEffect(() => {
    if (!articleId) return;
    setFetching(true);
    articleAPI.getArticle(articleId).then((data) => {
      setArticle(data);
      setContent(data.content || '');
      setTemplate(data.template || 'GENERIC');
    }).catch((err) => {
      console.error('Failed to load article:', err);
    }).finally(() => setFetching(false));
  }, [articleId]);

  const handleSave = useCallback(async () => {
    if (!articleId || !article) return;
    setSaving(true);
    try {
      const update: ArticleUpdate = { content };
      const updated = await articleAPI.updateArticle(articleId, update);
      setArticle(updated);
    } catch (err) {
      console.error('Failed to save:', err);
    } finally {
      setSaving(false);
    }
  }, [articleId, article, content]);

  const handleChange = useCallback((newContent: string | undefined) => {
    setContent(newContent || '');
  }, []);

  const checkGrammar = async () => {
    if (!content) return;
    setLoading(true);
    try {
      const grammarSuggestions = await editorAPI.checkGrammar(content, template);
      const formatSuggestions = await editorAPI.checkFormatting(content, template);
      setSuggestions([...grammarSuggestions, ...formatSuggestions]);
    } catch (err) {
      console.error('Failed to check grammar:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendations = async () => {
    if (!content) return;
    setLoading(true);
    try {
      const papers = await recommendationAPI.recommendPapers(content, 5);
      setRecommendations(papers);
    } catch (err) {
      console.error('Failed to get recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const applySuggestion = (suggestion: Suggestion) => {
    const before = content.substring(0, suggestion.position);
    const after = content.substring(suggestion.position + suggestion.length);
    const newContent = before + suggestion.suggestion + after;
    setContent(newContent);
    setSuggestions(suggestions.filter(s => s !== suggestion));
  };

  if (fetching) {
    return <div className="loading">Loading article...</div>;
  }

  if (!article) {
    return <div className="error">Article not found. <Link to="/articles">Back to articles</Link></div>;
  }

  return (
    <div className="academic-editor">
      <div className="editor-header">
        <div className="editor-header-left">
          <Link to="/articles" className="editor-back-link">&larr; Back to articles</Link>
          <h1>{article.title}</h1>
        </div>
        <button onClick={handleSave} disabled={saving} className="btn btn-primary">
          {saving ? 'Saving...' : 'Save'}
        </button>
      </div>

      <div className="editor-toolbar">
        <button onClick={checkGrammar} disabled={loading} className="editor-toolbar-btn">
          Check Grammar & Formatting
        </button>
        <button onClick={getRecommendations} disabled={loading} className="editor-toolbar-btn">
          Get Literature Recommendations
        </button>
        <div className="editor-tabs">
          {(['editor', 'suggestions', 'recommendations'] as const).map((tab) => (
            <button key={tab}
              className={`editor-tab ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}>
              {tab === 'editor' ? 'Editor' : tab === 'suggestions' ? `Suggestions (${suggestions.length})` : `Recommendations (${recommendations.length})`}
            </button>
          ))}
        </div>
      </div>

      <div className="editor-content">
        {activeTab === 'editor' && (
          <Editor
            height="70vh"
            defaultLanguage="markdown"
            theme="vs-dark"
            value={content}
            onChange={handleChange}
            options={{
              minimap: { enabled: false },
              wordWrap: 'on',
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              fontSize: 14,
            }}
          />
        )}

        {activeTab === 'suggestions' && (
          <div className="suggestions-panel">
            <h3>Writing Suggestions</h3>
            {suggestions.length === 0 ? (
              <p>No suggestions. Click "Check Grammar & Formatting" to analyze your text.</p>
            ) : (
              suggestions.map((suggestion, index) => (
                <div key={index} className="suggestion-card">
                  <div className="suggestion-type">{suggestion.type}</div>
                  <p><strong>Original:</strong> {suggestion.original}</p>
                  <p><strong>Suggestion:</strong> {suggestion.suggestion}</p>
                  <p><em>{suggestion.explanation}</em></p>
                  <button onClick={() => applySuggestion(suggestion)} className="btn btn-primary btn-sm" style={{ marginTop: 8 }}>
                    Apply
                  </button>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="recommendations-panel">
            <h3>Literature Recommendations</h3>
            {recommendations.length === 0 ? (
              <p>No recommendations. Click "Get Literature Recommendations" to find relevant papers.</p>
            ) : (
              recommendations.map((paper) => (
                <div key={paper.paper_id} className="paper-card">
                  <h4>{paper.title}</h4>
                  <p className="authors">{paper.authors.join(', ')}</p>
                  <p className="venue">{paper.venue} ({paper.year})</p>
                  <p className="citations">Citations: {paper.citations}</p>
                  <p className="abstract">{paper.abstract.substring(0, 200)}...</p>
                  {paper.doi && (
                    <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noopener noreferrer">View Paper</a>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};
