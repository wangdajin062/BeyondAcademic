import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { articleAPI } from '../services/articleAPI';
import { paperWritingAPI } from '../services/paperWritingAPI';
import { UIUXDesignWorkflow } from '../templates/uiux-workflow';
import type { Article } from '../types/article';
import type { WritingStep, SectionState } from '../types/paperWriting';
import WorkflowOutline from './WorkflowOutline';
import SectionEditor from './SectionEditor';
import AIAssistant from './AIAssistant';
import CompileDialog from './CompileDialog';

function extractSteps(): WritingStep[] {
  const orderMap: Record<string, number> = {};
  UIUXDesignWorkflow.nodes.forEach((n, i) => {
    orderMap[n.id] = i;
  });

  const steps: WritingStep[] = [];

  // Determine upstream relationships from edges
  const upstreamMap: Record<string, string[]> = {};
  for (const node of UIUXDesignWorkflow.nodes) {
    if (node.type === 'prompt') {
      const incoming = UIUXDesignWorkflow.edges
        .filter((e) => e.target === node.id)
        .map((e) => e.source);
      upstreamMap[node.id] = incoming;
    }
  }

  for (const node of UIUXDesignWorkflow.nodes) {
    if (node.type !== 'prompt') continue;
    const data = node.data || {};
    steps.push({
      id: node.id,
      label: (data.label as string) || node.id,
      type: 'prompt',
      order: orderMap[node.id] || 0,
      prompt: (data.prompt as string) || '',
      systemPrompt: (data.system_prompt as string) || '',
      upstreamIds: upstreamMap[node.id] || [],
      provider: data.provider as string,
      model: data.model as string,
    });
  }

  steps.sort((a, b) => a.order - b.order);
  return steps;
}

