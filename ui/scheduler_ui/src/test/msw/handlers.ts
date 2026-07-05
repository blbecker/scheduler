import { getScheduleSolvesMock } from "@/api/client/schedule-solves/schedule-solves.msw";

// add more as generated:
// import { getWorkersMock } from "@/api/client/workers.msw";

export const handlers = [
  ...getScheduleSolvesMock(),
  // ...getWorkersMock(),
];
