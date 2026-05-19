import type { ParsedIdentifiers, ServiceKind } from '../../types';

const orderPatterns = [
  /order_id\s*[:=]\s*([A-Z0-9-]+)/i,
  /заказ[ау]?\s*(?:N|№|#)?\s*([A-Z0-9-]+)/i,
  /\b(TAXI-\d{4,})\b/i,
  /\b(AFISHA-\d{4,})\b/i,
];

const transactionPatterns = [
  /transaction_id\s*[:=]\s*([A-Z0-9-]+)/i,
  /транзакци[ияю]\s*(?:N|№|#)?\s*([A-Z0-9-]+)/i,
  /\b(TXN-\d{4,})\b/i,
];

const userPatterns = [
  /user_id\s*[:=]\s*([A-Z0-9-]+)/i,
  /клиент\s*(?:N|№|#)?\s*([A-Z0-9-]+)/i,
];

const pick = (text: string, patterns: RegExp[]) => {
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match?.[1]) {
      return match[1].toUpperCase();
    }
  }

  return undefined;
};

const detectService = (text: string, orderId?: string): ServiceKind => {
  const normalized = `${text} ${orderId ?? ''}`.toLowerCase();

  if (/(такси|taxi|ride|поездк)/.test(normalized)) {
    return 'taxi';
  }

  if (/(афиша|afisha|билет|событи|концерт|театр)/.test(normalized)) {
    return 'afisha';
  }

  return 'unknown';
};

export const parseIncomingMessage = (message: string): ParsedIdentifiers => {
  const orderId = pick(message, orderPatterns);
  const transactionId = pick(message, transactionPatterns);
  const userId = pick(message, userPatterns);
  const service = detectService(message, orderId);
  const signals = [orderId, transactionId, userId, service !== 'unknown'].filter(Boolean).length;

  return {
    orderId,
    transactionId,
    userId,
    service,
    confidence: Math.min(98, 42 + signals * 14),
  };
};

export const buildOperatorAnswer = (
  parsed: ParsedIdentifiers,
  amount: string,
  customerName: string,
) => {
  if (parsed.service === 'taxi') {
    return `Транзакция подтверждена. Поездка по заказу ${parsed.orderId ?? 'не определен'} не состоялась, списание ${amount} будет возвращено клиенту ${customerName}.`;
  }

  if (parsed.service === 'afisha') {
    return `Транзакция подтверждена. Билет по заказу ${parsed.orderId ?? 'не определен'} не был активирован, списание ${amount} будет возвращено клиенту ${customerName}.`;
  }

  return `Требуется ручная проверка: по обращению не удалось надежно определить сервис для заказа ${parsed.orderId ?? 'не определен'} и транзакции ${parsed.transactionId ?? 'не определена'}.`;
};
