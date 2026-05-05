import { useMemo, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  Copy,
  FileSearch,
  Inbox,
  MessageSquareText,
  Play,
  RefreshCw,
  Route,
  Send,
  ShieldCheck,
  Ticket,
} from 'lucide-react';
import { createConnectors, mockDisputes } from './data/mockDisputes';
import { buildOperatorAnswer, parseIncomingMessage } from './lib/parser';
import type { ConnectorStatus, DisputeCase, McpConnector, ParsedIdentifiers } from './types';

const statusLabel: Record<DisputeCase['status'], string> = {
  new: 'Новый',
  processing: 'В работе',
  attention: 'Проверка',
  resolved: 'Готов',
};

const connectorStatusLabel: Record<ConnectorStatus, string> = {
  ready: 'Готов',
  queued: 'Очередь',
  running: 'Запрос',
  done: 'Ответ',
  failed: 'Ошибка',
};

const serviceLabel: Record<ParsedIdentifiers['service'], string> = {
  taxi: 'Такси',
  afisha: 'Афиша',
  unknown: 'Не определен',
};

const formatNow = () =>
  new Intl.DateTimeFormat('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date());

const getNextConnectors = (connectors: McpConnector[], parsed: ParsedIdentifiers) =>
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

const getCaseTone = (status: DisputeCase['status']) => `case-row case-row--${status}`;

function App() {
  const [cases, setCases] = useState<DisputeCase[]>(mockDisputes);
  const [selectedId, setSelectedId] = useState(mockDisputes[0].id);
  const [draftMessage, setDraftMessage] = useState(mockDisputes[0].message);

  const selectedCase = useMemo(
    () => cases.find((item) => item.id === selectedId) ?? cases[0],
    [cases, selectedId],
  );

  const parsedPreview = useMemo(() => parseIncomingMessage(draftMessage), [draftMessage]);

  const updateSelectedCase = (updater: (item: DisputeCase) => DisputeCase) => {
    setCases((current) => current.map((item) => (item.id === selectedCase.id ? updater(item) : item)));
  };

  const selectCase = (caseId: string) => {
    const nextCase = cases.find((item) => item.id === caseId);
    if (!nextCase) {
      return;
    }

    setSelectedId(caseId);
    setDraftMessage(nextCase.message);
  };

  const applyParsing = () => {
    const parsed = parseIncomingMessage(draftMessage);
    updateSelectedCase((item) => ({
      ...item,
      status: parsed.confidence < 70 ? 'attention' : 'processing',
      message: draftMessage,
      identifiers: parsed,
      timeline: [
        ...item.timeline,
        {
          id: `evt-${item.timeline.length + 1}`,
          title: 'Парсинг выполнен',
          detail: `Найдены service=${serviceLabel[parsed.service]}, order_id=${parsed.orderId ?? 'нет'}, transaction_id=${parsed.transactionId ?? 'нет'}`,
          time: formatNow(),
          status: parsed.confidence < 70 ? 'warning' : 'success',
        },
      ],
    }));
  };

  const runMcp = () => {
    updateSelectedCase((item) => {
      const parsed = parseIncomingMessage(draftMessage);
      const nextConnectors = getNextConnectors(item.connectors.length ? item.connectors : createConnectors(), parsed);

      return {
        ...item,
        status: parsed.service === 'unknown' ? 'attention' : 'processing',
        message: draftMessage,
        identifiers: parsed,
        connectors: nextConnectors,
        timeline: [
          ...item.timeline,
          {
            id: `evt-${item.timeline.length + 1}`,
            title: parsed.service === 'unknown' ? 'Маршрутизация остановлена' : 'MCP-ответ получен',
            detail:
              parsed.service === 'unknown'
                ? 'Сервис не определен, нужен ручной выбор'
                : `Запрос направлен в ${serviceLabel[parsed.service]}`,
            time: formatNow(),
            status: parsed.service === 'unknown' ? 'warning' : 'success',
          },
        ],
      };
    });
  };

  const generateResult = () => {
    updateSelectedCase((item) => {
      const parsed = parseIncomingMessage(draftMessage);

      return {
        ...item,
        status: parsed.service === 'unknown' ? 'attention' : 'resolved',
        message: draftMessage,
        identifiers: parsed,
        result: buildOperatorAnswer(parsed, item.amount, item.customerName),
        timeline: [
          ...item.timeline,
          {
            id: `evt-${item.timeline.length + 1}`,
            title: 'Ответ сформирован',
            detail: parsed.service === 'unknown' ? 'Добавлен комментарий для ручной проверки' : 'Итог готов для передачи в НСПК',
            time: formatNow(),
            status: parsed.service === 'unknown' ? 'warning' : 'success',
          },
        ],
      };
    });
  };

  const copyResult = async () => {
    if (!selectedCase.result) {
      return;
    }

    await navigator.clipboard?.writeText(selectedCase.result);
  };

  const resolvedCount = cases.filter((item) => item.status === 'resolved').length;
  const attentionCount = cases.filter((item) => item.status === 'attention').length;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Dispute MCP Ops</p>
          <h1>Рабочее место операциониста</h1>
        </div>

        <div className="metrics-strip" aria-label="Сводка очереди">
          <div className="metric">
            <span>{cases.length}</span>
            <small>в очереди</small>
          </div>
          <div className="metric metric--amber">
            <span>{attentionCount}</span>
            <small>ручная проверка</small>
          </div>
          <div className="metric metric--green">
            <span>{resolvedCount}</span>
            <small>готово</small>
          </div>
        </div>
      </header>

      <div className="workspace">
        <aside className="queue-panel" aria-label="Очередь диспутов">
          <div className="panel-heading">
            <Inbox size={18} aria-hidden="true" />
            <span>Очередь</span>
          </div>

          <div className="case-list">
            {cases.map((item) => (
              <button
                className={`${getCaseTone(item.status)} ${item.id === selectedCase.id ? 'is-selected' : ''}`}
                key={item.id}
                onClick={() => selectCase(item.id)}
                type="button"
              >
                <span className="case-row__top">
                  <strong>{item.id}</strong>
                  <span className="priority">{item.priority}</span>
                </span>
                <span className="case-row__title">{item.title}</span>
                <span className="case-row__meta">
                  {statusLabel[item.status]} · {item.channel} · {item.receivedAt}
                </span>
              </button>
            ))}
          </div>
        </aside>

        <main className="case-board">
          <section className="case-header">
            <div>
              <span className={`status-pill status-pill--${selectedCase.status}`}>{statusLabel[selectedCase.status]}</span>
              <h2>{selectedCase.title}</h2>
              <p>
                {selectedCase.partner} · {selectedCase.customerName} · {selectedCase.amount}
              </p>
            </div>
            <button className="ghost-button" type="button" onClick={() => setDraftMessage(selectedCase.message)}>
              <RefreshCw size={16} aria-hidden="true" />
              Обновить
            </button>
          </section>

          <section className="work-surface intake-surface">
            <div className="surface-title">
              <MessageSquareText size={18} aria-hidden="true" />
              <h3>Входящее сообщение</h3>
            </div>
            <textarea
              aria-label="Текст входящего диспута"
              value={draftMessage}
              onChange={(event) => setDraftMessage(event.target.value)}
            />
            <div className="action-row">
              <button className="primary-button" onClick={applyParsing} type="button">
                <FileSearch size={16} aria-hidden="true" />
                Распарсить
              </button>
              <button className="secondary-button" onClick={runMcp} type="button">
                <Play size={16} aria-hidden="true" />
                Запросить MCP
              </button>
              <button className="secondary-button" onClick={generateResult} type="button">
                <Send size={16} aria-hidden="true" />
                Сформировать ответ
              </button>
            </div>
          </section>

          <section className="identifier-grid" aria-label="Извлеченные идентификаторы">
            <div className="identifier-tile">
              <span>order_id</span>
              <strong>{parsedPreview.orderId ?? 'нет данных'}</strong>
            </div>
            <div className="identifier-tile">
              <span>transaction_id</span>
              <strong>{parsedPreview.transactionId ?? 'нет данных'}</strong>
            </div>
            <div className="identifier-tile">
              <span>service</span>
              <strong>{serviceLabel[parsedPreview.service]}</strong>
            </div>
            <div className="identifier-tile">
              <span>уверенность</span>
              <strong>{parsedPreview.confidence}%</strong>
            </div>
          </section>

          <section className="connectors-section">
            <div className="surface-title">
              <ShieldCheck size={18} aria-hidden="true" />
              <h3>MCP-серверы</h3>
            </div>
            <div className="connector-grid">
              {selectedCase.connectors.map((connector) => (
                <article className="connector-card" key={connector.id}>
                  <div className="connector-card__top">
                    <div className="connector-icon">
                      {connector.service === 'taxi' ? <Route size={18} /> : <Ticket size={18} />}
                    </div>
                    <div>
                      <h4>{connector.name}</h4>
                      <span className={`connector-status connector-status--${connector.status}`}>
                        {connectorStatusLabel[connector.status]}
                      </span>
                    </div>
                  </div>
                  <dl>
                    {connector.fields.map((field) => (
                      <div key={field.label}>
                        <dt>{field.label}</dt>
                        <dd>{field.value}</dd>
                      </div>
                    ))}
                  </dl>
                  <div className="connector-card__footer">
                    <span>
                      <Clock3 size={14} aria-hidden="true" />
                      SLA {connector.sla}
                    </span>
                    <span>{connector.confidence}%</span>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="work-surface result-surface">
            <div className="surface-title">
              <ClipboardCheck size={18} aria-hidden="true" />
              <h3>Итоговый ответ</h3>
            </div>
            <textarea
              aria-label="Итоговый ответ"
              value={selectedCase.result}
              onChange={(event) =>
                updateSelectedCase((item) => ({
                  ...item,
                  result: event.target.value,
                }))
              }
              placeholder="Ответ появится после обработки"
            />
            <div className="action-row">
              <button className="secondary-button" onClick={copyResult} type="button" disabled={!selectedCase.result}>
                <Copy size={16} aria-hidden="true" />
                Копировать
              </button>
              <button className="primary-button" onClick={generateResult} type="button">
                <CheckCircle2 size={16} aria-hidden="true" />
                Завершить
              </button>
            </div>
          </section>
        </main>

        <aside className="inspector-panel" aria-label="Контроль обработки">
          <section>
            <div className="panel-heading">
              <AlertTriangle size={18} aria-hidden="true" />
              <span>Контроль</span>
            </div>
            <div className="control-list">
              <div>
                <span>Маршрутизация</span>
                <strong>{serviceLabel[selectedCase.identifiers.service]}</strong>
              </div>
              <div>
                <span>Уверенность</span>
                <strong>{selectedCase.identifiers.confidence}%</strong>
              </div>
              <div>
                <span>Канал</span>
                <strong>{selectedCase.channel}</strong>
              </div>
              <div>
                <span>Партнер</span>
                <strong>{selectedCase.partner}</strong>
              </div>
            </div>
          </section>

          <section>
            <div className="panel-heading">
              <Clock3 size={18} aria-hidden="true" />
              <span>Журнал</span>
            </div>
            <ol className="timeline">
              {selectedCase.timeline.map((event) => (
                <li className={`timeline__item timeline__item--${event.status}`} key={event.id}>
                  <time>{event.time}</time>
                  <strong>{event.title}</strong>
                  <span>{event.detail}</span>
                </li>
              ))}
            </ol>
          </section>
        </aside>
      </div>
    </div>
  );
}

export default App;
