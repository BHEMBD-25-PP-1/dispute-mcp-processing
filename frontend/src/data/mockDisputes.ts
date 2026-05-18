import type { DisputeCase, McpConnector, ParsedIdentifiers, TimelineEvent } from '../types';

export const createConnectors = (): McpConnector[] => [
  {
    id: 'taxi',
    name: 'MCP Такси',
    service: 'taxi',
    status: 'ready',
    sla: '00:28',
    confidence: 0,
    fields: [
      { label: 'Маршрут', value: 'ожидает запроса' },
      { label: 'Статус поездки', value: 'ожидает запроса' },
      { label: 'Оплата', value: 'ожидает запроса' },
    ],
  },
  {
    id: 'afisha',
    name: 'MCP Афиша',
    service: 'afisha',
    status: 'ready',
    sla: '00:33',
    confidence: 0,
    fields: [
      { label: 'Событие', value: 'ожидает запроса' },
      { label: 'Статус билета', value: 'ожидает запроса' },
      { label: 'Возврат', value: 'ожидает запроса' },
    ],
  },
];

const baseTimeline: TimelineEvent[] = [
  {
    id: 'evt-1',
    title: 'Сообщение принято',
    detail: 'Кейс создан из входящего обращения НСПК',
    time: '09:41',
    status: 'info',
  },
];

export const emptyIdentifiers: ParsedIdentifiers = {
  service: 'unknown',
  confidence: 0,
};

export const mockDisputes: DisputeCase[] = [
  {
    id: 'DSP-1042',
    title: 'Списание за несостоявшуюся поездку',
    partner: 'НСПК',
    channel: 'JSON',
    priority: 'P1',
    status: 'new',
    receivedAt: '09:41',
    amount: '1 280 ₽',
    customerName: 'Ирина С.',
    message:
      'От НСПК поступил диспут: transaction_id=TXN-98765, order_id=TAXI-240518, service=taxi. Клиент сообщает, что поездка не состоялась, но оплата списана.',
    identifiers: {
      orderId: 'TAXI-240518',
      transactionId: 'TXN-98765',
      service: 'taxi',
      confidence: 96,
    },
    connectors: createConnectors(),
    timeline: baseTimeline,
    result: '',
  },
  {
    id: 'DSP-1041',
    title: 'Билет не активирован',
    partner: 'НСПК',
    channel: 'XML',
    priority: 'P2',
    status: 'processing',
    receivedAt: '09:18',
    amount: '3 600 ₽',
    customerName: 'Максим К.',
    message:
      'Диспут по транзакции TXN-77210. Заказ AFISHA-8891, сервис Афиша. Клиент оплатил билет, QR не был использован.',
    identifiers: {
      orderId: 'AFISHA-8891',
      transactionId: 'TXN-77210',
      service: 'afisha',
      confidence: 88,
    },
    connectors: createConnectors().map((connector) =>
      connector.id === 'afisha'
        ? {
            ...connector,
            status: 'done',
            confidence: 93,
            fields: [
              { label: 'Событие', value: 'Stand-up Hall, 12 мая' },
              { label: 'Статус билета', value: 'не активирован' },
              { label: 'Возврат', value: 'разрешен' },
            ],
          }
        : connector,
    ),
    timeline: [
      ...baseTimeline,
      {
        id: 'evt-2',
        title: 'Афиша ответила',
        detail: 'Билет найден и не был активирован',
        time: '09:20',
        status: 'success',
      },
    ],
    result: '',
  },
  {
    id: 'DSP-1039',
    title: 'Не хватает идентификаторов',
    partner: 'НСПК',
    channel: 'TXT',
    priority: 'P2',
    status: 'attention',
    receivedAt: '08:56',
    amount: 'не определена',
    customerName: 'Клиент',
    message: 'Клиент оспаривает списание, сервис не указан. Нужна ручная проверка.',
    identifiers: emptyIdentifiers,
    connectors: createConnectors(),
    timeline: [
      ...baseTimeline,
      {
        id: 'evt-2',
        title: 'Низкая уверенность',
        detail: 'Парсер не нашел order_id и service',
        time: '08:57',
        status: 'warning',
      },
    ],
    result: 'Требуется ручная проверка: недостаточно данных для обращения к MCP-серверам.',
  },
];
