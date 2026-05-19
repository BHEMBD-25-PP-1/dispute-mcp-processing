import type { DisputeCase } from '../../types';

const ACTIVE_STATUSES: Array<DisputeCase['status']> = ['new', 'processing', 'attention'];

export const getActiveQueueCases = (cases: DisputeCase[]) =>
  cases.filter((item) => ACTIVE_STATUSES.includes(item.status));

export const getQueueSummary = (cases: DisputeCase[]) => ({
  active: getActiveQueueCases(cases).length,
  attention: cases.filter((item) => item.status === 'attention').length,
  resolved: cases.filter((item) => item.status === 'resolved').length,
});

export const pickVisibleCaseId = (
  cases: DisputeCase[],
  currentId: string,
  fallbackId?: string,
) => {
  const activeCases = getActiveQueueCases(cases);
  if (activeCases.some((item) => item.id === currentId)) {
    return currentId;
  }
  return activeCases[0]?.id ?? fallbackId ?? cases[0]?.id;
};
