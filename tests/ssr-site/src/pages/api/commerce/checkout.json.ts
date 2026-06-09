import type { APIRoute } from 'astro';
import { json } from '../../../lib/http';

async function readBody(request: Request): Promise<Record<string, unknown>> {
  try {
    const body = await request.json();
    return typeof body === 'object' && body !== null ? body as Record<string, unknown> : {};
  } catch {
    return {};
  }
}

export const POST: APIRoute = async ({ request }) => {
  const body = await readBody(request);
  const email = String(body.email || 'missing@example.test');
  const items = Array.isArray(body.items) ? body.items : [];
  const orderId = `ORDER-${String(email.length + items.length * 17).padStart(4, '0')}`;

  return json({
    ok: true,
    orderId,
    email,
    itemCount: items.length,
    status: 'reserved',
    nextAction: 'confirm-payment',
  });
};
