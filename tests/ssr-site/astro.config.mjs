import { defineConfig } from 'astro/config';
import vercel from '@astrojs/vercel';

export default defineConfig({
  output: 'server',
  adapter: vercel({
    maxDuration: 10,
  }),
  server: {
    host: '127.0.0.1',
    port: 4321,
  },
});
