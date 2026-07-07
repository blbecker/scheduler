import { getScheduleSolvesMock } from "@/api/client/schedule-solves/schedule-solves.msw";
import { getWorkersMock } from "@/api/client/workers/workers.msw";
import { getSkillsMock } from "@/api/client/skills/skills.msw";
import { getScheduleTemplatesMock } from "@/api/client/schedule-templates/schedule-templates.msw";
import { getShiftTemplatesMock } from "@/api/client/shift-templates/shift-templates.msw";
import { getSchedulesMock } from "@/api/client/schedules/schedules.msw";
import { getShiftsMock } from "@/api/client/shifts/shifts.msw";

export const handlers = [...getScheduleSolvesMock(), ...getWorkersMock(), ...getSkillsMock(), ...getScheduleTemplatesMock(), ...getShiftTemplatesMock(), ...getSchedulesMock(), ...getShiftsMock()];
