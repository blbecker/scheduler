import { api } from 'src/boot/axios';
import type { Worker } from 'src/models';

export const WorkersClient = {
  list(): Promise<Worker[]> {
    return api.get('/v1/workers').then((r) => r.data);
  },
  get(id: string): Promise<Worker> {
    return api.get(`/v1/workers/${id}`).then((r) => r.data);
  },
  // create(payload: CreateWorkerRequest): Promise<worker> {
  //   return api.post('/v1/workers', payload).then((r) => r.data);
  // },
  // update(id: string, payload: UpdateWorkerRequest): Promise<worker> {
  //   return api.patch(`/v1/workers/${id}`, payload).then((r) => r.data);
  // },
  delete(id: string): Promise<void> {
    return api.delete(`/v1/workers/${id}`).then(() => undefined);
  },
};
