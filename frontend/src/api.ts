import type { DisputeCase } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

type LoginResponse = {
  access_token: string;
  token_type: string;
};

export type Session = {
  token: string;
  username: string;
};

const request = async <T>(path: string, token: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
};

export const login = async (username: string, password: string): Promise<Session> => {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error('Неверный логин или пароль');
  }

  const data = (await response.json()) as LoginResponse;
  return { token: data.access_token, username };
};

export const fetchCases = (token: string) => request<DisputeCase[]>('/operator/cases', token);

export const parseCase = (token: string, caseId: string, message: string) =>
  request<DisputeCase>(`/operator/cases/${caseId}/parse`, token, {
    method: 'POST',
    body: JSON.stringify({ message }),
  });

export const runCaseMcp = (token: string, caseId: string, message: string) =>
  request<DisputeCase>(`/operator/cases/${caseId}/mcp`, token, {
    method: 'POST',
    body: JSON.stringify({ message }),
  });

export const generateCaseResult = (token: string, caseId: string, message: string) =>
  request<DisputeCase>(`/operator/cases/${caseId}/result`, token, {
    method: 'POST',
    body: JSON.stringify({ message }),
  });

export const updateCaseResult = (token: string, caseId: string, result: string) =>
  request<DisputeCase>(`/operator/cases/${caseId}/result`, token, {
    method: 'PATCH',
    body: JSON.stringify({ result }),
  });
