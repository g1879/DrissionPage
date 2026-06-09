import type { APIRoute } from 'astro';
import { boundedDelay, sleep } from '../../lib/http';

export const GET: APIRoute = async ({ url }) => {
  const count = Math.min(Number(url.searchParams.get('count') || 3), 10);
  const interval = boundedDelay(url.searchParams.get('interval'), 100, 1000);
  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      for (let i = 1; i <= count; i += 1) {
        controller.enqueue(encoder.encode(`id: ${i}\nevent: check\ndata: {"index":${i},"source":"astro-ssr"}\n\n`));
        await sleep(interval);
      }
      controller.enqueue(encoder.encode('event: done\ndata: complete\n\n'));
      controller.close();
    },
  });
  return new Response(stream, {
    headers: {
      'content-type': 'text/event-stream; charset=utf-8',
      'cache-control': 'no-cache, no-transform',
      connection: 'keep-alive',
    },
  });
};
