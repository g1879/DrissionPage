export type ActivityStatus = 'active' | 'pending' | 'blocked';
export type ActivityPriority = 'low' | 'medium' | 'high';

export interface Activity {
  id: number;
  title: string;
  status: ActivityStatus;
  priority: ActivityPriority;
  owner: string;
  amount: number;
}

export type ActivitySummary = Record<ActivityStatus, number>;

export function makeActivity(id: number): Activity {
  const status: ActivityStatus = id % 10 === 0 ? 'blocked' : id % 4 === 0 ? 'pending' : 'active';
  const priority: ActivityPriority = id % 9 === 0 ? 'high' : id % 3 === 0 ? 'medium' : 'low';
  return {
    id,
    title: `Activity ${String(id).padStart(3, '0')}`,
    status,
    priority,
    owner: `team-${(id % 5) + 1}`,
    amount: 1000 + id * 13,
  };
}

export function makeActivities(count: number, offset = 0): Activity[] {
  return Array.from({ length: count }, (_, index) => makeActivity(offset + index + 1));
}

export function summarizeActivities(items: Activity[]): ActivitySummary {
  return items.reduce<ActivitySummary>((acc, item) => {
    acc[item.status] += 1;
    return acc;
  }, { active: 0, pending: 0, blocked: 0 });
}
