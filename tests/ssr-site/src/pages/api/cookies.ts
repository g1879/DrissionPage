import type { APIRoute } from 'astro';
import { json } from '../../lib/http';

export const GET: APIRoute = ({ cookies }) => {
  cookies.set('dp_session', 'server-cookie', {
    path: '/',
    sameSite: 'lax',
    httpOnly: false,
  });
  return json({ ok: true, cookie: 'dp_session=server-cookie' });
};
