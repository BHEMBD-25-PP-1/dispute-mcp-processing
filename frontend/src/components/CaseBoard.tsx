import {
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  Copy,
  FileSearch,
  MessageSquareText,
  Play,
  RefreshCw,
  Route,
  Send,
  ShieldCheck,
  Ticket,
} from 'lucide-react';
import { connectorStatusLabel, serviceLabel, statusLabel } from '../constants';
import type { DisputeCase, ParsedIdentifiers } from '../types';

type CaseBoardProps = {
  selectedCase: DisputeCase;
  draftMessage: string;
  parsedPreview: ParsedIdentifiers;
  onDraftChange: (value: string) => void;
  onResetDraft: () => void;
  onParse: () => void;
  onRunMcp: () => void;
  onGenerateResult: () => void;
  onCopyResult: () => void;
  onResultChange: (value: string) => void;
};

export function CaseBoard({
  selectedCase,
  draftMessage,
  parsedPreview,
  onDraftChange,
  onResetDraft,
  onParse,
  onRunMcp,
  onGenerateResult,
  onCopyResult,
  onResultChange,
}: CaseBoardProps) {
  return (
    <main className="case-board">
      <section className="case-header">
        <div>
          <span className={`status-pill status-pill--${selectedCase.status}`}>{statusLabel[selectedCase.status]}</span>
          <h2>{selectedCase.title}</h2>
          <p>
            {selectedCase.partner} · {selectedCase.customerName} · {selectedCase.amount}
          </p>
        </div>
        <button className="ghost-button" type="button" onClick={onResetDraft}>
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
          onChange={(event) => onDraftChange(event.target.value)}
        />
        <div className="action-row">
          <button className="primary-button" onClick={onParse} type="button">
            <FileSearch size={16} aria-hidden="true" />
            Распарсить
          </button>
          <button className="secondary-button" onClick={onRunMcp} type="button">
            <Play size={16} aria-hidden="true" />
            Запросить MCP
          </button>
          <button className="secondary-button" onClick={onGenerateResult} type="button">
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
          onChange={(event) => onResultChange(event.target.value)}
          placeholder="Ответ появится после обработки"
        />
        <div className="action-row">
          <button className="secondary-button" onClick={onCopyResult} type="button" disabled={!selectedCase.result}>
            <Copy size={16} aria-hidden="true" />
            Копировать
          </button>
          <button className="primary-button" onClick={onGenerateResult} type="button">
            <CheckCircle2 size={16} aria-hidden="true" />
            Завершить
          </button>
        </div>
      </section>
    </main>
  );
}
