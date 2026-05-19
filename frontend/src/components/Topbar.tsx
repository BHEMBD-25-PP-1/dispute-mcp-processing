import { LogOut } from 'lucide-react';
import { getQueueSummary } from '../features/disputes/queue';
import type { DisputeCase, Operator } from '../types';

type TopbarProps = {
  cases: DisputeCase[];
  operator: Operator;
  onLogout: () => void;
};

export function Topbar({ cases, operator, onLogout }: TopbarProps) {
  const queueSummary = getQueueSummary(cases);

  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Dispute MCP Ops</p>
        <h1>Рабочее место операциониста</h1>
      </div>

      <div className="topbar__right">
        <div className="metrics-strip" aria-label="Сводка очереди">
          <div className="metric">
            <span>{queueSummary.active}</span>
            <small>активно</small>
          </div>
          <div className="metric metric--amber">
            <span>{queueSummary.attention}</span>
            <small>ручная проверка</small>
          </div>
          <div className="metric metric--green">
            <span>{queueSummary.resolved}</span>
            <small>готово</small>
          </div>
        </div>

        <div className="operator-card">
          <div>
            <strong>{operator.name}</strong>
            <span>{operator.role}</span>
          </div>
          <button className="icon-button" onClick={onLogout} type="button" aria-label="Выйти">
            <LogOut size={16} aria-hidden="true" />
          </button>
        </div>
      </div>
    </header>
  );
}
