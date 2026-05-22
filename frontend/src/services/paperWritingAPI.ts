import type { SectionResponse, GenerateResponse, CompileResponse, PaperStatusResponse } from '../types/paperWriting';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8765/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('access_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

export const paperWritingAPI = {
  getSection(articleId: string, nodeId: string) {
    return request<SectionResponse>(`/paper-writing/${articleId}/sections/${nodeId}`);
  },

  updateSection(articleId: string, nodeId: string, content: string, status: string) {
    return request<{ ok: boolean }>(`/paper-writing/${articleId}/sections/${nodeId}`, {
      method: 'PUT',
      body: JSON.stringify({ content, status }),
    });
  },

  generateSection(articleId: string, nodeId: string, upstreamIds: string[]) {
    return request<GenerateResponse>(`/paper-writing/${articleId}/generate/${nodeId}`, {
      method: 'POST',
      body: JSON.stringify({ upstream_ids: upstreamIds }),
    });
  },

  compilePaper(articleId: string) {
    return request<CompileResponse>(`/paper-writing/${articleId}/compile`);
  },

  getPaperStatus(articleId: string) {
    return request<PaperStatusResponse>(`/paper-writing/${articleId}/status`);
  },
};
