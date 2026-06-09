import type { APIRoute } from 'astro';
import { boundedDelay, json, sleep } from '../../lib/http';

export const GET: APIRoute = async ({ url }) => {
  const delay = boundedDelay(url.searchParams.get('delay'));
  await sleep(delay);
  return json({ ok: true, delay, renderedAt: new Date().toISOString() });
};
