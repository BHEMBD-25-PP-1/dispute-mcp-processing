import { useMemo, useState } from 'react';
import { CaseBoard } from './components/CaseBoard';
import { InspectorPanel } from './components/InspectorPanel';
import { LoginView } from './components/LoginView';
import { QueuePanel } from './components/QueuePanel';
import { Topbar } from './components/Topbar';
import { serviceLabel } from './constants';
import { createConnectors, mockDisputes } from './data/mockDisputes';
import { getNextConnectors, formatNow } from './lib/caseProcessing';
import { buildOperatorAnswer, parseIncomingMessage } from './lib/parser';
import type { DisputeCase, Operator } from './types';

function App() {
  const [operator, setOperator] = useState<Operator | null>(null);
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
      const connectors = item.connectors.length ? item.connectors : createConnectors();

      return {
        ...item,
        status: parsed.service === 'unknown' ? 'attention' : 'processing',
        message: draftMessage,
        identifiers: parsed,
        connectors: getNextConnectors(connectors, parsed),
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
    if (selectedCase.result) {
      await navigator.clipboard?.writeText(selectedCase.result);
    }
  };

  if (!operator) {
    return <LoginView onLogin={setOperator} />;
  }

  return (
    <div className="app-shell">
      <Topbar cases={cases} operator={operator} onLogout={() => setOperator(null)} />

      <div className="workspace">
        <QueuePanel cases={cases} selectedId={selectedCase.id} onSelect={selectCase} />
        <CaseBoard
          selectedCase={selectedCase}
          draftMessage={draftMessage}
          parsedPreview={parsedPreview}
          onDraftChange={setDraftMessage}
          onResetDraft={() => setDraftMessage(selectedCase.message)}
          onParse={applyParsing}
          onRunMcp={runMcp}
          onGenerateResult={generateResult}
          onCopyResult={copyResult}
          onResultChange={(result) => updateSelectedCase((item) => ({ ...item, result }))}
        />
        <InspectorPanel selectedCase={selectedCase} />
      </div>
    </div>
  );
}

export default App;
