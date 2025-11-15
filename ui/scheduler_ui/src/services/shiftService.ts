// services/shifts.ts
import { ShiftsClient } from 'src/clients/shifts/shifts';
import type { Shift } from 'src/models/shift';

export const ShiftsService = {
  async getShifts(): Promise<Shift[]> {
    console.log('Fetching shifts from ShiftsClient');
    return await ShiftsClient.list();
  },

  async getShift(id: string): Promise<Shift> {
    return await ShiftsClient.get(id);
  },

  // async createShift(payload: Omit<Shift, 'id'>): Promise<Shift> {
  //   return await ShiftsClient.create(payload);
  // }

  // async updateShift(id: string, payload: Partial<Shift>): Promise<Shift> {
  //   return await ShiftsClient.update(id, payload as Shift);
  // }

  async deleteShift(id: string): Promise<void> {
    return await ShiftsClient.delete(id);
  },
};
