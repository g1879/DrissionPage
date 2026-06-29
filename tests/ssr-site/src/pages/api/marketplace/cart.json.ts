import type { APIRoute } from 'astro';
import { json } from '../../../lib/http';
import { makeMarketplaceItem } from '../../../lib/marketplace';

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
  const id = Math.max(Number(body.id || 1), 1);
  const quantity = Math.min(Math.max(Number(body.quantity || 1), 1), 99);
  const color = String(body.color || '奶油白');
  const spec = String(body.spec || '标准款');
  const item = makeMarketplaceItem(id);
  const subtotal = Number((item.price * quantity).toFixed(2));
  cookies.set('marketplace_cart_count', String(quantity), { path: '/', sameSite: 'lax', httpOnly: false });
  cookies.set('marketplace_cart_item_id', String(item.id), { path: '/', sameSite: 'lax', httpOnly: false });
  cookies.set('marketplace_cart_color', color, { path: '/', sameSite: 'lax', httpOnly: false });
  cookies.set('marketplace_cart_spec', spec, { path: '/', sameSite: 'lax', httpOnly: false });

  return json({
    ok: true,
    cartCount: quantity,
    line: {
      id: item.id,
      title: item.title,
      shop: item.shop,
      color,
      spec,
      quantity,
      unitPrice: item.price,
      subtotal,
    },
  });
};
