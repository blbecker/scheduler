import { getWorkers as clientGetWorkers, createWorker as clientCreateWorker, updateWorker as clientUpdateWorker, deleteWorker as clientDeleteWorker } from '../clients/workerClient';

export interface Worker {
  id: number;
  name: string;
  skills: number[];
}

export async function getWorkers(): Promise<Worker[]> {
  const response = await clientGetWorkers();
  return response.data;
}

export async function createWorker(payload: Omit<Worker, 'id'>): Promise<Worker> {
  const response = await clientCreateWorker(payload);
  return response.data;
}

export async function updateWorker(workerId: number, payload: Partial<Worker>): Promise<Worker> {
  const response = await clientUpdateWorker(workerId, payload);
  return response.data;
}

export async function deleteWorker(workerId: number): Promise<void> {
  await clientDeleteWorker(workerId);
}
