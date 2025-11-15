import { api } from 'src/boot/axios';
import type { Skill } from 'src/models';

export const SkillsClient = {
  list(): Promise<Skill[]> {
    return api.get('/v1/skills').then((r) => r.data);
  },
  get(id: string): Promise<Skill> {
    return api.get(`/v1/skills/${id}`).then((r) => r.data);
  },
  // create(payload: CreateSkillRequest): Promise<skill> {
  //   return api.post('/v1/skills', payload).then((r) => r.data);
  // },
  // update(id: string, payload: UpdateSkillRequest): Promise<skill> {
  //   return api.patch(`/v1/skills/${id}`, payload).then((r) => r.data);
  // },
  delete(id: string): Promise<void> {
    return api.delete(`/v1/skills/${id}`).then(() => undefined);
  },
};
