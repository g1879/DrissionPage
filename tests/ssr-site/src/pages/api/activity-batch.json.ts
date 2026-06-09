import type { APIRoute } from 'astro';
import { makeActivities } from '../../lib/activities';
import { boundedDelay, json, sleep } from '../../lib/http';

export const GET: APIRoute = async ({ request, url }) => {
  const count = Math.min(Math.max(Number(url.searchParams.get('count') || 8), 1), 50);
  const offset = Math.max(Number(url.searchParams.get('offset') || 0), 0);
  const delay = boundedDelay(url.searchParams.get('delay'), 25, 1000);
  await sleep(delay);

  const items = makeActivities(count, offset);

  return json({
    ok: true,
    method: request.method,
    count: items.length,
    offset,
    nextOffset: offset + items.length,
    items,
    generatedAt: new Date().toISOString(),
  });
};
