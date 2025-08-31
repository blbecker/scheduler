import { api } from 'boot/axios';

export interface Shift {
  id: number;
  title: string;
  completed: boolean;
}

export async function getShifts(): Promise<Shift[]> {
  const response = await api.get<Shift[]>('/shifts/');
  return response.data;
}

export async function createShift(payload: Omit<Shift, 'id'>): Promise<Shift> {
  const response = await api.post<Shift>('/shifts/', payload);
  return response.data;
}

export async function updateShift(shiftId: number, payload: Partial<Shift>): Promise<Shift> {
  const response = await api.patch<Shift>(`/shifts/${shiftId}/`, payload);
  return response.data;
}
