import type { APIRoute } from 'astro';

export const GET: APIRoute = ({ url }) => {
  const name = url.searchParams.get('name') || 'dp-fixture.txt';
  const body = `DrissionPage download fixture\nname=${name}\n`;
  return new Response(body, {
    headers: {
      'content-type': 'text/plain; charset=utf-8',
      'content-disposition': `attachment; filename="${name.replace(/[^a-zA-Z0-9._-]/g, '_')}"`,
      'cache-control': 'no-store',
    },
  });
};
