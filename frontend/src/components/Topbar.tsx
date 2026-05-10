import { LogOut } from 'lucide-react';
import type { DisputeCase, Operator } from '../types';

type TopbarProps = {
  cases: DisputeCase[];
  operator: Operator;
  onLogout: () => void;
};

export function Topbar({ cases, operator, onLogout }: TopbarProps) {
  const resolvedCount = cases.filter((item) => item.status === 'resolved').length;
  const attentionCount = cases.filter((item) => item.status === 'attention').length;

  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Dispute MCP Ops</p>
        <h1>Рабочее место операциониста</h1>
      </div>

      <div className="topbar__right">
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
