import { api } from 'boot/axios';

export interface Skill {
  id: number;
  name: string;
}

export async function getSkills(): Promise<Skill[]> {
  const response = await api.get<Skill[]>('/v1/skills/');
  return response.data;
}

export async function createSkill(payload: Omit<Skill, 'id'>): Promise<Skill> {
  const response = await api.post<Skill>('/v1/skills/', payload);
  return response.data;
}

export async function updateSkill(skillId: number, payload: Partial<Skill>): Promise<Skill> {
  const response = await api.patch<Skill>(`/v1/skills/${skillId}/`, payload);
  return response.data;
}

export async function deleteSkill(skillId: number): Promise<void> {
  await api.delete(`/v1/skills/${skillId}/`);
}
