import type { APIRoute } from 'astro';
import { makeProducts } from '../../../lib/products';
import { boundedDelay, json, sleep } from '../../../lib/http';

export const GET: APIRoute = async ({ url }) => {
  const seed = Math.max(Number(url.searchParams.get('seed') || 1), 1);
  const count = Math.min(Math.max(Number(url.searchParams.get('count') || 4), 1), 12);
  const delay = boundedDelay(url.searchParams.get('delay'), 15, 1000);
  await sleep(delay);
  const offset = (seed % 10) * 10;
  return json({ ok: true, seed, count, items: makeProducts(count, offset) });
};
