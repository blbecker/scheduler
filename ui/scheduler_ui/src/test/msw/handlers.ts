import { getScheduleSolvesMock } from "@/api/client/schedule-solves/schedule-solves.msw";
import { getWorkersMock } from "@/api/client/workers/workers.msw";

export const handlers = [
  ...getScheduleSolvesMock(),
  ...getWorkersMock(),
];
