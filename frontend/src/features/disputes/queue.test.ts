import { describe, expect, it } from 'vitest';
import type { DisputeCase } from '../../types';
import { getActiveQueueCases, getQueueSummary, pickVisibleCaseId } from './queue';

const makeCase = (id: string, status: DisputeCase['status']): DisputeCase => ({
  id,
  status,
  title: id,
  partner: 'НСПК',
  channel: 'HTTP',
  priority: 'P2',
  receivedAt: '10:00',
  amount: '100 ₽',
  customerName: 'Клиент',
  message: 'message',
  identifiers: { service: 'unknown', confidence: 0 },
  connectors: [],
  timeline: [],
  result: '',
});

describe('queue helpers', () => {
  const cases = [
    makeCase('new-case', 'new'),
    makeCase('processing-case', 'processing'),
    makeCase('attention-case', 'attention'),
    makeCase('resolved-case', 'resolved'),
  ];

  it('hides resolved cases from active queue', () => {
    expect(getActiveQueueCases(cases).map((item) => item.id)).toEqual([
      'new-case',
      'processing-case',
      'attention-case',
    ]);
  });

  it('counts active and resolved cases separately', () => {
    expect(getQueueSummary(cases)).toEqual({
      active: 3,
      attention: 1,
      resolved: 1,
    });
  });

  it('selects next active case when current case is resolved', () => {
    expect(pickVisibleCaseId(cases, 'resolved-case')).toBe('new-case');
  });

  it('keeps current selected case when it is still active', () => {
    expect(pickVisibleCaseId(cases, 'processing-case')).toBe('processing-case');
  });
});
