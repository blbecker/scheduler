import { WorkersClient } from 'src/clients/workers/workers';
import type { Worker } from 'src/models/worker';

export const WorkersService = {
  async getWorkers(): Promise<Worker[]> {
    return await WorkersClient.list();
  },

  async getWorker(id: string): Promise<Worker> {
    return await WorkersClient.get(id);
  },

  // async createWorker(payload: Omit<Worker, 'id'>): Promise<Worker> {
  //   return await WorkersClient.create(payload);
  // }

  // async updateWorker(id: string, payload: Partial<Worker>): Promise<Worker> {
  //   return await WorkersClient.update(id, payload as Worker);
  // }

  async deleteWorker(id: string): Promise<void> {
    return await WorkersClient.delete(id);
  },
};
