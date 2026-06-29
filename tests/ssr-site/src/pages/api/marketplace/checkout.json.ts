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

export const POST: APIRoute = async ({ cookies, request }) => {
  const body = await readBody(request);
  const addressId = String(body.addressId || 'addr-hangzhou');
  const payment = String(body.payment || 'mock-alipay');
  const invoice = String(body.invoice || 'personal');
  const itemCount = Number(body.itemCount || 1);
  const total = Number(body.total || 0);
  const orderId = `TBMOCK-${String(addressId.length + payment.length + invoice.length + itemCount * 31).padStart(6, '0')}`;
  cookies.set('marketplace_last_order', orderId, { path: '/', sameSite: 'lax', httpOnly: false });

  return json({
    ok: true,
    orderId,
    status: 'created',
    payment,
    invoice,
    addressId,
    itemCount,
    total,
    nextUrl: `/scenarios/marketplace/order-result?order=${encodeURIComponent(orderId)}`,
  });
};
