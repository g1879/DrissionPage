import type { APIRoute } from 'astro';
import { json } from '../../lib/http';

async function readBody(request: Request): Promise<unknown> {
  const type = request.headers.get('content-type') || '';
  if (type.includes('application/json')) {
    try {
      return await request.json();
    } catch {
      return null;
    }
  }
  if (type.includes('application/x-www-form-urlencoded') || type.includes('multipart/form-data')) {
    return Object.fromEntries(await request.formData());
  }
  const text = await request.text();
  return text || null;
}

const respond: APIRoute = async ({ request, url }) => json({
  ok: true,
  method: request.method,
  query: Object.fromEntries(url.searchParams),
  headers: {
    'x-dp-test': request.headers.get('x-dp-test'),
    'content-type': request.headers.get('content-type'),
  },
  body: request.method === 'GET' || request.method === 'HEAD' ? null : await readBody(request),
});

export const GET = respond;
export const POST = respond;
export const PUT = respond;
export const PATCH = respond;
export const DELETE = respond;
