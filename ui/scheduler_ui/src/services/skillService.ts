import { SkillsClient } from 'src/clients/skills/skills';

import type { Skill } from 'src/models/skill';

export const SkillsService = {
  async getSkills(): Promise<Skill[]> {
    return await SkillsClient.list();
  },

  async getSkill(id: string): Promise<Skill> {
    return await SkillsClient.get(id);
  },

  // async createSkill(payload: Omit<Skill, 'id'>): Promise<Skill> {
  //   return await SkillsClient.create(payload);
  // }

  // async updateSkill(id: string, payload: Partial<Skill>): Promise<Skill> {
  //   return await SkillsClient.update(id, payload as Skill);
  // }

  async deleteSkill(id: string): Promise<void> {
    return await SkillsClient.delete(id);
  },
};
