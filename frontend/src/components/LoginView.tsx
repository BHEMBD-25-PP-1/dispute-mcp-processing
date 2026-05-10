import { FormEvent, useState } from 'react';
import { KeyRound, LogIn, ShieldCheck, UserRound } from 'lucide-react';
import type { Operator } from '../types';

type LoginViewProps = {
  onLogin: (operator: Operator) => void;
};

export function LoginView({ onLogin }: LoginViewProps) {
  const [email, setEmail] = useState('operator@nspk.ru');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const submitLogin = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!email.trim() || !password.trim()) {
      setError('Заполните логин и пароль');
      return;
    }

    onLogin({
      name: email.split('@')[0] || 'operator',
      email,
      role: 'Операционист',
    });
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
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="operator@nspk.ru"
              type="email"
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

        <button className="primary-button login-submit" type="submit">
          <LogIn size={16} aria-hidden="true" />
          Войти
        </button>
      </form>
    </main>
  );
}
