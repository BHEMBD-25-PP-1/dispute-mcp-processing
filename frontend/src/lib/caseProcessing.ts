import type { ConnectorStatus, McpConnector, ParsedIdentifiers } from '../types';

export const formatNow = () =>
  new Intl.DateTimeFormat('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date());

export const getNextConnectors = (connectors: McpConnector[], parsed: ParsedIdentifiers) =>
  connectors.map((connector) => {
    if (parsed.service !== connector.service) {
      return {
        ...connector,
        status: 'queued' as ConnectorStatus,
        confidence: 12,
      };
    }

    if (connector.service === 'taxi') {
      return {
        ...connector,
        status: 'done' as ConnectorStatus,
        confidence: 97,
        fields: [
          { label: 'Маршрут', value: 'Аэропорт Внуково -> Тверская, 9' },
          { label: 'Статус поездки', value: 'не состоялась' },
          { label: 'Оплата', value: 'списана, возврат разрешен' },
        ],
      };
    }

    return {
      ...connector,
      status: 'done' as ConnectorStatus,
      confidence: 93,
      fields: [
        { label: 'Событие', value: 'Stand-up Hall, 12 мая' },
        { label: 'Статус билета', value: 'не активирован' },
        { label: 'Возврат', value: 'разрешен' },
      ],
    };
  });
