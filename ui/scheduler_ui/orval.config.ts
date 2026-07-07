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
      target: "./src/api/client",
      schemas: "./src/api/models",
      baseUrl: {
        runtime: "process.env.NEXT_PUBLIC_V1_API_BASE_URL",
      },
      mock: true,
    },
  },
});
