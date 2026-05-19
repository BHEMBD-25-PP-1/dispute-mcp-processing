import { useEffect, useMemo, useState } from 'react';
import {
  fetchCases,
  generateCaseResult,
  parseCase,
  runCaseMcp,
  updateCaseResult,
} from './api';
import { CaseBoard } from './components/CaseBoard';
import { InspectorPanel } from './components/InspectorPanel';
import { LoginView } from './components/LoginView';
import { QueuePanel } from './components/QueuePanel';
import { Topbar } from './components/Topbar';
import { pickVisibleCaseId } from './features/disputes/queue';
import type { DisputeCase, Operator } from './types';

function App() {
  const [operator, setOperator] = useState<Operator | null>(null);
  const [cases, setCases] = useState<DisputeCase[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [draftMessage, setDraftMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const selectedCase = useMemo(
    () => cases.find((item) => item.id === selectedId) ?? cases[0],
    [cases, selectedId],
  );

  const parsedPreview = selectedCase?.identifiers ?? { service: 'unknown' as const, confidence: 0 };

  useEffect(() => {
    if (!operator) {
      setCases([]);
      setSelectedId('');
      setDraftMessage('');
      return;
    }

    setIsLoading(true);
    setError('');
    fetchCases(operator.token)
      .then((nextCases) => {
        setCases(nextCases);
        const nextSelectedId = pickVisibleCaseId(nextCases, nextCases[0]?.id ?? '');
        const nextCase = nextCases.find((item) => item.id === nextSelectedId) ?? nextCases[0];
        setSelectedId(nextCase?.id ?? '');
        setDraftMessage(nextCase?.message ?? '');
      })
      .catch(() => setError('Не удалось загрузить очередь диспутов'))
      .finally(() => setIsLoading(false));
  }, [operator]);

  const applyCaseUpdate = (updatedCase: DisputeCase) => {
    setCases((current) => {
      const nextCases = current.map((item) => (item.id === updatedCase.id ? updatedCase : item));
      const nextSelectedId = pickVisibleCaseId(nextCases, updatedCase.id, updatedCase.id);
      if (nextSelectedId !== updatedCase.id) {
        const nextCase = nextCases.find((item) => item.id === nextSelectedId);
        setSelectedId(nextSelectedId);
        if (nextCase) {
          setDraftMessage(nextCase.message);
        }
      } else {
        setDraftMessage(updatedCase.message);
      }
      return nextCases;
    });
  };

  const selectCase = (caseId: string) => {
    const nextCase = cases.find((item) => item.id === caseId);
    if (!nextCase) {
      return;
    }

    setSelectedId(caseId);
    setDraftMessage(nextCase.message);
  };

  const runCaseAction = async (action: (token: string, caseId: string, message: string) => Promise<DisputeCase>) => {
    if (!operator || !selectedCase) {
      return;
    }

    setError('');
    try {
      applyCaseUpdate(await action(operator.token, selectedCase.id, draftMessage));
    } catch {
      setError('Backend не смог выполнить действие по кейсу');
    }
  };

  const copyResult = async () => {
    if (selectedCase?.result) {
      await navigator.clipboard?.writeText(selectedCase.result);
    }
  };

  if (!operator) {
    return <LoginView onLogin={setOperator} />;
  }

  if (isLoading || !selectedCase) {
    return (
      <div className="app-shell">
        <Topbar cases={cases} operator={operator} onLogout={() => setOperator(null)} />
        <p className="empty-queue">{isLoading ? 'Загружаем очередь...' : 'Нет доступных кейсов'}</p>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Topbar cases={cases} operator={operator} onLogout={() => setOperator(null)} />
      {error ? <p className="form-error">{error}</p> : null}

      <div className="workspace">
        <QueuePanel cases={cases} selectedId={selectedCase.id} onSelect={selectCase} />
        <CaseBoard
          selectedCase={selectedCase}
          draftMessage={draftMessage}
          parsedPreview={parsedPreview}
          onDraftChange={setDraftMessage}
          onResetDraft={() => setDraftMessage(selectedCase.message)}
          onParse={() => runCaseAction(parseCase)}
          onRunMcp={() => runCaseAction(runCaseMcp)}
          onGenerateResult={() => runCaseAction(generateCaseResult)}
          onCopyResult={copyResult}
          onResultChange={(result) => {
            if (!operator || !selectedCase) {
              return;
            }
            updateCaseResult(operator.token, selectedCase.id, result)
              .then(applyCaseUpdate)
              .catch(() => setError('Не удалось сохранить итоговый ответ'));
          }}
        />
        <InspectorPanel selectedCase={selectedCase} />
      </div>
    </div>
  );
}

export default App;
