import type { Workflow, ExecutionResults } from '../types/workflow';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8765/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('access_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    headers,
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API error ${res.status}: ${err}`);
  }
  return res.json();
}

export const api = {
  listWorkflows: () =>
    request<{ workflows: Workflow[] }>('/workflows'),

  getWorkflow: (id: string) =>
    request<Workflow>(`/workflows/${id}`),

  createWorkflow: (data: Partial<Workflow>) =>
    request<Workflow>('/workflows', { method: 'POST', body: JSON.stringify(data) }),

  updateWorkflow: (id: string, data: Partial<Workflow>) =>
    request<Workflow>(`/workflows/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  deleteWorkflow: (id: string) =>
    request<{ ok: boolean }>(`/workflows/${id}`, { method: 'DELETE' }),

  runWorkflow: (workflowId: string, providerOverrides?: Record<string, unknown>, useReferences?: boolean) =>
    request<ExecutionResults>('/execution/run', {
      method: 'POST',
      body: JSON.stringify({
        workflow_id: workflowId,
        provider_overrides: providerOverrides || {},
        use_references: useReferences || false,
      }),
    }),

  listReferences: () =>
    request<{ references: Record<string, unknown>[] }>('/references'),

  importReference: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const token = localStorage.getItem('access_token');
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const res = await fetch(`${API_BASE}/references/import`, {
      method: 'POST',
      body: formData,
      headers,
    });
    // Note: don't set Content-Type for FormData, browser sets it with boundary
    if (!res.ok) {
      const err = await res.text();
      throw new Error(`API error ${res.status}: ${err}`);
    }
    return res.json() as Promise<{ imported: number; references: Record<string, unknown>[] }>;
  },

  deleteReference: (id: string) =>
    request<{ deleted: boolean }>(`/references/${id}`, { method: 'DELETE' }),

  deleteAllReferences: () =>
    request<{ deleted: number }>('/references', { method: 'DELETE' }),
};
