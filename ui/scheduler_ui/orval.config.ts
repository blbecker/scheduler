// scheduler-ui/orval.config.ts
import { defineConfig } from "orval";

export default defineConfig({
  scheduler: {
    input: {
      target: "http://localhost:8000/api/v1/openapi.json",
    },
    output: {
      mode: "tags-split",
      client: "react-query",
      target: "./src/api/generated",
      schemas: "./src/api/models",
      baseUrl: "process.env.API_BASE_URL",
      mock: true,
    },
  },
});
