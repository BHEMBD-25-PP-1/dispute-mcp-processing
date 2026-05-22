import { afterEach, describe, expect, it, vi } from 'vitest';
import { login } from './api';

const response = (ok: boolean, status: number, payload: unknown) =>
  ({
    ok,
    status,
    json: vi.fn().mockResolvedValue(payload),
  }) as unknown as Response;

describe('auth api', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('maps backend login response to operator session', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(response(true, 200, { access_token: 'jwt-1', token_type: 'bearer' })),
    );

    await expect(login('operator', 'operator123')).resolves.toEqual({
      token: 'jwt-1',
      username: 'operator',
    });
  });

  it('normalizes backend auth errors for the login form', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response(false, 401, {})));

    await expect(login('operator', 'wrong')).rejects.toThrow('Неверный логин или пароль');
  });
});
