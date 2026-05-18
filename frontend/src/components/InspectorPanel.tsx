import { AlertTriangle, Clock3 } from 'lucide-react';
import { serviceLabel } from '../constants';
import type { DisputeCase } from '../types';

type InspectorPanelProps = {
  selectedCase: DisputeCase;
};

export function InspectorPanel({ selectedCase }: InspectorPanelProps) {
  return (
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
  );
}
