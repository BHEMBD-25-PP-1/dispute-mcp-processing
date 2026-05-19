import { FormEvent, useState } from 'react';
import { ExternalLink, KeyRound, LogIn, ShieldCheck, UserRound } from 'lucide-react';
import type { Operator } from '../types';
import { login } from '../features/auth/api';

type LoginViewProps = {
  onLogin: (operator: Operator) => void;
};

export function LoginView({ onLogin }: LoginViewProps) {
  const [username, setUsername] = useState('operator');
  const [password, setPassword] = useState('operator123');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submitLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!username.trim() || !password.trim()) {
      setError('Заполните логин и пароль');
      return;
    }

    setIsSubmitting(true);
    setError('');
    try {
      const session = await login(username, password);
      onLogin({
        name: session.username,
        username: session.username,
        role: 'Операционист',
        token: session.token,
      });
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Не удалось войти');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="login-page">
      <form className="login-panel" onSubmit={submitLogin}>
        <div className="login-panel__brand">
          <span className="login-badge">
            <ShieldCheck size={22} aria-hidden="true" />
          </span>
          <div>
            <p className="eyebrow">Dispute MCP Ops</p>
            <h1>Вход операциониста</h1>
          </div>
        </div>

        <label className="field">
          <span>Логин</span>
          <div className="field-control">
            <UserRound size={18} aria-hidden="true" />
            <input
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="Введите username"
              type="text"
            />
          </div>
        </label>

        <label className="field">
          <span>Пароль</span>
          <div className="field-control">
            <KeyRound size={18} aria-hidden="true" />
            <input
              autoComplete="current-password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                setError('');
              }}
              placeholder="Введите пароль"
              type="password"
            />
          </div>
        </label>

        {error ? <p className="form-error">{error}</p> : null}

        <button className="primary-button login-submit" type="submit" disabled={isSubmitting}>
          <LogIn size={16} aria-hidden="true" />
          {isSubmitting ? 'Входим...' : 'Войти'}
        </button>
      </form>

      <section className="demo-note" aria-label="Информация о демо режиме">
        <strong>ДЕМО-режим</strong>
        <p>
          Данные и сценарии операторской очереди обслуживаются backend API. Используйте тестовую учетную
          запись ниже для входа в стенд.
        </p>
        <dl>
          <div>
            <dt>Логин</dt>
            <dd>operator</dd>
          </div>
          <div>
            <dt>Пароль</dt>
            <dd>operator123</dd>
          </div>
        </dl>
        <a
          href="https://github.com/BHEMBD-25-PP-1/dispute-mcp-processing"
          rel="noreferrer"
          target="_blank"
        >
          Репозиторий проекта
          <ExternalLink size={14} aria-hidden="true" />
        </a>
      </section>
    </main>
  );
}
