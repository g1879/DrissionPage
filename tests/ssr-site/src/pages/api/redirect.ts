import type { APIRoute } from 'astro';

export const GET: APIRoute = ({ url }) => {
  const to = url.searchParams.get('to') || '/';
  const status = Number(url.searchParams.get('status') || 302);
  return new Response(null, {
    status: Number.isInteger(status) && status >= 300 && status <= 399 ? status : 302,
    headers: {
      location: to,
      'cache-control': 'no-store',
    },
  });
};
