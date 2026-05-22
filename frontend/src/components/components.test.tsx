import { isValidElement, type ReactElement, type ReactNode } from 'react';
import { describe, expect, it, vi } from 'vitest';
import { CaseBoard } from './CaseBoard';
import { InspectorPanel } from './InspectorPanel';
import { QueuePanel } from './QueuePanel';
import { Topbar } from './Topbar';
import type { DisputeCase, McpConnector, ParsedIdentifiers } from '../types';

const connector = (service: 'taxi' | 'afisha'): McpConnector => ({
  id: service,
  name: service === 'taxi' ? 'MCP Такси' : 'MCP Афиша',
  service,
  status: service === 'taxi' ? 'done' : 'ready',
  sla: service === 'taxi' ? '00:28' : '00:33',
  confidence: service === 'taxi' ? 97 : 0,
  fields:
    service === 'taxi'
      ? [
          { label: 'Маршрут', value: 'Аэропорт Внуково -> Тверская, 9' },
          { label: 'Статус поездки', value: 'not_completed' },
        ]
      : [
          { label: 'Событие', value: 'Stand-up Hall' },
          { label: 'Возврат', value: 'ожидает запроса' },
        ],
});

const makeCase = (overrides: Partial<DisputeCase> = {}): DisputeCase => ({
  id: 'DSP-1',
  title: 'Списание за поездку',
  partner: 'НСПК',
  channel: 'HTTP',
  priority: 'P1',
  status: 'new',
  receivedAt: '10:00',
  amount: '100 ₽',
  customerName: 'Клиент',
  message: 'message',
  identifiers: { orderId: 'TAXI-240518', transactionId: 'TXN-98765', service: 'taxi', confidence: 96 },
  connectors: [connector('taxi'), connector('afisha')],
  timeline: [
    { id: 'evt-1', title: 'Принято', detail: 'Кейс создан', time: '10:00', status: 'info' },
    { id: 'evt-2', title: 'MCP', detail: 'Ответ получен', time: '10:01', status: 'success' },
  ],
  result: 'Готовый ответ',
  ...overrides,
});

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

const findAll = (
  node: ReactNode,
  predicate: (element: ReactElement<any>) => boolean,
): ReactElement<any>[] => {
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

describe('operator components', () => {
  it('renders topbar queue metrics and calls logout', () => {
    const onLogout = vi.fn();
    const tree = Topbar({
      cases: [
        makeCase({ id: 'DSP-1', status: 'new' }),
        makeCase({ id: 'DSP-2', status: 'attention' }),
        makeCase({ id: 'DSP-3', status: 'resolved' }),
      ],
      operator: { name: 'Оператор', username: 'operator', role: 'Операционист', token: 'token' },
      onLogout,
    });

    findAll(tree, (element) => element.type === 'button')[0].props.onClick?.();

    expect(textOf(tree)).toContain('Оператор');
    expect(textOf(tree)).toContain('активно');
    expect(onLogout).toHaveBeenCalledOnce();
  });

  it('renders active queue rows, selected state, and empty queue copy', () => {
    const onSelect = vi.fn();
    const tree = QueuePanel({
      cases: [
        makeCase({ id: 'DSP-1', status: 'new' }),
        makeCase({ id: 'DSP-2', status: 'processing' }),
        makeCase({ id: 'DSP-3', status: 'resolved' }),
      ],
      selectedId: 'DSP-1',
      onSelect,
    });
    const buttons = findAll(tree, (element) => element.type === 'button');

    buttons[0].props.onClick?.();

    expect(buttons).toHaveLength(2);
    expect(buttons[0].props.className).toContain('is-selected');
    expect(buttons[1].props.className).not.toContain('is-selected');
    expect(textOf(tree)).toContain('Новый');
    expect(onSelect).toHaveBeenCalledWith('DSP-1');

    const empty = QueuePanel({ cases: [makeCase({ status: 'resolved' })], selectedId: '', onSelect });
    expect(textOf(empty)).toContain('Активных диспутов нет');
  });

  it('wires case board controls and renders connector data', () => {
    const handlers = {
      onDraftChange: vi.fn(),
      onResetDraft: vi.fn(),
      onParse: vi.fn(),
      onRunMcp: vi.fn(),
      onGenerateResult: vi.fn(),
      onCopyResult: vi.fn(),
      onResultChange: vi.fn(),
    };
    const parsedPreview: ParsedIdentifiers = { service: 'taxi', confidence: 96 };
    const tree = CaseBoard({
      selectedCase: makeCase(),
      draftMessage: 'draft',
      parsedPreview,
      ...handlers,
    });

    const textareas = findAll(tree, (element) => element.type === 'textarea');
    textareas[0].props.onChange?.({ target: { value: 'next draft' } });
    textareas[1].props.onChange?.({ target: { value: 'next result' } });
    findAll(tree, (element) => element.type === 'button').forEach((button) => button.props.onClick?.());

    expect(textOf(tree)).toContain('нет данных');
    expect(textOf(tree)).toContain('Аэропорт Внуково -> Тверская, 9');
    expect(textOf(tree)).toContain('Stand-up Hall');
    expect(handlers.onDraftChange).toHaveBeenCalledWith('next draft');
    expect(handlers.onResultChange).toHaveBeenCalledWith('next result');
    expect(handlers.onResetDraft).toHaveBeenCalledOnce();
    expect(handlers.onParse).toHaveBeenCalledOnce();
    expect(handlers.onRunMcp).toHaveBeenCalledOnce();
    expect(handlers.onGenerateResult).toHaveBeenCalledTimes(2);
    expect(handlers.onCopyResult).toHaveBeenCalledOnce();

    const disabledCopy = findAll(
      CaseBoard({
        selectedCase: makeCase({ result: '' }),
        draftMessage: 'draft',
        parsedPreview: { orderId: 'TAXI-240518', transactionId: 'TXN-98765', service: 'taxi', confidence: 96 },
        ...handlers,
      }),
      (element) => element.type === 'button' && element.props.disabled === true,
    );
    expect(disabledCopy).toHaveLength(1);
  });

  it('renders inspector control data and timeline', () => {
    const tree = InspectorPanel({ selectedCase: makeCase({ status: 'processing' }) });

    expect(textOf(tree)).toContain('Такси');
    expect(textOf(tree)).toContain('96%');
    expect(textOf(tree)).toContain('Ответ получен');
  });
});
