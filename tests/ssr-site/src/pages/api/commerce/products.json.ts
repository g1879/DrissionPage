import type { APIRoute } from 'astro';
import { makeProducts, summarizeProducts } from '../../../lib/products';
import { boundedDelay, json, sleep } from '../../../lib/http';

export const GET: APIRoute = async ({ request, url }) => {
  const count = Math.min(Math.max(Number(url.searchParams.get('count') || 20), 1), 100);
  const offset = Math.max(Number(url.searchParams.get('offset') || 0), 0);
  const delay = boundedDelay(url.searchParams.get('delay'), 20, 1000);
  await sleep(delay);
  const items = makeProducts(count, offset);

  return json({
    ok: true,
    method: request.method,
    count: items.length,
    offset,
    nextOffset: offset + items.length,
    summary: summarizeProducts(items),
    items,
    generatedAt: new Date().toISOString(),
  });
};
