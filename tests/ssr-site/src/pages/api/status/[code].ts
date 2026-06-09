import type { APIRoute } from 'astro';
import { json } from '../../../lib/http';

export const prerender = false;

export const ALL: APIRoute = ({ params, request }) => {
  const code = Number(params.code || 200);
  const status = Number.isInteger(code) && code >= 100 && code <= 599 ? code : 400;
  return json({
    ok: status >= 200 && status < 400,
    status,
    method: request.method,
    path: new URL(request.url).pathname,
  }, { status });
};
