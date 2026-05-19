import { apiRequest } from '../../shared/api/client';
import type { DisputeCase } from '../../types';

export type CaseAction = (token: string, caseId: string, message: string) => Promise<DisputeCase>;

export const fetchCases = (token: string) =>
  apiRequest<DisputeCase[]>('/operator/cases', { token });

export const parseCase: CaseAction = (token, caseId, message) =>
  apiRequest<DisputeCase>(`/operator/cases/${caseId}/parse`, {
    token,
    method: 'POST',
    body: JSON.stringify({ message }),
  });

export const runCaseMcp: CaseAction = (token, caseId, message) =>
  apiRequest<DisputeCase>(`/operator/cases/${caseId}/mcp`, {
    token,
    method: 'POST',
    body: JSON.stringify({ message }),
  });

export const generateCaseResult: CaseAction = (token, caseId, message) =>
  apiRequest<DisputeCase>(`/operator/cases/${caseId}/result`, {
    token,
    method: 'POST',
    body: JSON.stringify({ message }),
  });

export const updateCaseResult = (token: string, caseId: string, result: string) =>
  apiRequest<DisputeCase>(`/operator/cases/${caseId}/result`, {
    token,
    method: 'PATCH',
    body: JSON.stringify({ result }),
  });
