import type { APIRoute } from 'astro';
import { boundedDelay, json, sleep } from '../../../lib/http';
import { searchMarketplaceItems, marketplaceSummary } from '../../../lib/marketplace';
import type { MarketplaceCategory, MarketplaceSort } from '../../../lib/marketplace';

export const GET: APIRoute = async ({ request, url }) => {
  const query = url.searchParams.get('query') || url.searchParams.get('q') || '';
  const category = (url.searchParams.get('category') || 'all') as MarketplaceCategory | 'all';
  const sort = (url.searchParams.get('sort') || 'relevance') as MarketplaceSort;
  const count = Math.min(Math.max(Number(url.searchParams.get('count') || 12), 1), 60);
  const offset = Math.max(Number(url.searchParams.get('offset') || 0), 0);
  const delay = boundedDelay(url.searchParams.get('delay'), 20, 1000);
  await sleep(delay);
  const items = searchMarketplaceItems({ query, category, sort, count, offset });
  return json({
    ok: true,
    method: request.method,
    query,
    category,
    sort,
    count: items.length,
    offset,
    nextOffset: offset + items.length,
    summary: marketplaceSummary(),
    items,
    generatedAt: new Date().toISOString(),
  });
};
