import "@testing-library/jest-dom";
import { afterAll, afterEach, beforeAll } from "vitest";
import { server } from "@/test/msw/server";

// Start MSW before any tests run
beforeAll(() => {
  server.listen({
    onUnhandledRequest: "error",
  });
});

// Reset handlers between tests (prevents cross-test leakage)
afterEach(() => {
  server.resetHandlers();
});

// Shutdown MSW
afterAll(() => {
  server.close();
});
