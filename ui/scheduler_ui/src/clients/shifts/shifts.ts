import { api } from 'src/boot/axios';
import type { Shift } from 'src/models';

export const ShiftsClient = {
  list(): Promise<Shift[]> {
    return api.get('/v1/shifts').then((r) => r.data);
  },
  get(id: string): Promise<Shift> {
    return api.get(`/v1/shifts/${id}`).then((r) => r.data);
  },
  // create(payload: CreateShiftRequest): Promise<Shift> {
  //   return api.post('/shifts', payload).then((r) => r.data);
  // },
  // update(id: string, payload: UpdateShiftRequest): Promise<Shift> {
  //   return api.patch(`/shifts/${id}`, payload).then((r) => r.data);
  // },
  delete(id: string): Promise<void> {
    return api.delete(`/v1/shifts/${id}`).then(() => undefined);
  },
};
