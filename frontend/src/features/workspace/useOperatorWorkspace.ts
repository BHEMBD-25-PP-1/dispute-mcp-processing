import { useEffect, useMemo, useState } from 'react';
import type { CaseAction } from '../disputes/api';
import { fetchCases, updateCaseResult } from '../disputes/api';
import { pickVisibleCaseId } from '../disputes/queue';
import { mergeTimeline } from '../disputes/timeline';
import type { DisputeCase, Operator } from '../../types';

const emptyIdentifiers = { service: 'unknown' as const, confidence: 0 };

export const useOperatorWorkspace = (operator: Operator | null) => {
  const [cases, setCases] = useState<DisputeCase[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [draftMessage, setDraftMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const selectedCase = useMemo(
    () => cases.find((item) => item.id === selectedId) ?? cases[0],
    [cases, selectedId],
  );

  const parsedPreview = selectedCase?.identifiers ?? emptyIdentifiers;

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
        selectInitialCase(nextCases);
      })
      .catch(() => setError('Не удалось загрузить очередь диспутов'))
      .finally(() => setIsLoading(false));
  }, [operator]);

  const selectInitialCase = (nextCases: DisputeCase[]) => {
    const nextSelectedId = pickVisibleCaseId(nextCases, nextCases[0]?.id ?? '');
    const nextCase = nextCases.find((item) => item.id === nextSelectedId) ?? nextCases[0];
    setSelectedId(nextCase?.id ?? '');
    setDraftMessage(nextCase?.message ?? '');
  };

  const applyCaseUpdate = (updatedCase: DisputeCase) => {
    setCases((current) => {
      const nextCases = current.map((item) =>
        item.id === updatedCase.id
          ? {
              ...updatedCase,
              timeline: mergeTimeline(item.timeline, updatedCase.timeline),
            }
          : item,
      );
      syncSelectedCase(nextCases, updatedCase);
      return nextCases;
    });
  };

  const syncSelectedCase = (nextCases: DisputeCase[], updatedCase: DisputeCase) => {
    const nextSelectedId = pickVisibleCaseId(nextCases, updatedCase.id, updatedCase.id);
    if (nextSelectedId !== updatedCase.id) {
      const nextCase = nextCases.find((item) => item.id === nextSelectedId);
      setSelectedId(nextSelectedId);
      setDraftMessage(nextCase?.message ?? '');
      return;
    }

    setDraftMessage(updatedCase.message);
  };

  const selectCase = (caseId: string) => {
    const nextCase = cases.find((item) => item.id === caseId);
    if (!nextCase) {
      return;
    }

    setSelectedId(caseId);
    setDraftMessage(nextCase.message);
  };

  const runCaseAction = async (action: CaseAction) => {
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

  const updateResult = (result: string) => {
    if (!operator || !selectedCase) {
      return;
    }

    updateCaseResult(operator.token, selectedCase.id, result)
      .then(applyCaseUpdate)
      .catch(() => setError('Не удалось сохранить итоговый ответ'));
  };

  const copyResult = async () => {
    if (selectedCase?.result) {
      await navigator.clipboard?.writeText(selectedCase.result);
    }
  };

  return {
    cases,
    selectedCase,
    draftMessage,
    parsedPreview,
    error,
    isLoading,
    setDraftMessage,
    selectCase,
    runCaseAction,
    updateResult,
    copyResult,
  };
};
