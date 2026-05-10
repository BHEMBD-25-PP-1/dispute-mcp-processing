import type { ConnectorStatus, DisputeCase, ParsedIdentifiers } from './types';

export const statusLabel: Record<DisputeCase['status'], string> = {
  new: 'Новый',
  processing: 'В работе',
  attention: 'Проверка',
  resolved: 'Готов',
};

export const connectorStatusLabel: Record<ConnectorStatus, string> = {
  ready: 'Готов',
  queued: 'Очередь',
  running: 'Запрос',
  done: 'Ответ',
  failed: 'Ошибка',
};

export const serviceLabel: Record<ParsedIdentifiers['service'], string> = {
  taxi: 'Такси',
  afisha: 'Афиша',
  unknown: 'Не определен',
};
