// scheduler-ui/orval.config.ts
import { defineConfig } from "orval";

export default defineConfig({
  scheduler: {
    input: {
      target: "http://localhost:8000/api/v1/openapi.json",
    },
    baseUrl: {
      runtime: "process.env.API_BASE_URL",
    },
    output: {
      mode: "tags-split",
      client: "vue-query",
      target: "./src/api/generated",
      schemas: "./src/api/models",
    },
  },
});
