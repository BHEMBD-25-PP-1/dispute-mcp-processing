import { afterEach, describe, expect, it, vi } from 'vitest';
import type { CaseAction } from '../disputes/api';
import type { DisputeCase, Operator } from '../../types';

const operator: Operator = {
  name: 'Оператор',
  username: 'operator',
  role: 'Операционист',
  token: 'token-1',
};

const makeCase = (id: string, status: DisputeCase['status'] = 'new'): DisputeCase => ({
  id,
  title: id,
  partner: 'НСПК',
  channel: 'HTTP',
  priority: 'P1',
  receivedAt: '10:00',
  amount: '100 ₽',
  customerName: 'Клиент',
  status,
  message: `message-${id}`,
  identifiers: { orderId: id, transactionId: `TXN-${id}`, service: 'taxi', confidence: 96 },
  connectors: [],
  timeline: [{ id: 'evt-1', title: 'Принято', detail: 'Кейс создан', time: '10:00', status: 'info' }],
  result: '',
});

const flushPromises = async () => {
  await Promise.resolve();
  await Promise.resolve();
};

type LoadOptions = {
  cases?: DisputeCase[];
  selectedId?: string;
  draftMessage?: string;
  error?: string;
  isLoading?: boolean;
  currentCases?: DisputeCase[];
  fetchCases?: ReturnType<typeof vi.fn>;
  updateCaseResult?: ReturnType<typeof vi.fn>;
  pickVisibleCaseId?: ReturnType<typeof vi.fn>;
};

const loadWorkspace = async (currentOperator: Operator | null, options: LoadOptions = {}) => {
  vi.resetModules();
  const cases = options.cases ?? [];
  const stateValues = [
    cases,
    options.selectedId ?? '',
    options.draftMessage ?? '',
    options.error ?? '',
    options.isLoading ?? false,
  ];
  const effects: Array<() => void> = [];
  const setCases = vi.fn((next: DisputeCase[] | ((current: DisputeCase[]) => DisputeCase[])) =>
    typeof next === 'function' ? next(options.currentCases ?? cases) : next,
  );
  const setSelectedId = vi.fn();
  const setDraftMessage = vi.fn();
  const setError = vi.fn();
  const setIsLoading = vi.fn();
  const setters = [setCases, setSelectedId, setDraftMessage, setError, setIsLoading];
  const fetchCases = options.fetchCases ?? vi.fn().mockResolvedValue([]);
  const updateCaseResult = options.updateCaseResult ?? vi.fn().mockResolvedValue(makeCase('DSP-1'));
  let stateIndex = 0;

  vi.doMock('react', async () => {
    const actual = await vi.importActual<typeof import('react')>('react');
    return {
      ...actual,
      useState: vi.fn((initial: unknown) => [stateValues[stateIndex] ?? initial, setters[stateIndex++]]),
      useMemo: vi.fn((factory: () => unknown) => factory()),
      useEffect: vi.fn((effect: () => void) => {
        effects.push(effect);
      }),
    };
  });
  vi.doMock('../disputes/api', () => ({ fetchCases, updateCaseResult }));
  if (options.pickVisibleCaseId) {
    vi.doMock('../disputes/queue', () => ({ pickVisibleCaseId: options.pickVisibleCaseId }));
  }

  const { useOperatorWorkspace } = await import('./useOperatorWorkspace');
  return {
    workspace: useOperatorWorkspace(currentOperator),
    effects,
    setters: { setCases, setSelectedId, setDraftMessage, setError, setIsLoading },
    fetchCases,
    updateCaseResult,
  };
};

