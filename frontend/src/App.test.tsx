import { isValidElement, type ReactElement, type ReactNode } from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { DisputeCase, Operator } from './types';

const operator: Operator = {
  name: 'Оператор',
  username: 'operator',
  role: 'Операционист',
  token: 'token-1',
};

const selectedCase: DisputeCase = {
  id: 'DSP-1',
  title: 'Кейс',
  partner: 'НСПК',
  channel: 'HTTP',
  priority: 'P1',
  status: 'new',
  receivedAt: '10:00',
  amount: '100 ₽',
  customerName: 'Клиент',
  message: 'Исходное сообщение',
  identifiers: { service: 'taxi', confidence: 96 },
  connectors: [],
  timeline: [],
  result: '',
};

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

const workspaceDefaults = () => ({
  cases: [selectedCase],
  selectedCase,
  draftMessage: selectedCase.message,
  parsedPreview: selectedCase.identifiers,
  error: '',
  isLoading: false,
  setDraftMessage: vi.fn(),
  selectCase: vi.fn(),
  runCaseAction: vi.fn(),
  updateResult: vi.fn(),
  copyResult: vi.fn(),
});

type WorkspaceMock = Omit<ReturnType<typeof workspaceDefaults>, 'selectedCase'> & {
  selectedCase?: DisputeCase;
};

const renderApp = async (
  currentOperator: Operator | null,
  workspace: WorkspaceMock,
) => {
  vi.resetModules();
  const setOperator = vi.fn();
  const workspaceMock = vi.fn(() => workspace);
  const parseCase = vi.fn();
  const runCaseMcp = vi.fn();
  const generateCaseResult = vi.fn();

  vi.doMock('react', async () => {
    const actual = await vi.importActual<typeof import('react')>('react');
    return { ...actual, useState: vi.fn(() => [currentOperator, setOperator]) };
  });
  vi.doMock('./features/workspace/useOperatorWorkspace', () => ({ useOperatorWorkspace: workspaceMock }));
  vi.doMock('./features/disputes/api', () => ({ parseCase, runCaseMcp, generateCaseResult }));
  vi.doMock('./components/LoginView', () => ({ LoginView: 'login-view' }));
  vi.doMock('./components/Topbar', () => ({ Topbar: 'topbar-view' }));
  vi.doMock('./components/QueuePanel', () => ({ QueuePanel: 'queue-panel' }));
  vi.doMock('./components/CaseBoard', () => ({ CaseBoard: 'case-board' }));
  vi.doMock('./components/InspectorPanel', () => ({ InspectorPanel: 'inspector-panel' }));

  const { default: App } = await import('./App');
  return {
    tree: App(),
    setOperator,
    workspaceMock,
    actions: { parseCase, runCaseMcp, generateCaseResult },
  };
};

describe('App', () => {
  afterEach(() => {
    vi.resetModules();
    vi.doUnmock('react');
    vi.doUnmock('./features/workspace/useOperatorWorkspace');
    vi.doUnmock('./features/disputes/api');
    vi.doUnmock('./components/LoginView');
    vi.doUnmock('./components/Topbar');
    vi.doUnmock('./components/QueuePanel');
    vi.doUnmock('./components/CaseBoard');
    vi.doUnmock('./components/InspectorPanel');
  });

  it('shows login while there is no operator and accepts login callback', async () => {
    const rendered = await renderApp(null, workspaceDefaults());
    const login = findAll(rendered.tree, (element) => element.type === 'login-view')[0];

    login.props.onLogin(operator);

    expect(rendered.workspaceMock).toHaveBeenCalledWith(null);
    expect(rendered.setOperator).toHaveBeenCalledWith(operator);
  });

  it('shows loading and empty queue states', async () => {
    const loading = await renderApp(operator, {
      ...workspaceDefaults(),
      isLoading: true,
      selectedCase: undefined,
    });
    findAll(loading.tree, (element) => element.type === 'topbar-view')[0].props.onLogout();

    const empty = await renderApp(operator, {
      ...workspaceDefaults(),
      cases: [],
      isLoading: false,
      selectedCase: undefined,
    });

    expect(textOf(loading.tree)).toContain('Загружаем очередь...');
    expect(textOf(empty.tree)).toContain('Нет доступных кейсов');
    expect(loading.setOperator).toHaveBeenCalledWith(null);
  });

  it('wires full workspace actions and error rendering', async () => {
    const workspace = { ...workspaceDefaults(), error: 'Ошибка backend' };
    const rendered = await renderApp(operator, workspace);
    const topbar = findAll(rendered.tree, (element) => element.type === 'topbar-view')[0];
    const queue = findAll(rendered.tree, (element) => element.type === 'queue-panel')[0];
    const board = findAll(rendered.tree, (element) => element.type === 'case-board')[0];

    topbar.props.onLogout();
    queue.props.onSelect('DSP-1');
    board.props.onResetDraft();
    board.props.onParse();
    board.props.onRunMcp();
    board.props.onGenerateResult();
    board.props.onDraftChange('draft');
    board.props.onCopyResult();
    board.props.onResultChange('result');

    expect(textOf(rendered.tree)).toContain('Ошибка backend');
    expect(rendered.setOperator).toHaveBeenCalledWith(null);
    expect(workspace.selectCase).toHaveBeenCalledWith('DSP-1');
    expect(workspace.setDraftMessage).toHaveBeenCalledWith('Исходное сообщение');
    expect(workspace.runCaseAction).toHaveBeenNthCalledWith(1, rendered.actions.parseCase);
    expect(workspace.runCaseAction).toHaveBeenNthCalledWith(2, rendered.actions.runCaseMcp);
    expect(workspace.runCaseAction).toHaveBeenNthCalledWith(3, rendered.actions.generateCaseResult);
    expect(workspace.setDraftMessage).toHaveBeenCalledWith('draft');
    expect(workspace.copyResult).toHaveBeenCalledOnce();
    expect(workspace.updateResult).toHaveBeenCalledWith('result');
  });

  it('renders full workspace without an error banner', async () => {
    const rendered = await renderApp(operator, workspaceDefaults());

    expect(findAll(rendered.tree, (element) => element.props.className === 'form-error')).toHaveLength(0);
    expect(findAll(rendered.tree, (element) => element.type === 'inspector-panel')).toHaveLength(1);
  });
});