export default function PaperWritingPlatform() {
  const { articleId } = useParams<{ articleId: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [steps] = useState<WritingStep[]>(() => extractSteps());
  const [selectedStepId, setSelectedStepId] = useState<string | null>(null);
  const [sections, setSections] = useState<Record<string, SectionState>>({});
  const [generatedOutput, setGeneratedOutput] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isCompileView, setIsCompileView] = useState(false);
  const [compiledContent, setCompiledContent] = useState('');
  const [isCompiling, setIsCompiling] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoSaveStatus, setAutoSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Load article and status on mount
  useEffect(() => {
    if (!articleId) return;
    const load = async () => {
      try {
        setLoading(true);
        const [art, status] = await Promise.all([
          articleAPI.getArticle(articleId),
          paperWritingAPI.getPaperStatus(articleId),
        ]);
        setArticle(art);

        const initialSections: Record<string, SectionState> = {};
        for (const s of status.sections) {
          initialSections[s.node_id] = {
            content: '',
            status: s.status as 'pending' | 'generating' | 'complete',
            updatedAt: '',
          };
        }
        setSections(initialSections);

        if (steps.length > 0) {
          setSelectedStepId(steps[0].id);
        }
      } catch (err) {
        setError('Failed to load article');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [articleId]);

  // Load section content when selected step changes
  useEffect(() => {
    if (!selectedStepId || !articleId) return;
    const existing = sections[selectedStepId];
    if (existing && existing.content) return;

    paperWritingAPI.getSection(articleId, selectedStepId).then((section) => {
      setSections((prev) => ({
        ...prev,
        [selectedStepId]: {
          content: section.content || '',
          status: (section.status as SectionState['status']) || 'pending',
          updatedAt: new Date().toISOString(),
        },
      }));
    }).catch(() => {});
  }, [selectedStepId, articleId]);

  const currentStep = steps.find((s) => s.id === selectedStepId) || null;
  const currentSection = selectedStepId ? sections[selectedStepId] : null;

  const handleContentChange = useCallback(
    (newContent: string) => {
      if (!selectedStepId) return;
      setSections((prev) => ({
        ...prev,
        [selectedStepId]: {
          content: newContent,
          status: prev[selectedStepId]?.status || 'pending',
          updatedAt: new Date().toISOString(),
        },
      }));
      setAutoSaveStatus('saving');

      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
      saveTimerRef.current = setTimeout(async () => {
        if (!articleId || !selectedStepId) return;
        try {
          await paperWritingAPI.updateSection(articleId, selectedStepId, newContent, 'pending');
          setAutoSaveStatus('saved');
        } catch {
          setAutoSaveStatus('error');
        }
      }, 1500);
    },
    [articleId, selectedStepId]
  );

  const handleGenerate = useCallback(
    async (stepId: string) => {
      if (!articleId) return;
      setIsGenerating(true);
      setGeneratedOutput(null);
      try {
        const step = steps.find((s) => s.id === stepId);
        const upstreamIds = step?.upstreamIds || [];
        const result = await paperWritingAPI.generateSection(articleId, stepId, upstreamIds);
        setGeneratedOutput(result.output);
      } catch (err) {
        console.error('Generation failed', err);
        setGeneratedOutput('Error: Failed to generate content. Please try again.');
      } finally {
        setIsGenerating(false);
      }
    },
    [articleId, steps]
  );

  const handleAccept = useCallback(
    async (content: string) => {
      if (!selectedStepId || !articleId) return;

      setSections((prev) => ({
        ...prev,
        [selectedStepId]: {
          content,
          status: 'complete',
          updatedAt: new Date().toISOString(),
        },
      }));
      setGeneratedOutput(null);

      try {
        await paperWritingAPI.updateSection(articleId, selectedStepId, content, 'complete');
        setAutoSaveStatus('saved');
      } catch {
        setAutoSaveStatus('error');
      }
    },
    [articleId, selectedStepId]
  );

  const handleCompile = useCallback(async () => {
    if (!articleId) return;
    setIsCompileView(true);
    setIsCompiling(true);
    try {
      const result = await paperWritingAPI.compilePaper(articleId);
      setCompiledContent(result.compiled);
    } catch (err) {
      console.error('Compile failed', err);
      setCompiledContent('Error: Failed to compile paper.');
    } finally {
      setIsCompiling(false);
    }
  }, [articleId]);

  const handleExportMarkdown = useCallback(() => {
    const blob = new Blob([compiledContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${article?.title || 'paper'}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }, [compiledContent, article]);

  if (loading) {
    return (
      <div className="write-loading">
        <p>Loading paper workspace...</p>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="write-error">
        <h2>Article Not Found</h2>
        <p>{error || 'The requested article could not be found.'}</p>
        <Link to="/articles">Back to Articles</Link>
      </div>
    );
  }

  const compiledContentForEditor = currentSection?.content || '';

  return (
    <div className="write-layout">
      {/* Left: Workflow Outline */}
      <WorkflowOutline
        steps={steps}
        selectedStepId={selectedStepId}
        sectionStatuses={Object.fromEntries(
          Object.entries(sections).map(([k, v]) => [k, v.status])
        )}
        onStepSelect={(id) => {
          // Trigger save for current section before switching
          if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
          setSelectedStepId(id);
          setGeneratedOutput(null);
        }}
      />

      {/* Center: Editor */}
      <div className="write-main">
        <div className="write-toolbar">
          <div className="write-breadcrumb">
            <Link to="/articles">Articles</Link>
            <span className="write-breadcrumb-sep">/</span>
            <span>{article.title}</span>
          </div>
          <div className="write-toolbar-actions">
            <button
              className="write-toolbar-btn compile-btn"
              onClick={handleCompile}
            >
              Compile Paper
            </button>
          </div>
        </div>
        <div className="write-editor-area">
          <SectionEditor
            content={compiledContentForEditor}
            autoSaveStatus={autoSaveStatus}
            onContentChange={handleContentChange}
            sectionLabel={currentStep?.label || 'Editor'}
          />
        </div>
      </div>

      {/* Right: AI Assistant */}
      <AIAssistant
        step={currentStep}
        generatedOutput={generatedOutput}
        isGenerating={isGenerating}
        sectionContent={compiledContentForEditor}
        onGenerate={handleGenerate}
        onAccept={handleAccept}
      />

      {/* Compile Dialog */}
      <CompileDialog
        isOpen={isCompileView}
        compiledContent={compiledContent}
        isLoading={isCompiling}
        onClose={() => setIsCompileView(false)}
        onExportMarkdown={handleExportMarkdown}
      />
    </div>
  );
}
