import { getSkills as clientGetSkills, createSkill as clientCreateSkill, updateSkill as clientUpdateSkill, deleteSkill as clientDeleteSkill } from '../clients/skillClient';

export interface Skill {
  id: number;
  name: string;
}

export async function getSkills(): Promise<Skill[]> {
  const response = await clientGetSkills();
  return response.data;
}

export async function createSkill(payload: Omit<Skill, 'id'>): Promise<Skill> {
  const response = await clientCreateSkill(payload);
  return response.data;
}

export async function updateSkill(skillId: number, payload: Partial<Skill>): Promise<Skill> {
  const response = await clientUpdateSkill(skillId, payload);
  return response.data;
}

export async function deleteSkill(skillId: number): Promise<void> {
  await clientDeleteSkill(skillId);
}
