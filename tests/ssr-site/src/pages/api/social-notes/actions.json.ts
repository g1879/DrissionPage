import type { APIRoute } from 'astro';
import { json } from '../../../lib/http';
import { getSocialNote } from '../../../lib/socialNotes';
import type { SocialAction } from '../../../lib/socialNotes';

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
  const noteId = String(body.noteId || 'note-001');
  const action = String(body.action || 'like') as SocialAction;
  const enabled = body.enabled !== false;
  const note = getSocialNote(noteId);
  return json({
    ok: true,
    noteId,
    action,
    enabled,
    counts: {
      likes: note.likes + (action === 'like' && enabled ? 1 : 0),
      collects: note.collects + (action === 'collect' && enabled ? 1 : 0),
      comments: note.comments,
    },
    state: {
      liked: action === 'like' ? enabled : false,
      collected: action === 'collect' ? enabled : false,
      followed: action === 'follow' ? enabled : false,
      shared: action === 'share' ? enabled : false,
    },
  });
};
