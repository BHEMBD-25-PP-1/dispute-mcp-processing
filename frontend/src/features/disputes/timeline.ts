import type { TimelineEvent } from '../../types';

export const mergeTimeline = (current: TimelineEvent[], next: TimelineEvent[]) => {
  const merged = [...current];

  next.forEach((event) => {
    const exists = merged.some(
      (item) => item.title === event.title && item.detail === event.detail && item.status === event.status,
    );
    if (!exists) {
      merged.push({ ...event, id: `evt-${merged.length + 1}` });
    }
  });

  return merged;
};
