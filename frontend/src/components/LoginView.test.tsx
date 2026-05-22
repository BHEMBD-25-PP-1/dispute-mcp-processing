import { isValidElement, type ReactElement, type ReactNode } from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';

const childrenOf = (node: ReactNode): ReactNode[] => {
  if (Array.isArray(node)) {
    return node;
  }
  if (isValidElement<{ children?: ReactNode }>(node)) {
    const children = node.props.children;
    return Array.isArray(children) ? children : children === undefined ? [] : [children];
  }
  return [];
};

const findAll = (node: ReactNode, predicate: (element: ReactElement<any>) => boolean): ReactElement<any>[] => {
  if (Array.isArray(node)) {
    return node.flatMap((child) => findAll(child, predicate));
  }
  if (!isValidElement<any>(node)) {
    return [];
  }
  const current = predicate(node) ? [node] : [];
  return [...current, ...childrenOf(node).flatMap((child) => findAll(child, predicate))];
};

const textOf = (node: ReactNode): string => {
  if (typeof node === 'string' || typeof node === 'number') {
    return String(node);
  }
  return childrenOf(node).map(textOf).join('');
};

const renderLoginView = async (
  stateValues: unknown[],
  loginMock = vi.fn().mockResolvedValue({ token: 'jwt-1', username: 'operator' }),
) => {
  vi.resetModules();
  const setters = [vi.fn(), vi.fn(), vi.fn(), vi.fn()];
  let index = 0;

  vi.doMock('react', async () => {
    const actual = await vi.importActual<typeof import('react')>('react');
    return {
      ...actual,
      useState: vi.fn((initial: unknown) => [stateValues[index] ?? initial, setters[index++]]),
    };
  });
  vi.doMock('../features/auth/api', () => ({ login: loginMock }));

  const { LoginView } = await import('./LoginView');
  const onLogin = vi.fn();
  const tree = LoginView({ onLogin });
  return { tree, onLogin, setters, loginMock };
};

describe('LoginView', () => {
  afterEach(() => {
    vi.resetModules();
    vi.doUnmock('react');
    vi.doUnmock('../features/auth/api');
  });

  it('submits credentials and maps session to operator', async () => {
    const { tree, onLogin, setters, loginMock } = await renderLoginView(['operator', 'operator123', '', false]);
    const form = findAll(tree, (element) => element.type === 'form')[0];
    const preventDefault = vi.fn();

    await form.props.onSubmit({ preventDefault });

    expect(preventDefault).toHaveBeenCalledOnce();
    expect(loginMock).toHaveBeenCalledWith('operator', 'operator123');
    expect(setters[3]).toHaveBeenNthCalledWith(1, true);
    expect(setters[2]).toHaveBeenCalledWith('');
    expect(onLogin).toHaveBeenCalledWith({
      name: 'operator',
      username: 'operator',
      role: 'Операционист',
      token: 'jwt-1',
    });
    expect(setters[3]).toHaveBeenLastCalledWith(false);
  });

  it('validates required credentials before calling backend', async () => {
    const { tree, setters, loginMock } = await renderLoginView([' ', 'operator123', '', false]);
    const form = findAll(tree, (element) => element.type === 'form')[0];

    await form.props.onSubmit({ preventDefault: vi.fn() });

    expect(setters[2]).toHaveBeenCalledWith('Заполните логин и пароль');
    expect(loginMock).not.toHaveBeenCalled();
  });

  it('shows backend and generic login errors', async () => {
    const errorLogin = vi.fn().mockRejectedValue(new Error('Неверный логин или пароль'));
    const genericLogin = vi.fn().mockRejectedValue('network');
    const errorRender = await renderLoginView(['operator', 'bad', '', false], errorLogin);
    const genericRender = await renderLoginView(['operator', 'bad', '', false], genericLogin);

    await findAll(errorRender.tree, (element) => element.type === 'form')[0].props.onSubmit({
      preventDefault: vi.fn(),
    });
    await findAll(genericRender.tree, (element) => element.type === 'form')[0].props.onSubmit({
      preventDefault: vi.fn(),
    });

    expect(errorRender.setters[2]).toHaveBeenCalledWith('Неверный логин или пароль');
    expect(genericRender.setters[2]).toHaveBeenCalledWith('Не удалось войти');
  });

  it('wires field changes and submitting/error render states', async () => {
    const { tree, setters } = await renderLoginView(['operator', 'operator123', 'Ошибка', true]);
    const inputs = findAll(tree, (element) => element.type === 'input');

    inputs[0].props.onChange({ target: { value: 'next-operator' } });
    inputs[1].props.onChange({ target: { value: 'next-password' } });

    expect(textOf(tree)).toContain('Ошибка');
    expect(textOf(tree)).toContain('Входим...');
    expect(setters[0]).toHaveBeenCalledWith('next-operator');
    expect(setters[1]).toHaveBeenCalledWith('next-password');
    expect(setters[2]).toHaveBeenCalledWith('');
  });
});
