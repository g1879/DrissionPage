import type { APIRoute } from 'astro';
import { json } from '../../lib/http';

export const GET: APIRoute = ({ request }) => json({
  ok: true,
  service: 'drissionpage-ssr-test-site',
  method: request.method,
  renderedAt: new Date().toISOString(),
});
