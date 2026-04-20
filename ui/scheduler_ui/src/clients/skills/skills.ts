import { api } from 'src/boot/axios';
import type { SkillRead, SkillUpdate, SkillCreate } from 'src/models';

export const SkillsClient = {
  list(): Promise<SkillRead[]> {
    return api.get('/v1/skills').then((r) => r.data);
  },
  get(id: string): Promise<SkillRead> {
    return api.get(`/v1/skills/${id}`).then((r) => r.data);
  },
  create(payload: SkillCreate): Promise<SkillRead> {
    return api.post('/v1/skills', payload).then((r) => r.data);
  },
  update(id: string, payload: SkillUpdate): Promise<SkillRead> {
    return api.put(`/v1/skills/${id}`, payload).then((r) => r.data);
  },
  delete(id: string): Promise<void> {
    return api.delete(`/v1/skills/${id}`).then(() => undefined);
  },
};
