import type { APIRoute } from 'astro';
import { json } from '../../../lib/http';

const RAY = '79f4c2d4b8b9dp01-SJC';

function cfHeaders(extra: Record<string, string> = {}) {
  return {
    'cf-ray': RAY,
    'server': 'cloudflare-fixture',
    ...extra,
  };
}

export const GET: APIRoute = ({ cookies, request, url }) => {
  const mode = url.searchParams.get('mode') || 'protected';
  if (mode === 'blocked') {
    return json({
      ok: false,
      provider: 'cloudflare-fixture',
      code: 1020,
      reason: 'access_denied',
      rayId: RAY,
      message: 'Synthetic WAF block page fixture.',
    }, { status: 403, headers: cfHeaders() });
  }
  if (mode === 'rate-limit') {
    return json({
      ok: false,
      provider: 'cloudflare-fixture',
      code: 1015,
      reason: 'rate_limited',
      rayId: RAY,
      retryAfter: 3,
    }, { status: 429, headers: cfHeaders({ 'retry-after': '3' }) });
  }

  const clearance = cookies.get('cf_clearance')?.value || '';
  if (clearance !== 'fixture-pass') {
    return json({
      ok: false,
      provider: 'cloudflare-fixture',
      code: 'managed_challenge',
      reason: 'challenge_required',
      rayId: RAY,
      userAgent: request.headers.get('user-agent'),
    }, { status: 403, headers: cfHeaders() });
  }

  return json({
    ok: true,
    provider: 'cloudflare-fixture',
    clearance: 'accepted',
    rayId: RAY,
    payload: { account: 'fixture-account', records: 3 },
  }, { headers: cfHeaders() });
};
