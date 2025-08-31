import { defineConfig } from 'orval';

export default defineConfig({
  scheduler_api: {
    input: { target: './openapi.json' },

    output: {
      mode: 'tags-split',
      target: 'src/scheduler_api.ts',
      schemas: 'src/models',
      client: 'vue-query',
      baseUrl: 'https://localhost:8000',
      mock: true,
    },

    hooks: {
      afterAllFilesWrite: 'prettier --write',
    },
  },
});