describe('useOperatorWorkspace', () => {
  afterEach(() => {
    vi.resetModules();
    vi.doUnmock('react');
    vi.doUnmock('../disputes/api');
    vi.doUnmock('../disputes/queue');
    vi.unstubAllGlobals();
  });

  it('clears workspace state when operator is absent', async () => {
    const loaded = await loadWorkspace(null, {
      cases: [makeCase('DSP-1')],
      selectedId: 'DSP-1',
      draftMessage: 'draft',
    });

    loaded.effects[0]();

    expect(loaded.setters.setCases).toHaveBeenCalledWith([]);
    expect(loaded.setters.setSelectedId).toHaveBeenCalledWith('');
    expect(loaded.setters.setDraftMessage).toHaveBeenCalledWith('');
  });

  it('loads cases and selects the first visible case', async () => {
    const first = makeCase('DSP-1');
    const fetchCases = vi.fn().mockResolvedValue([first]);
    const loaded = await loadWorkspace(operator, { fetchCases });

    loaded.effects[0]();
    await flushPromises();

    expect(loaded.setters.setIsLoading).toHaveBeenNthCalledWith(1, true);
    expect(loaded.setters.setError).toHaveBeenCalledWith('');
    expect(fetchCases).toHaveBeenCalledWith('token-1');
    expect(loaded.setters.setCases).toHaveBeenCalledWith([first]);
    expect(loaded.setters.setSelectedId).toHaveBeenCalledWith('DSP-1');
    expect(loaded.setters.setDraftMessage).toHaveBeenCalledWith('message-DSP-1');
    expect(loaded.setters.setIsLoading).toHaveBeenLastCalledWith(false);
  });

  it('handles an empty queue after successful loading', async () => {
    const loaded = await loadWorkspace(operator, {
      fetchCases: vi.fn().mockResolvedValue([]),
    });

    loaded.effects[0]();
    await flushPromises();

    expect(loaded.setters.setCases).toHaveBeenCalledWith([]);
    expect(loaded.setters.setSelectedId).toHaveBeenCalledWith('');
    expect(loaded.setters.setDraftMessage).toHaveBeenCalledWith('');
  });

  it('reports queue loading failures', async () => {
    const loaded = await loadWorkspace(operator, {
      fetchCases: vi.fn().mockRejectedValue(new Error('network')),
    });

    loaded.effects[0]();
    await flushPromises();

    expect(loaded.setters.setError).toHaveBeenCalledWith('Не удалось загрузить очередь диспутов');
    expect(loaded.setters.setIsLoading).toHaveBeenLastCalledWith(false);
  });

  it('selects cases and applies successful action updates', async () => {
    const first = makeCase('DSP-1');
    const second = makeCase('DSP-2', 'attention');
    const updated = {
      ...first,
      status: 'processing' as const,
      message: 'updated-message',
      timeline: [
        first.timeline[0],
        { id: 'evt-backend', title: 'MCP', detail: 'Ответ получен', time: '10:01', status: 'success' as const },
      ],
    };
    const action: CaseAction = vi.fn().mockResolvedValue(updated);
    const loaded = await loadWorkspace(operator, {
      cases: [first, second],
      currentCases: [first, second],
      selectedId: 'DSP-1',
      draftMessage: 'draft-message',
    });

    loaded.workspace.selectCase('missing');
    loaded.workspace.selectCase('DSP-2');
    await loaded.workspace.runCaseAction(action);

    const nextCases = loaded.setters.setCases.mock.results[0].value as DisputeCase[];

    expect(loaded.setters.setSelectedId).toHaveBeenCalledWith('DSP-2');
    expect(loaded.setters.setDraftMessage).toHaveBeenCalledWith('message-DSP-2');
    expect(action).toHaveBeenCalledWith('token-1', 'DSP-1', 'draft-message');
    expect(loaded.setters.setError).toHaveBeenCalledWith('');
    expect(nextCases[0].timeline).toEqual([
      first.timeline[0],
      { id: 'evt-2', title: 'MCP', detail: 'Ответ получен', time: '10:01', status: 'success' },
    ]);
    expect(loaded.setters.setDraftMessage).toHaveBeenCalledWith('updated-message');
  });

  it('moves selection away from a case that leaves the active queue', async () => {
    const first = makeCase('DSP-1');
    const second = makeCase('DSP-2', 'attention');
    const action: CaseAction = vi.fn().mockResolvedValue({ ...first, status: 'resolved' as const });
    const loaded = await loadWorkspace(operator, {
      cases: [first, second],
      currentCases: [first, second],
      selectedId: 'DSP-1',
      draftMessage: 'draft-message',
    });

    await loaded.workspace.runCaseAction(action);

    expect(loaded.setters.setSelectedId).toHaveBeenCalledWith('DSP-2');
    expect(loaded.setters.setDraftMessage).toHaveBeenCalledWith('message-DSP-2');
  });

  it('clears draft when queue helper points to a missing selected case', async () => {
    const first = makeCase('DSP-1');
    const action: CaseAction = vi.fn().mockResolvedValue({ ...first, status: 'resolved' as const });
    const loaded = await loadWorkspace(operator, {
      cases: [first],
      currentCases: [first],
      selectedId: 'DSP-1',
      draftMessage: 'draft-message',
      pickVisibleCaseId: vi.fn(() => 'missing-id'),
    });

    await loaded.workspace.runCaseAction(action);

    expect(loaded.setters.setSelectedId).toHaveBeenCalledWith('missing-id');
    expect(loaded.setters.setDraftMessage).toHaveBeenCalledWith('');
  });

  it('guards unavailable actions and reports action failures', async () => {
    const guardedAction: CaseAction = vi.fn();
    const noOperator = await loadWorkspace(null, { cases: [makeCase('DSP-1')], selectedId: 'DSP-1' });
    const noSelection = await loadWorkspace(operator);
    const failing = await loadWorkspace(operator, { cases: [makeCase('DSP-1')], selectedId: 'DSP-1' });
    const failingAction: CaseAction = vi.fn().mockRejectedValue(new Error('backend'));

    await noOperator.workspace.runCaseAction(guardedAction);
    await noSelection.workspace.runCaseAction(guardedAction);
    await failing.workspace.runCaseAction(failingAction);

    expect(guardedAction).not.toHaveBeenCalled();
    expect(noSelection.workspace.parsedPreview).toEqual({ service: 'unknown', confidence: 0 });
    expect(failing.setters.setError).toHaveBeenCalledWith('Backend не смог выполнить действие по кейсу');
  });

  it('saves result changes and reports save failures', async () => {
    const first = makeCase('DSP-1');
    const updated = { ...first, result: 'saved' };
    const updateCaseResult = vi.fn().mockResolvedValue(updated);
    const loaded = await loadWorkspace(operator, {
      cases: [first],
      currentCases: [first],
      selectedId: 'DSP-1',
      updateCaseResult,
    });
    const failed = await loadWorkspace(operator, {
      cases: [first],
      selectedId: 'DSP-1',
      updateCaseResult: vi.fn().mockRejectedValue(new Error('backend')),
    });

    loaded.workspace.updateResult('saved');
    failed.workspace.updateResult('failed');
    await flushPromises();

    expect(updateCaseResult).toHaveBeenCalledWith('token-1', 'DSP-1', 'saved');
    expect(loaded.setters.setCases).toHaveBeenCalled();
    expect(failed.setters.setError).toHaveBeenCalledWith('Не удалось сохранить итоговый ответ');

    const noOperator = await loadWorkspace(null, { cases: [first], selectedId: 'DSP-1' });
    const noSelection = await loadWorkspace(operator);
    noOperator.workspace.updateResult('ignored');
    noSelection.workspace.updateResult('ignored');
    expect(noOperator.updateCaseResult).not.toHaveBeenCalled();
    expect(noSelection.updateCaseResult).not.toHaveBeenCalled();
  });

  it('copies result text when available', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal('navigator', { clipboard: { writeText } });
    const withResult = await loadWorkspace(operator, {
      cases: [makeCase('DSP-1')],
      selectedId: 'DSP-1',
    });
    withResult.workspace.selectedCase!.result = 'copy me';
    const withoutResult = await loadWorkspace(operator, {
      cases: [makeCase('DSP-2')],
      selectedId: 'DSP-2',
    });

    await withResult.workspace.copyResult();
    await withoutResult.workspace.copyResult();

    expect(writeText).toHaveBeenCalledOnce();
    expect(writeText).toHaveBeenCalledWith('copy me');
  });
});
