import type { APIRoute } from 'astro';
import { boundedDelay, json, sleep } from '../../../lib/http';
import { searchSocialNotes, socialChannels } from '../../../lib/socialNotes';
import type { SocialChannel } from '../../../lib/socialNotes';

export const GET: APIRoute = async ({ request, url }) => {
  const query = url.searchParams.get('query') || url.searchParams.get('q') || '';
  const channel = (url.searchParams.get('channel') || 'recommend') as SocialChannel | 'all';
  const count = Math.min(Math.max(Number(url.searchParams.get('count') || 16), 1), 48);
  const offset = Math.max(Number(url.searchParams.get('offset') || 0), 0);
  const delay = boundedDelay(url.searchParams.get('delay'), 20, 1000);
  await sleep(delay);
  const items = searchSocialNotes({ query, channel, count, offset });
  return json({
    ok: true,
    method: request.method,
    query,
    channel,
    count: items.length,
    offset,
    nextOffset: offset + items.length,
    isOver: offset + items.length >= 160,
    filters: socialChannels,
    items,
    generatedAt: new Date().toISOString(),
  });
};
