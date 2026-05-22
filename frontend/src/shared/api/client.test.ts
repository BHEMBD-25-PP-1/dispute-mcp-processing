import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiRequest } from './client';

const jsonResponse = (ok: boolean, status: number, payload: unknown) =>
  ({
    ok,
    status,
    json: vi.fn().mockResolvedValue(payload),
  }) as unknown as Response;

describe('apiRequest', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('sends json headers, auth token, and returns parsed payload', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(true, 200, { ok: true }));
    vi.stubGlobal('fetch', fetchMock);

    const result = await apiRequest<{ ok: boolean }>('/demo', {
      token: 'token-1',
      method: 'POST',
      headers: { 'X-Trace': 'trace-1' },
      body: JSON.stringify({ value: 1 }),
    });

    expect(result).toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/api/v1/demo', {
      method: 'POST',
      body: JSON.stringify({ value: 1 }),
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer token-1',
        'X-Trace': 'trace-1',
      },
    });
  });

  it('throws on non-2xx backend responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(false, 500, {})));

    await expect(apiRequest('/demo')).rejects.toThrow('Backend request failed: 500');
  });
});
