import { useState } from 'react';
import { CaseBoard } from './components/CaseBoard';
import { InspectorPanel } from './components/InspectorPanel';
import { LoginView } from './components/LoginView';
import { QueuePanel } from './components/QueuePanel';
import { Topbar } from './components/Topbar';
import { generateCaseResult, parseCase, runCaseMcp } from './features/disputes/api';
import { useOperatorWorkspace } from './features/workspace/useOperatorWorkspace';
import type { Operator } from './types';

function App() {
  const [operator, setOperator] = useState<Operator | null>(null);
  const workspace = useOperatorWorkspace(operator);

  if (!operator) {
    return <LoginView onLogin={setOperator} />;
  }

  if (workspace.isLoading || !workspace.selectedCase) {
    return (
      <div className="app-shell">
        <Topbar cases={workspace.cases} operator={operator} onLogout={() => setOperator(null)} />
        <p className="empty-queue">{workspace.isLoading ? 'Загружаем очередь...' : 'Нет доступных кейсов'}</p>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Topbar cases={workspace.cases} operator={operator} onLogout={() => setOperator(null)} />
      {workspace.error ? <p className="form-error">{workspace.error}</p> : null}

      <div className="workspace">
        <QueuePanel
          cases={workspace.cases}
          selectedId={workspace.selectedCase.id}
          onSelect={workspace.selectCase}
        />
        <CaseBoard
          selectedCase={workspace.selectedCase}
          draftMessage={workspace.draftMessage}
          parsedPreview={workspace.parsedPreview}
          onDraftChange={workspace.setDraftMessage}
          onResetDraft={() => workspace.setDraftMessage(workspace.selectedCase.message)}
          onParse={() => workspace.runCaseAction(parseCase)}
          onRunMcp={() => workspace.runCaseAction(runCaseMcp)}
          onGenerateResult={() => workspace.runCaseAction(generateCaseResult)}
          onCopyResult={workspace.copyResult}
          onResultChange={workspace.updateResult}
        />
        <InspectorPanel selectedCase={workspace.selectedCase} />
      </div>
    </div>
  );
}

export default App;
