export interface WritingStep {
  id: string;
  label: string;
  type: 'prompt' | 'code' | 'output' | 'start';
  order: number;
  prompt: string;
  systemPrompt: string;
  upstreamIds: string[];
  provider?: string;
  model?: string;
}

export interface SectionState {
  content: string;
  status: 'pending' | 'generating' | 'complete';
  updatedAt: string;
}

export interface GenerateRequest {
  upstream_ids: string[];
}

export interface GenerateResponse {
  output: string;
}

export interface CompileResponse {
  compiled: string;
  sectionCount: number;
}

export interface PaperStatusResponse {
  sections: Array<{
    node_id: string;
    label: string;
    type: string;
    status: string;
  }>;
}

export interface SectionResponse {
  content: string;
  status: string;
}
