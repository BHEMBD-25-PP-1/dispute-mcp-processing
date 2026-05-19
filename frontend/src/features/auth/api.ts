import { apiRequest } from '../../shared/api/client';

type LoginResponse = {
  access_token: string;
  token_type: string;
};

export type Session = {
  token: string;
  username: string;
};

export const login = async (username: string, password: string): Promise<Session> => {
  try {
    const data = await apiRequest<LoginResponse>('/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });

    return { token: data.access_token, username };
  } catch {
    throw new Error('Неверный логин или пароль');
  }
};
