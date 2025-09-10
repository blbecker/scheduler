import { api } from 'boot/axios';

export interface Worker {
  id: number;
  name: string;
  skills: number[];
}

export async function getWorkers(): Promise<Worker[]> {
  const response = await api.get<Worker[]>('/v1/workers/');
  return response.data;
}

export async function createWorker(payload: Omit<Worker, 'id'>): Promise<Worker> {
  const response = await api.post<Worker>('/v1/workers/', payload);
  return response.data;
}

export async function updateWorker(workerId: number, payload: Partial<Worker>): Promise<Worker> {
  const response = await api.patch<Worker>(`/v1/workers/${workerId}/`, payload);
  return response.data;
}

export async function deleteWorker(workerId: number): Promise<void> {
  await api.delete(`/v1/workers/${workerId}/`);
}
