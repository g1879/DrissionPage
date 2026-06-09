import type { APIRoute } from 'astro';
import { json } from '../../../lib/http';

export const GET: APIRoute = ({ cookies }) => {
  cookies.set('cf_clearance', 'fixture-pass', {
    path: '/',
    sameSite: 'lax',
    httpOnly: false,
    maxAge: 30 * 60,
  });
  return json({
    ok: true,
    provider: 'cloudflare-fixture',
    clearance: 'issued',
    challenge: 'managed',
    rayId: '79f4c2d4b8b9dp01-SJC',
  }, {
    headers: {
      'cf-ray': '79f4c2d4b8b9dp01-SJC',
      'server': 'cloudflare-fixture',
    },
  });
};
