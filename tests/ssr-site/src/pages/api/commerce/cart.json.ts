import type { APIRoute } from 'astro';
import { makeProduct } from '../../../lib/products';
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
  const id = Math.max(Number(body.id || 1), 1);
  const quantity = Math.min(Math.max(Number(body.quantity || 1), 1), 9);
  const variant = String(body.variant || 'standard');
  const product = makeProduct(id);
  const subtotal = Number((product.price * quantity).toFixed(2));

  return json({
    ok: true,
    line: {
      id: product.id,
      sku: product.sku,
      title: product.title,
      category: product.category,
      variant,
      quantity,
      unitPrice: product.price,
      subtotal,
    },
  });
};
