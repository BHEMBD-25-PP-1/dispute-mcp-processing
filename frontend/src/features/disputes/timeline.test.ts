import { describe, expect, it } from 'vitest';
import { mergeTimeline } from './timeline';

describe('mergeTimeline', () => {
  it('keeps existing events and appends unique events with stable ids', () => {
    const current = [
      { id: 'evt-1', title: 'Принято', detail: 'Кейс создан', time: '10:00', status: 'info' as const },
    ];
    const next = [
      { id: 'evt-backend-1', title: 'Принято', detail: 'Кейс создан', time: '10:01', status: 'info' as const },
      { id: 'evt-backend-2', title: 'MCP', detail: 'Ответ получен', time: '10:02', status: 'success' as const },
    ];

    expect(mergeTimeline(current, next)).toEqual([
      current[0],
      { ...next[1], id: 'evt-2' },
    ]);
  });
});
