import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  fetchCases,
  generateCaseResult,
  parseCase,
  runCaseMcp,
  updateCaseResult,
} from './api';
import type { DisputeCase } from '../../types';

const casePayload: DisputeCase = {
  id: 'DSP-1',
  title: 'Demo',
  partner: 'НСПК',
  channel: 'HTTP',
  priority: 'P1',
  status: 'new',
  receivedAt: '10:00',
  amount: '100 ₽',
  customerName: 'Клиент',
  message: 'message',
  identifiers: { service: 'unknown', confidence: 0 },
  connectors: [],
  timeline: [],
  result: '',
};

const response = (payload: unknown) =>
  ({
    ok: true,
    status: 200,
    json: vi.fn().mockResolvedValue(payload),
  }) as unknown as Response;

describe('disputes api', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('fetches operator cases with bearer token', async () => {
    const fetchMock = vi.fn().mockResolvedValue(response([casePayload]));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchCases('token-1')).resolves.toEqual([casePayload]);

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/operator/cases',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer token-1' }),
      }),
    );
  });

  it.each([
    [parseCase, '/operator/cases/DSP-1/parse', 'POST', { message: 'message' }],
    [runCaseMcp, '/operator/cases/DSP-1/mcp', 'POST', { message: 'message' }],
    [generateCaseResult, '/operator/cases/DSP-1/result', 'POST', { message: 'message' }],
    [updateCaseResult, '/operator/cases/DSP-1/result', 'PATCH', { result: 'result' }],
  ])('calls %s endpoint', async (action, path, method, payload) => {
    const fetchMock = vi.fn().mockResolvedValue(response(casePayload));
    vi.stubGlobal('fetch', fetchMock);

    if (action === updateCaseResult) {
      await action('token-1', 'DSP-1', 'result');
    } else {
      await action('token-1', 'DSP-1', 'message');
    }

    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8000/api/v1${path}`,
      expect.objectContaining({
        method,
        body: JSON.stringify(payload),
        headers: expect.objectContaining({ Authorization: 'Bearer token-1' }),
      }),
    );
  });
});
