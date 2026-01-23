/**
 * AcademicEditor Component
 * Main editor interface with grammar checking and formatting
 */
import React, { useState, useEffect } from 'react';
import { editorAPI } from '../services/editorAPI';
import { recommendationAPI } from '../services/recommendationAPI';
import { Suggestion } from '../types/editor';
import { Paper } from '../types/recommendation';

interface AcademicEditorProps {
  content: string;
  template: string;
  onChange: (content: string) => void;
}

export const AcademicEditor: React.FC<AcademicEditorProps> = ({ 
  content, 
  template, 
  onChange 
}) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [recommendations, setRecommendations] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'editor' | 'suggestions' | 'recommendations'>('editor');

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
    onChange(newContent);
    
    // Remove applied suggestion
    setSuggestions(suggestions.filter(s => s !== suggestion));
  };

  return (
    <div className="academic-editor">
      <div className="editor-toolbar">
        <button onClick={checkGrammar} disabled={loading}>
          Check Grammar & Formatting
        </button>
        <button onClick={getRecommendations} disabled={loading}>
          Get Literature Recommendations
        </button>
        <div className="tabs">
          <button 
            className={activeTab === 'editor' ? 'active' : ''}
            onClick={() => setActiveTab('editor')}
          >
            Editor
          </button>
          <button 
            className={activeTab === 'suggestions' ? 'active' : ''}
            onClick={() => setActiveTab('suggestions')}
          >
            Suggestions ({suggestions.length})
          </button>
          <button 
            className={activeTab === 'recommendations' ? 'active' : ''}
            onClick={() => setActiveTab('recommendations')}
          >
            Recommendations ({recommendations.length})
          </button>
        </div>
      </div>

      <div className="editor-content">
        {activeTab === 'editor' && (
          <textarea
            className="editor-textarea"
            value={content}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Start writing your academic paper here..."
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
                  <div className="suggestion-content">
                    <p><strong>Original:</strong> {suggestion.original}</p>
                    <p><strong>Suggestion:</strong> {suggestion.suggestion}</p>
                    <p><em>{suggestion.explanation}</em></p>
                  </div>
                  <button onClick={() => applySuggestion(suggestion)}>
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
                    <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noopener noreferrer">
                      View Paper
                    </a>
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
