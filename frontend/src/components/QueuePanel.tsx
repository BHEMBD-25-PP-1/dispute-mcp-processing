import { Inbox } from 'lucide-react';
import { statusLabel } from '../constants';
import type { DisputeCase } from '../types';

type QueuePanelProps = {
  cases: DisputeCase[];
  selectedId: string;
  onSelect: (caseId: string) => void;
};

const getCaseTone = (status: DisputeCase['status']) => `case-row case-row--${status}`;

export function QueuePanel({ cases, selectedId, onSelect }: QueuePanelProps) {
  return (
    <aside className="queue-panel" aria-label="Очередь диспутов">
      <div className="panel-heading">
        <Inbox size={18} aria-hidden="true" />
        <span>Очередь</span>
      </div>

      <div className="case-list">
        {cases.map((item) => (
          <button
            className={`${getCaseTone(item.status)} ${item.id === selectedId ? 'is-selected' : ''}`}
            key={item.id}
            onClick={() => onSelect(item.id)}
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
  );
}
