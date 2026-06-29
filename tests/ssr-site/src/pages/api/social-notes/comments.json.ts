import type { APIRoute } from 'astro';
import { json } from '../../../lib/http';
import { makeSocialComments } from '../../../lib/socialNotes';

async function readBody(request: Request): Promise<Record<string, unknown>> {
  try {
    const body = await request.json();
    return typeof body === 'object' && body !== null ? body as Record<string, unknown> : {};
  } catch {
    return {};
  }
}

export const GET: APIRoute = ({ url }) => {
  const noteId = url.searchParams.get('noteId') || 'note-001';
  return json({ ok: true, noteId, comments: makeSocialComments(noteId), generatedAt: new Date().toISOString() });
};

export const POST: APIRoute = async ({ request }) => {
  const body = await readBody(request);
  const noteId = String(body.noteId || 'note-001');
  const text = String(body.text || '').trim() || '合成评论';
  return json({
    ok: true,
    noteId,
    comment: {
      id: `${noteId}-comment-new`,
      author: '自动化用户',
      text,
      likes: 0,
    },
    total: makeSocialComments(noteId).length + 1,
  });
};
