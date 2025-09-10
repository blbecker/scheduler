import { getShifts as clientGetShifts, createShift as clientCreateShift, updateShift as clientUpdateShift } from '../clients/shiftClient';
import type { Shift } from '../models/shift';

export async function getShifts(): Promise<Shift[]> {
  const response = await clientGetShifts();
  return response.data;
}

export async function createShift(payload: Omit<Shift, 'id'>): Promise<Shift> {
  const response = await clientCreateShift(payload);
  return response.data;
}

export async function updateShift(shiftId: number, payload: Partial<Shift>): Promise<Shift> {
  const response = await clientUpdateShift(shiftId, payload);
  return response.data;
}
