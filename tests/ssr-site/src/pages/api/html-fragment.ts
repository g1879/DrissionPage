import type { APIRoute } from 'astro';
import { html } from '../../lib/http';

export const GET: APIRoute = () => html('<section id="fragment" data-testid="html-fragment"><h1>HTML fragment</h1></section>');
