import api from './api';
import { QASession, QASessionListItem, CreateSessionRequest } from '../types/session';

export const sessionService = {
  async getSessions(): Promise<QASessionListItem[]> {
    const { data } = await api.get<QASessionListItem[]>('/sessions');
    return data;
  },

  async createSession(req: CreateSessionRequest): Promise<QASession> {
    const { data } = await api.post<QASession>('/sessions', req);
    return data;
  },

  async getSession(id: number): Promise<QASession> {
    const { data } = await api.get<QASession>(`/sessions/${id}`);
    return data;
  },

  async deleteSession(id: number): Promise<void> {
    await api.delete(`/sessions/${id}`);
  },

  async regenerateSession(id: number): Promise<QASession> {
    const { data } = await api.post<QASession>(`/sessions/${id}/regenerate`);
    return data;
  },

  async extractTextFromFile(file: File): Promise<{ text: string; filename: string; char_count: number }> {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post('/sessions/extract-text', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  getExportUrl(id: number): string {
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/sessions/${id}/export`;
  },
};
