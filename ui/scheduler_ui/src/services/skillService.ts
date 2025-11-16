import { SkillsClient } from 'src/clients/skills/skills';

import type { SkillRead, SkillUpdate, SkillCreate } from 'src/models/skill';

export const SkillsService = {
  async getSkills(): Promise<SkillRead[]> {
    return await SkillsClient.list();
  },

  async getSkill(id: string): Promise<SkillRead> {
    return await SkillsClient.get(id);
  },

  async createSkill(payload: SkillCreate): Promise<SkillRead> {
    return await SkillsClient.create(payload);
  },

  async updateSkill(id: string, payload: SkillUpdate): Promise<SkillRead> {
    return await SkillsClient.update(id, payload);
  },

  async deleteSkill(id: string): Promise<void> {
    return await SkillsClient.delete(id);
  },
};
